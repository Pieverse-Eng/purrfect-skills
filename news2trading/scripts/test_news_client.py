import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import news_client
from news_client import NewsClientError, publish_batch, read_text_file


BATCH_ID = '22222222-2222-4222-8222-222222222222'
INSTANCE_ID = '11111111-1111-4111-8111-111111111111'
TOKEN = 'super-secret-token'


class _Server:
	def __init__(self, responder):
		self.requests = []
		owner = self

		class Handler(BaseHTTPRequestHandler):
			def do_POST(self):
				length = int(self.headers.get('content-length', '0'))
				owner.requests.append(
					{
						'path': self.path,
						'authorization': self.headers.get('authorization'),
						'content_type': self.headers.get('content-type'),
						'body': self.rfile.read(length),
					}
				)
				responder(self)

			def log_message(self, _format, *_args):
				return

		self.httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
		self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

	def __enter__(self):
		self.thread.start()
		return self

	def __exit__(self, *_args):
		self.httpd.shutdown()
		self.httpd.server_close()
		self.thread.join()

	@property
	def url(self):
		return f'http://127.0.0.1:{self.httpd.server_port}'


def _json_response(handler, status, body, headers=None):
	payload = json.dumps(body).encode()
	handler.send_response(status)
	for name, value in (headers or {}).items():
		handler.send_header(name, value)
	handler.send_header('content-type', 'application/json')
	handler.send_header('content-length', str(len(payload)))
	handler.end_headers()
	handler.wfile.write(payload)


def _receipt(runtime='openclaw'):
	context = {'status': 'recorded', 'runtimeType': 'openclaw'}
	if runtime == 'hermes':
		context = {
			'status': 'required',
			'runtimeType': 'hermes',
			'sessionId': 'session-1',
			'sessionKey': 'agent:main:telegram:dm:42:100',
			'userId': '42',
		}
	return {
		'ok': True,
		'data': {
			'batchId': BATCH_ID,
			'channelAccepted': True,
			'runtimeType': runtime,
			'target': {'channel': 'telegram', 'chatId': '42', 'threadId': '100'},
			'context': context,
		},
	}


class NewsClientTest(unittest.TestCase):
	def test_malformed_credentials_fail_safely_without_sending(self):
		def respond(handler):
			_json_response(handler, 200, _receipt())

		with _Server(respond) as server, self._env(server.url), tempfile.TemporaryDirectory() as directory:
			text_file = Path(directory) / 'idea.txt'
			text_file.write_text('Neutral idea', encoding='utf-8')
			for token in (TOKEN + '\ninvalid', TOKEN + '\rinvalid', TOKEN + '\n continued', TOKEN + '密钥', TOKEN + '\v', TOKEN + '\u00a0'):
				with self.subTest(token_type=repr(token[len(TOKEN):])), patch.dict(os.environ, {'WALLET_API_TOKEN': token}):
					result = subprocess.run(
						[sys.executable, str(SCRIPT_DIR / 'publish.py'), '--batch-id', BATCH_ID, '--text-file', str(text_file)],
						capture_output=True, text=True, check=False,
					)
					self.assertEqual(result.returncode, 1)
					self.assertNotIn(TOKEN, result.stdout + result.stderr)
					self.assertNotIn('Traceback', result.stderr)
					diagnostic = json.loads(result.stderr)
					self.assertEqual(diagnostic['code'], 'invalid_hosted_identity')
					self.assertIs(diagnostic['channelAccepted'], False)
			self.assertEqual(server.requests, [])

	def _env(self, url):
		return patch.dict(
			os.environ,
			{
				'WALLET_API_URL': url,
				'WALLET_API_TOKEN': TOKEN,
				'INSTANCE_ID': INSTANCE_ID,
			},
			clear=False,
		)

	def test_posts_exact_json_to_fixed_instance_batch_route(self):
		def respond(handler):
			_json_response(handler, 200, _receipt())

		with _Server(respond) as server, self._env(server.url):
			result = publish_batch(BATCH_ID, 'Neutral idea', expected_runtime='openclaw')

		self.assertEqual(result['runtimeType'], 'openclaw')
		self.assertEqual(len(server.requests), 1)
		request = server.requests[0]
		self.assertEqual(
			request['path'],
			f'/v1/instances/{INSTANCE_ID}/news/batches/{BATCH_ID}/publish',
		)
		self.assertEqual(request['authorization'], f'Bearer {TOKEN}')
		self.assertEqual(request['content_type'], 'application/json')
		self.assertEqual(json.loads(request['body']), {'text': 'Neutral idea'})

	def test_accepts_complete_hermes_receipt_for_hermes_entry(self):
		def respond(handler):
			_json_response(handler, 200, _receipt('hermes'))

		with _Server(respond) as server, self._env(server.url):
			result = publish_batch(BATCH_ID, 'Idea', expected_runtime='hermes')

		self.assertEqual(result['context']['sessionId'], 'session-1')
		self.assertEqual(len(server.requests), 1)

	def test_does_not_follow_redirect_or_send_a_second_post(self):
		def respond(handler):
			_json_response(handler, 307, {'ok': False}, {'location': '/redirected'})

		with _Server(respond) as server, self._env(server.url):
			with self.assertRaises(NewsClientError) as raised:
				publish_batch(BATCH_ID, 'Idea', expected_runtime='openclaw')

		self.assertEqual(raised.exception.code, 'unexpected_http_status')
		self.assertEqual(raised.exception.channel_accepted, 'unknown')
		self.assertEqual([request['path'] for request in server.requests], [
			f'/v1/instances/{INSTANCE_ID}/news/batches/{BATCH_ID}/publish'
		])

	def test_known_api_errors_preserve_acceptance_semantics(self):
		cases = [
			('batch_missing', 404, None, False),
			('profile_paused', 409, None, False),
			('channel_missing', 409, False, False),
			('upstream_rejected', 502, False, False),
			('upstream_unknown', 502, 'unknown', 'unknown'),
			('context_missing', 502, True, True),
		]
		for code, status, response_acceptance, expected in cases:
			with self.subTest(code=code):
				body = {'ok': False, 'code': code, 'error': 'safe public error'}
				if response_acceptance is not None:
					body['channelAccepted'] = response_acceptance

				def respond(handler, status=status, body=body):
					_json_response(handler, status, body)

				with _Server(respond) as server, self._env(server.url):
					with self.assertRaises(NewsClientError) as raised:
						publish_batch(BATCH_ID, 'Idea', expected_runtime='openclaw')
				self.assertEqual(raised.exception.code, code)
				self.assertEqual(raised.exception.channel_accepted, expected)
				self.assertEqual(len(server.requests), 1)

	def test_wrong_runtime_and_malformed_success_are_unknown_not_unsent(self):
		cases = [_receipt('hermes'), {'ok': True, 'data': {'batchId': BATCH_ID}}]
		for body in cases:
			with self.subTest(body=body):
				def respond(handler, body=body):
					_json_response(handler, 200, body)

				with _Server(respond) as server, self._env(server.url):
					with self.assertRaises(NewsClientError) as raised:
						publish_batch(BATCH_ID, 'Idea', expected_runtime='openclaw')
				self.assertEqual(raised.exception.code, 'malformed_response')
				self.assertEqual(raised.exception.channel_accepted, 'unknown')
				self.assertEqual(len(server.requests), 1)

	def test_rejects_oversized_response_without_a_second_post(self):
		def respond(handler):
			payload = b'x' * (128 * 1024 + 1)
			handler.send_response(200)
			handler.send_header('content-length', str(len(payload)))
			handler.end_headers()
			handler.wfile.write(payload)

		with _Server(respond) as server, self._env(server.url):
			with self.assertRaises(NewsClientError) as raised:
				publish_batch(BATCH_ID, 'Idea', expected_runtime='openclaw')
		self.assertEqual(raised.exception.code, 'response_too_large')
		self.assertEqual(raised.exception.channel_accepted, 'unknown')
		self.assertEqual(len(server.requests), 1)

	def test_network_loss_is_unknown_and_does_not_expose_credentials(self):
		with socket.socket() as probe:
			probe.bind(('127.0.0.1', 0))
			url = f'http://127.0.0.1:{probe.getsockname()[1]}'
		with self._env(url):
			with self.assertRaises(NewsClientError) as raised:
				publish_batch(BATCH_ID, 'Idea', expected_runtime='openclaw')
		self.assertEqual(raised.exception.channel_accepted, 'unknown')
		self.assertNotIn(TOKEN, str(raised.exception))
		self.assertNotIn(url, str(raised.exception))

	def test_closing_response_read_uses_response_socket_and_absolute_deadline(self):
		class Clock:
			def __init__(self):
				self.values = iter((0.0, 0.0, 0.0, 0.11))

			def monotonic(self):
				return next(self.values, 0.11)

		clock = Clock()
		payload = json.dumps(_receipt()).encode()
		client_socket, server_socket = socket.socketpair()

		class CapturingConnection(news_client.http.client.HTTPConnection):
			def getresponse(self):
				self.captured_response = super().getresponse()
				return self.captured_response

		connection = CapturingConnection('platform.invalid')
		connection.sock = client_socket
		server_socket.sendall(
			b'HTTP/1.1 200 OK\r\n'
			b'Connection: close\r\n'
			+ f'Content-Length: {len(payload)}\r\n'.encode()
			+ b'Content-Type: application/json\r\n\r\n'
			+ payload
		)
		server_socket.shutdown(socket.SHUT_WR)
		with self._env('https://platform.invalid'), \
			patch.object(news_client, '_connection', return_value=connection), \
			patch.object(news_client.time, 'monotonic', side_effect=clock.monotonic), \
			patch.object(news_client, 'TOTAL_BUDGET_SECONDS', 0.1), \
			patch.object(news_client, 'IO_TIMEOUT_SECONDS', 0.08):
			with self.assertRaises(NewsClientError) as raised:
				publish_batch(BATCH_ID, 'Idea', expected_runtime='openclaw')

		self.assertEqual(raised.exception.code, 'network_error')
		self.assertEqual(raised.exception.channel_accepted, 'unknown')
		self.assertIsNone(connection.sock)
		server_socket.settimeout(0.1)
		request = server_socket.recv(64 * 1024)
		self.assertEqual(request.count(b'POST '), 1)
		self.assertIn(
			f'/v1/instances/{INSTANCE_ID}/news/batches/{BATCH_ID}/publish'.encode(),
			request,
		)
		connection.captured_response.close()
		client_socket.close()
		server_socket.close()

	def test_rejects_invalid_identity_and_text_before_network(self):
		with patch.dict(os.environ, {}, clear=True):
			with self.assertRaises(NewsClientError) as missing:
				publish_batch(BATCH_ID, 'Idea', expected_runtime='openclaw')
		self.assertEqual(missing.exception.channel_accepted, False)

		with self._env('http://127.0.0.1:1'):
			for batch_id, text in [
				('not-a-uuid', 'Idea'),
				(BATCH_ID, '   '),
			]:
				with self.subTest(batch_id=batch_id, text_length=len(text)):
					with self.assertRaises(NewsClientError) as raised:
						publish_batch(batch_id, text, expected_runtime='openclaw')
					self.assertEqual(raised.exception.channel_accepted, False)

	def test_supplementary_unicode_uses_two_utf16_units_per_character(self):
		def respond(handler):
			_json_response(handler, 200, _receipt())

		with _Server(respond) as server, self._env(server.url):
			result = publish_batch(BATCH_ID, '🚀' * 1500, expected_runtime='openclaw')
			with self.assertRaises(NewsClientError) as raised:
				publish_batch(BATCH_ID, '🚀' * 1501, expected_runtime='openclaw')

		self.assertEqual(result['runtimeType'], 'openclaw')
		self.assertEqual(raised.exception.code, 'invalid_text')
		self.assertEqual(raised.exception.channel_accepted, False)
		self.assertEqual(len(server.requests), 1)

	def test_reads_message_only_from_a_local_regular_file(self):
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / 'brief.txt'
			path.write_text('final brief\n', encoding='utf-8')
			self.assertEqual(read_text_file(path), 'final brief\n')
			with self.assertRaises(NewsClientError):
				read_text_file(Path(directory))


if __name__ == '__main__':
	unittest.main()

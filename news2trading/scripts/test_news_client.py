import importlib.util
import io
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stderr, redirect_stdout
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


def _context_missing():
	target = {'channel': 'telegram', 'chatId': '42', 'threadId': '100'}
	return {
		'ok': False, 'code': 'context_missing', 'channelAccepted': True,
		'target': target,
		'web': {'status': 'published', 'sessionId': 'web-session-1'},
		'external': {
			'status': 'accepted', 'channelAccepted': True,
			'contextRecorded': False, 'target': target,
		},
		'publishedText': 'Canonical analysis A',
	}


def _web_receipt(runtime='openclaw', external='disabled'):
	data = {
		'batchId': BATCH_ID,
		'web': {'status': 'published', 'sessionId': 'web-session-1'},
		'external': {'status': external},
	}
	if external == 'published':
		receipt = _receipt(runtime)['data']
		data.update(receipt)
		data['external']['receipt'] = receipt
	return {'ok': True, 'data': data}


def _context_missing_response(channel='telegram'):
	return {
		'ok': False, 'code': 'context_missing', 'channelAccepted': True,
		'target': {'channel': channel, 'chatId': '42', 'threadId': '100'},
		'web': {'status': 'published', 'sessionId': 'web-session-1'},
		'external': {
			'status': 'accepted', 'channelAccepted': True, 'contextRecorded': False,
			'target': {'channel': channel, 'chatId': '42', 'threadId': '100'},
		},
		'publishedText': 'Canonical analysis A',
	}


class NewsClientTest(unittest.TestCase):
	def test_context_missing_preserves_partial_publication_for_both_runtimes_and_channels(self):
		for runtime in ('openclaw', 'hermes'):
			for channel in ('telegram', 'line'):
				with self.subTest(runtime=runtime, channel=channel):
					body = _context_missing_response(channel)
					if runtime == 'hermes':
						body['batchId'] = BATCH_ID
					def respond(handler):
						_json_response(handler, 502, body)
					with _Server(respond) as server, self._env(server.url):
						with self.assertRaises(NewsClientError) as raised:
							publish_batch(BATCH_ID, 'Competing analysis B', expected_runtime=runtime)
					diagnostic = raised.exception.diagnostic()
					self.assertEqual(diagnostic['code'], 'context_missing')
					self.assertEqual(diagnostic['httpStatus'], 502)
					self.assertEqual(diagnostic['batchId'], BATCH_ID)
					for key in ('target', 'web', 'external', 'publishedText'):
						self.assertEqual(diagnostic[key], body[key])
					self.assertIs(diagnostic['ok'], False)
					self.assertIs(diagnostic['channelAccepted'], True)
					self.assertIs(diagnostic['contextRecorded'], False)
					self.assertEqual(len(server.requests), 1)

	def test_runtime_clis_preserve_api_partial_failure_without_retry_or_mirror(self):
		for runtime in ('openclaw', 'hermes'):
			with self.subTest(runtime=runtime):
				body = _context_missing_response()
				def respond(handler):
					_json_response(handler, 502, body)
				with _Server(respond) as server, self._env(server.url), tempfile.TemporaryDirectory() as directory:
					text_file = Path(directory) / 'brief.txt'
					text_file.write_text('Competing analysis B', encoding='utf-8')
					args = ['--batch-id', BATCH_ID, '--text-file', str(text_file)]
					if runtime == 'openclaw':
						result = subprocess.run([sys.executable, str(SCRIPT_DIR / 'publish.py'), *args],
							capture_output=True, text=True, check=False)
						code, stdout, stderr = result.returncode, result.stdout, result.stderr
					else:
						path = SCRIPT_DIR.parent / 'runtime-variants' / 'hermes' / 'scripts' / 'publish.py'
						spec = importlib.util.spec_from_file_location('hermes_api_error_test', path)
						module = importlib.util.module_from_spec(spec)
						spec.loader.exec_module(module)
						out, err = io.StringIO(), io.StringIO()
						with patch.object(module, 'ensure_hermes_python'), \
							patch.object(module, 'HermesContextAdapter') as adapter, \
							redirect_stdout(out), redirect_stderr(err):
							code = module.main(args)
						adapter.assert_not_called()
						stdout, stderr = out.getvalue(), err.getvalue()
				self.assertEqual(code, 1)
				self.assertEqual(stdout, '')
				self.assertNotIn(TOKEN, stderr)
				diagnostic = json.loads(stderr)
				self.assertIs(diagnostic['ok'], False)
				self.assertIs(diagnostic['channelAccepted'], True)
				self.assertIs(diagnostic['contextRecorded'], False)
				self.assertEqual(diagnostic['batchId'], BATCH_ID)
				for key in ('target', 'web', 'external', 'publishedText'):
					self.assertEqual(diagnostic[key], body[key])
				self.assertEqual(len(server.requests), 1)

	def test_external_only_context_missing_preserves_top_level_target(self):
		for runtime in ('openclaw', 'hermes'):
			for channel in ('telegram', 'line'):
				with self.subTest(runtime=runtime, channel=channel):
					target = _context_missing_response(channel)['target']
					body = {'ok': False, 'code': 'context_missing', 'channelAccepted': True,
						'target': target}
					def respond(handler):
						_json_response(handler, 502, body)
					with _Server(respond) as server, self._env(server.url):
						with self.assertRaises(NewsClientError) as raised:
							publish_batch(BATCH_ID, 'Final brief', expected_runtime=runtime)
					diagnostic = raised.exception.diagnostic()
					self.assertEqual(diagnostic['target'], target)
					self.assertEqual(diagnostic['batchId'], BATCH_ID)
					self.assertIs(diagnostic['ok'], False)
					self.assertIs(diagnostic['channelAccepted'], True)
					self.assertIs(diagnostic['contextRecorded'], False)
					for key in ('web', 'external', 'publishedText'):
						self.assertNotIn(key, diagnostic)
					self.assertEqual(len(server.requests), 1)

	def test_partial_error_details_omit_invalid_fields_without_losing_valid_destinations(self):
		cases = [
			('target', None), ('target', {'channel': 'email', 'chatId': '42'}),
			('target', {'channel': 'telegram', 'chatId': '42', 'threadId': 100}),
			('web', None), ('web', {'status': 'published', 'sessionId': ' '}),
			('web', {'status': 'disabled', 'sessionId': 'web-session-1'}),
			('external', None), ('external', {'status': 'published'}),
			('external', {'status': 'accepted', 'channelAccepted': True, 'contextRecorded': True}),
			('external', {'status': 'accepted', 'channelAccepted': 1, 'contextRecorded': False}),
			('external', {'status': 'accepted', 'channelAccepted': True, 'contextRecorded': False,
				'receipt': _receipt('hermes')['data']}),
			('external', {'status': 'accepted', 'channelAccepted': True, 'contextRecorded': False,
				'target': {'channel': 'email', 'chatId': '42'}}),
			('external', {'status': 'accepted', 'channelAccepted': True, 'contextRecorded': False,
				'target': {'channel': 'line', 'chatId': ' '}}),
			('external', {'status': 'accepted', 'channelAccepted': True, 'contextRecorded': False,
				'target': {'channel': 'line', 'chatId': '42', 'threadId': 1}}),
			('publishedText', None), ('publishedText', ''), ('publishedText', 42),
			('publishedText', 'x' * 3001), ('publishedText', '\ud800'),
		]
		for key, value in cases:
			with self.subTest(key=key, value=value):
				body = _context_missing_response()
				body[key] = value
				with self.assertRaises(NewsClientError) as raised:
					news_client._raise_api_error(body, 502, BATCH_ID)
				diagnostic = raised.exception.diagnostic()
				self.assertNotIn(key, diagnostic)
				for valid_key in {'target', 'web', 'external', 'publishedText'} - {key}:
					self.assertEqual(diagnostic[valid_key], body[valid_key])
				self.assertIs(diagnostic['channelAccepted'], True)
				self.assertIs(diagnostic['contextRecorded'], False)

	def test_partial_diagnostic_identifiers_are_bounded_and_control_free(self):
		invalid = ('', ' ', 42, 'x' * 513, '42\nunsafe', '42\runsafe', '42\x00', '42\x7f')
		for value in invalid:
			for field in ('chatId', 'threadId'):
				for location in ('target', 'external'):
					with self.subTest(value=value, field=field, location=location):
						body = _context_missing_response()
						target = body['target'] if location == 'target' else body['external']['target']
						target[field] = value
						with self.assertRaises(NewsClientError) as raised:
							news_client._raise_api_error(body, 502, BATCH_ID)
						diagnostic = raised.exception.diagnostic()
						self.assertNotIn(location, diagnostic)
						for key in {'target', 'web', 'external', 'publishedText'} - {location}:
							self.assertEqual(diagnostic[key], body[key])
						self.assertIs(diagnostic['channelAccepted'], True)
			with self.subTest(value=value, field='sessionId'):
				body = _context_missing_response()
				body['web']['sessionId'] = value
				with self.assertRaises(NewsClientError) as raised:
					news_client._raise_api_error(body, 502, BATCH_ID)
				diagnostic = raised.exception.diagnostic()
				self.assertNotIn('web', diagnostic)
				for key in ('target', 'external', 'publishedText'):
					self.assertEqual(diagnostic[key], body[key])
				self.assertIs(diagnostic['channelAccepted'], True)

	def test_partial_diagnostics_accept_identifier_limit_and_optional_thread(self):
		for with_thread in (True, False):
			with self.subTest(with_thread=with_thread):
				body = _context_missing_response('line')
				target = {'channel': 'line', 'chatId': 'x' * 512}
				if with_thread:
					target['threadId'] = 'x' * 512
				body['target'] = dict(target)
				body['external']['target'] = dict(target)
				body['web']['sessionId'] = 'x' * 512
				with self.assertRaises(NewsClientError) as raised:
					news_client._raise_api_error(body, 502, BATCH_ID)
				diagnostic = raised.exception.diagnostic()
				for key in ('target', 'web', 'external', 'publishedText'):
					self.assertEqual(diagnostic[key], body[key])

	def test_partial_diagnostics_filter_conflicting_targets_without_losing_other_evidence(self):
		cases = (
			{'channel': 'line', 'chatId': 'U_other'},
			{'channel': 'telegram', 'chatId': '84', 'threadId': '100'},
			{'channel': 'telegram', 'chatId': '42', 'threadId': '101'},
			{'channel': 'telegram', 'chatId': '42'},
		)
		for target in cases:
			with self.subTest(target=target):
				body = _context_missing_response()
				body['external']['target'] = target
				with self.assertRaises(NewsClientError) as raised:
					news_client._raise_api_error(body, 502, BATCH_ID)
				diagnostic = raised.exception.diagnostic()
				self.assertNotIn('external', diagnostic)
				for key in ('target', 'web', 'publishedText'):
					self.assertEqual(diagnostic[key], body[key])
				self.assertIs(diagnostic['channelAccepted'], True)
				self.assertIs(diagnostic['contextRecorded'], False)

	def test_partial_context_acceptance_does_not_require_top_level_target(self):
		body = _context_missing_response()
		body.pop('target')
		with self.assertRaises(NewsClientError) as raised:
			news_client._raise_api_error(body, 502, BATCH_ID)
		diagnostic = raised.exception.diagnostic()
		self.assertNotIn('target', diagnostic)
		self.assertEqual(diagnostic['external'], body['external'])
		self.assertIs(diagnostic['channelAccepted'], True)

	def test_partial_context_acceptance_does_not_require_a_target_or_canonical_text(self):
		body = _context_missing_response()
		body.pop('target')
		body['external'].pop('target')
		body.pop('publishedText')
		with self.assertRaises(NewsClientError) as raised:
			news_client._raise_api_error(body, 502, BATCH_ID)
		diagnostic = raised.exception.diagnostic()
		self.assertEqual(diagnostic['web'], body['web'])
		self.assertEqual(diagnostic['external'], body['external'])
		self.assertNotIn('target', diagnostic)
		self.assertNotIn('publishedText', diagnostic)
		self.assertIs(diagnostic['ok'], False)
		self.assertIs(diagnostic['contextRecorded'], False)

	def test_partial_error_details_are_allowlisted_and_bound_to_this_batch(self):
		body = _context_missing_response()
		body.update(error=TOKEN, token=TOKEN, contextRecorded=True)
		body['target']['token'] = TOKEN
		body['web']['token'] = TOKEN
		body['external']['token'] = TOKEN
		body['external']['target']['token'] = TOKEN
		with self.assertRaises(NewsClientError) as raised:
			news_client._raise_api_error(body, 502, BATCH_ID)
		diagnostic = raised.exception.diagnostic()
		self.assertNotIn(TOKEN, json.dumps(diagnostic))
		self.assertEqual(diagnostic['target'], _context_missing_response()['target'])
		self.assertEqual(diagnostic['web'], _context_missing_response()['web'])
		self.assertEqual(diagnostic['external'], _context_missing_response()['external'])
		self.assertIs(diagnostic['contextRecorded'], False)
		body['batchId'] = INSTANCE_ID
		with self.assertRaises(NewsClientError) as raised:
			news_client._raise_api_error(body, 502, BATCH_ID)
		self.assertEqual(raised.exception.code, 'malformed_response')
		self.assertEqual(raised.exception.channel_accepted, 'unknown')
		for key in ('batchId', 'target', 'web', 'external', 'publishedText'):
			self.assertNotIn(key, raised.exception.diagnostic())

	def test_partial_receipts_are_not_successes_or_details_of_unrelated_errors(self):
		body = _context_missing_response()
		for code, status, accepted in (('profile_paused', 409, False),
			('context_missing', 502, 'unknown'), ('context_missing', 502, 1),
			('context_missing', 400, True)):
			with self.subTest(code=code, status=status, accepted=accepted):
				body.update(code=code, channelAccepted=accepted)
				with self.assertRaises(NewsClientError) as raised:
					news_client._raise_api_error(body, status, BATCH_ID)
				for key in ('target', 'web', 'external', 'publishedText'):
					self.assertNotIn(key, raised.exception.diagnostic())
		body = _web_receipt()
		body['data']['external'] = _context_missing_response()['external']
		with self.assertRaises(NewsClientError) as raised:
			news_client._validate_receipt(body, BATCH_ID, 'openclaw')
		self.assertEqual(raised.exception.code, 'malformed_response')

	def test_web_only_cli_confirms_web_without_claiming_external_delivery(self):
		def respond(handler):
			_json_response(handler, 200, _web_receipt())

		with _Server(respond) as server, self._env(server.url), tempfile.TemporaryDirectory() as directory:
			text_file = Path(directory) / 'brief.txt'
			text_file.write_text('Neutral analysis', encoding='utf-8')
			result = subprocess.run(
				[sys.executable, str(SCRIPT_DIR / 'publish.py'), '--batch-id', BATCH_ID, '--text-file', str(text_file)],
				capture_output=True, text=True, check=False,
			)
		self.assertEqual(result.returncode, 0, result.stderr)
		data = json.loads(result.stdout)
		self.assertEqual(data['web'], {'status': 'published', 'sessionId': 'web-session-1'})
		self.assertEqual(data['external'], {'status': 'disabled'})
		self.assertNotIn('channelAccepted', data)
		self.assertEqual(len(server.requests), 1)

	def test_web_publication_retains_external_rejected_or_unknown_without_retry(self):
		for status in ('rejected', 'unknown'):
			with self.subTest(status=status):
				def respond(handler):
					_json_response(handler, 200, _web_receipt(external=status))
				with _Server(respond) as server, self._env(server.url):
					data = publish_batch(BATCH_ID, 'Neutral analysis', expected_runtime='openclaw')
				self.assertEqual(data['web']['status'], 'published')
				self.assertEqual(data['external']['status'], status)
				self.assertNotIn('channelAccepted', data)
				self.assertEqual(len(server.requests), 1)

	def test_web_receipt_requires_durable_session_and_matching_external_runtime(self):
		cases = [_web_receipt(), _web_receipt('hermes', 'published')]
		cases[0]['data']['web']['sessionId'] = ''
		for body in cases:
			with self.subTest(body=body):
				def respond(handler):
					_json_response(handler, 200, body)
				with _Server(respond) as server, self._env(server.url):
					with self.assertRaises(NewsClientError) as raised:
						publish_batch(BATCH_ID, 'Neutral analysis', expected_runtime='openclaw')
				self.assertEqual(raised.exception.channel_accepted, 'unknown')
				self.assertEqual(len(server.requests), 1)

	def test_web_and_external_success_retains_runtime_context_and_separate_destinations(self):
		for runtime in ('openclaw', 'hermes'):
			with self.subTest(runtime=runtime):
				def respond(handler):
					_json_response(handler, 200, _web_receipt(runtime, 'published'))
				with _Server(respond) as server, self._env(server.url):
					data = publish_batch(BATCH_ID, 'Neutral analysis', expected_runtime=runtime)
				self.assertEqual(data['web']['sessionId'], 'web-session-1')
				self.assertEqual(data['external']['receipt'], _receipt(runtime)['data'])
				self.assertEqual(data['context']['runtimeType'], runtime)
				self.assertEqual(len(server.requests), 1)

	def test_canonical_publication_text_is_additive_and_validated(self):
		for text in ('Canonical analysis A', None, '', '  ', 42, 'x' * 3001):
			with self.subTest(text_type=type(text).__name__):
				body = _web_receipt('hermes', 'published')
				body['data']['publishedText'] = text
				def respond(handler):
					_json_response(handler, 200, body)
				with _Server(respond) as server, self._env(server.url):
					if text == 'Canonical analysis A':
						data = publish_batch(BATCH_ID, 'Competing analysis B', expected_runtime='hermes')
						self.assertEqual(data['publishedText'], text)
					else:
						with self.assertRaises(NewsClientError) as raised:
							publish_batch(BATCH_ID, 'Competing analysis B', expected_runtime='hermes')
						self.assertEqual(raised.exception.code, 'malformed_response')
						self.assertEqual(raised.exception.channel_accepted, 'unknown')
				self.assertEqual(len(server.requests), 1)

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
				for key in ('batchId', 'web', 'external', 'publishedText'):
					self.assertNotIn(key, raised.exception.diagnostic())
				self.assertEqual(len(server.requests), 1)

	def test_context_missing_preserves_partial_publication_for_both_runtimes(self):
		for runtime in ('openclaw', 'hermes'):
			with self.subTest(runtime=runtime):
				body = _context_missing()
				def respond(handler):
					_json_response(handler, 502, body)
				with _Server(respond) as server, self._env(server.url):
					with self.assertRaises(NewsClientError) as raised:
						publish_batch(BATCH_ID, 'Competing analysis B', expected_runtime=runtime)
				diagnostic = raised.exception.diagnostic()
				for key in ('target', 'web', 'external', 'publishedText'):
					self.assertEqual(diagnostic[key], body[key])
				self.assertIs(diagnostic['channelAccepted'], True)
				self.assertIs(diagnostic['contextRecorded'], False)
				self.assertEqual(diagnostic['httpStatus'], 502)
				self.assertEqual(len(server.requests), 1)

	def test_openclaw_cli_retains_saved_web_on_context_missing_without_retry(self):
		body = _context_missing()
		def respond(handler):
			_json_response(handler, 502, body)
		with _Server(respond) as server, self._env(server.url), tempfile.TemporaryDirectory() as directory:
			text_file = Path(directory) / 'brief.txt'
			text_file.write_text('Competing analysis B', encoding='utf-8')
			result = subprocess.run(
				[sys.executable, str(SCRIPT_DIR / 'publish.py'), '--batch-id', BATCH_ID, '--text-file', str(text_file)],
				capture_output=True, text=True, check=False,
			)
		self.assertEqual(result.returncode, 1)
		self.assertEqual(result.stdout, '')
		diagnostic = json.loads(result.stderr)
		for key in ('target', 'web', 'external', 'publishedText'):
			self.assertEqual(diagnostic[key], body[key])
		self.assertNotIn(TOKEN, result.stderr)
		self.assertEqual(len(server.requests), 1)

	def test_partial_diagnostics_validate_fields_and_do_not_echo_arbitrary_payload(self):
		cases = (
			('target', {'channel': 'email', 'chatId': '42'}),
			('target', {'channel': 'telegram', 'chatId': '42\nunsafe'}),
			('target', {'channel': 'telegram', 'chatId': 'x' * 513}),
			('target', {'channel': 'telegram', 'chatId': '42', 'threadId': 100}),
			('web', {'status': 'published', 'sessionId': ''}),
			('web', {'status': 'published', 'sessionId': 'x' * 513}),
			('external', {'status': 'published', 'receipt': _receipt()['data']}),
			('external', {'status': 'accepted', 'channelAccepted': 1, 'contextRecorded': False}),
			('external', {'status': 'accepted', 'channelAccepted': True, 'contextRecorded': True}),
			('publishedText', None),
			('publishedText', ' '),
			('publishedText', 'x' * 3001),
		)
		for field, invalid in cases:
			with self.subTest(field=field, invalid=invalid):
				body = _context_missing()
				body[field] = invalid
				body['credential'] = TOKEN
				with self.assertRaises(NewsClientError) as raised:
					news_client._raise_api_error(body, 502, BATCH_ID)
				diagnostic = raised.exception.diagnostic()
				self.assertNotIn(field, diagnostic)
				self.assertIs(diagnostic['channelAccepted'], True)
				self.assertEqual(diagnostic['code'], 'context_missing')
				self.assertNotIn(TOKEN, json.dumps(diagnostic))

	def test_partial_diagnostics_strip_unknown_keys_and_conflicting_targets(self):
		body = _context_missing()
		for field in ('target', 'web', 'external'):
			body[field] = {**body[field], 'credential': TOKEN}
		body['external']['target'] = {'channel': 'line', 'chatId': 'U_other'}
		with self.assertRaises(NewsClientError) as raised:
			news_client._raise_api_error(body, 502, BATCH_ID)
		diagnostic = raised.exception.diagnostic()
		self.assertNotIn('external', diagnostic)
		self.assertEqual(diagnostic['target'], _context_missing()['target'])
		self.assertEqual(diagnostic['web'], _context_missing()['web'])
		self.assertEqual(diagnostic['publishedText'], body['publishedText'])
		self.assertNotIn(TOKEN, json.dumps(diagnostic))

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

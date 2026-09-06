import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERMES_PUBLISH = ROOT / 'runtime-variants' / 'hermes' / 'scripts' / 'publish.py'
BATCH_ID = '22222222-2222-4222-8222-222222222222'


def _load_publish_module():
	spec = importlib.util.spec_from_file_location('news2trading_hermes_publish', HERMES_PUBLISH)
	module = importlib.util.module_from_spec(spec)
	assert spec.loader is not None
	spec.loader.exec_module(module)
	return module


class FakeAdapter:
	def __init__(self, *, mirror_results=(True,), row=None, messages=None, found='session-1'):
		self.mirror_results = list(mirror_results)
		self.row = row or {
			'id': 'session-1',
			'source': 'telegram',
			'chat_id': '42',
			'chat_type': 'dm',
			'thread_id': '100',
			'user_id': '42',
			'session_key': 'agent:main:telegram:dm:42:100',
		}
		self.messages = list(messages or [])
		self.found = found
		self.mirror_calls = []

	def find_session_id(self, **_origin):
		return self.found

	def get_session(self, _session_id):
		return self.row

	def get_messages(self, _session_id):
		return list(self.messages)

	def mirror(self, *, text, **kwargs):
		self.mirror_calls.append({'text': text, **kwargs})
		result = self.mirror_results.pop(0) if self.mirror_results else False
		if result:
			self.messages.append({'role': 'user', 'content': text})
		return result


def _receipt(**overrides):
	receipt = {
		'batchId': BATCH_ID,
		'channelAccepted': True,
		'runtimeType': 'hermes',
		'target': {'channel': 'telegram', 'chatId': '42', 'threadId': '100'},
		'context': {
			'status': 'required',
			'runtimeType': 'hermes',
			'sessionId': 'session-1',
			'sessionKey': 'agent:main:telegram:dm:42:100',
			'userId': '42',
		},
	}
	receipt.update(overrides)
	return receipt


class HermesContextUnitTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.publish = _load_publish_module()

	def test_validates_receipt_route_then_appends_marker_as_user_and_reads_back(self):
		adapter = FakeAdapter()
		result = self.publish.mirror_receipt(_receipt(), 'Final brief', adapter=adapter)
		self.assertTrue(result['contextRecorded'])
		self.assertTrue(result['mirrored'])
		self.assertEqual(len(adapter.mirror_calls), 1)
		self.assertEqual(adapter.mirror_calls[0], {
			'platform': 'telegram',
			'chat_id': '42',
			'thread_id': '100',
			'user_id': '42',
			'text': f'[Purr-Fect News batch {BATCH_ID}]\nFinal brief',
			'source_label': 'news2trading',
			'role': 'user',
		})

	def test_existing_exact_batch_marker_is_idempotent(self):
		text = f'[Purr-Fect News batch {BATCH_ID}]\nFinal brief'
		adapter = FakeAdapter(messages=[{'role': 'user', 'content': text}])
		result = self.publish.mirror_receipt(_receipt(), 'Final brief', adapter=adapter)
		self.assertTrue(result['contextRecorded'])
		self.assertFalse(result['mirrored'])
		self.assertEqual(adapter.mirror_calls, [])

	def test_same_batch_with_different_text_is_a_conflict(self):
		text = f'[Purr-Fect News batch {BATCH_ID}]\nDifferent brief'
		adapter = FakeAdapter(messages=[{'role': 'user', 'content': text}])
		with self.assertRaises(self.publish.ContextMirrorError) as raised:
			self.publish.mirror_receipt(_receipt(), 'Final brief', adapter=adapter)
		self.assertEqual(raised.exception.code, 'batch_marker_conflict')
		self.assertEqual(adapter.mirror_calls, [])

	def test_rejects_finder_fallback_to_wrong_session_or_origin(self):
		cases = [
			FakeAdapter(found='wrong-session'),
			FakeAdapter(row={
				'id': 'different-session', 'source': 'telegram', 'chat_id': '42',
				'chat_type': 'dm', 'thread_id': '100', 'user_id': '42',
				'session_key': 'agent:main:telegram:dm:42:100',
			}),
			FakeAdapter(row={
				'id': 'session-1', 'source': 'telegram', 'chat_id': '42',
				'chat_type': 'dm', 'thread_id': '100', 'user_id': 'other',
				'session_key': 'agent:main:telegram:dm:42:100',
			}),
		]
		for adapter in cases:
			with self.subTest(adapter=adapter):
				with self.assertRaises(self.publish.ContextMirrorError):
					self.publish.mirror_receipt(_receipt(), 'Final brief', adapter=adapter)
				self.assertEqual(adapter.mirror_calls, [])

	def test_retries_only_mirror_once_when_readback_is_missing(self):
		class NoWriteAdapter(FakeAdapter):
			def mirror(self, *, text, **kwargs):
				self.mirror_calls.append({'text': text, **kwargs})
				return True

		adapter = NoWriteAdapter(mirror_results=(True, True))
		with self.assertRaises(self.publish.ContextMirrorError) as raised:
			self.publish.mirror_receipt(_receipt(), 'Final brief', adapter=adapter)
		self.assertEqual(raised.exception.code, 'context_readback_missing')
		self.assertEqual(len(adapter.mirror_calls), 2)

	def test_readback_exception_is_bounded_and_reported_as_incomplete_context(self):
		class BrokenReadAdapter(FakeAdapter):
			def get_messages(self, _session_id):
				raise OSError('locked')

		adapter = BrokenReadAdapter(mirror_results=(False, False))
		with self.assertRaises(self.publish.ContextMirrorError) as raised:
			self.publish.mirror_receipt(_receipt(), 'Final brief', adapter=adapter)
		self.assertEqual(raised.exception.code, 'context_readback_missing')
		self.assertEqual(len(adapter.mirror_calls), 2)

	def test_publish_is_called_once_when_both_mirror_attempts_fail(self):
		calls = []
		adapter = FakeAdapter(mirror_results=(False, False))

		def publisher(batch_id, text, expected_runtime):
			calls.append((batch_id, text, expected_runtime))
			return _receipt()

		with self.assertRaises(self.publish.ContextMirrorError):
			self.publish.publish_and_mirror(
				BATCH_ID, 'Final brief', publisher=publisher, adapter=adapter
			)
		self.assertEqual(calls, [(BATCH_ID, 'Final brief', 'hermes')])
		self.assertEqual(len(adapter.mirror_calls), 2)


@unittest.skipUnless(
	os.environ.get('NEWS2TRADING_HERMES_REAL') == '1',
	'set NEWS2TRADING_HERMES_REAL=1 with the pinned Hermes PYTHONPATH',
)
class HermesPinnedRuntimeTest(unittest.TestCase):
	def test_real_session_store_routes_and_readback(self):
		with tempfile.TemporaryDirectory(prefix='news2trading-hermes-') as home:
			os.environ['HERMES_HOME'] = home
			from gateway.config import GatewayConfig, Platform
			from gateway.session import SessionSource, SessionStore

			publish = _load_publish_module()
			store = SessionStore(Path(home) / 'sessions', GatewayConfig())
			self.assertIsNotNone(store._db)

			def source(platform, chat, thread=None):
				return SessionSource(
					platform=Platform(platform), chat_id=chat, chat_type='dm',
					user_id=chat, thread_id=thread,
				)

			def receipt(entry, platform, chat, thread=None, batch=BATCH_ID):
				return {
					'batchId': batch,
					'channelAccepted': True,
					'runtimeType': 'hermes',
					'target': {
						'channel': platform, 'chatId': chat,
						**({'threadId': thread} if thread is not None else {}),
					},
					'context': {
						'status': 'required', 'runtimeType': 'hermes',
						'sessionId': entry.session_id, 'sessionKey': entry.session_key,
						'userId': chat,
					},
				}

			main = store.get_or_create_session(source('telegram', '42'))
			other = store.get_or_create_session(source('telegram', '84', '100'))
			topic = store.get_or_create_session(source('telegram', '42', '100'))
			before = store._db.get_session(topic.session_id)['message_count']
			result = publish.mirror_receipt(receipt(topic, 'telegram', '42', '100'), 'TG brief')
			self.assertTrue(result['contextRecorded'])
			self.assertGreater(store._db.get_session(topic.session_id)['message_count'], before)
			transcript = store.load_transcript(topic.session_id)
			self.assertTrue(any('TG brief' in str(message.get('content')) for message in transcript))
			self.assertFalse(any('TG brief' in str(message.get('content')) for message in store.load_transcript(main.session_id)))
			self.assertFalse(any('TG brief' in str(message.get('content')) for message in store.load_transcript(other.session_id)))

			count = store._db.get_session(topic.session_id)['message_count']
			duplicate = publish.mirror_receipt(receipt(topic, 'telegram', '42', '100'), 'TG brief')
			self.assertFalse(duplicate['mirrored'])
			self.assertEqual(store._db.get_session(topic.session_id)['message_count'], count)

			new_topic = store.get_or_create_session(source('telegram', '42', '101'))
			publish.mirror_receipt(
				receipt(new_topic, 'telegram', '42', '101', '33333333-3333-4333-8333-333333333333'),
				'New topic brief',
			)
			self.assertTrue(any(
				'New topic brief' in str(message.get('content'))
				for message in store.load_transcript(new_topic.session_id)
			))

			line = store.get_or_create_session(source('line', 'U_news_user'))
			publish.mirror_receipt(
				receipt(line, 'line', 'U_news_user', batch='44444444-4444-4444-8444-444444444444'),
				'LINE brief',
			)
			self.assertTrue(any(
				'LINE brief' in str(message.get('content'))
				for message in store.load_transcript(line.session_id)
			))
			self.assertFalse(any(
				'New topic brief' in str(message.get('content'))
				for message in store.load_transcript(line.session_id)
			))
			store._db.close()


if __name__ == '__main__':
	unittest.main()

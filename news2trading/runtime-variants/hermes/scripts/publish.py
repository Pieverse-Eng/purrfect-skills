#!/usr/bin/env python3
"""Hermes entry point: publish once, then verify and mirror local context."""

import argparse
import json
import sys
from pathlib import Path

try:
	from news_client import NewsClientError, publish_batch, read_text_file
except ModuleNotFoundError:
	# Source-tree tests run before materialization; installed artifacts keep the
	# common client beside this entry point.
	_source_scripts = Path(__file__).resolve().parents[3] / 'scripts'
	sys.path.insert(0, str(_source_scripts))
	from news_client import NewsClientError, publish_batch, read_text_file


class ContextMirrorError(Exception):
	def __init__(self, code, message):
		super().__init__(message)
		self.code = code

	def diagnostic(self):
		return {
			'ok': False,
			'code': self.code,
			'error': str(self),
			'channelAccepted': True,
			'contextRecorded': False,
		}


class HermesContextAdapter:
	"""Thin adapter over the runtime's existing SessionDB and mirror APIs."""

	def find_session_id(self, *, platform, chat_id, thread_id, user_id):
		from gateway.mirror import _find_session_id

		return _find_session_id(
			platform, chat_id, thread_id=thread_id, user_id=user_id
		)

	def get_session(self, session_id):
		from hermes_state import SessionDB

		db = SessionDB()
		try:
			return db.get_session(session_id)
		finally:
			db.close()

	def get_messages(self, session_id):
		from hermes_state import SessionDB

		db = SessionDB()
		try:
			return db.get_messages(session_id)
		finally:
			db.close()

	def mirror(self, *, platform, chat_id, text, source_label, thread_id, user_id, role):
		from gateway.mirror import mirror_to_session

		return mirror_to_session(
			platform,
			chat_id,
			text,
			source_label=source_label,
			thread_id=thread_id,
			user_id=user_id,
			role=role,
		)


def mirror_receipt(receipt, text, adapter=None):
	"""Mirror the exact final brief only after validating the prewarmed route."""
	adapter = adapter or HermesContextAdapter()
	target = receipt['target']
	context = receipt['context']
	platform = target['channel']
	chat_id = target['chatId']
	thread_id = target.get('threadId')
	user_id = context.get('userId') or chat_id
	session_id = context['sessionId']
	session_key = context['sessionKey']
	try:
		found = adapter.find_session_id(
			platform=platform,
			chat_id=chat_id,
			thread_id=thread_id,
			user_id=user_id,
		)
	except Exception:
		raise ContextMirrorError(
			'session_route_unavailable',
			'Channel accepted the message, but the local session route could not be read.',
		)
	if found != session_id:
		raise ContextMirrorError(
			'session_route_mismatch',
			'Channel accepted the message, but the receipt session route did not match.',
		)
	try:
		row = adapter.get_session(session_id)
	except Exception:
		raise ContextMirrorError(
			'session_origin_unavailable',
			'Channel accepted the message, but the stored session origin could not be read.',
		)
	if not _route_matches(
		row,
		session_id=session_id,
		platform=platform,
		chat_id=chat_id,
		thread_id=thread_id,
		user_id=user_id,
		session_key=session_key,
	):
		raise ContextMirrorError(
			'session_origin_mismatch',
			'Channel accepted the message, but the stored session origin did not match.',
		)

	marker = f'[Purr-Fect News batch {receipt["batchId"]}]'
	mirrored_text = marker + '\n' + text
	for attempt in range(2):
		messages = _read_messages(adapter, session_id)
		state = _marker_state(messages, marker, mirrored_text) if messages is not None else 'missing'
		if state == 'exact':
			return {'channelAccepted': True, 'contextRecorded': True, 'mirrored': attempt > 0}
		if state == 'conflict':
			raise ContextMirrorError(
				'batch_marker_conflict',
				'Channel accepted the message, but this batch marker has different local text.',
			)
		try:
			adapter.mirror(
				platform=platform,
				chat_id=chat_id,
				text=mirrored_text,
				source_label='news2trading',
				thread_id=thread_id,
				user_id=user_id,
				role='user',
			)
		except Exception:
			pass
		messages = _read_messages(adapter, session_id)
		if messages is not None and _marker_state(messages, marker, mirrored_text) == 'exact':
			return {'channelAccepted': True, 'contextRecorded': True, 'mirrored': True}
	messages = _read_messages(adapter, session_id)
	if messages is not None and _marker_state(messages, marker, mirrored_text) == 'conflict':
		raise ContextMirrorError(
			'batch_marker_conflict',
			'Channel accepted the message, but this batch marker has different local text.',
		)
	raise ContextMirrorError(
		'context_readback_missing',
		'Channel accepted the message, but local context could not be read back after two mirror attempts.',
	)


def publish_and_mirror(batch_id, text, publisher=publish_batch, adapter=None):
	receipt = publisher(batch_id, text, expected_runtime='hermes')
	result = mirror_receipt(receipt, text, adapter=adapter)
	return {
		'ok': True,
		'batchId': receipt['batchId'],
		'runtimeType': 'hermes',
		**result,
	}


def _route_matches(row, *, session_id, platform, chat_id, thread_id, user_id, session_key):
	if not isinstance(row, dict):
		return False
	if (
		str(row.get('id') or '') != str(session_id)
		or str(row.get('source') or '').lower() != platform.lower()
		or str(row.get('chat_id') or '') != str(chat_id)
		or str(row.get('chat_type') or '').lower() != 'dm'
		or str(row.get('thread_id') or '') != str(thread_id or '')
		or str(row.get('user_id') or '') != str(user_id)
		or str(row.get('session_key') or '') != str(session_key)
	):
		return False
	origin_raw = row.get('origin_json')
	if origin_raw:
		try:
			origin = json.loads(origin_raw) if isinstance(origin_raw, str) else origin_raw
		except (TypeError, json.JSONDecodeError):
			return False
		if not isinstance(origin, dict):
			return False
		if (
			str(origin.get('platform') or '').lower() != platform.lower()
			or str(origin.get('chat_id') or '') != str(chat_id)
			or str(origin.get('thread_id') or '') != str(thread_id or '')
			or str(origin.get('user_id') or '') != str(user_id)
		):
			return False
	return True


def _read_messages(adapter, session_id):
	try:
		messages = adapter.get_messages(session_id)
		return messages if isinstance(messages, list) else None
	except Exception:
		return None


def _marker_state(messages, marker, expected_text):
	for message in messages:
		content = message.get('content') if isinstance(message, dict) else None
		if content == expected_text:
			return 'exact'
		if isinstance(content, str) and content.startswith(marker):
			return 'conflict'
	return 'missing'


def _parser():
	parser = argparse.ArgumentParser(description='Publish and mirror one Purr-Fect News batch.')
	parser.add_argument('--batch-id', required=True)
	parser.add_argument('--text-file', required=True)
	return parser


def main(argv=None):
	args = _parser().parse_args(argv)
	try:
		text = read_text_file(args.text_file)
		print(json.dumps(
			publish_and_mirror(args.batch_id, text), ensure_ascii=False, separators=(',', ':')
		))
		return 0
	except NewsClientError as error:
		print(json.dumps(error.diagnostic(), separators=(',', ':')), file=sys.stderr)
		return 1
	except ContextMirrorError as error:
		print(json.dumps(error.diagnostic(), separators=(',', ':')), file=sys.stderr)
		return 2
	except (ImportError, KeyError, TypeError):
		error = ContextMirrorError(
			'context_runtime_unavailable',
			'Channel acceptance is known, but Hermes context verification is unavailable.',
		)
		print(json.dumps(error.diagnostic(), separators=(',', ':')), file=sys.stderr)
		return 2


if __name__ == '__main__':
	raise SystemExit(main())

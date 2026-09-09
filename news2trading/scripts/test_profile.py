"""Exercise the installed CLI against a local stateful Profile API, not production."""

import copy
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SCRIPT = Path(__file__).with_name('profile.py')
INSTANCE = '11111111-1111-4111-8111-111111111111'
TOKEN = 'fixture-token-not-a-real-secret'
BASE = '/v1/instances/' + INSTANCE + '/news/profile'


def fixture():
	return {
		'instanceId': INSTANCE, 'status': 'active', 'version': 7,
		'preferredLanguage': 'zh-CN', 'deliveryIntervalMinutes': 240,
		'interestOriginal': '关注以太坊安全事件；排除空投。',
		'interestEn': 'Follow Ethereum security incidents; exclude airdrops.',
		'includeTerms': [{'type': 'event_type', 'displayValue': 'Exploit Security',
			'normalizedValue': 'exploit security'}],
		'excludeTerms': [], 'sourceAllowlist': ['panews'], 'sourceBlocklist': [],
		'minScore': 30, 'explorationEnabled': False,
	}


class ProfileTests(unittest.TestCase):
	def setUp(self):
		self.profile = fixture()
		self.requests = []
		self.failure = None
		self.receipt_change = None
		self.race = False
		self.drop_write_response = False
		case = self

		class Handler(BaseHTTPRequestHandler):
			def log_message(self, *args):
				pass

			def do_GET(self):
				self.handle_api()

			def do_PUT(self):
				self.handle_api()

			def do_POST(self):
				self.handle_api()

			def handle_api(self):
				body = json.loads(self.rfile.read(int(self.headers['Content-Length']))) if self.headers.get('Content-Length') else None
				case.requests.append((self.command, self.path, body))
				if self.headers.get('Authorization') != 'Bearer ' + TOKEN:
					return self.reply(403, {'ok': False, 'error': 'Token not authorized for this instance'})
				if case.failure:
					return self.reply(case.failure, {'ok': False, 'error': TOKEN})
				if self.path not in (BASE, BASE + '/pause'):
					return self.reply(404, {'ok': False})
				if self.command == 'GET':
					return self.reply(200, {'ok': True, 'data': case.profile})
				if case.race:
					case.profile['version'] += 1
					case.profile['deliveryIntervalMinutes'] = 60
				if body['expectedVersion'] != (case.profile['version'] if case.profile else 0):
					return self.reply(409, {'ok': False, 'code': 'version_conflict'})
				if self.command == 'POST':
					case.profile.update(status='paused', version=case.profile['version'] + 1)
				else:
					case.profile = dict(body, instanceId=INSTANCE, status='active', version=body['expectedVersion'] + 1)
					case.profile.pop('expectedVersion')
					for key in ('includeTerms', 'excludeTerms'):
						case.profile[key] = [dict(type=t['type'], displayValue=t['value'], normalizedValue=t['value'].lower()) for t in body[key]]
				data = copy.deepcopy(case.profile)
				if case.receipt_change:
					data.update(case.receipt_change)
				if case.drop_write_response:
					self.close_connection = True
					return
				self.reply(200, {'ok': True, 'data': data})

			def reply(self, status, data):
				raw = json.dumps(data).encode()
				self.send_response(status)
				self.send_header('Content-Length', str(len(raw)))
				self.end_headers()
				self.wfile.write(raw)

		self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
		self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
		self.thread.start()
		self.directory = tempfile.TemporaryDirectory()

	def tearDown(self):
		self.server.shutdown()
		self.server.server_close()
		self.thread.join()
		self.directory.cleanup()

	def run_cli(self, action, changes=None, version=7, extra=(), env=None):
		self.assertTrue(SCRIPT.is_file(), 'Missing executable Profile workflow')
		args = [sys.executable, str(SCRIPT), action]
		if action in ('update', 'pause', 'resume'):
			args += ['--expected-version', str(version)]
		if changes is not None:
			path = Path(self.directory.name) / 'changes.json'
			path.write_text(json.dumps(changes, ensure_ascii=False))
			args += ['--changes-file', str(path)]
		args += list(extra)
		process = subprocess.run(args, text=True, capture_output=True, timeout=10, env={
			**os.environ, 'WALLET_API_URL': f'http://127.0.0.1:{self.server.server_port}',
			'WALLET_API_TOKEN': TOKEN, 'INSTANCE_ID': INSTANCE, **(env or {}),
		})
		self.assertNotIn(TOKEN, process.stdout + process.stderr)
		return process.returncode, json.loads(process.stdout)

	def test_cadence_update_preserves_actual_platform_preferences_and_legacy_terms(self):
		before = copy.deepcopy(self.profile)
		code, result = self.run_cli('update', {'deliveryIntervalMinutes': 20})
		self.assertEqual(code, 0, result)
		self.assertTrue(result['verified'])
		self.assertEqual(self.profile, dict(before, version=8, deliveryIntervalMinutes=20))
		self.assertIn('unverified_legacy_event_selector', result['warnings'])

	def test_read_uses_hosted_identity_without_exposing_it(self):
		code, result = self.run_cli('get')
		self.assertEqual(code, 0)
		self.assertEqual(result['profile'], self.profile)
		self.assertEqual(len(self.requests), 1)

	def test_paused_update_never_silently_resumes(self):
		self.profile['status'] = 'paused'
		code, result = self.run_cli('update', {'deliveryIntervalMinutes': 20})
		self.assertNotEqual(code, 0)
		self.assertEqual(result['code'], 'resume_required')
		self.assertEqual(self.profile['status'], 'paused')
		self.assertFalse(any(m != 'GET' for m, _, _ in self.requests))

	def test_explicit_resume_and_pause_verify_status(self):
		self.profile['status'] = 'paused'
		code, result = self.run_cli('resume')
		self.assertEqual(code, 0, result)
		self.assertEqual(self.profile['status'], 'active')
		code, result = self.run_cli('pause', version=8)
		self.assertEqual(code, 0, result)
		self.assertEqual(self.profile['status'], 'paused')

	def test_stale_version_does_not_overwrite_concurrent_changes(self):
		code, result = self.run_cli('update', {'deliveryIntervalMinutes': 20}, version=6)
		self.assertNotEqual(code, 0)
		self.assertEqual(result['code'], 'version_conflict')
		self.assertEqual(self.profile['version'], 7)

	def test_race_at_put_is_not_blindly_retried(self):
		self.race = True
		code, result = self.run_cli('update', {'deliveryIntervalMinutes': 20})
		self.assertNotEqual(code, 0)
		self.assertEqual(result['code'], 'version_conflict')
		self.assertEqual(self.profile['deliveryIntervalMinutes'], 60)
		self.assertEqual(sum(m == 'PUT' for m, _, _ in self.requests), 1)

	def test_auth_failure_does_not_claim_success_or_create_a_local_subscription(self):
		self.failure = 403
		code, result = self.run_cli('update', {'deliveryIntervalMinutes': 20})
		self.assertNotEqual(code, 0)
		self.assertEqual(result['code'], 'auth_denied')
		self.assertFalse(result['verified'])
		self.assertEqual(self.profile['version'], 7)

	def test_new_interests_require_paired_text_and_canonical_events(self):
		for changes in (
			{'includeTerms': [{'type': 'event_type', 'value': 'ETF Flow'}]},
			{'interestEn': 'Follow Bitcoin.'},
			{'includeTerms': [{'type': 'event_type', 'value': 'etf_flow'}]},
			{'token': TOKEN},
		):
			code, result = self.run_cli('update', changes)
			self.assertNotEqual(code, 0, changes)
			self.assertEqual(self.profile['version'], 7)

	def test_english_interests_remain_english_with_chinese_reply_language(self):
		changes = {
			'interestOriginal': 'Follow Bitcoin ETF flows.', 'interestEn': 'Follow Bitcoin ETF flows.',
			'includeTerms': [{'type': 'event_type', 'value': 'etf_flow'}],
		}
		code, result = self.run_cli('update', changes)
		self.assertEqual(code, 0, result)
		self.assertEqual(self.profile['interestOriginal'], 'Follow Bitcoin ETF flows.')
		self.assertEqual(self.profile['preferredLanguage'], 'zh-CN')
		self.assertEqual(self.profile['includeTerms'][0]['normalizedValue'], 'etf_flow')

	def test_create_requires_no_existing_profile_and_explicit_preferences(self):
		changes = {'preferredLanguage': 'en', 'interestOriginal': 'Follow BTC.', 'interestEn': 'Follow BTC.',
			'includeTerms': [{'type': 'asset', 'value': 'BTC'}]}
		code, result = self.run_cli('create', changes)
		self.assertNotEqual(code, 0)
		self.profile = None
		code, result = self.run_cli('create', changes)
		self.assertEqual(code, 0, result)
		self.assertEqual(self.profile['version'], 1)
		self.assertEqual(self.profile['deliveryIntervalMinutes'], 360)

	def test_wrong_receipt_never_reports_verified_success(self):
		self.receipt_change = {'deliveryIntervalMinutes': 999}
		code, result = self.run_cli('update', {'deliveryIntervalMinutes': 20})
		self.assertNotEqual(code, 0)
		self.assertEqual(result['code'], 'verification_failed')
		self.assertEqual(result['writeOutcome'], 'unknown')

	def test_redirect_is_not_followed(self):
		self.failure = 302
		code, result = self.run_cli('get')
		self.assertNotEqual(code, 0)
		self.assertEqual(result['code'], 'redirect_refused')
		self.assertEqual(len(self.requests), 1)

	def test_missing_or_masked_credentials_never_reach_api(self):
		for token in ('', '***'):
			code, result = self.run_cli('get', env={'WALLET_API_TOKEN': token})
			self.assertNotEqual(code, 0)
			self.assertEqual(result['code'], 'invalid_hosted_identity')
		self.assertEqual(self.requests, [])

	def test_explicit_resume_can_apply_changes_in_the_same_write(self):
		self.profile['status'] = 'paused'
		code, result = self.run_cli('resume', {'deliveryIntervalMinutes': 20})
		self.assertEqual(code, 0, result)
		self.assertEqual(self.profile['status'], 'active')
		self.assertEqual(self.profile['deliveryIntervalMinutes'], 20)
		self.assertEqual(sum(m == 'PUT' for m, _, _ in self.requests), 1)

	def test_wrong_normalized_event_in_receipt_is_not_accepted(self):
		self.receipt_change = {'includeTerms': [{'type': 'event_type', 'displayValue': 'etf_flow', 'normalizedValue': 'etf flow'}]}
		code, result = self.run_cli('update', {
			'includeTerms': [{'type': 'event_type', 'value': 'etf_flow'}],
			'interestOriginal': 'ETF flows', 'interestEn': 'ETF flows',
		})
		self.assertNotEqual(code, 0)
		self.assertFalse(result['verified'])

	def test_lost_write_receipt_is_unknown_not_retried(self):
		self.drop_write_response = True
		code, result = self.run_cli('update', {'deliveryIntervalMinutes': 20})
		self.assertNotEqual(code, 0)
		self.assertEqual(result['writeOutcome'], 'unknown')
		self.assertFalse(result['verified'])
		self.assertEqual(self.profile['deliveryIntervalMinutes'], 20)
		self.assertEqual(sum(m == 'PUT' for m, _, _ in self.requests), 1)

	def test_noncanonical_source_receipt_is_not_verified(self):
		self.receipt_change = {'sourceAllowlist': ['PANews']}
		code, result = self.run_cli('update', {'deliveryIntervalMinutes': 20})
		self.assertNotEqual(code, 0)
		self.assertEqual(result['code'], 'verification_failed')
		self.assertEqual(result['writeOutcome'], 'unknown')

	def test_incomplete_asset_receipt_returns_safe_unknown_outcome(self):
		self.receipt_change = {'includeTerms': [{'type': 'asset', 'displayValue': 'BTC'}]}
		code, result = self.run_cli('update', {
			'includeTerms': [{'type': 'asset', 'value': 'BTC'}],
			'interestOriginal': 'Bitcoin news', 'interestEn': 'Bitcoin news',
		})
		self.assertNotEqual(code, 0)
		self.assertEqual(result['code'], 'verification_failed')
		self.assertEqual(result['writeOutcome'], 'unknown')
		self.assertEqual(sum(m == 'PUT' for m, _, _ in self.requests), 1)

	def test_canonicalized_alias_and_source_receipt_is_verified(self):
		self.receipt_change = {
			'sourceAllowlist': ['panews'],
			'includeTerms': [{'type': 'asset', 'displayValue': 'Bitcoin', 'normalizedValue': 'btc'}],
		}
		code, result = self.run_cli('update', {
			'includeTerms': [{'type': 'asset', 'value': 'Bitcoin'}, {'type': 'asset', 'value': 'BTC'}],
			'sourceAllowlist': [' PANews ', 'panews'],
			'interestOriginal': 'Bitcoin news on PANews', 'interestEn': 'Bitcoin news on PANews',
		})
		self.assertEqual(code, 0, result)
		self.assertTrue(result['verified'])

	def test_runtime_package_cli_can_read_only_an_explicit_item_uuid(self):
		code, result = self.run_cli('item', extra=('--item-id', INSTANCE))
		self.assertNotEqual(code, 0)
		self.assertEqual(result['code'], 'not_found')
		self.assertEqual(self.requests, [('GET', '/v1/instances/' + INSTANCE + '/news/items/' + INSTANCE, None)])


if __name__ == '__main__':
	unittest.main()

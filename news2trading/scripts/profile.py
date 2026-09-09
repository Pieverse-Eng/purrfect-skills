#!/usr/bin/env python3
"""Pawpilot Profile workflow. Hosted credentials stay inside this process."""

import argparse
import http.client
import json
import os
import sys
import time
import unicodedata
from pathlib import Path

from news_client import (
	NewsClientError, _connection, _parse_base_url, _read_bounded, _validate_uuid,
	IO_TIMEOUT_SECONDS, TOTAL_BUDGET_SECONDS,
)


EVENTS = frozenset((
	'listing_delisting', 'funding_investment', 'partnership_launch', 'exploit_security',
	'regulation_legal', 'etf_flow', 'token_unlock_burn', 'buyback', 'liquidation', 'macro_data',
))
FIELDS = frozenset((
	'preferredLanguage', 'sourceAllowlist', 'sourceBlocklist', 'includeTerms', 'excludeTerms',
	'minScore', 'explorationEnabled', 'deliveryIntervalMinutes', 'interestOriginal', 'interestEn',
))
TEXT_FIELDS = frozenset(('interestOriginal', 'interestEn'))
ROUTING_FIELDS = frozenset(('includeTerms', 'excludeTerms', 'sourceAllowlist', 'sourceBlocklist'))
DEFAULTS = {
	'sourceAllowlist': [], 'sourceBlocklist': [], 'excludeTerms': [],
	'minScore': 50, 'explorationEnabled': False, 'deliveryIntervalMinutes': 360,
}


class ProfileError(Exception):
	def __init__(self, code, message, outcome='not_attempted', status=None):
		super().__init__(message)
		self.code, self.outcome, self.status = code, outcome, status


def fail(code, message):
	raise ProfileError(code, message)


def integer(value, minimum, maximum):
	return type(value) is int and minimum <= value <= maximum


def text(value, maximum, minimum=1):
	try:
		return isinstance(value, str) and minimum <= len(value.strip().encode('utf-16-le')) // 2 <= maximum
	except UnicodeError:
		return False


def normalized(value):
	return ' '.join(unicodedata.normalize('NFKC', value).split()).lower()


def term_key(term):
	value = normalized(term['value'])
	if term['type'] == 'asset':
		value = {'bitcoin': 'btc', '比特币': 'btc', 'ethereum': 'eth', '以太坊': 'eth', 'solana': 'sol'}.get(value, value)
	return term['type'], value


def validate_preferences(body, new_terms=()):
	if set(body) - FIELDS or not (FIELDS - TEXT_FIELDS) <= body.keys():
		fail('invalid_preferences', 'Provide only writable Profile preferences.')
	if not text(body['preferredLanguage'], 35, 2):
		fail('invalid_preferences', 'Reply language must contain 2–35 characters.')
	for key, lo, hi in (('minScore', 0, 160), ('deliveryIntervalMinutes', 10, 1440)):
		if not integer(body[key], lo, hi):
			fail('invalid_preferences', 'Score or check interval is outside its supported range.')
	if type(body['explorationEnabled']) is not bool:
		fail('invalid_preferences', 'explorationEnabled must be boolean.')
	for key in ('sourceAllowlist', 'sourceBlocklist'):
		values = body[key]
		if not isinstance(values, list) or len(values) > 20 or not all(text(v, 64) for v in values):
			fail('invalid_preferences', 'Invalid source list.')
	for key in ('includeTerms', 'excludeTerms'):
		terms = body[key]
		if not isinstance(terms, list) or len(terms) > 100:
			fail('invalid_preferences', 'Invalid routing terms.')
		for term in terms:
			if (not isinstance(term, dict) or set(term) != {'type', 'value'}
				or term['type'] not in ('asset', 'event_type') or not text(term['value'], 128)):
				fail('invalid_preferences', 'Terms require type and value, not API response fields.')
			if key in new_terms and term['type'] == 'event_type' and term['value'] not in EVENTS:
				fail('invalid_event', 'Use a canonical event identifier from the Profile reference.')
	if not body['includeTerms'] and not body['explorationEnabled']:
		fail('invalid_preferences', 'At least one include term is required without exploration.')
	if TEXT_FIELDS & body.keys():
		if not TEXT_FIELDS <= body.keys() or not (
			all(body[k] is None for k in TEXT_FIELDS) or all(text(body[k], 4000) for k in TEXT_FIELDS)
		):
			fail('invalid_interest_pair', 'Provide both complete interest texts, or both null.')


def writable(profile):
	body = {k: profile[k] for k in FIELDS if k in profile}
	try:
		for key in ('includeTerms', 'excludeTerms'):
			for term in profile[key]:
				if (not isinstance(term, dict) or not isinstance(term.get('normalizedValue'), str)
					or not term['normalizedValue'].strip()):
					fail('malformed_profile', 'Platform term is missing its stored routing value.')
			body[key] = [
				{'type': t['type'], 'value': t['normalizedValue'] if
				 t['type'] == 'event_type' and t['normalizedValue'] in EVENTS else t['displayValue']}
				for t in profile[key]
			]
		validate_preferences(body)
	except (KeyError, TypeError, ProfileError):
		fail('malformed_profile', 'Platform Profile is incomplete; no changes were sent.')
	return body


def comparable(body):
	"""Compare server-normalized lists, retaining the first display value per alias."""
	result = dict(body)
	for key in ('sourceAllowlist', 'sourceBlocklist'):
		result[key] = sorted(set(normalized(v) for v in body[key]))
	for key in ('includeTerms', 'excludeTerms'):
		result[key] = sorted(set(term_key(t) for t in body[key]))
	for key in ('preferredLanguage', 'interestOriginal', 'interestEn'):
		if isinstance(result.get(key), str):
			result[key] = result[key].strip()
	return result


class Client:
	def __init__(self):
		values = [os.environ.get(k, '').strip() for k in ('WALLET_API_URL', 'WALLET_API_TOKEN', 'INSTANCE_ID')]
		if any(not v or '\n' in v or '\r' in v for v in values) or values[1] == '***':
			fail('invalid_hosted_identity', 'Hosted API identity is unavailable; do not supply a replacement.')
		base, self.token, self.instance = values
		try:
			self.parsed = _parse_base_url(base)
			_validate_uuid(self.instance, 'Instance ID')
		except (NewsClientError, ValueError):
			fail('invalid_hosted_identity', 'Hosted API identity is invalid.')
		self.path = self.parsed.path.rstrip('/') + '/v1/instances/' + self.instance + '/news/profile'

	def request(self, method, body=None, suffix=''):
		outcome = 'not_attempted' if method == 'GET' else 'unknown'
		connection = _connection(self.parsed, IO_TIMEOUT_SECONDS)
		deadline = time.monotonic() + TOTAL_BUDGET_SECONDS
		try:
			connection.request(method, self.path + suffix,
				body=json.dumps(body, ensure_ascii=False).encode() if body is not None else None,
				headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json', 'Accept': 'application/json'})
			response = connection.getresponse()
			raw = _read_bounded(response, connection, deadline)
		except (OSError, http.client.HTTPException, NewsClientError, ValueError, UnicodeError):
			raise ProfileError('network_error', 'Request failed; read current state before another write.', outcome)
		finally:
			connection.close()
		status = response.status
		if status != 200:
			code = {401: 'auth_denied', 403: 'auth_denied', 409: 'version_conflict', 404: 'not_found', 400: 'invalid_preferences'}.get(status, 'http_error')
			if 300 <= status < 400:
				code = 'redirect_refused'
			raise ProfileError(code, 'Platform request was not confirmed. Inspect current state before retrying.',
				'rejected' if method != 'GET' and status in (400, 401, 403, 404, 409) else outcome, status)
		try:
			payload = json.loads(raw)
			if not isinstance(payload, dict) or payload.get('ok') is not True or 'data' not in payload:
				raise ValueError()
			return payload['data']
		except (ValueError, UnicodeError):
			raise ProfileError('malformed_response', 'Platform response could not be verified.', outcome, status)

	def check_profile(self, profile):
		if (not isinstance(profile, dict) or profile.get('instanceId') != self.instance
			or not integer(profile.get('version'), 1, 2**53 - 1) or profile.get('status') not in ('active', 'paused')):
			fail('malformed_profile', 'Platform response does not identify this Profile.')
		writable(profile)
		return profile


def load_changes(path):
	try:
		file = Path(path)
		if not file.is_file() or file.stat().st_size > 64 * 1024:
			raise ValueError()
		value = json.loads(file.read_text(encoding='utf-8'))
	except (OSError, ValueError, UnicodeError):
		fail('invalid_changes_file', 'Use one bounded local UTF-8 JSON changes file.')
	if not isinstance(value, dict) or not value or set(value) - FIELDS:
		fail('invalid_preferences', 'Changes must contain only writable preferences, never credentials or identity.')
	return value


def run(args):
	client = Client()
	if args.action == 'item':
		try:
			_validate_uuid(args.item_id, 'Item ID')
		except NewsClientError:
			fail('invalid_item_id', 'Use the complete item UUID from a platform delivery.')
		client.path = client.path.removesuffix('/profile') + '/items/' + args.item_id
		return {'ok': True, 'operation': 'item', 'item': client.request('GET')}
	changes = load_changes(args.changes_file) if getattr(args, 'changes_file', None) else {}
	current = client.request('GET')
	if current is not None:
		client.check_profile(current)
	if args.action == 'get':
		return {'ok': True, 'operation': 'get', 'verified': True, 'profile': current}
	if args.action == 'create':
		if current is not None:
			fail('profile_exists', 'Profile already exists; read and update it instead.')
		if not TEXT_FIELDS <= changes.keys():
			fail('invalid_interest_pair', 'Onboarding requires the agreed original and English interests.')
		version, body = 0, dict(DEFAULTS)
	else:
		if current is None:
			fail('profile_missing', 'No Profile exists; onboarding requires explicit subscription consent.')
		version = current['version']
		if args.expected_version != version:
			fail('version_conflict', 'Profile changed since it was read. Read again and reconcile the user request.')
		if args.action == 'update' and current['status'] == 'paused':
			fail('resume_required', 'Updating would resume news. Ask for explicit resume authorization first.')
		body = writable(current)
		if TEXT_FIELDS & changes.keys() and not TEXT_FIELDS <= body.keys():
			fail('unsupported_interest_fields', 'Platform has not confirmed support for paired interests.')
	if TEXT_FIELDS & changes.keys() and not TEXT_FIELDS <= changes.keys():
		fail('invalid_interest_pair', 'An interest change must supply both text fields together.')
	if ROUTING_FIELDS & changes.keys() and not TEXT_FIELDS <= changes.keys():
		fail('interest_reconciliation_required', 'Routing changes require both reconciled interests, or both null.')
	body.update(changes)
	validate_preferences(body, new_terms=changes.keys())
	warnings = []
	if any(t['type'] == 'event_type' and t['value'] not in EVENTS for key in ('includeTerms', 'excludeTerms') for t in body[key]):
		warnings.append('unverified_legacy_event_selector')
	status = 'paused' if args.action == 'pause' else 'active'
	if current is not None and current['status'] == status and args.action in ('pause', 'resume') and not changes:
		return {'ok': True, 'operation': args.action, 'verified': True, 'changed': False, 'profile': current, 'warnings': warnings}
	if args.action == 'pause':
		saved = client.request('POST', {'expectedVersion': version}, '/pause')
	else:
		saved = client.request('PUT', dict(body, expectedVersion=version))
	try:
		client.check_profile(saved)
		if (saved['version'] != version + 1 or saved['status'] != status
			or comparable(writable(saved)) != comparable(body)):
			raise ValueError()
		for key in ('includeTerms', 'excludeTerms'):
			if {(t['type'], t['normalizedValue']) for t in saved[key]} != {term_key(t) for t in body[key]}:
				raise ValueError()
		for key in ('sourceAllowlist', 'sourceBlocklist'):
			if set(saved[key]) != {normalized(value) for value in body[key]}:
				raise ValueError()
	except (ProfileError, KeyError, ValueError, TypeError):
		raise ProfileError('verification_failed', 'Write receipt did not confirm all settings. Read current state; do not repeat the write blindly.', 'unknown')
	return {'ok': True, 'operation': args.action, 'verified': True, 'changed': True,
		'writeOutcome': 'confirmed', 'profile': saved, 'warnings': warnings}


class Parser(argparse.ArgumentParser):
	def error(self, message):
		fail('invalid_arguments', 'Invalid arguments. Use profile.py --help; never pass a token or API URL.')


def main():
	parser = Parser(description='Manage this Agent\'s platform News Profile; credentials are read internally.')
	sub = parser.add_subparsers(dest='action', required=True)
	sub.add_parser('get', help='Read the actual platform Profile without changing it.')
	sub.add_parser('item', help='Read an item from a platform delivery.').add_argument('--item-id', required=True)
	for action in ('create', 'update', 'pause', 'resume'):
		p = sub.add_parser(action)
		if action != 'create':
			p.add_argument('--expected-version', type=int, required=True)
		if action in ('create', 'update'):
			p.add_argument('--changes-file', required=True)
		elif action == 'resume':
			p.add_argument('--changes-file', help='Apply agreed changes while explicitly resuming, in one write.')
	try:
		result = run(parser.parse_args())
	except ProfileError as error:
		result = {'ok': False, 'verified': False, 'code': error.code, 'error': str(error), 'writeOutcome': error.outcome}
		if error.status is not None:
			result['httpStatus'] = error.status
	# Even a malformed upstream response must not echo the actual hosted credential.
	output = json.dumps(result, ensure_ascii=False)
	token = os.environ.get('WALLET_API_TOKEN')
	if token:
		output = output.replace(token, '[REDACTED]')
	print(output)
	return 0 if result['ok'] else 1


if __name__ == '__main__':
	sys.exit(main())

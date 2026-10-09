"""Fixed-identity client for the Purr-Fect News publication endpoint."""

import http.client
import json
import os
import ssl
import time
import uuid
from pathlib import Path
from urllib.parse import quote, urlsplit


MAX_TEXT_UTF16_UNITS = 3_000
MAX_TEXT_FILE_BYTES = 24_000
MAX_RESPONSE_BYTES = 128 * 1024
IO_TIMEOUT_SECONDS = 15
TOTAL_BUDGET_SECONDS = 55

_KNOWN_FALSE_CODES = {
	'batch_missing',
	'batch_expired',
	'profile_paused',
	'profile_replaced',
	'channel_missing',
	'upstream_rejected',
	'invalid_news_publication',
}


class NewsClientError(Exception):
	"""Safe local diagnostic carrying truthful channel-acceptance state."""

	def __init__(self, code, message, channel_accepted, http_status=None, publication=None):
		super().__init__(message)
		self.code = code
		self.channel_accepted = channel_accepted
		self.http_status = http_status
		self.publication = publication or {}

	def diagnostic(self):
		result = {
			'ok': False,
			'code': self.code,
			'error': str(self),
			'channelAccepted': self.channel_accepted,
			'contextRecorded': False,
		}
		if self.http_status is not None:
			result['httpStatus'] = self.http_status
		result.update(self.publication)
		return result


def read_text_file(path):
	"""Read a bounded UTF-8 regular file; stdin and inline text are unsupported."""
	file_path = Path(path)
	try:
		if not file_path.is_file():
			raise NewsClientError(
				'invalid_text_file', 'Text input must be a local regular file.', False
			)
		if file_path.stat().st_size > MAX_TEXT_FILE_BYTES:
			raise NewsClientError('invalid_text', 'Publication text exceeds the limit.', False)
		text = file_path.read_text(encoding='utf-8')
	except NewsClientError:
		raise
	except (OSError, UnicodeError):
		raise NewsClientError('invalid_text_file', 'Could not read the local text file.', False)
	_validate_text(text)
	return text


def publish_batch(batch_id, text, expected_runtime):
	"""POST one publication attempt and validate the runtime-specific receipt."""
	_validate_uuid(batch_id, 'batch ID')
	_validate_text(text)
	if expected_runtime not in ('openclaw', 'hermes'):
		raise NewsClientError('invalid_runtime', 'Unsupported fixed runtime.', False)

	base_url = _required_env('WALLET_API_URL')
	token = _required_env('WALLET_API_TOKEN')
	instance_id = _required_env('INSTANCE_ID')
	_validate_uuid(instance_id, 'Instance ID')
	parsed = _parse_base_url(base_url)
	path = (
		parsed.path.rstrip('/')
		+ '/v1/instances/'
		+ quote(instance_id, safe='')
		+ '/news/batches/'
		+ quote(batch_id, safe='')
		+ '/publish'
	)
	body = json.dumps({'text': text}, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
	deadline = time.monotonic() + TOTAL_BUDGET_SECONDS
	connection = _connection(parsed, min(IO_TIMEOUT_SECONDS, _remaining(deadline)))
	try:
		connection.request(
			'POST',
			path,
			body=body,
			headers={
				'Authorization': 'Bearer ' + token,
				'Content-Type': 'application/json',
				'Accept': 'application/json',
			},
		)
		response = connection.getresponse()
		content_length = response.getheader('content-length')
		if content_length is not None:
			try:
				if int(content_length) > MAX_RESPONSE_BYTES:
					raise NewsClientError(
						'response_too_large', 'Platform response exceeded the limit.', 'unknown'
					)
			except ValueError:
				raise NewsClientError(
					'malformed_response', 'Platform returned an invalid response.', 'unknown'
				)
		raw = _read_bounded(response, connection, deadline)
	except NewsClientError:
		raise
	except (OSError, TimeoutError, http.client.HTTPException, ssl.SSLError):
		raise NewsClientError(
			'network_error',
			'Publication result is unknown because the platform connection failed.',
			'unknown',
		)
	finally:
		connection.close()

	try:
		payload = json.loads(raw.decode('utf-8'))
	except (UnicodeError, json.JSONDecodeError):
		raise NewsClientError(
			'malformed_response', 'Platform returned an invalid response.', 'unknown', response.status
		)

	if response.status == 200:
		return _validate_receipt(payload, batch_id, expected_runtime)
	if 300 <= response.status < 400:
		raise NewsClientError(
			'unexpected_http_status',
			'Platform returned a redirect; publication was not retried.',
			'unknown',
			response.status,
		)
	_raise_api_error(payload, response.status)


def _required_env(name):
	value = os.environ.get(name)
	if value and ('\n' in value or '\r' in value):
		raise NewsClientError('invalid_hosted_identity', 'Hosted publication identity is invalid.', False)
	if not value or not value.strip():
		raise NewsClientError(
			'missing_hosted_identity',
			'Hosted publication identity is unavailable.',
			False,
		)
	if name == 'WALLET_API_TOKEN' and (
		value == '***' or any(ord(char) < 33 or ord(char) > 126 for char in value)
	):
		raise NewsClientError('invalid_hosted_identity', 'Hosted publication credential is invalid.', False)
	return value.strip()


def _validate_uuid(value, label):
	try:
		parsed = uuid.UUID(str(value))
	except (ValueError, AttributeError, TypeError):
		raise NewsClientError('invalid_identifier', f'{label} must be a UUID.', False)
	if str(parsed) != str(value).lower():
		raise NewsClientError('invalid_identifier', f'{label} must be a complete UUID.', False)


def _validate_text(text):
	if not isinstance(text, str) or not text.strip():
		raise NewsClientError('invalid_text', 'Publication text must not be blank.', False)
	try:
		units = len(text.encode('utf-16-le')) // 2
	except UnicodeEncodeError:
		raise NewsClientError('invalid_text', 'Publication text is not valid Unicode.', False)
	if units > MAX_TEXT_UTF16_UNITS:
		raise NewsClientError('invalid_text', 'Publication text exceeds the limit.', False)


def _parse_base_url(value):
	parsed = urlsplit(value)
	try:
		parsed.port
	except ValueError:
		raise NewsClientError('invalid_hosted_identity', 'Hosted API URL is invalid.', False)
	if (
		parsed.scheme not in ('http', 'https')
		or not parsed.hostname
		or parsed.username is not None
		or parsed.password is not None
		or parsed.query
		or parsed.fragment
	):
		raise NewsClientError('invalid_hosted_identity', 'Hosted API URL is invalid.', False)
	return parsed


def _connection(parsed, timeout):
	if parsed.scheme == 'https':
		return http.client.HTTPSConnection(
			parsed.hostname, parsed.port, timeout=timeout, context=ssl.create_default_context()
		)
	return http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=timeout)


def _remaining(deadline):
	remaining = deadline - time.monotonic()
	if remaining <= 0:
		raise NewsClientError(
			'network_error', 'Publication result is unknown because the time budget expired.', 'unknown'
		)
	return remaining


def _read_bounded(response, connection, deadline):
	chunks = []
	size = 0
	while True:
		remaining = _remaining(deadline)
		_set_response_timeout(response, connection, min(IO_TIMEOUT_SECONDS, remaining))
		chunk = response.read1(min(16 * 1024, MAX_RESPONSE_BYTES + 1 - size))
		_remaining(deadline)
		if not chunk:
			return b''.join(chunks)
		chunks.append(chunk)
		size += len(chunk)
		if size > MAX_RESPONSE_BYTES:
			raise NewsClientError(
				'response_too_large', 'Platform response exceeded the limit.', 'unknown'
			)


def _set_response_timeout(response, connection, timeout):
	"""Bound reads whether the connection or a closing response owns the socket."""
	sock = connection.sock
	if sock is None:
		response_file = getattr(response, 'fp', None)
		raw = getattr(response_file, 'raw', None)
		sock = getattr(raw, '_sock', None) or getattr(response_file, '_sock', None)
	if sock is not None:
		sock.settimeout(timeout)


def _validate_receipt(payload, batch_id, expected_runtime):
	try:
		data = payload['data']
		valid = payload.get('ok') is True and data.get('batchId') == batch_id
		if 'web' in data or 'external' in data:
			web, external = data['web'], data['external']
			valid = (
				valid and web.get('status') == 'published'
				and isinstance(web.get('sessionId'), str) and bool(web['sessionId'].strip())
				and external.get('status') in ('disabled', 'published', 'rejected', 'unknown')
			)
			if external.get('status') == 'published':
				receipt = external['receipt']
				valid = valid and _valid_external_receipt(receipt, batch_id, expected_runtime)
				# The platform flattens a successful external receipt for legacy clients.
				valid = valid and all(data.get(key) == value for key, value in receipt.items())
			else:
				valid = valid and 'receipt' not in external and 'channelAccepted' not in data
		else:
			valid = valid and _valid_external_receipt(data, batch_id, expected_runtime)
	except (KeyError, TypeError, AttributeError):
		valid = False
	if not valid:
		raise NewsClientError(
			'malformed_response',
			'Platform returned a receipt that does not match this runtime.',
			'unknown',
			200,
		)
	if 'publishedText' in data:
		canonical_publication_text(data, '')
	return data


def _valid_external_receipt(data, batch_id, expected_runtime):
	try:
		context, target = data['context'], data['target']
		valid = (
			data.get('batchId') == batch_id and data.get('channelAccepted') is True
			and data.get('runtimeType') == expected_runtime
			and target.get('channel') in ('telegram', 'line')
			and isinstance(target.get('chatId'), str)
			and bool(target['chatId'].strip())
			and ('threadId' not in target or isinstance(target['threadId'], str))
			and context.get('runtimeType') == expected_runtime
		)
		if expected_runtime == 'openclaw':
			valid = valid and context.get('status') == 'recorded'
		else:
			valid = (
				valid
				and context.get('status') == 'required'
				and isinstance(context.get('sessionId'), str)
				and bool(context['sessionId'].strip())
				and isinstance(context.get('sessionKey'), str)
				and bool(context['sessionKey'].strip())
				and ('userId' not in context or isinstance(context['userId'], str))
			)
	except (KeyError, TypeError, AttributeError):
		return False
	return valid


def external_publication_receipt(receipt):
	if 'web' in receipt:
		return receipt['external'].get('receipt')
	return receipt


def canonical_publication_text(receipt, fallback):
	"""Use the immutable server result; old servers omit this additive field."""
	if 'publishedText' not in receipt:
		return fallback
	text = receipt['publishedText']
	try:
		_validate_text(text)
	except NewsClientError:
		raise NewsClientError(
			'malformed_response', 'Platform returned invalid published analysis text.', 'unknown', 200
		) from None
	return text


def publication_summary(receipt, runtime):
	result = {'ok': True, 'batchId': receipt['batchId'], 'runtimeType': runtime}
	if 'publishedText' in receipt:
		result['publishedText'] = receipt['publishedText']
	if 'web' in receipt:
		result.update(web=receipt['web'], external=receipt['external'])
	return result


def _diagnostic_identifier(value):
	return (
		isinstance(value, str) and bool(value.strip()) and len(value) <= 512
		and not any(ord(char) < 32 or ord(char) == 127 for char in value)
	)


def _diagnostic_target(value):
	if not isinstance(value, dict) or value.get('channel') not in ('telegram', 'line'):
		return None
	if not _diagnostic_identifier(value.get('chatId')):
		return None
	target = {'channel': value['channel'], 'chatId': value['chatId']}
	if 'threadId' in value:
		if not _diagnostic_identifier(value['threadId']):
			return None
		target['threadId'] = value['threadId']
	return target


def _partial_publication_diagnostic(payload):
	"""Whitelist diagnostic evidence, never a send/mirror authorization.

	Malformed optional evidence is omitted independently: it cannot turn known
	channel acceptance into uncertainty or discard a valid saved Web receipt.
	"""
	details = {}
	target = _diagnostic_target(payload.get('target'))
	if target is not None:
		details['target'] = target
	web = payload.get('web')
	if isinstance(web, dict) and web.get('status') == 'published' and _diagnostic_identifier(web.get('sessionId')):
		details['web'] = {'status': 'published', 'sessionId': web['sessionId']}
	external = payload.get('external')
	if (
		isinstance(external, dict) and external.get('status') == 'accepted'
		and external.get('channelAccepted') is True
		and external.get('contextRecorded') is False and 'receipt' not in external
	):
		external_target = _diagnostic_target(external.get('target'))
		if 'target' not in external or (external_target is not None and (target is None or external_target == target)):
			details['external'] = {'status': 'accepted', 'channelAccepted': True, 'contextRecorded': False}
			if external_target is not None:
				details['external']['target'] = external_target
	if 'publishedText' in payload:
		try:
			_validate_text(payload['publishedText'])
		except NewsClientError:
			pass
		else:
			details['publishedText'] = payload['publishedText']
	return details


def _raise_api_error(payload, status):
	if not isinstance(payload, dict) or payload.get('ok') is not False:
		raise NewsClientError(
			'malformed_response', 'Platform returned an invalid error response.', 'unknown', status
		)
	code = payload.get('code')
	if not isinstance(code, str) or not code:
		raise NewsClientError(
			'malformed_response', 'Platform returned an invalid error response.', 'unknown', status
		)
	accepted = payload.get('channelAccepted')
	if not isinstance(accepted, bool) and accepted != 'unknown':
		accepted = False if code in _KNOWN_FALSE_CODES or status in (400, 401, 403, 404) else 'unknown'
	message = {
		'context_missing': 'Channel accepted the message, but runtime context is incomplete.',
		'upstream_unknown': 'The publication channel result is unknown.',
	}.get(code, 'Platform declined the publication request.')
	publication = _partial_publication_diagnostic(payload) if code == 'context_missing' and accepted is True else None
	raise NewsClientError(code, message, accepted, status, publication)

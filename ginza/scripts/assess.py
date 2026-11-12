#!/usr/bin/env python3
"""Call the hosted Ginza proxy. Standard library only; never reads a Ginza key."""
import argparse
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

DECIMALS = {'WETH': 18, 'USDC': 6, 'USDT': 6, 'DAI': 18, 'WBTC': 8}
CODES = {'quota_exceeded', 'state_unavailable', 'ginza_unavailable',
         'unsupported_token', 'pool_not_found', 'invalid_request'}


class Failure(Exception):
    def __init__(self, code, status=None, retry_after=None):
        super().__init__(code)
        self.code, self.status, self.retry_after = code, status, retry_after


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def order(token_in, token_out, amount, fee, tip=None):
    tin, tout = token_in.upper(), token_out.upper()
    tin = 'WETH' if tin == 'ETH' else tin
    tout = 'WETH' if tout == 'ETH' else tout
    if tin not in DECIMALS or tout not in DECIMALS:
        raise Failure('unsupported_token')
    if tin == tout or not re.fullmatch(r'(?:0|[1-9][0-9]*)(?:\.[0-9]+)?', amount):
        raise Failure('invalid_request')
    if len(amount) > 100 or len(amount.partition('.')[2]) > DECIMALS[tin]:
        raise Failure('invalid_request')
    whole, _, fraction = amount.partition('.')
    raw = int(whole) * 10**DECIMALS[tin] + int(fraction.ljust(DECIMALS[tin], '0'))
    if not 0 < raw <= 2**256 - 1 or fee not in (100, 500, 3000, 10000):
        raise Failure('invalid_request')
    result = {'tokenIn': tin, 'tokenOut': tout, 'amountIn': amount, 'feeTier': fee}
    if tip is not None:
        try:
            value = float(tip)
        except (ValueError, OverflowError):
            raise Failure('invalid_request') from None
        if not math.isfinite(value) or value < 0:
            raise Failure('invalid_request')
        result['tipGwei'] = value
    return result


def runtime(env):
    values = [env.get(k, '').strip() for k in ('WALLET_API_URL', 'WALLET_API_TOKEN', 'INSTANCE_ID')]
    if any(not v or '*' in v or any(c in v for c in '\r\n') for v in values):
        raise Failure('hosted_instance_required')
    base, token, instance = values
    try:
        parsed = urllib.parse.urlsplit(base)
        if (parsed.scheme not in ('http', 'https') or not parsed.hostname or
                parsed.username is not None or parsed.password is not None or
                parsed.query or parsed.fragment):
            raise ValueError()
        _ = parsed.port
        identifier = str(uuid.UUID(instance))
        if identifier != instance.lower():
            raise ValueError()
    except ValueError:
        raise Failure('invalid_runtime_config') from None
    return base.rstrip('/') + '/v1/instances/' + identifier + '/ginza/assess', token


def validate_response(data):
    if not isinstance(data, dict):
        raise Failure('invalid_platform_response')
    required = {'pool', 'quote', 'capturedAt', 'blockNumber', 'model', 'missingFields', 'predictions'}
    if not required <= data.keys() or not isinstance(data['model'], str) or not data['model']:
        raise Failure('invalid_platform_response')
    if (not isinstance(data['pool'], dict) or not isinstance(data['quote'], dict) or
            not isinstance(data['capturedAt'], str) or not data['capturedAt'] or
            type(data['blockNumber']) is not int or data['blockNumber'] <= 0 or
            not isinstance(data['missingFields'], list) or
            not all(isinstance(x, str) for x in data['missingFields']) or
            not isinstance(data['predictions'], dict) or not data['predictions']):
        raise Failure('invalid_platform_response')
    try:
        json.dumps(data, allow_nan=False)
    except (ValueError, TypeError):
        raise Failure('invalid_platform_response') from None
    # Keep only the public contract; never echo arbitrary top-level debug fields.
    result = {k: data[k] for k in required}
    if 'assumptions' in data:
        if not isinstance(data['assumptions'], list) or not all(isinstance(x, str) for x in data['assumptions']):
            raise Failure('invalid_platform_response')
        result['assumptions'] = data['assumptions']
    if 'blockHash' in data:
        if not isinstance(data['blockHash'], str) or not re.fullmatch(r'0x[0-9a-fA-F]{64}', data['blockHash']):
            raise Failure('invalid_platform_response')
        result['blockHash'] = data['blockHash']
    return result


def assess(payload, env=None):
    url, token = runtime(os.environ if env is None else env)
    request = urllib.request.Request(url, data=json.dumps(payload, allow_nan=False).encode(),
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=60) as response:
            if response.status != 200 or 'json' not in response.headers.get('Content-Type', '').lower():
                raise Failure('invalid_platform_response')
            raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise Failure('invalid_platform_response')
            # A server accidentally reflecting a credential must not expose it to the Agent.
            if token in raw.decode('utf-8'):
                raise Failure('invalid_platform_response')
            return validate_response(json.loads(raw))
    except urllib.error.HTTPError as exc:
        code = {401: 'authentication_failed', 403: 'access_denied', 429: 'quota_exceeded',
                502: 'state_unavailable', 503: 'ginza_unavailable'}.get(exc.code, 'platform_request_failed')
        retry = exc.headers.get('Retry-After', '') if exc.headers else ''
        retry = retry if re.fullmatch(r'[0-9]{1,8}', retry) else None
        try:
            body = json.loads(exc.read(8192))
            candidate = body.get('code') or body.get('error', {}).get('code')
            if candidate in CODES:
                code = candidate
        except (ValueError, AttributeError, TypeError):
            pass
        finally:
            exc.close()
        raise Failure(code, exc.code, retry) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise Failure('platform_unavailable') from None
    except (ValueError, UnicodeError):
        raise Failure('invalid_platform_response') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--token-in', required=True)
    parser.add_argument('--token-out', required=True)
    parser.add_argument('--amount-in', required=True)
    parser.add_argument('--fee-tier', type=int, required=True)
    parser.add_argument('--tip-gwei')
    args = parser.parse_args()
    try:
        payload = order(args.token_in, args.token_out, args.amount_in, args.fee_tier, args.tip_gwei)
        print(json.dumps({'ok': True, **assess(payload)}, ensure_ascii=False, allow_nan=False))
        return 0
    except Failure as exc:
        result = {'ok': False, 'code': exc.code}
        if exc.status is not None:
            result['httpStatus'] = exc.status
        if exc.retry_after is not None:
            result['retryAfterSeconds'] = int(exc.retry_after)
        if exc.code == 'hosted_instance_required':
            result['message'] = '需要已注入平台环境变量的托管实例；本地验收请使用独立试验入口。'
        print(json.dumps(result, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

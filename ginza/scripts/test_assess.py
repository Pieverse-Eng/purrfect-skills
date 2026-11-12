import io
import json
import unittest
from unittest.mock import MagicMock, patch
import urllib.error
from assess import Failure, NoRedirect, assess, order, runtime, validate_response

ENV = {'WALLET_API_URL': 'https://platform.example', 'WALLET_API_TOKEN': 'private-instance-test-token',
       'INSTANCE_ID': '00000000-0000-4000-8000-000000000001'}
RESPONSE = {'pool': {'address': '0xpool'}, 'quote': {'amountOut': '2000'},
            'capturedAt': '2026-11-12T00:00:00Z', 'blockNumber': 1, 'model': 'test-model',
            'missingFields': ['pending'], 'predictions': {'sandwiched': {'probs': {'yes': .1, 'no': .9}}}}


class AssessTests(unittest.TestCase):
    def test_normalize_eth(self):
        self.assertEqual(order('ETH', 'usdc', '1', 100)['tokenIn'], 'WETH')

    def test_invalid_orders(self):
        for amount in ['0', '-1', '1e3', 'NaN', '01', '1.0000000000000000001', str(2**256)]:
            with self.subTest(amount=amount), self.assertRaises(Failure):
                order('ETH', 'USDC', amount, 100)
        for args in [('ETH', 'WETH', '1', 100), ('DOGE', 'USDC', '1', 100),
                     ('USDC', 'ETH', '0.0000001', 100), ('ETH', 'USDC', '1', 200)]:
            with self.subTest(args=args), self.assertRaises(Failure): order(*args)
        for tip in ['nan', 'inf', '-1', 'bad']:
            with self.subTest(tip=tip), self.assertRaises(Failure): order('ETH', 'USDC', '1', 100, tip)

    def test_exact_uint_boundary(self):
        n = 2**256 - 1
        value = str(n // 10**18) + '.' + str(n % 10**18).zfill(18)
        order('ETH', 'USDC', value, 100)
        n += 1
        value = str(n // 10**18) + '.' + str(n % 10**18).zfill(18)
        with self.assertRaises(Failure): order('ETH', 'USDC', value, 100)

    def test_runtime_missing_and_placeholder(self):
        for key in ENV:
            for value in ['', '***', 'bad\r\nheader']:
                with self.subTest(key=key, value=value), self.assertRaises(Failure):
                    runtime({**ENV, key: value})

    def test_bad_runtime(self):
        for url in ['file:///tmp/a', 'https://user:pass@example.com', 'https://example.com?key=x',
                    'https://example.com#frag', 'https://example.com:bad']:
            with self.subTest(url=url), self.assertRaises(Failure):
                runtime({**ENV, 'WALLET_API_URL': url})
        with self.assertRaises(Failure): runtime({**ENV, 'INSTANCE_ID': '../other'})

    @patch('assess.urllib.request.build_opener')
    def test_success_contract(self, build):
        response = MagicMock(status=200)
        response.headers = {'Content-Type': 'application/json'}
        response.read.return_value = json.dumps({**RESPONSE, 'debug': 'not public'}).encode()
        build.return_value.open.return_value.__enter__.return_value = response
        result = assess(order('ETH', 'USDC', '1', 100), ENV)
        self.assertEqual(result, RESPONSE)
        req = build.return_value.open.call_args.args[0]
        self.assertEqual(req.full_url, ENV['WALLET_API_URL']+'/v1/instances/'+ENV['INSTANCE_ID']+'/ginza/assess')
        self.assertEqual(req.get_header('Authorization'), 'Bearer '+ENV['WALLET_API_TOKEN'])
        self.assertEqual(build.return_value.open.call_args.kwargs['timeout'], 60)

    @patch('assess.urllib.request.build_opener')
    def test_errors_sanitized(self, build):
        for status in [401, 403, 429, 502, 503, 302]:
            build.return_value.open.side_effect = urllib.error.HTTPError(
                'https://platform.example', status, 'secret raw error', {'Retry-After': '12'},
                io.BytesIO(b'<html>private upstream error</html>'))
            with self.subTest(status=status), self.assertRaises(Failure) as caught:
                assess({}, ENV)
            self.assertNotIn('secret', str(caught.exception))
            self.assertEqual(caught.exception.status, status)
            self.assertEqual(caught.exception.retry_after, '12')

    @patch('assess.urllib.request.build_opener')
    def test_unavailable(self, build):
        for exc in [TimeoutError(), urllib.error.URLError('secret URL')]:
            build.return_value.open.side_effect = exc
            with self.assertRaises(Failure) as caught: assess({}, ENV)
            self.assertEqual(caught.exception.code, 'platform_unavailable')

    @patch('assess.urllib.request.build_opener')
    def test_reject_bad_response(self, build):
        for raw in [b'{}', b'not json', ENV['WALLET_API_TOKEN'].encode(), b'x'*(1024*1024+1)]:
            response = MagicMock(status=200)
            response.headers = {'Content-Type': 'application/json'}
            response.read.return_value = raw
            build.return_value.open.return_value.__enter__.return_value = response
            with self.subTest(size=len(raw)), self.assertRaises(Failure): assess({}, ENV)

    def test_assumptions_and_block_identity(self):
        data = {**RESPONSE, 'assumptions': ['USDC assumed 1 USD'], 'blockHash': '0x' + '1' * 64}
        self.assertEqual(validate_response(data), data)
        for invalid in [{'assumptions': 'guess'}, {'blockHash': 'bad'}]:
            with self.assertRaises(Failure): validate_response({**RESPONSE, **invalid})

    def test_non_finite_platform_output(self):
        with self.assertRaises(Failure):
            validate_response({**RESPONSE, 'quote': {'impactBps': float('nan')}})

    def test_redirect_refused(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, '', {}, 'https://evil.example'))


if __name__ == '__main__': unittest.main()

#!/usr/bin/env python3
"""OpenClaw entry point for one fixed-runtime news publication attempt."""

import argparse
import json
import sys

from news_client import NewsClientError, publish_batch, read_text_file


def _parser():
	parser = argparse.ArgumentParser(description='Publish one Purr-Fect News batch.')
	parser.add_argument('--batch-id', required=True)
	parser.add_argument('--text-file', required=True)
	return parser


def main(argv=None):
	args = _parser().parse_args(argv)
	try:
		text = read_text_file(args.text_file)
		receipt = publish_batch(args.batch_id, text, expected_runtime='openclaw')
		print(json.dumps({
			'ok': True,
			'batchId': receipt['batchId'],
			'runtimeType': 'openclaw',
			'channelAccepted': True,
			'contextRecorded': True,
		}, separators=(',', ':')))
		return 0
	except NewsClientError as error:
		print(json.dumps(error.diagnostic(), separators=(',', ':')), file=sys.stderr)
		return 1


if __name__ == '__main__':
	raise SystemExit(main())

#!/usr/bin/env python
"""MailChimp list backup script."""

import argparse
import os

import requests
from mailchimp3 import MailChimp


def _client(key):
    """Return MailChimp API client object."""
    headers = requests.utils.default_headers()
    headers['User-Agent'] = (
        'Mailchimp Backup script '
        '(https://github.com/max-arnold/mailchimp-backup)'
    )
    return MailChimp(mc_api=key)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MailChimp list backup script')
    parser.add_argument('--key', type=str, help='API key')
    parser.add_argument(
        '--show-lists', action='store_true', help='Show available lists'
    )
    options = parser.parse_args()

    key = getattr(options, 'key', os.environ.get('MAILCHIMP_KEY'))
    if key is None:
        parser.exit(
            status=1,
            message=(
                'Please specify either the MAILCHIMP_KEY '
                'environment variable or the --key argument\n'
            ),
        )

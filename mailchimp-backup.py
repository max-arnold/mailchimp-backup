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


def get_lists(key):
    """Return lists info."""
    return _client(key).lists.all(get_all=True)


def show_lists(key):
    """Display lists info."""
    lists = get_lists(key)
    for lst in lists['lists']:
        print(
            'ID: {}, Name: "{}", Members: {}'.format(
                lst['id'], lst['name'], lst['stats']['member_count']
            )
        )


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

    if options.show_lists:
        show_lists(key)

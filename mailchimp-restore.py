#!/usr/bin/env python
"""MailChimp list restore script."""

import argparse
import csv
import json
import os
import re

import requests
from mailchimp3 import MailChimp
from mailchimp3.helpers import get_subscriber_hash

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


def restore(key, options):
    with open(options._in, 'r') as fp:
        cr = csv.DictReader(fp)
        subscribers = []
        for row in cr:
            row['merge_fields'] = {}
            row['location'] = {}
            for k, v in list(row.items()):
                if k.startswith('merge_fields.'):
                    row.pop(k)
                    row['merge_fields'][k[len('merge_fields.'):]] = v
                if k.startswith('location.'):
                    row.pop(k)
                    row['location'][k[len('location.'):]] = v
            row['tags'] = json.loads(row['tags'])
            row['vip'] = row['vip'] == 'True'
            row['timestamp_signup'] = re.sub('\+00:00$', "Z", row['timestamp_signup'])
            if 'timestamp_opt' not in row:
                row['timestamp_opt'] = row['timestamp_signup']
            if 'ip_opt' not in row:
                row['ip_opt'] = row['ip_signup']
            subscribers.append(row)

    client = _client(key)
    for sub in subscribers:
        sub['status_if_new'] = sub['status']
        client.lists.members.create_or_update(
            options.list,
            get_subscriber_hash(sub['email_address']),
            sub
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='MailChimp list restore script'
    )
    parser.add_argument('--key', type=str, help='API key')
    parser.add_argument(
        '--show-lists', action='store_true', help='Show available lists'
    )
    parser.add_argument('--list', type=str, help='List ID')
    parser.add_argument('--in', dest='_in', type=str, help='Input file')
    options = parser.parse_args()

    key = options.key or os.environ.get('MAILCHIMP_KEY')
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
        parser.exit()

    if not options._in:
        parser.exit(
            status=1,
            message=(
                'Please specify input file\n'
            ),
        )

    if not options.list:
        parser.exit(
            status=1,
            message=(
                'Please specify list id\n'
            ),
        )
    restore(key, options)

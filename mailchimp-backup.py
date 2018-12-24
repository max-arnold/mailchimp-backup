#!/usr/bin/env python
"""MailChimp list backup script."""

import argparse
import csv
import io
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


FIELDS = [
    'email_address',
    'email_type',
    'status',
    'vip',
    'merge_fields.*',
    'ip_signup',
    'timestamp_signup',
    'language',
    'location.latitude',
    'location.longitude',
    'location.country_code',
    'location.timezone',
    'tags',
]


def _export_member(member):
    """Unpack a list member into a data structure specified by FIELDS."""
    mem = {}
    for field in FIELDS:
        if '.' not in field:
            mem[field] = member[field]
        else:
            fields = field.split('.')
            if fields[1] == '*':
                nested_fields = member[fields[0]].keys()
            else:
                nested_fields = [fields[1]]
            for nf in nested_fields:
                mem['%s.%s' % (fields[0], nf)] = member[fields[0]][nf]
    return mem


def to_csv(members):
    """Convert JSON data structure to CSV string."""
    with io.StringIO() as fp:
        cw = csv.writer(fp)
        if len(members):
            cw.writerow(members[0].keys())
        for member in members:
            cw.writerow(member.values())
        value = fp.getvalue()
    return value


def export_list(key, list_id):
    """Export list."""
    lst = _client(key).lists.members.all(list_id, get_all=True)
    export = []
    for member in lst.get('members', []):
        export.append(_export_member(member))
    return to_csv(export)


def export_all_lists(key, options):
    """Export all existing lists."""
    for lst in get_lists(key)['lists']:
        yield export_list(key, lst['id'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MailChimp list backup script')
    parser.add_argument('--key', type=str, help='API key')
    parser.add_argument(
        '--show-lists', action='store_true', help='Show available lists'
    )
    parser.add_argument('--list', type=str, help='List ID')
    parser.add_argument('--all-lists', action='store_true', help='List ID')
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
        parser.exit()

    if options.list:
        export_list(key, options.list)
        parser.exit()

    if options.all_lists:
        export_all_lists(key, options)
        parser.exit()

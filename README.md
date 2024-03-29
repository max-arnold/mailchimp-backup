# MailChimp list backup/restore tool

Apparently, MailChimp thinks it is completely fine to [delete your account with no warning or notification](https://blog.rongarret.info/2018/12/mailchimp-deleted-my-account-with-no.html). You can lose access to your account with no chance to backup your list, and the support won't help you. Moreover, if you go through all the comments on [the HN thread](https://news.ycombinator.com/item?id=18715866), you will find other people who had the same experience.

Fortunately, the author of that post was lucky, and his account was reinstated when the story got popular on the HN. This doesn't mean that you will be lucky as well, so you need a backup plan.

This has been on my to-do list for more than two years, and only after I read that blog post, I finally felt motivated enough to make a tool to automatically backup my personal mailing lists.

## 2022 UPDATE

The risk has been realized! Think twice if you still want to have business with Mailchimp/Intuit. They banned a whole country (Russia 🇷🇺) with no ability to save the hard-earned mailing lists.

![Mailchimp country ban](mailchimp-country-ban.png)

Now we (Russians) have a community-maintained black list of Russophobic vendors who engaged in similar practices and even stole prepaid funds: [#ВСЁЗАПОМНИМ](https://всезапомним.рф/).

If your country has data locality laws, do your due diligence and check whether your software vendor is compliant. If it is compliant and will do something like Mailchimp did, you will be able to sue it using domestic customer protection laws and save your data.

## Installation

```bash
git clone https://github.com/max-arnold/mailchimp-backup.git
cd mailchimp-backup
mkvirtualenv -p python3 mailchimp-backup
setvirtualenvproject
hash -r
pip install -r requirements.txt
```

## Backup script usage

Go to your Mailchimp account and [create an API key](https://mailchimp.com/help/about-api-keys/#Find_or_Generate_Your_API_Key). Store your API key in the environment variable named `MAILCHIMP_KEY`. Alternatively, you can specify it on the command line, but this is less secure because the key will be visible in a process list.

First, try to display your lists:

```bash
./mailchimp-backup.py --key 11223344556677889900aabbccddeeff-us0 --show-lists

ID: 1122334455, Name: "Acme Corporation", Members: 123
ID: 6677889900, Name: "Monsters Inc", Members: 456
```

If that works well, then you can export any specific list into a CSV file:

```bash
./mailchimp-backup.py --key 11223344556677889900aabbccddeeff-us0 --list 1122334455 --out 'list-{list}.csv'
```

Or you can export all lists:

```bash
./mailchimp-backup.py --key 11223344556677889900aabbccddeeff-us0 --all --out '/mnt/backup/{year}-{month}/list-{day}-{list}.csv'
```

Possible format variables: `year`, `month`, `day`, `hour`, `minute`, `second`, `list`.

## Restore script usage

```bash
./mailchimp-restore.py --key 11223344556677889900aabbccddeeff-us0 --show-lists

ID: 1122334455, Name: "Acme Corporation", Members: 1
ID: 6677889900, Name: "Monsters Inc", Members: 1
```

If that works well, then you can restore a previously exported CSV file into any specific list:

```bash
./mailchimp-restore.py --key 11223344556677889900aabbccddeeff-us0 --list 1122334455 --in 'list.csv'
```

Please note that a backup/restore cycle will lose some data (registration timestamps, stats, etc).

## Things you may also want to do

1. Ensure that backups actually contain some data (i.e. not empty)
2. Keep previous backups (will help if you accidentally destroy your own mailing list)
3. Compress and encrypt the backups
4. Automate the whole process

To do that, you can wrap the tool into a bash script and setup a daily/weekly cron job. Please make sure that you are able to receive email messages sent by the cron daemon, otherwise you will miss very important notifications.

```bash
#!/usr/bin/env bash
set -euo pipefail

export MAILCHIMP_KEY=11223344556677889900aabbccddeeff-us0
export GNUPGHOME=~/mailchimp-backup/gpg
BACKUP_DIR=~/mailchimp-backup/backup
PYTHON_BIN=~/.virtualenvs/mailchimp-backup/bin/python3
BACKUP_SCRIPT=~/mailchimp-backup/mailchimp-backup.py

# Backup
mkdir -p "${BACKUP_DIR}"
$PYTHON_BIN $BACKUP_SCRIPT --all-lists --fail-if-empty --out \
     "${BACKUP_DIR}/{year}-{month}/list-{list}-{day}-{hour}-{minute}-{second}.csv"

# Compress and encrypt
find "${BACKUP_DIR}/" -type f -name 'list-*.csv' -exec gzip \{\} \; \
     -exec gpg --encrypt --recipient you@example.com --trust-model always \{\}.gz \; \
     -exec rm -f \{\}.gz \;

# Remove backups older than 90 days
find "${BACKUP_DIR}/" -type f -name 'list-*.csv.gz.gpg' -mtime +90 -delete
find "${BACKUP_DIR}/" -mindepth 1 -type d -empty -delete
```

## Other tools

* https://mailchimp.com/help/export-and-back-up-account-data/ - built-in manual export tool (you will need to do this at least once per week)
* https://stompapp.xyz/ - was mentioned on the HN thread, but I never tried it

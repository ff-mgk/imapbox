#!/usr/bin/env python3

import os
import argparse
import configparser
from mailboxresource import MailboxClient


def load_configuration(args):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(os.path.expanduser(args.config_path))

    options = {
        'days': config.get('imapbox', 'days', fallback=args.days),
        'folder': os.path.expanduser(
            config.get('imapbox', 'folder', fallback=args.folder)
        ),
        'accounts': []
    }

    for section_name in config.sections():

        if (section_name == 'imapbox'):
            continue

        if (args.account and (args.account != section_name)):
            continue

        section = config[section_name]
        account = {
            'name': section_name,
            'host': section.get('host', args.host),
            'port': section.get('port', args.port),
            'username': section.get('username', args.username),
            'password': section.get('password', args.password),
            'imap_folder': section.get('imap_folder', args.imap_folder)
        }

        if (account['host'] is None or account['username'] is None or account['password'] is None):
            continue

        options['accounts'].append(account)

    return options


def main():
    argparser = argparse.ArgumentParser(
        description='Export messages into .eml files using IMAP protocol'
    )
    argparser.add_argument(
        '-host',
        dest='host',
        help='IMAP host'
    )
    argparser.add_argument(
        '-port',
        dest='port',
        help='IMAP port',
        type=int,
        default=993
    )
    argparser.add_argument(
        '-u',
        dest='username',
        help='Username to access email account'
    )
    argparser.add_argument(
        '-p',
        dest='password',
        help='Password to access email account'
    )
    argparser.add_argument(
        '-c',
        dest='config_path',
        help='Path to configuration file',
        default='config.ini'
    )
    argparser.add_argument(
        '-l',
        dest='folder',
        help='Local folder where to create the email folders',
        default='./archive'
    )
    argparser.add_argument(
        '-r',
        dest='imap_folder',
        help='Remote IMAP folder that should be backed up',
        default='INBOX'
    )
    argparser.add_argument(
        '-d',
        dest='days',
        help='Local folder where to create the email folders',
        type=int,
        default=None
    )
    argparser.add_argument(
        '-a',
        dest='account',
        help='Select a specific account to backup',
        default=None
    )
    args = argparser.parse_args()
    options = load_configuration(args)

    for account in options['accounts']:

        print('{}/{} (on {}:{})'.format(
            account['name'],
            account['imap_folder'],
            account['host'],
            account['port']
            )
        )

        mailbox = MailboxClient(account, options)
        stats = mailbox.copy_emails()
        mailbox.cleanup()

        print('{}/{}: {} emails created, {} emails already existed'.format(
            account['name'],
            account['imap_folder'],
            stats[0],
            stats[1]
            )
        )


if __name__ == '__main__':
    main()

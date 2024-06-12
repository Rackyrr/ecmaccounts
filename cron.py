import argparse

from app import create_app
from app.tasks.scheduled_tasks import sync_accounts, last_connection

parser = argparse.ArgumentParser(description='Check action to do on accounts')
parser.add_argument('action', type=str, help='Action to do on accounts',
                    choices=['synchro-account', 'last-connection'])

app = create_app()

if parser.parse_args().action == 'synchro-account':
    sync_accounts(app)
elif parser.parse_args().action == 'last-connection':
    last_connection(app)

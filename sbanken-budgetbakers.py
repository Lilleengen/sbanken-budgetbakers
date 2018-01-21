#!/usr/bin/python3

import json
import os

import requests
from requests.auth import HTTPBasicAuth

config = dict()

try:
    config = json.load(open(os.path.dirname(os.path.realpath(__file__)) + '/config.json'))
except OSError as e:
    print('config.json not found in script-dir')
    exit(1)

try:
    imported = json.load(open(os.path.dirname(os.path.realpath(__file__)) + '/imported.json'))
except OSError as e:
    imported = list()

token_request = requests.post('https://api.sbanken.no/identityserver/connect/token',
                              {'grant_type': 'client_credentials'},
                              auth=HTTPBasicAuth(config['sbClientId'], config['sbSecret']))

token = json.loads(token_request.text)['access_token']

sb_headers = {
    'Authorization': 'Bearer ' + token,
}

bb_headers = {
    'X-Token': config['bbToken'],
    'X-User': config['bbUser']
}

account_details_request = requests.get('https://api.sbanken.no/bank/api/v1/accounts/' + config['sbUserId'],
                                       headers=sb_headers)

account_details = json.loads(account_details_request.text)['items']

bb_accounts_request = requests.get('https://api.budgetbakers.com/api/v1/accounts', headers=bb_headers)

bb_accounts = json.loads(bb_accounts_request.text)

to_import = []

for account_detail in account_details:
    bb_account = next((x for x in bb_accounts if x['name'] == account_detail['name']), None)
    if not bb_account:
        bb_account_request = requests.post('https://api.budgetbakers.com/api/v1/account', json={
            'name': account_detail['name'],
            'initAmount': account_detail['balance']
        }, headers=bb_headers)
        bb_account = json.loads(bb_account_request.text)

    bb_accounts_request = requests.get('https://api.budgetbakers.com/api/v1/records', headers=bb_headers)

    account_transactions_request = requests.get(
        'https://api.sbanken.no/bank/api/v1/transactions/' + config['sbUserId'] + '/' + account_detail['accountNumber'],
        headers=sb_headers)
    account_transactions = json.loads(account_transactions_request.text)['items']

    for account_transaction in account_transactions:
        if account_transaction['transactionId'] not in imported:
            to_import.append(account_transaction)

bb_accounts_request = requests.get('https://api.budgetbakers.com/api/v1/accounts', headers=bb_headers)

bb_accounts = json.loads(bb_accounts_request.text)

bb_accounts_dict = dict()

for bb_account in bb_accounts:
    for account_detail in account_details:
        if bb_account['name'] == account_detail['name']:
            bb_accounts_dict[account_detail['accountNumber']] = bb_account['id']

bb_import_list = list()

for transaction in to_import:
    imported.append(transaction['transactionId'])
    bb_import_list.append({
        'categoryId': config['bbCategory'],
        'accountId': bb_accounts_dict[transaction['accountNumber']],
        'currencyId': config['bbCurrency'],
        'amount': transaction['amount'],
        'paymentType': 'debit_card',
        'note': transaction['text'],
        'date': transaction['accountingDate'][:-6] + '.000Z'
    })

bb_transaction_create_request = requests.post('https://api.budgetbakers.com/api/v1/records-bulk', json=bb_import_list,
                                              headers=bb_headers)

with open(os.path.dirname(os.path.realpath(__file__)) + '/imported.json', 'w') as outfile:
    json.dump(imported, outfile)

from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
import os
import config
import sys
import util
import json
import time
import threading
from datetime import datetime

from azure.keyvault import KeyVaultClient, KeyVaultAuthentication
from azure.common.credentials import ServicePrincipalCredentials
from web3 import Web3, HTTPProvider
from eth_account.internal.transactions import encode_transaction, serializable_unsigned_transaction_from_dict
from eth_keys import KeyAPI

def auth_callback(server, resource, scope):
    credentials = ServicePrincipalCredentials(
        client_id=config.CLIENT_ID,
        secret=config.PASSWORD,
        tenant=config.TENANT_ID,
        resource='https://vault.azure.net'
    )
    token = credentials.token
    return token['token_type'], token['access_token']

def sign_keyvault(signingClient, vault_url, key_name, key_version, tx, chain_id=0):
    unsigned_tx = serializable_unsigned_transaction_from_dict(tx)
    unsigned_tx_hash = unsigned_tx.hash()
    sig_resp = signingClient.sign(vault_url, key_name, key_version, 'ES512', unsigned_tx_hash)
    return

def signature_task(repetitions, key_name, key_version, unsigned_tx_hash, signingClient, vault_url):
    for i in range (0, repetitions):
        signingClient.sign(vault_url, key_name, key_version, 'ES512', unsigned_tx_hash)

def get_task(repetitions, key_name, key_version, key_client):
    for i in range (0, repetitions):
        key_client.get_key(key_name, version=key_version).key

def both_task(repetitions, key_name, key_version, unsigned_tx_hash, signingClient, vault_url, key_client):
    for i in range (0, repetitions):
        key_client.get_key(key_name, version=key_version).key
        signingClient.sign(vault_url, key_name, key_version, 'ES256K', unsigned_tx_hash)

if __name__ == "__main__":
    t0= time.time()

    os.environ['AZURE_CLIENT_ID'] = config.CLIENT_ID # visible in this process + all children
    os.environ['AZURE_CLIENT_SECRET'] = config.PASSWORD
    os.environ['AZURE_TENANT_ID'] = config.TENANT_ID
    credential = DefaultAzureCredential()
    key_client = KeyClient(vault_url=config.VAULT_URL, credential=credential)
    signClient = KeyVaultClient(KeyVaultAuthentication(auth_callback))

    repetitions = int(sys.argv[1])
    task = sys.argv[2]
    mode = sys.argv[3]
    if mode == "multi":
        threads = int(sys.argv[4])
    key_name = ["" for i in range(4)]
    key_version = ["" for i in range(4)]
    key_name[0] = config.KEY_NAME_TEST
    key_version[0] = config.KEY_VERSION_TEST
    key_name[1] = config.KEY_NAME_SAN
    key_version[1] = config.KEY_VERSION_SAN
    key_name[2] = config.KEY_NAME_BANKIA
    key_version[2] = config.KEY_VERSION_BANKIA
    key_name[3] = config.KEY_NAME_BBVA
    key_version[3] = config.KEY_VERSION_BBVA

    sendEthTx = {'value': 1, 'chainId': None, 'gas': 70000, 'gasPrice': 1000000000, 'nonce': 0, 'to': '0x145dc3442412EdC113b01b63e14e85BA99926830'}
    built_tx = sendEthTx
    unsigned_tx = serializable_unsigned_transaction_from_dict(built_tx)
    unsigned_tx_hash = unsigned_tx.hash()
    if mode == "multi":
        list_threads = []
        thread_repetitions = repetitions//threads
        for i in range(0, threads):
            j = 0
            if task == "sign":
                t = threading.Thread(target=signature_task, args=(thread_repetitions, key_name[j], key_version[j], unsigned_tx_hash, signClient, config.VAULT_URL))
            elif task == "get":
                t = threading.Thread(target=get_task, args=(thread_repetitions, key_name[j], key_version[j], key_client))
            else:
                t = threading.Thread(target=both_task, args=(thread_repetitions, key_name[j], key_version[j], unsigned_tx_hash, signClient, config.VAULT_URL, key_client))
            list_threads.append(t)
            t.start()
        for t in list_threads:
            t.join()
    else:
        if task == "sign":
            signature_task(repetitions, key_name[0], key_version[0], unsigned_tx_hash, signClient, config.VAULT_URL)
        elif task == "get":
            get_task(repetitions, key_name[0], key_version[0], key_client)
        else:
            both_task(repetitions, key_name[0], key_version[0], unsigned_tx_hash, signClient, config.VAULT_URL, key_client)

    t1 = time.time() - t0
    print("Time elapsed: ", t1)


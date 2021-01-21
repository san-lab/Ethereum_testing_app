#from azure.identity import DefaultAzureCredential
#from azure.keyvault.keys import KeyClient
import os
import config
import util
import sys
import json
import time
from random import seed
from random import randint
from datetime import datetime

#from azure.keyvault import KeyVaultClient, KeyVaultAuthentication
#from azure.common.credentials import ServicePrincipalCredentials
from web3 import Web3, HTTPProvider
from ethtoken.abi import EIP20_ABI
import secp256k1
from eth_account.internal.transactions import encode_transaction, serializable_unsigned_transaction_from_dict
from eth_keys import KeyAPI

from sdkms import v1

def createKey(name):
    ec_key = key_client.create_ec_key(name, curve=config.CURVE)
    packedKey = ec_key.key.x.hex() + ec_key.key.y.hex()
    publicKeyHash = w3.sha3(hexstr=packedKey)
    print(publicKeyHash.hex()[:-40])
    address = '0x' + publicKeyHash.hex()[-40:]
    checksumAdd = w3.toChecksumAddress(address)
    return { 'address': checksumAdd, 'name': name }

def auth_callback(server, resource, scope):
    credentials = ServicePrincipalCredentials(
        client_id=config.CLIENT_ID,
        secret=config.PASSWORD,
        tenant=config.TENANT_ID,
        resource='https://vault.azure.net'
    )
    token = credentials.token
    return token['token_type'], token['access_token']

#def sign_keyvault(addressSigner, signingClient, vault_url, key_name, key_version, tx, chain_id=0):
#    unsigned_tx = serializable_unsigned_transaction_from_dict(tx)
#    unsigned_tx_hash = unsigned_tx.hash()
#    valid = False
#    while not valid:
#        sig_resp = signingClient.sign(vault_url, key_name, key_version, 'ES256K', unsigned_tx_hash)
#        v, r, s, valid = util.convert_azure_secp256k1_signature_to_vrs(pubkey, unsigned_tx_hash, sig_resp.result, chain_id)
#
#    vrs = (v,r,s)
#    ret_signed_transaction = encode_transaction(unsigned_tx, vrs)
#    return address_signer, ret_signed_transaction

def login_fortanix():
    config = v1.Configuration()
    config.host = config.SDKMS_API_ENDPOINT
    config.app_api_key = config.SDKMS_API_KEY
    client = v1.ApiClient(configuration=config)
    auth_instance = v1.AuthenticationApi(api_client=client)
    try:
        auth = auth_instance.authorize()
        config.api_key['Authorization'] = auth.access_token
        config.api_key_prefix['Authorization'] = 'Bearer'
        return client
    except Exception as e:
        print("Exception when calling AuthenticationApi->authorize: %s\n" % e)
        return None

def sign_fortanix(client, tx, chain_id=0):
    unsigned_tx = serializable_unsigned_transaction_from_dict(tx)
    unsigned_tx_hash = unsigned_tx.hash()

    api_ins = v1.SecurityObjectsApi(api_client=client)
    keys = api_ins.get_security_objects(name=config.SDKMS_KEY_NAME)
    key_kid = keys[0].kid
    pubK = keys[0].pub_key.hex()

    api_instance = sdkms.v1.SignAndVerifyApi(api_client=client)
    request = sdkms.v1.SignRequest(hash_alg=v1.DigestAlgorithm.SHA256 ,hash=unsigned_tx_hash)
    try:
        signature = api_instance.sign(key_kid, request).signature
        v, r, s, valid = util.convert_azure_secp256k1_signature_to_vrs(pubK, unsigned_tx_hash, signature, chain_id)
        vrs = (v,r,s)
        ret_signed_transaction = encode_transaction(unsigned_tx, vrs)
        return address_signer, ret_signed_transaction

    except Exception as e:
        print("Exception when calling SignAndVerifyApi->sign: %s\n" % e)
        return None

#Find how not to set on environment
if __name__ == "__main__":
    t0= time.clock()

    #os.environ['AZURE_CLIENT_ID'] = config.CLIENT_ID # visible in this process + all children
    #os.environ['AZURE_CLIENT_SECRET'] = config.PASSWORD
    #os.environ['AZURE_TENANT_ID'] = config.TENANT_ID
    #credential = DefaultAzureCredential()
    #key_client = KeyClient(vault_url=config.VAULT_URL, credential=credential)
    #signClient = KeyVaultClient(KeyVaultAuthentication(auth_callback))
    fortanixClient = login_fortanix()

    arg1 = sys.argv[1]
    if arg1 == "help":
        print("\n\nCommand used to send a burst of transactions to a blockchain network. The command has this form:\n\npython akv_ethereum_signing.py mode num sig_mode account [list_endpoints]\n - mode: it can either be \"deploy\" to deploy a contract or a blockchain address to send ether to that address\n - num: number of repetitions that will be executed\n - sig_mode: can be set to local or akv to either sign locally or go through the akv \n - account: It can be santander,bbva,bankia or test selects which of the address from the AKV will be used. If sig_mode was set to local this value will be ignored and always use local account\n - [list_endpoints]: any parameter after those will be interpreted as a endpoint, you can enter as many as you want and the programm will distribute the sending of the transactions randomly among them.\n")
        sys.exit(0)
    elif arg1 == "create":
        name = sys.argv[2]
        print(name)
        w3 = Web3(HTTPProvider(config.ETHEREUM_ENDPOINT))
        createKey(name)
        sys.exit(0)
    repetitions = int(sys.argv[2])
    mode = sys.argv[1]
    signing_mode = sys.argv[3]
    signing_key = sys.argv[4]
    endpoints_addr = sys.argv[5:]

    if signing_key == "santander":
        key_name = config.KEY_NAME_SAN
        key_version = config.KEY_VERSION_SAN
    elif signing_key == "bbva":
        key_name = config.KEY_NAME_BBVA
        key_version = config.KEY_VERSION_BBVA
    elif signing_key == "bankia":
        key_name = config.KEY_NAME_BANKIA
        key_version = config.KEY_VERSION_BANKIA
    else:
        key_name = config.KEY_NAME_TEST
        key_version = config.KEY_VERSION_TEST

    web3_endpoints = list(map(lambda x: Web3(HTTPProvider(x)), endpoints_addr))
    seed(datetime.now())

    with open("./Abi.json") as f:
        ABI = json.load(f)
    with open("./Bytecode.json") as f:
        Bytecode = json.load(f)
    myContract = web3_endpoints[0].eth.contract(abi=ABI, bytecode=Bytecode['object'])
    
    if  signing_mode == "local":
        if signing_key == "local1":
            address_signer = config.LOCAL1_KEY_ADDR
            priv_key = config.LOCAL1_KEY_PRIV
        elif signing_key == "local2":
            address_signer = config.LOCAL2_KEY_ADDR
            priv_key = config.LOCAL2_KEY_PRIV
        elif signing_key == "local3":
            address_signer = config.LOCAL3_KEY_ADDR
            priv_key = config.LOCAL3_KEY_PRIV
        else:
            address_signer = config.LOCAL4_KEY_ADDR
            priv_key = config.LOCAL4_KEY_PRIV

    elif signing_mode == "fortanix":
        api_ins = v1.SecurityObjectsApi(api_client=fortanixClient)
        keys = api_ins.get_security_objects(name=config.SDKMS_KEY_NAME)
        key_pubK = keys[0].pub_key.hex()
        print("KEY_PUBK")
        print(key_pubK)
        address_signer = util.public_key_to_address(key_pubK[1:])

    else :
        #json_key = key_client.get_key(key_name, version=key_version).key
        #pubkey = util.convert_json_key_to_public_key_bytes(json_key)
        #address_signer = util.public_key_to_address(pubkey[1:])
        print("a")
    
    deployContTx = myContract.constructor('0x145dc3442412EdC113b01b63e14e85BA99926830').buildTransaction({
        'chainId': None,
        'gas': 4600000,
        'gasPrice': 1000000000,
        'nonce': web3_endpoints[0].eth.getTransactionCount(address_signer),
    })
    sendEthTx = {'value': 1, 'chainId': None, 'gas': 70000, 'gasPrice': 1000000000, 'nonce': web3_endpoints[0].eth.getTransactionCount(address_signer), 'to': mode}
    
    if mode == "deploy":
        built_tx = deployContTx
    else:
        built_tx = sendEthTx

    print(built_tx['nonce'])

    for i in range (built_tx['nonce'], built_tx['nonce']+repetitions):
        built_tx['nonce'] = i
        rand_endpoint_pos = randint(0,len(endpoints_addr)-1)
        if signing_mode == "akv":
            #address_signer, signed_transaction = sign_keyvault(address_signer, signClient, config.VAULT_URL, key_name, key_version, built_tx)
            #rawTx = signed_transaction.hex()
            print("b")
        elif signing_mode == "fortanix":
            address_signer, signed_transaction = sign_fortanix(fortanixClient, built_tx)
            rawTx = signed_transaction.hex()
        else:
            signed_transaction = web3_endpoints[rand_endpoint_pos].eth.account.signTransaction(built_tx, private_key=priv_key)
            rawTx = signed_transaction.rawTransaction

        tx_hash = web3_endpoints[rand_endpoint_pos].eth.sendRawTransaction(rawTx)
        print("tx on etherscan: ", "https://rinkeby.etherscan.io/tx/" + tx_hash.hex())
        print("Transaction hash: " + tx_hash.hex())

    print("Sent whole " + str(repetitions) +  " transactions")
    t1 = time.clock() - t0
    print("Time elapsed: ", t1) # CPU seconds elapsed (floating point)

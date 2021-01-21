import secp256k1
from eth_keys import KeyAPI
import config
from cffi import FFI
ffi = FFI()

def convert_json_key_to_public_key_bytes(json_key):
    pubkey = bytearray()
    pubkey.append(0x04)
    pubkey.extend(json_key.x)
    pubkey.extend(json_key.y)
    pubkey = bytes(pubkey)
    return pubkey

def public_key_to_address(public_key):
    return KeyAPI.PublicKey(public_key_bytes=public_key).to_checksum_address()

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')

def is_high(s):
    return s > config.HALF_CURV_ORDER


def make_canonical(sig_bytes):
    r = sig_bytes[0:32]
    s = sig_bytes[32:64]

    r_int = int_from_bytes(r)
    s_int = int_from_bytes(s)

    if is_high(s_int):
        s_int = config.CURVE_ORDER - s_int

    canonical = bytearray()
    r = int_to_bytes(r_int)
    s = int_to_bytes(s_int)
    canonical.extend(r)
    canonical.extend(s)
    return canonical

def convert_azure_secp256k1_signature_to_vrs(pub_key_bytes, msg_hash_bytes, sig_bytes, chain_id=0):
    sig_bytes = bytes(make_canonical(sig_bytes))
    print("1111")
    # Check the signature is still valid
    ecdsa_pubkey = secp256k1.PublicKey(pubkey=pub_key_bytes, raw=True)
    print("1111")
    if len(sig_bytes)<64:
        return 0,0,0, False
    sig_ser = ecdsa_pubkey.ecdsa_deserialize_compact(sig_bytes)
    print("1111")
    msg_hash_cdata = ffi.new("unsigned char[32]", bytes(msg_hash_bytes))
    verified_ecdsa = ecdsa_pubkey.ecdsa_verify(msg_hash_cdata, sig_ser, raw=True)#<----
    print("2222")
    v = -1
    unrelated = MyECDSA()
    for i in range(0, 2):
        print("aaaaa")
        recsig = unrelated.ecdsa_recoverable_deserialize(sig_bytes, i)
        print("aaaaa")
        pubkey_recovered = unrelated.ecdsa_recover(msg_hash_cdata, recsig, raw=True)#<---- parece ser msg_hash_bytes
        print("5555")
        pubser = secp256k1.PublicKey(pubkey_recovered).serialize(compressed=False)
        if pubser == pub_key_bytes:
            v = i
            break
    print("3333")
    print(v)

    assert v == 0 or v == 1

    v += 27

    print("4444")

    if chain_id > 0:
        v += chain_id * 2 + 8

    r = sig_bytes[0:32]
    s = sig_bytes[32:64]
    v = v

    return v, int_from_bytes(r), int_from_bytes(s), True

class MyECDSA(secp256k1.Base, secp256k1.ECDSA):
    def __init__(self):
        secp256k1.Base.__init__(self, ctx=None, flags=secp256k1.ALL_FLAGS)
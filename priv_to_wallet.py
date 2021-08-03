#!/usr/bin/env python
# see 
# https://www.freecodecamp.org/news/how-to-create-an-ethereum-wallet-address-from-a-private-key-ae72b0eee27b/
import sys
import ecdsa
from Crypto.Hash import keccak

# Extract public key from private key
def priv_to_pub(priv_key: bytes) -> bytes:
    key = ecdsa.SigningKey.from_string(priv_key, curve=ecdsa.SECP256k1).verifying_key
    return key.to_string()


def pub_to_wallet(pub_key: bytes) -> str:
    keccak_hash = keccak.new(data=pub_key, digest_bits=256)
    keccak_digest = keccak_hash.digest()
    # Ethereum wallet is last 20 bytes
    wallet_len = 20
    address = keccak_digest[-20:]
    return '0x' + address.hex()



if __name__ == "__main__":
    for kk in sys.argv[1:]:
        priv_key = bytes.fromhex(kk)
        pub_key = priv_to_pub(priv_key)
        wallet = pub_to_wallet(pub_key)
        print(f"{priv_key.hex()}:{wallet}")

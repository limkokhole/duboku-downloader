
#Credit: Artjom B. at https://stackoverflow.com/a/36780727/1074998

from Cryptodome import Random
from Cryptodome.Cipher import AES
import base64
from hashlib import md5

BLOCK_SIZE = 16

def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + (chr(length)*length).encode()

def unpad(data):
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

def bytes_to_key(data, salt, output=48):
    # extended from https://gist.github.com/gsakkis/4546068
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]

def encrypt(message, passphrase):
    salt = Random.new().read(8)
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message)))

def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(encrypted[16:]))

def main(ct_b64, passwd):
    return decrypt(ct_b64, passwd.encode())

#password = "ppvod".encode() #.encode: "must be str, not bytes" in `data += salt` above
#ct_b64 = "U2FsdGVkX1+WdwDTruo/F0Es1X90cKgMmW8DyzOMvxXUnZURZlHLTjgn4rd6tBDHD2LkrYoofUWzLFpaq4gCk5u3RJZmlsojry5oJjnq7Xj0jBJNsg4FkXD/5tlV1QMWVYOCZNS1Z5Jx9No22b2hc7bmbeTpRRONhKe/e7P1FVUbSjfSBjWyw80q09sr5laIsJ8BNCOK1/L5lfsVUAGLFNiQTf3SJ4YHSPprpGXmt58imaBsodeYO5Lg6thHZUEmHdjFjtyAo5ntz1Ae/nbKF4Bb6edigogE4Z2EIVtDyEYXU9m2R7rKcfu97lhv1O5FpZNhfi18p6fRzPvjT0PCygWrjT4KySn76HqQ3ingk2ryW9jTYfYyQCgOYDLpOjLP57dLgCLnRf9Ey+5X7Q/WblvfkEuy2QiOoV6mHhvDVnm9eJMrnZGmEbsby3zuQliVjOxDPtpe3WZCqncWLnMP/UU54mNEqUyB9tN35k95VXleIH8xR3hhmH8tN9fm3QcCyc3zqddTxaf5zRR/1StlteemrV95fIcFc+Vh28a3ji4NJuYkzkeynWl2YvU/gHtdoBPObHRUsOUCE04MNxQbm+0Ux7vo77Thsujl29lBG+voHmSDktXX8iVv13l3MJKtB0xLzDAZVoN7pn0rN+IVLRVxVVdBjpPkbBFaMyJ8pJLWu29kGGqFX7zDSJqyVyCElp/P8kzHEGDFgDZ17UlFpy62F57ugWRdgtNJgmoZ2LmMMdqENPe86fuuuE7FSXGXV2JLYHodX1aMkBDSMdhQj9k7dFmwfccMzUhb5tKXWQn+B2ECu+XbyUaijeb1XMwuEhaRrDjsRABGTui1xZmUbBc+imepDkyvOn3/Oft3Av3sSh4ah2G/A2GfG5vdYH+/U+RI+5MhwZCIrSZI1Ge+2wMu3MHvzhWsmJ9ZbFFgdJac+lrZ7X9doQm7GdZUNVu3YkfOvBawei0FfdeeSwSjlLog6Efcr9vUBe66KCgM2PmjKPikhPVfVXctj/zvkCEuySES5tYBBCYaUt3T4lDIdA=="
#pt = decrypt(ct_b64, password)
#print("pt", pt)
#print("pt", decrypt(encrypt(pt, password), password))




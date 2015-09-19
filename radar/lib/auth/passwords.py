import base64
import os
from random import SystemRandom
import string
import werkzeug.security

RESET_PASSWORD_MAX_AGE = 86400  # 1 day

# Parameters to user for password generation
# log2(36 ^ 10) = ~51 bits
GENERATE_PASSWORD_ALPHABET = string.ascii_lowercase + string.digits
GENERATE_PASSWORD_LENGTH = 10

NATO_ALPHABET = {
    'a': 'ALFA',
    'b': 'BRAVO',
    'c': 'CHARLIE',
    'd': 'DELTA',
    'e': 'ECHO',
    'f': 'FOXTROT',
    'g': 'GOLF',
    'h': 'HOTEL',
    'i': 'INDIA',
    'j': 'JULIETT',
    'k': 'KILO',
    'l': 'LIMA',
    'm': 'MIKE',
    'n': 'NOVEMBER',
    'o': 'OSCAR',
    'p': 'PAPA',
    'q': 'QUEBEC',
    'r': 'ROMEO',
    's': 'SIERRA',
    't': 'TANGO',
    'u': 'UNIFORM',
    'v': 'VICTOR',
    'w': 'WHISKEY',
    'x': 'XRAY',
    'y': 'YANKEE',
    'z': 'ZULU',
    '0': 'ZERO',
    '1': 'ONE',
    '2': 'TWO',
    '3': 'THREE',
    '4': 'FOUR',
    '5': 'FIVE',
    '6': 'SIX',
    '7': 'SEVEN',
    '8': 'EIGHT',
    '9': 'NINE',
}


def generate_reset_password_token():
    # Token is given to user, hash is stored
    token = base64.urlsafe_b64encode(os.urandom(32))
    token_hash = generate_password_hash(token)
    return token, token_hash


def generate_password():
    return ''.join(SystemRandom().sample(GENERATE_PASSWORD_ALPHABET, GENERATE_PASSWORD_LENGTH))


def check_reset_password_token_hash(reset_token_hash, reset_token):
    return werkzeug.security.check_password_hash(reset_token_hash, reset_token)


def generate_password_hash(password):
    # 50000 iterations
    return werkzeug.security.generate_password_hash(password, 'pbkdf2:sha1:50000')


def check_password_hash(password_hash, password):
    return werkzeug.security.check_password_hash(password_hash, password)


def password_to_nato_values(password):
    nato_values = []

    for x in password:
        nato_value = NATO_ALPHABET.get(x.lower(), x)

        if x.isupper():
            nato_value = 'CAPITAL ' + nato_value
        elif x.islower():
            nato_value = 'SMALL ' + nato_value

        nato_values.append(nato_value)

    return nato_values


def password_to_nato_str(password):
    return ', '.join(password_to_nato_values(password))


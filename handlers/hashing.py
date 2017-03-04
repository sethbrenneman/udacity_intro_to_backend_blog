import hmac
import hashlib
from string import letters
from random import choice

SECRET = 'uFxTzRVmbRmagKN9KYmu'


def hash_val(s):
    return hmac.new(SECRET, s).hexdigest()


def make_secure_val(s):
    return '%s|%s' % (s, hash_val(s))


def valid_user(h):
    user = h.split('|')[0]
    if make_secure_val(user) == h:
        return user


def make_salt(length=5):
    return ''.join(choice(letters) for l in range(length))


def make_hashed_password(p, salt=''):
    if not salt:
        salt = make_salt()
    return '%s|%s' % (salt, hashlib.sha256(salt + p).hexdigest())


def check_password(plaintext_password, hashed_password):
    salt = hashed_password.split('|')[0]
    if make_hashed_password(plaintext_password, salt=salt) == hashed_password:
        return True

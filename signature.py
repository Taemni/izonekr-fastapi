import os, hmac, hashlib
from dotenv import load_dotenv

load_dotenv(verbose=True)

def generate_hash(timestamp, msg=""):
    SecretKey = os.getenv('HMAC_SECRET_KEY')
    return hmac.new(SecretKey.encode('utf-8'), f'{msg}{timestamp}'.encode('utf-8'), hashlib.sha1).hexdigest()
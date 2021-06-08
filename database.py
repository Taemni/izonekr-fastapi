import os, pymysql
from dotenv import load_dotenv

load_dotenv(verbose=True)

def get_connection(database):
    return pymysql.connect(host=os.getenv('MYSQL_HOST'), user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD'), db=database, charset='utf8mb4')
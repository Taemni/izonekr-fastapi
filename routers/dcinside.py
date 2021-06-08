import os, time, re
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from typing import Optional
from pymysql.cursors import DictCursor

from database import get_connection
from signature import generate_hash
from utility import error

from dotenv import load_dotenv
load_dotenv(verbose=True)

Dcinside = APIRouter()

@Dcinside.get("/{gall_id}")
async def list(request: Request, gall_id: str, field: Optional[str] = None, keyword: Optional[str] = None, page: Optional[int] = 1):
    client_key = request.headers.get('X-API-KEY')
    t = request.headers.get('X-TIMESTAMP')

    server_key = generate_hash(t, gall_id)
    if server_key != client_key or int(time.time()) - int(t) > 300:
        return JSONResponse(status_code=400, content={'result':False, 'message':'API key not valid. Please pass a valid API key.'})

    conn = get_connection(os.getenv('MYSQL_DATABASE_DC'))
    page = (page-1)*20

    sql = "SELECT {} from gall_{} where 1=1"
    sql_data = []

    if field and keyword:
        sql += " and {} like %s".format(field)
        sql_data.append("%"+keyword+"%")

    try:
        with conn.cursor() as cursor:
            status = cursor.execute(sql.format("COUNT(*)", gall_id), sql_data)
            cnt = cursor.fetchone()[0]
    except:
        cnt = 0

    try:
        # Add order, limit
        sql += " {}".format(f" order by no desc limit {page}, 20")

        with conn.cursor(DictCursor) as cursor:
            status = cursor.execute(sql.format(f"no,subject,user_type,name,user_id,ip,memo,datetime,img_icon", gall_id), sql_data)
            if status:
                result = cursor.fetchall()
                for row in result:
                    if row['user_type'] == 3:
                        row['name'] = f"{row['name']} ({row['ip']})"
                    else:
                        row['name'] = f"{row['name']} ({row['user_id']}) <a href='https://gallog.dcinside.com/{row['user_id']}' target='_blank'><img style='vertical-align:middle;' src='/static/img/dcinside/{row['user_type']}.gif'></a>"
                    row['gall_id'] = gall_id
                return {'result':True, 'total':cnt, 'data':result}
            else:
                return {'result':False, 'total':0, 'data':None}
    finally:
        conn.close()

@Dcinside.get("/{gall_id}/{no}")
async def list(request: Request, gall_id: str, no: int):
    client_key = request.headers.get('X-API-KEY')
    t = request.headers.get('X-TIMESTAMP')

    server_key = str(no) + generate_hash(t, gall_id)
    if server_key != client_key or int(time.time()) - int(t) > 10:
        return JSONResponse(status_code=400, content={'result':False, 'message':'API key not valid. Please pass a valid API key.'})

    conn = get_connection(os.getenv('MYSQL_DATABASE_DC'))

    try:
        with conn.cursor(DictCursor) as cursor:
            cursor.execute(f"SELECT memo from gall_{gall_id} where no = %s", no)
            result = cursor.fetchone()
            result['memo'] = re.sub(r'(dcimg[0-9].dcinside.co.kr)', 'images.dcinside.com', result['memo'])
            result['memo'] = re.sub(r'(dcimg[0-9].dcinside.com)', 'images.dcinside.com', result['memo'])
            result['memo'] = result['memo'] + '<br><br>'
            return {'result':True, 'data':result}
    finally:
        conn.close()
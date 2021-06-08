import os, time
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
from pymysql.cursors import DictCursor
from datetime import datetime

from database import get_connection
from signature import generate_hash
from utility import error, remove_tag, myNick

from dotenv import load_dotenv
load_dotenv(verbose=True)

class MailIn(BaseModel):
    mail_id: str
    member: str
    subject: str
    content: str
    time: datetime
    is_img: int

Mail = APIRouter()

@Mail.get("", summary="Get All Mail")
async def get_mail(request: Request, q: Optional[str] = None, member: Optional[str] = None, date: Optional[str] = None, sort: Optional[str] = 'desc', birthday: Optional[str] = None, page: Optional[int] = 1):
    client_key = request.headers.get('X-API-KEY')
    t = request.headers.get('X-TIMESTAMP')

    server_key = generate_hash(t)
    if server_key != client_key or int(time.time()) - int(t) > 600:
        return JSONResponse(status_code=400, content={'result':False, 'message':'API key not valid. Please pass a valid API key.'})

    conn = get_connection(os.getenv('MYSQL_DATABASE_PM'))
    page = (page-1)*20

    sql = "SELECT {} FROM private_mail where 1=1"
    sql_data = []

    if q:
        sql += " and (subject like %s or content like %s)"
        sql_data.extend(["%"+q+"%", "%"+q+"%"])

    if member:
        sql += " and member = %s"
        sql_data.append(member)

    if date:
        sql += " and time like %s"
        sql_data.append(date+"%")

    if birthday == '1':
        sql += " and is_birthday = %s"
        sql_data.append(1)

    try:
        with conn.cursor() as cursor:
            status = cursor.execute(sql.format("COUNT(*)"), sql_data)
            cnt = cursor.fetchone()[0]
    except:
        cnt = 0

    try:
        # Add order, limit
        sql += " {}".format(f" order by idx {sort} limit {page}, 20")

        with conn.cursor(DictCursor) as cursor:
            status = cursor.execute(sql.format(f"id,member,preview,subject,time,is_img,is_unread"), sql_data)
            if status:
                result = cursor.fetchall()
                for row in result:
                    row['time'] = row['time'].strftime("%Y-%m-%d %H:%M")
                    row['subject'] = myNick(row['subject'])
                    row['preview'] = myNick(row['preview'])
                return {'result':True, 'total':cnt, 'data':result}
            else:
                return {'result':False, 'total':0, 'data':None}
    finally:
        conn.close()

@Mail.post("", status_code=201)
async def create_mail(request: Request, mail: MailIn):
    client_key = request.headers.get('X-API-KEY')
    t = request.headers.get('X-TIMESTAMP')

    server_key = generate_hash(t)
    if server_key != client_key or int(time.time()) - int(t) > 600:
        return JSONResponse(status_code=400, content={'result':False, 'message':'API key not valid. Please pass a valid API key.'})

    conn = get_connection(os.getenv('MYSQL_DATABASE_PM'))

    sql = "INSERT INTO private_mail (`id`, `member`, `subject`, `preview`, `content`, `time`, `is_img`) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    sql_data = (mail.mail_id, mail.member, mail.subject, remove_tag(mail.content)[:50], mail.content, mail.time, mail.is_img)

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, sql_data)
        conn.commit()
    finally:
        conn.close()

    return {'result':True}

@Mail.get("/{mail_id}", summary="Get Mail")
async def mail_view(request: Request, mail_id: str):
    client_key = request.headers.get('X-API-KEY')
    t = request.headers.get('X-TIMESTAMP')

    server_key = generate_hash(t, mail_id)
    if server_key != client_key or int(time.time()) - int(t) > 10:
        return JSONResponse(status_code=400, content={'result':False, 'message':'API key not valid. Please pass a valid API key.'})

    conn = get_connection(os.getenv('MYSQL_DATABASE_PM'))

    try:
        with conn.cursor(DictCursor) as cursor:
            status = cursor.execute("SELECT id,member,subject,content,time,is_img FROM private_mail where id = %s", (mail_id,))
            if status:
                result = cursor.fetchone()
                result['subject'] = myNick(result['subject'])
                result['content'] = myNick(result['content'])
                result['time'] = result['time'].strftime("%Y-%m-%d %H:%M")
                return result
            else:
                return error("메일이 존재하지 않습니다.")
    finally:
        conn.close()

@Mail.delete("/{mail_id}", summary="Delete Mail")
async def mail_view(request: Request, mail_id: str):
    client_key = request.headers.get('X-API-KEY')
    t = request.headers.get('X-TIMESTAMP')

    server_key = generate_hash(t, mail_id)
    if server_key != client_key or int(time.time()) - int(t) > 600:
        return JSONResponse(status_code=400, content={'result':False, 'message':'API key not valid. Please pass a valid API key.'})

    conn = get_connection(os.getenv('MYSQL_DATABASE_PM'))

    try:
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("DELETE FROM private_mail where id = %s", (mail_id,))
        conn.commit()
    finally:
        conn.close()

    return {'result':True}

@Mail.put("/{mail_id}", summary="Update Mail")
async def mail_update(request: Request, mail: MailIn):
    client_key = request.headers.get('X-API-KEY')
    t = request.headers.get('X-TIMESTAMP')

    server_key = generate_hash(t, mail.mail_id)
    if server_key != client_key or int(time.time()) - int(t) > 600:
        return JSONResponse(status_code=400, content={'result':False, 'message':'API key not valid. Please pass a valid API key.'})

    conn = get_connection(os.getenv('MYSQL_DATABASE_PM'))

    sql = "UPDATE private_mail set `member` = %s, `subject` = %s, `preview` = %s, `content` = %s, `time` = %s, `is_img` = %s where id = %s;"
    sql_data = (mail.member, mail.subject, remove_tag(mail.content)[:50], mail.content, mail.time, mail.is_img, mail.mail_id)

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, sql_data)
        conn.commit()
    finally:
        conn.close()

    return {'result':True}
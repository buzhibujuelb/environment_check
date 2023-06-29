#!/usr/bin/python
import os
import requests
import psycopg2
import smtplib
from flask import Flask, render_template,request, url_for, redirect,jsonify
from email.mime.text import MIMEText
HOST='::'
#HOST='0.0.0.0'
PORT=5001
LIMIT = 10
app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='127.0.0.1',
                            database='sensordata',
                            user='postgres',
                            password='3.1415926',port="5432")
    return conn





@app.route('/sensor1')
def sensor1():
    start_tis_tamp = request.args.get('start')
    end_tis_tamp = request.args.get('end')
    limit = request.args.get('limit')
    conn = get_db_connection()
    sql = 'SELECT * FROM sensor1'
    if end_tis_tamp and start_tis_tamp:
        sql += ' WHERE tistamp >= %s AND tistamp <= %s'
    elif start_tis_tamp:
        sql += ' WHERE tistamp >= %s'
    elif end_tis_tamp:
        sql += ' WHERE tistamp <= %s'

    sql += ' order by tistamp '
    if limit:
        sql += f' OFFSET (SELECT COUNT(*) FROM sensor2) - {limit}'
        sql += ' LIMIT %s' % (limit)
    elif (not end_tis_tamp) and (not start_tis_tamp):
        sql += f' OFFSET (SELECT COUNT(*) FROM sensor2) - {LIMIT}'
        sql += ' LIMIT %s' % (LIMIT)
    elif start_tis_tamp and end_tis_tamp:
        sql = 'SELECT * FROM sensor1 WHERE tistamp >= %s AND tistamp <= %s AND MOD(tistamp::int, (SELECT COUNT(*)/200 FROM sensor1 WHERE tistamp >= %s AND tistamp <= %s)) = 0 ORDER BY tistamp LIMIT 200'


    cur = conn.cursor()
    if start_tis_tamp and end_tis_tamp and limit:
        cur.execute(sql, (start_tis_tamp,end_tis_tamp))
    elif start_tis_tamp and end_tis_tamp:
        cur.execute(sql, (start_tis_tamp,end_tis_tamp,start_tis_tamp,end_tis_tamp))
    elif start_tis_tamp:
        cur.execute(sql, (start_tis_tamp,))
    elif end_tis_tamp:
        cur.execute(sql, (end_tis_tamp,))
    else:
        cur.execute(sql)
    measuredatas = cur.fetchall()
    cur.close()
    conn.close()
    response = jsonify(measuredatas)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response




@app.route('/sensor2')
def sensor2():
    start_tis_tamp = request.args.get('start')
    end_tis_tamp = request.args.get('end')
    limit = request.args.get('limit')
    conn = get_db_connection()
    sql = 'SELECT * FROM sensor2'
    if end_tis_tamp and start_tis_tamp:
        sql += ' WHERE tistamp >= %s AND tistamp <= %s'
    elif start_tis_tamp:
        sql += ' WHERE tistamp >= %s'
    elif end_tis_tamp:
        sql += ' WHERE tistamp <= %s'

    sql += ' order by tistamp '
    if limit:
        sql += f' OFFSET (SELECT COUNT(*) FROM sensor2) - {limit}'
        sql += ' LIMIT %s' % (limit)
    elif (not end_tis_tamp) and (not start_tis_tamp):
        sql += f' OFFSET (SELECT COUNT(*) FROM sensor2) - {LIMIT}'
        sql += ' LIMIT %s' % (LIMIT)
    elif start_tis_tamp and start_tis_tamp:
       sql = 'SELECT * FROM sensor2 WHERE tistamp >= %s AND tistamp <= %s AND MOD(tistamp::int, (SELECT COUNT(*)/200 FROM sensor2 WHERE tistamp >= %s AND tistamp <= %s)) = 0 ORDER BY tistamp LIMIT 200'


    cur = conn.cursor()
    if end_tis_tamp and start_tis_tamp and limit:
        cur.execute(sql, (start_tis_tamp,end_tis_tamp))
    elif end_tis_tamp and start_tis_tamp:
        cur.execute(sql, (start_tis_tamp,end_tis_tamp,start_tis_tamp,end_tis_tamp))
    elif start_tis_tamp:
        cur.execute(sql, (start_tis_tamp,))
    elif end_tis_tamp:
        cur.execute(sql, (end_tis_tamp,))
    else:
        cur.execute(sql)
    measuredatas = cur.fetchall()
    cur.close()
    conn.close()
    response = jsonify(measuredatas)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
@app.route('/api/send-wechat',methods=['GET'])
def send():
    url='https://sctapi.ftqq.com/SCT214259TNqTtqelm8r5agYzSDZttV785.send'
    title_tis_tamp=request.args.get('title')
    desp_tis_tamp=request.args.get('desp')
    if title_tis_tamp:
        pass
    else:
        title_tis_tamp='EXCEPTION OCCURRED'
    if desp_tis_tamp:
        pass
    else:
        desp_tis_tamp=666

    myParams={'title':title_tis_tamp,'desp':desp_tis_tamp,'channel':9}
    res=requests.post(url=url,data=myParams)
    print('url:',res.request.url)
    print (res.text)
    return "Notification sent"

@app.route('/api/send-email',methods=['GET'])
def send2():
    desp_tis_tamp=request.args.get('desp')
    title_tis_tamp=request.args.get('title')
    if title_tis_tamp:
        pass
    else:
        title_tis_tamp='Exception Occurred'
    if desp_tis_tamp:
        pass
    else:
        desp_tis_tamp='666'
    HOST='smtp.qq.com'
    FROM='1968374004@qq.com'
    TO=request.args.get('to')
    if TO:
        pass
    else:
        TO='1752862657@qq.com'
    msg=MIMEText(desp_tis_tamp,'html','utf-8')
    msg['tltle']=title_tis_tamp
    msg['From']=FROM
    msg['To']=TO

    server=smtplib.SMTP_SSL(HOST,465)
    server.login(FROM,'lkyvupmrvdgnfccc')
    server.sendmail(FROM,[TO],msg.as_string())
    server.quit()
    return "Notification sent"
if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug =True)

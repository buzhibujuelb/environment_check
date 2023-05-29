import os
import psycopg2
from flask import Flask, render_template,request, url_for, redirect,jsonify

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
    else:
        sql += f' OFFSET (SELECT COUNT(*) FROM sensor2) - {LIMIT}'
        sql += ' LIMIT %s' % (LIMIT)

    cur = conn.cursor()
    if start_tis_tamp and end_tis_tamp:
        cur.execute(sql, (start_tis_tamp,end_tis_tamp))
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
    else:
        sql += f' OFFSET (SELECT COUNT(*) FROM sensor2) - {LIMIT}'
        sql += ' LIMIT %s' % (LIMIT)

    cur = conn.cursor()
    if end_tis_tamp and start_tis_tamp:
        cur.execute(sql, (start_tis_tamp,end_tis_tamp))
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

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug =True)

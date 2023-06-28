import psycopg2
import pandas as pd

gongsi_conn = psycopg2.connect(database="sensordata", user="postgres",
 password="3.1415926", host="127.0.0.1", port="5432")

# 获取数据
data = pd.read_sql("select * from sensor1;",con=gongsi_conn)
gongsi_conn.close # 关闭数据库连接

print(data)
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def execute_query(sql):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        results = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return {'success': True, 'results': results, 'columns': columns}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        cur.close()
        conn.close()


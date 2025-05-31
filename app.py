from flask import Flask, render_template, jsonify, request
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import pytz

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL',  <'ENTER DATABASE URL HERE'>)

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT 
            app_name,
            overall_app_rating,
            ios_app_rating,
            android_app_rating,
            android_detailed_app_rating,
            ios_total_reviews,
            android_total_reviews,
            combined_total_reviews,
            ios_app_rank,
            date,
            timestamp
        FROM app_stats 
        WHERE (date, app_name) IN (
            SELECT date, app_name
            FROM app_stats
            WHERE date = (SELECT MAX(date) FROM app_stats)
        )
        ORDER BY overall_app_rating DESC
    """)
    app_stats = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', app_stats=app_stats)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    date = request.args.get('date')
    app_name = request.args.get('app_name')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if date and app_name:
        cur.execute("""
            SELECT * FROM app_stats 
            WHERE date = %s AND app_name = %s
        """, (date, app_name))
    elif date:
        cur.execute("""
            SELECT * FROM app_stats 
            WHERE date = %s
        """, (date,))
    else:
        cur.execute("""
            SELECT * FROM app_stats 
            WHERE date = (SELECT MAX(date) FROM app_stats)
        """)

    stats = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(stats)

@app.template_filter('format_number')
def format_number(value):
    return "{:,}".format(int(value))

@app.template_filter('format_datetime')
def format_datetime(value):
    mountain_tz = pytz.timezone('US/Mountain')
    value = value.astimezone(mountain_tz)
    return value.strftime('%Y-%m-%d %I:%M:%S %p %Z')

if __name__ == '__main__':
    app.run(debug=True)
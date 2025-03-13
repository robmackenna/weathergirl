ffrom flask import Flask, jsonify, request, render_template
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Load DB credentials from environment or use defaults.
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'weather_db')
DB_USER = os.environ.get('DB_USER', 'weather_user')
DB_PASS = os.environ.get('DB_PASS', 'YourStrongPassword')
DB_PORT = os.environ.get('DB_PORT', '5432')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather_data', methods=['GET'])
def weather_data():
    """
    Returns JSON array of weather data rows. Expects query parameters:
      start (ISO datetime), end (ISO datetime).
    """
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    if not start_time or not end_time:
        return jsonify({'error': 'Must provide start and end parameters'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT time, temp, pressure
        FROM weather
        WHERE time BETWEEN %s AND %s
        ORDER BY time ASC
    """
    cur.execute(query, (start_time, end_time))
    rows = cur.fetchall()

    data = []
    for row in rows:
        data.append({
            'time': row[0].isoformat() if row[0] else None,
            'temp': row[1],
            'pressure': row[2]
        })

    cur.close()
    conn.close()

    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

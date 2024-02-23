from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# Function to create a database connection
def create_connection():
    conn = sqlite3.connect('data.db')
    return conn

# Function to create tables if they don't exist
def create_tables(conn):
    print('creating tables')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deviceId TEXT UNIQUE,
            name TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            heap INTEGER,
            deviceId TEXT,
            rssi INTEGER,
            value REAL,
            timestamp TEXT,
            FOREIGN KEY (deviceId) REFERENCES device (deviceId)
        )
    ''')
    conn.commit()

# Function to insert data into device table
def insert_device(conn, deviceId, name):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO device (deviceId, name)
        VALUES (?, ?)
    ''', (deviceId, name,))
    conn.commit()

# Function to insert data into sensor_data table
def insert_data(conn, deviceId, rssi, value, heap):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (deviceId, rssi, value, heap, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (deviceId, rssi, value, heap, timestamp))
    conn.commit()

# Route to receive JSON data and save it into the database
@app.route('/api/save_data', methods=['POST'])
def save_data():
    data = request.json
    deviceId = data.get('deviceId')
    rssi = data.get('rssi')
    value = data.get('value')
    heap = data.get('heap')

    conn = create_connection()
    insert_data(conn, deviceId, rssi, value, heap)
    conn.close()

    return jsonify({'message': 'Data saved successfully'}), 200

# Params: from, to, id
@app.route('/api/sensors/<id>/data', methods=['GET'])
@cross_origin()
def get_sensor_data(id):
    from_date = request.args.get('from')
    to_date = request.args.get('to')

    conn = create_connection()
    cursor = conn.cursor()

    args = [id]
    sql = 'SELECT timestamp, value FROM sensor_data WHERE deviceId = ?'
    if from_date:
        sql += ' AND timestamp >= ?'
        args.append(from_date)
    if to_date:
        sql += ' AND timestamp <= ?'
        args.append(to_date)
    
    cursor.execute(sql, tuple(args))
    data = cursor.fetchall()
    conn.close()
    result = [{"timestamp": x[0], "value": x[1]} for x in data]
    return jsonify(result)


# Initialization

conn = create_connection()
create_tables(conn)
insert_device(conn, '3f9176ec42af4511ee10', 'Water level sensor 1')
conn.close()

if __name__ == '__main__':
    app.run(debug=True)

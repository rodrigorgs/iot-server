from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

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
            deviceId TEXT,
            rssi INTEGER,
            distance REAL,
            heap INTEGER,
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
def insert_data(conn, deviceId, rssi, distance, heap):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (deviceId, rssi, distance, heap, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (deviceId, rssi, distance, heap, timestamp))
    conn.commit()

# Route to receive JSON data and save it into the database
@app.route('/api/save_data', methods=['POST'])
def save_data():
    data = request.json
    deviceId = data.get('deviceId')
    rssi = data.get('rssi')
    distance = data.get('distance')
    heap = data.get('heap')

    conn = create_connection()
    insert_data(conn, deviceId, rssi, distance, heap)
    conn.close()

    return jsonify({'message': 'Data saved successfully'}), 200

# Initialization

conn = create_connection()
create_tables(conn)
insert_device(conn, '3f9176ec42af4511ee10', 'Water level sensor 1')
conn.close()

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:secret@localhost:5432/iotserver')
# DATABASE_URL uses postgres:// but SQLAlchemy only accepts postgresql://
db_url = db_url.replace('postgres://', 'postgresql://')
engine = create_engine(db_url)


# Function to create tables if they don't exist
def create_tables(conn):
    print('creating tables')
    conn.execute(text('''
        CREATE TABLE IF NOT EXISTS device (
            id SERIAL PRIMARY KEY,
            deviceId TEXT UNIQUE,
            name TEXT
        )
    '''))
    conn.execute(text('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id SERIAL PRIMARY KEY,
            heap INTEGER,
            deviceId TEXT,
            rssi INTEGER,
            value REAL,
            timestamp TEXT,
            FOREIGN KEY (deviceId) REFERENCES device (deviceId)
        )
    '''))
    conn.commit()

# Function to insert data into device table
def insert_device(conn, deviceId, name):
    conn.execute(text('''
        INSERT INTO device (deviceId, name)
        VALUES (:deviceId, :name)
        ON CONFLICT DO NOTHING
    '''), {"deviceId": deviceId, "name": name,})
    conn.commit()

# Function to insert data into sensor_data table
def insert_data(conn, deviceId, rssi, value, heap):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(text('''
        INSERT INTO sensor_data (deviceId, rssi, value, heap, timestamp)
        VALUES (:deviceId, :rssi, :value, :heap, :timestamp)
    '''), {'deviceId': deviceId, 'rssi': rssi, 'value': value, 'heap': heap, 'timestamp': timestamp})
    conn.commit()

# Route to receive JSON data and save it into the database
@app.route('/api/save_data', methods=['POST'])
def save_data():
    data = request.json
    deviceId = data.get('deviceId')
    rssi = data.get('rssi')
    value = data.get('value')
    heap = data.get('heap')

    with engine.connect() as conn:
        insert_data(conn, deviceId, rssi, value, heap)
        conn.close()
        return jsonify({'message': 'Data saved successfully'}), 200

# Params: from, to, id
@app.route('/api/sensors/<id>/data', methods=['GET'])
@cross_origin()
def get_sensor_data(id):
    from_date = request.args.get('from')
    to_date = request.args.get('to')

    with engine.connect() as conn:
        args = {'deviceId': id}
        sql = 'SELECT timestamp, value FROM sensor_data WHERE deviceId = :deviceId'
        if from_date:
            sql += ' AND timestamp >= :from_date'
            args['from_date'] = from_date
        if to_date:
            sql += ' AND timestamp <= :to_date'
            args['to_date'] = to_date
        
        data = conn.execute(text(sql), args)
        result = [{"timestamp": x[0], "value": x[1]} for x in data]
        return jsonify(result)


# Initialization

with engine.connect() as conn:
    # conn = create_connection()
    create_tables(conn)
    insert_device(conn, '3f9176ec42af4511ee10', 'Water level sensor 1')
    print('done')

if __name__ == '__main__':
    app.run(debug=True)

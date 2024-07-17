from flask import Flask, request, jsonify, send_from_directory, render_template_string
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='static')

def init_db():
    conn = sqlite3.connect('gym.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS activities
                 (id INTEGER PRIMARY KEY, machine_id INTEGER, set1 INTEGER, set2 INTEGER, set3 INTEGER, date DATE)''')
    conn.commit()
    conn.close()

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    machine_id = data['machine']
    set1 = data['set1']
    set2 = data['set2']
    set3 = data['set3']
    date = datetime.now().date()

    print(f"Received data: {data}")

    conn = sqlite3.connect('gym.db')
    c = conn.cursor()
    c.execute("SELECT * FROM activities WHERE machine_id = ? AND date = ?", (machine_id, date))
    existing_record = c.fetchone()

    if existing_record:
        c.execute("UPDATE activities SET set1 = ?, set2 = ?, set3 = ? WHERE machine_id = ? AND date = ?", 
                  (set1, set2, set3, machine_id, date))
        print(f"Updated record for machine {machine_id} on date {date}")
    else:
        c.execute("INSERT INTO activities (machine_id, set1, set2, set3, date) VALUES (?, ?, ?, ?, ?)", 
                  (machine_id, set1, set2, set3, date))
        print(f"Inserted new record for machine {machine_id} on date {date}")

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

@app.route('/')
def serve_static():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/machine/<int:machine_id>')
def machine_records(machine_id):
    conn = sqlite3.connect('gym.db')
    c = conn.cursor()
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    c.execute("SELECT * FROM activities WHERE machine_id = ? AND date IN (?, ?)", (machine_id, today, yesterday))
    records = c.fetchall()
    conn.close()

    print(f"Fetched records for machine {machine_id}: {records}")

    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Machine {{ machine_id }} Records</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 20px;
            }
            h1 {
                margin-bottom: 20px;
            }
            table {
                width: 50%;
                margin: auto;
                border-collapse: collapse;
            }
            th, td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <h1>Records for Machine {{ machine_id }}</h1>
        <table>
            <tr>
                <th>Date</th>
                <th>Set 1 Weight</th>
                <th>Set 2 Weight</th>
                <th>Set 3 Weight</th>
            </tr>
            {% for record in records %}
            <tr>
                <td>{{ record[5] }}</td>
                <td>{{ record[2] }}</td>
                <td>{{ record[3] }}</td>
                <td>{{ record[4] }}</td>
            </tr>
            {% endfor %}
        </table>
        <br>
        <button onclick="window.location.href='/'">Go Back</button>
    </body>
    </html>
    '''
    return render_template_string(html, machine_id=machine_id, records=records)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)

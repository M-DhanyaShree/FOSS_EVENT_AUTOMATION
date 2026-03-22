from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os
import io
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, '.env'))
sys.path.append(ROOT_DIR)
from drive_integration.drive_handler import DriveHandler
from database.db_setup import init_db

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'event_management.db')

if not os.path.exists(DB_PATH):
    init_db()

drive_handler = DriveHandler()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events').fetchall()
    conn.close()
    return jsonify([dict(e) for e in events])

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    name = data.get('name')
    mode = data.get('mode') 

    conn = get_db_connection()
    existing = conn.execute('SELECT id FROM events WHERE name = ?', (name,)).fetchone()
    if existing:
        conn.close()
        return jsonify({'error': 'Event name already exists'}), 400
        
    folder_ids = drive_handler.initialize_event_folders(name)
    main_folder_id = folder_ids['root'] if folder_ids else None
    
    cursor = conn.cursor()
    cursor.execute('INSERT INTO events (name, mode, drive_folder_id) VALUES (?, ?, ?)',
                (name, mode, main_folder_id))
    event_id = cursor.lastrowid
    
    cursor.execute('INSERT INTO event_details (event_id) VALUES (?)', (event_id,))
    
    conn.commit()
    conn.close()
    return jsonify({'id': event_id, 'name': name})

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM budget_items WHERE event_id = ?', (event_id,))
    conn.execute('DELETE FROM event_flow WHERE event_id = ?', (event_id,))
    conn.execute('DELETE FROM event_details WHERE event_id = ?', (event_id,))
    conn.execute('DELETE FROM resources WHERE event_id = ?', (event_id,))
    conn.execute('DELETE FROM budget_bills WHERE event_id = ?', (event_id,))
    conn.execute('DELETE FROM tasks WHERE event_id = ?', (event_id,))
    conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Event deleted'})

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
        
    details = conn.execute('SELECT * FROM event_details WHERE event_id = ?', (event_id,)).fetchone()
    flow = conn.execute('SELECT * FROM event_flow WHERE event_id = ?', (event_id,)).fetchall()
    budget_items = conn.execute('SELECT * FROM budget_items WHERE event_id = ?', (event_id,)).fetchall()
    budget_bills = conn.execute('SELECT * FROM budget_bills WHERE event_id = ?', (event_id,)).fetchall()
    tasks = conn.execute('SELECT * FROM tasks WHERE event_id = ?', (event_id,)).fetchall()
    resources = conn.execute('SELECT * FROM resources WHERE event_id = ?', (event_id,)).fetchall()
    
    conn.close()
    
    return jsonify({
        'event': dict(event),
        'details': dict(details) if details else {},
        'flow': [dict(r) for r in flow],
        'budget_items': [dict(b) for b in budget_items],
        'budget_bills': [dict(b) for b in budget_bills],
        'tasks': [dict(t) for t in tasks],
        'resources': [dict(r) for r in resources]
    })

@app.route('/api/events/<int:event_id>/details', methods=['PUT'])
def update_details(event_id):
    data = request.json
    conn = get_db_connection()
    conn.execute('''
        UPDATE event_details SET
        venue = ?, time = ?, type = ?, description = ?, expected_participants = ?, organizers = ?
        WHERE event_id = ?
    ''', (data.get('venue'), data.get('time'), data.get('type'), data.get('description'), 
          data.get('expected_participants'), data.get('organizers'), event_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Details updated'})

@app.route('/api/events/<int:event_id>/flow', methods=['POST'])
def add_flow(event_id):
    data = request.json
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO event_flow (event_id, round_name, date_time, participants_count, volunteer_in_charge, faculty_in_charge)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (event_id, data.get('round_name'), data.get('date_time'), 
          data.get('participants_count'), data.get('volunteer_in_charge'), data.get('faculty_in_charge')))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Flow item added'})

@app.route('/api/events/<int:event_id>/budget', methods=['POST'])
def add_budget_item(event_id):
    data = request.json
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO budget_items (event_id, item_name, quantity, unit_price)
        VALUES (?, ?, ?, ?)
    ''', (event_id, data.get('item_name'), data.get('quantity'), data.get('unit_price')))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Budget item added'})

@app.route('/api/events/<int:event_id>/tasks', methods=['POST'])
def add_task(event_id):
    data = request.json
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO tasks (event_id, task_name, assigned_to, status, progress_comments)
        VALUES (?, ?, ?, ?, ?)
    ''', (event_id, data.get('task_name'), data.get('assigned_to'), 'pending', ''))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task added'})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task deleted'})

@app.route('/api/budget/<int:item_id>', methods=['DELETE'])
def delete_budget_item(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM budget_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Budget item deleted'})

@app.route('/api/flow/<int:flow_id>', methods=['DELETE'])
def delete_flow_item(flow_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM event_flow WHERE id = ?', (flow_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Flow item deleted'})

@app.route('/api/resources/<int:res_id>', methods=['DELETE'])
def delete_resource(res_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM resources WHERE id = ?', (res_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Resource deleted'})
def update_task(task_id):
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET status = ?, progress_comments = ? WHERE id = ?',
                (data.get('status'), data.get('progress_comments'), task_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task updated'})

@app.route('/api/events/<int:event_id>/upload', methods=['POST'])
def upload_file(event_id):
    category = request.form.get('category') 
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    conn = get_db_connection()
    event = conn.execute('SELECT name, drive_folder_id FROM events WHERE id = ?', (event_id,)).fetchone()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
        
    folder_mapping = {
        'Poster': 'Posters',
        'Resource': 'Resources',
        'Bill': 'Budget',
        'Content': 'Content',
        'Picture': 'Event_Pictures',
        'Video': 'Event_Videos',
        'Document': 'Resources'
    }
    
    target_folder_name = folder_mapping.get(category, 'Resources')
    
    main_folder_id = event['drive_folder_id']
    target_folder_id = main_folder_id 
    
    try:
        if not drive_handler.service:
            return jsonify({'error': 'Drive service not available'}), 500
            
        query = f"name = '{target_folder_name}' and '{main_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = drive_handler.service.files().list(q=query, fields='files(id)').execute()
        files = results.get('files', [])
        if files:
            target_folder_id = files[0]['id']
            
        file_bytes = file.read()
        file_stream = io.BytesIO(file_bytes)
        
        file_id, drive_link = drive_handler.upload_file_from_stream(
            file_stream, file.filename, file.mimetype or 'application/octet-stream', target_folder_id
        )
        
        if category == 'Bill':
            conn.execute('INSERT INTO budget_bills (event_id, file_name, drive_file_id, drive_link) VALUES (?, ?, ?, ?)',
                        (event_id, file.filename, file_id, drive_link))
        else:
            conn.execute('INSERT INTO resources (event_id, category, file_name, drive_file_id, drive_link) VALUES (?, ?, ?, ?, ?)',
                        (event_id, category, file.filename, file_id, drive_link))
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'File uploaded', 'link': drive_link, 'drive_id': file_id})
    except Exception as e:
        if 'conn' in locals(): conn.close()
        print(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/init_db', methods=['GET'])
def run_init_db():
    init_db()
    return jsonify({'message': 'DB initialized'})

from utils.pdf_generator import generate_event_pdf

@app.route('/api/events/<int:event_id>/report', methods=['GET'])
def get_report(event_id):
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
        
    details = conn.execute('SELECT * FROM event_details WHERE event_id = ?', (event_id,)).fetchone()
    flow = conn.execute('SELECT * FROM event_flow WHERE event_id = ?', (event_id,)).fetchall()
    budget_items = conn.execute('SELECT * FROM budget_items WHERE event_id = ?', (event_id,)).fetchall()
    resources = conn.execute('SELECT * FROM resources WHERE event_id = ?', (event_id,)).fetchall()
    conn.close()
    
    link_name = request.args.get('link_name')
    link_url = request.args.get('link_url')

    data = {
        'event': dict(event),
        'details': dict(details) if details else {},
        'flow': [dict(r) for r in flow],
        'budget_items': [dict(b) for b in budget_items],
        'resources': [dict(r) for r in resources],
        'custom_link_name': link_name,
        'custom_link_url': link_url
    }
    
    pdf_content = generate_event_pdf(data, drive_handler)
    
    return send_file(
        io.BytesIO(pdf_content),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{event['name']}_Report.pdf"
    )

if __name__ == '__main__':
    app.run(port=5000, debug=True)

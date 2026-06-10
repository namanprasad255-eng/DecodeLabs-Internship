from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')

DATA_FILE = 'tasks.json'

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def get_next_id(tasks):
    if not tasks:
        return 1
    return max(t['id'] for t in tasks) + 1

# Serve the frontend
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# GET all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

# POST - add new task
@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    if not data or not data.get('task', '').strip():
        return jsonify({'error': 'Task cannot be empty'}), 400

    tasks = load_tasks()
    new_task = {
        'id': get_next_id(tasks),
        'task': data['task'].strip(),
        'priority': data.get('priority', 'medium'),
        'completed': False,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

# PUT - toggle complete / update
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()
    if 'completed' in data:
        task['completed'] = data['completed']
    if 'task' in data and data['task'].strip():
        task['task'] = data['task'].strip()
    if 'priority' in data:
        task['priority'] = data['priority']

    save_tasks(tasks)
    return jsonify(task)

# DELETE - remove task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    original_len = len(tasks)
    tasks = [t for t in tasks if t['id'] != task_id]
    if len(tasks) == original_len:
        return jsonify({'error': 'Task not found'}), 404
    save_tasks(tasks)
    return jsonify({'message': 'Task deleted', 'id': task_id})

# DELETE all completed
@app.route('/api/tasks/completed', methods=['DELETE'])
def clear_completed():
    tasks = load_tasks()
    tasks = [t for t in tasks if not t['completed']]
    save_tasks(tasks)
    return jsonify({'message': 'Cleared completed tasks'})

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(debug=True, port=5000)
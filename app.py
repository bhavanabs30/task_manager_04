from flask import Flask, jsonify, request, send_from_directory
from uuid import uuid4
from datetime import datetime, date
import os
import sqlite3

app = Flask(__name__, static_folder=None)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'tasks.db')


# ---------- Database ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'medium',
            due_date TEXT,
            category TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            completed_at TEXT
        )
    ''')
    conn.commit()
    conn.close()


def row_to_task(row):
    return {
        'id': row['id'],
        'title': row['title'],
        'done': bool(row['done']),
        'priority': row['priority'] or 'medium',
        'due_date': row['due_date'],
        'category': row['category'],
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
        'completed_at': row['completed_at'],
    }


# ---------- Serve Frontend ----------
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


# ---------- API Routes ----------
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db()
    rows = conn.execute('SELECT * FROM tasks ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([row_to_task(r) for r in rows])


@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    priority = (data.get('priority') or 'medium').lower()
    due_date = data.get('due_date')
    category = data.get('category')

    if not title:
        return jsonify({'error': 'Title is required'}), 400
    if len(title) > 200:
        return jsonify({'error': 'Title too long (max 200 chars)'}), 400
    if priority not in ('low', 'medium', 'high'):
        priority = 'medium'

    # Validate due_date if provided
    if due_date:
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid due date format (YYYY-MM-DD)'}), 400

    task_id = str(uuid4())
    now = datetime.utcnow().isoformat()

    conn = get_db()
    conn.execute(
        'INSERT INTO tasks (id, title, done, priority, due_date, category, created_at) '
        'VALUES (?, ?, 0, ?, ?, ?, ?)',
        (task_id, title, priority, due_date, category, now)
    )
    conn.commit()
    row = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    return jsonify(row_to_task(row)), 201


@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    conn = get_db()
    row = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    fields = []
    values = []

    if 'title' in data:
        title = (data['title'] or '').strip()
        if not title:
            conn.close()
            return jsonify({'error': 'Title cannot be empty'}), 400
        if len(title) > 200:
            conn.close()
            return jsonify({'error': 'Title too long'}), 400
        fields.append('title = ?')
        values.append(title)

    if 'priority' in data:
        p = (data['priority'] or 'medium').lower()
        if p not in ('low', 'medium', 'high'):
            p = 'medium'
        fields.append('priority = ?')
        values.append(p)

    if 'due_date' in data:
        d = data['due_date']
        if d:
            try:
                datetime.strptime(d, '%Y-%m-%d')
            except ValueError:
                conn.close()
                return jsonify({'error': 'Invalid due date'}), 400
        fields.append('due_date = ?')
        values.append(d)

    if 'category' in data:
        fields.append('category = ?')
        values.append(data['category'])

    if not fields:
        conn.close()
        return jsonify(row_to_task(row))

    fields.append('updated_at = ?')
    values.append(datetime.utcnow().isoformat())
    values.append(task_id)

    conn.execute(f'UPDATE tasks SET {", ".join(fields)} WHERE id = ?', values)
    conn.commit()
    row = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    return jsonify(row_to_task(row))


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db()
    cur = conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({'success': True})


@app.route('/api/tasks/<task_id>/toggle', methods=['PATCH'])
def toggle_task(task_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    new_done = 0 if row['done'] else 1
    now = datetime.utcnow().isoformat()
    completed_at = now if new_done else None

    conn.execute(
        'UPDATE tasks SET done = ?, completed_at = ?, updated_at = ? WHERE id = ?',
        (new_done, completed_at, now, task_id)
    )
    conn.commit()
    row = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    return jsonify(row_to_task(row))


@app.route('/api/tasks/completed', methods=['DELETE'])
def clear_completed():
    conn = get_db()
    cur = conn.execute('DELETE FROM tasks WHERE done = 1')
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'deleted': cur.rowcount})


@app.route('/api/stats', methods=['GET'])
def stats():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
    done = conn.execute('SELECT COUNT(*) FROM tasks WHERE done = 1').fetchone()[0]
    overdue = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE done = 0 AND due_date IS NOT NULL AND due_date < ?",
        (date.today().isoformat(),)
    ).fetchone()[0]
    conn.close()
    return jsonify({
        'total': total,
        'active': total - done,
        'done': done,
        'overdue': overdue
    })


# ---------- Error Handlers ----------
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
import json
from app.db import get_db


def log_event(user_id, event_type, metadata=None):
    conn = get_db()
    cursor = conn.cursor()

    metadata_json = json.dumps(metadata) if metadata else None

    cursor.execute("""
        INSERT INTO events (user_id, event_type, metadata)
        VALUES (?, ?, ?)
    """, (user_id, event_type, metadata_json))

    conn.commit()
    conn.close()


def get_daily_active_users():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(DISTINCT user_id) AS dau
        FROM events
        WHERE date(timestamp) = date('now')
    """)

    result = cursor.fetchone()
    conn.close()

    return result["dau"]


def get_tasks_created_count():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM events
        WHERE event_type = 'create_task'
    """)

    result = cursor.fetchone()
    conn.close()

    return result["total"]


def get_completion_rate():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total_tasks FROM tasks")
    total_tasks = cursor.fetchone()["total_tasks"]

    cursor.execute("""
        SELECT COUNT(*) AS completed_tasks
        FROM tasks
        WHERE status = 'completed'
    """)
    completed_tasks = cursor.fetchone()["completed_tasks"]

    conn.close()

    if total_tasks == 0:
        return 0

    return round((completed_tasks / total_tasks) * 100, 2)

def get_tasks_by_priority():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT priority, COUNT(*) AS count
        FROM tasks
        GROUP BY priority
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_tasks_by_status():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status, COUNT(*) AS count
        FROM tasks
        GROUP BY status
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
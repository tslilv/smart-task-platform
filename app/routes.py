from flask import Blueprint, request, jsonify, render_template

from app.db import get_db
from app.analytics import (
    log_event,
    get_daily_active_users,
    get_tasks_created_count,
    get_completion_rate,
    get_tasks_by_priority,
    get_tasks_by_status,
)
from app.auth import register_user, login_user
from app.experiments import assign_variant, get_experiment_results
from app.features import (
    is_feature_enabled,
    enable_feature,
    disable_feature,
)

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return jsonify({
        "message": "Welcome to Smart Task Platform!"
    })


@main.route("/dashboard")
def dashboard():
    return render_template("index.html")


@main.route("/signup", methods=["POST"])
def signup():
    data = request.json

    result = register_user(
        data["name"],
        data["email"],
        data["password"]
    )

    return jsonify(result)


@main.route("/login", methods=["POST"])
def login():
    data = request.json

    result = login_user(
        data["email"],
        data["password"]
    )

    return jsonify(result)


@main.route("/task", methods=["POST"])
def create_task():
    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (
            user_id,
            title,
            description,
            priority
        )
        VALUES (?, ?, ?, ?)
    """, (
        data["user_id"],
        data["title"],
        data.get("description"),
        data.get("priority", "medium")
    ))

    task_id = cursor.lastrowid

    conn.commit()
    conn.close()

    log_event(
        data["user_id"],
        "create_task",
        {
            "task_id": task_id,
            "priority": data.get("priority", "medium")
        }
    )

    return jsonify({
        "message": "Task created successfully",
        "task_id": task_id
    })


@main.route("/task/<int:task_id>/complete", methods=["PUT"])
def complete_task(task_id):
    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status = 'completed',
            completed_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    """, (task_id, data["user_id"]))

    conn.commit()
    conn.close()

    log_event(
        data["user_id"],
        "complete_task",
        {"task_id": task_id}
    )

    return jsonify({
        "message": "Task completed successfully"
    })

@main.route("/task/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET title = ?,
            description = ?,
            priority = ?
        WHERE id = ? AND user_id = ?
    """, (
        data["title"],
        data.get("description"),
        data.get("priority", "medium"),
        task_id,
        data["user_id"]
    ))

    conn.commit()
    conn.close()

    log_event(
        data["user_id"],
        "update_task",
        {"task_id": task_id}
    )

    return jsonify({
        "message": "Task updated successfully"
    })


@main.route("/task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE id = ? AND user_id = ?
    """, (task_id, data["user_id"]))

    conn.commit()
    conn.close()

    log_event(
        data["user_id"],
        "delete_task",
        {"task_id": task_id}
    )

    return jsonify({
        "message": "Task deleted successfully"
    })


@main.route("/tasks/<int:user_id>")
def get_user_tasks(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM tasks
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))

    tasks = cursor.fetchall()
    conn.close()

    return jsonify([
        dict(task) for task in tasks
    ])


@main.route("/analytics/dau")
def dau():
    return jsonify({
        "daily_active_users": get_daily_active_users()
    })


@main.route("/analytics/tasks-created")
def tasks_created():
    return jsonify({
        "tasks_created": get_tasks_created_count()
    })


@main.route("/analytics/completion-rate")
def completion_rate():
    return jsonify({
        "completion_rate": get_completion_rate()
    })


@main.route("/experiment/<experiment_name>/<int:user_id>")
def experiment_variant(experiment_name, user_id):
    variant = assign_variant(user_id, experiment_name)

    return jsonify({
        "experiment_name": experiment_name,
        "user_id": user_id,
        "variant": variant
    })


@main.route("/experiment/<experiment_name>/results")
def experiment_results(experiment_name):
    return jsonify({
        "experiment_name": experiment_name,
        "results": get_experiment_results(experiment_name)
    })


@main.route("/feature/<feature_name>")
def feature_status(feature_name):
    return jsonify({
        "feature_name": feature_name,
        "enabled": is_feature_enabled(feature_name)
    })


@main.route("/feature/<feature_name>/enable", methods=["POST"])
def feature_enable(feature_name):
    enable_feature(feature_name)

    return jsonify({
        "feature_name": feature_name,
        "enabled": True
    })


@main.route("/feature/<feature_name>/disable", methods=["POST"])
def feature_disable(feature_name):
    disable_feature(feature_name)

    return jsonify({
        "feature_name": feature_name,
        "enabled": False
    })

@main.route("/analytics/tasks-by-priority")
def tasks_by_priority():
    return jsonify({
        "data": get_tasks_by_priority()
    })


@main.route("/analytics/tasks-by-status")
def tasks_by_status():
    return jsonify({
        "data": get_tasks_by_status()
    })
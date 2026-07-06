from flask import Blueprint, request, jsonify, render_template, session

from app.db import get_db
from app.analytics import (
    log_event,
    get_daily_active_users,
    get_tasks_created_count,
    get_completion_rate,
    get_tasks_by_priority,
    get_tasks_by_status,
)
from app.auth import register_user, login_user, login_required
from app.experiments import assign_variant, get_experiment_results
from app.features import (
    is_feature_enabled,
    enable_feature,
    disable_feature,
)
from app.validators import require_fields

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

    error = require_fields(data, ["name", "email", "password"])
    if error:
        return error

    result = register_user(data["name"], data["email"], data["password"])

    if result["success"]:
        session["user_id"] = result["user_id"]

    return jsonify(result)


@main.route("/login", methods=["POST"])
def login():
    data = request.json

    error = require_fields(data, ["email", "password"])
    if error:
        return error

    result = login_user(data["email"], data["password"])

    if result["success"]:
        session["user_id"] = result["user_id"]

    return jsonify(result)


@main.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"})


@main.route("/task", methods=["POST"])
@login_required
def create_task():
    data = request.json

    error = require_fields(data, ["title"])
    if error:
        return error

    user_id = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (user_id, title, description, priority, due_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        data["title"],
        data.get("description"),
        data.get("priority", "medium"),
        data.get("due_date")
    ))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_event(user_id, "create_task", {"task_id": task_id, "priority": data.get("priority", "medium")})

    return jsonify({"message": "Task created successfully", "task_id": task_id})


@main.route("/task/<int:task_id>/complete", methods=["PUT"])
@login_required
def complete_task(task_id):
    user_id = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status = 'completed',
            completed_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    """, (task_id, user_id))

    updated = cursor.rowcount
    conn.commit()
    conn.close()

    if updated == 0:
        return jsonify({"message": "Task not found"}), 404

    log_event(user_id, "complete_task", {"task_id": task_id})

    return jsonify({"message": "Task completed successfully"})


@main.route("/task/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    data = request.json

    error = require_fields(data, ["title"])
    if error:
        return error

    user_id = session["user_id"]

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
        user_id
    ))

    updated = cursor.rowcount
    conn.commit()
    conn.close()

    if updated == 0:
        return jsonify({"message": "Task not found"}), 404

    log_event(user_id, "update_task", {"task_id": task_id})

    return jsonify({"message": "Task updated successfully"})


@main.route("/task/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    user_id = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE id = ? AND user_id = ?
    """, (task_id, user_id))

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        return jsonify({"message": "Task not found"}), 404

    log_event(user_id, "delete_task", {"task_id": task_id})

    return jsonify({"message": "Task deleted successfully"})


@main.route("/tasks")
@login_required
def get_user_tasks():
    user_id = session["user_id"]

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


@main.route("/task/<int:task_id>/status", methods=["PUT"])
@login_required
def update_task_status(task_id):
    data = request.json

    error = require_fields(data, ["status"])
    if error:
        return error

    if data["status"] not in ("todo", "in_progress", "completed"):
        return jsonify({"message": "Invalid status value"}), 400

    user_id = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()

    completed_at_value = "CURRENT_TIMESTAMP" if data["status"] == "completed" else "NULL"

    cursor.execute(f"""
        UPDATE tasks
        SET status = ?,
            completed_at = {completed_at_value}
        WHERE id = ? AND user_id = ?
    """, (
        data["status"],
        task_id,
        user_id
    ))

    updated = cursor.rowcount
    conn.commit()
    conn.close()

    if updated == 0:
        return jsonify({"message": "Task not found"}), 404

    log_event(user_id, "update_task_status", {"task_id": task_id, "status": data["status"]})

    return jsonify({"message": "Task status updated successfully"})
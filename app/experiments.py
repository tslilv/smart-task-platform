"""Experiment helpers for variant assignment and result reporting."""

from app.db import get_db


def assign_variant(user_id, experiment_name):
    """Return the assigned variant and persist a new assignment if none exists."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT variant
        FROM experiments
        WHERE user_id = ? AND experiment_name = ?
    """, (user_id, experiment_name))

    existing = cursor.fetchone()

    if existing:
        conn.close()
        return existing["variant"]

    variant = "A" if user_id % 2 == 0 else "B"

    cursor.execute("""
        INSERT INTO experiments (user_id, experiment_name, variant)
        VALUES (?, ?, ?)
    """, (user_id, experiment_name, variant))

    conn.commit()
    conn.close()

    return variant


def get_experiment_results(experiment_name):
    """Return the user count for each variant in an experiment."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT variant, COUNT(*) AS users_count
        FROM experiments
        WHERE experiment_name = ?
        GROUP BY variant
    """, (experiment_name,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "variant": row["variant"],
            "users_count": row["users_count"]
        }
        for row in rows
    ]
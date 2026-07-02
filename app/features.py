from app.db import get_db


def is_feature_enabled(feature_name):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT is_enabled
        FROM feature_flags
        WHERE feature_name = ?
    """, (feature_name,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False

    return bool(row["is_enabled"])


def enable_feature(feature_name):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feature_flags(feature_name, is_enabled)
        VALUES(?, 1)
        ON CONFLICT(feature_name)
        DO UPDATE SET is_enabled = 1
    """, (feature_name,))

    conn.commit()
    conn.close()


def disable_feature(feature_name):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feature_flags(feature_name, is_enabled)
        VALUES(?, 0)
        ON CONFLICT(feature_name)
        DO UPDATE SET is_enabled = 0
    """, (feature_name,))

    conn.commit()
    conn.close()
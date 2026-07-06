from flask import jsonify


def require_fields(data, required_fields):
    """
    Checks that all required_fields exist and are non-empty in data.
    Returns a (response, status_code) tuple to return immediately if something
    is missing, or None if everything is fine.
    """
    if not data:
        return jsonify({"message": "Request body is required"}), 400

    missing = [field for field in required_fields if not data.get(field)]

    if missing:
        return jsonify({
            "message": f"Missing required field(s): {', '.join(missing)}"
        }), 400

    return None

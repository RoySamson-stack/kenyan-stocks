from flask import request, jsonify
from app.models import APIKey
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if not key:
            return jsonify({"error": "Missing X-API-Key header"}), 401
        
        api_key = APIKey.query.filter_by(key=key).first()
        if not api_key:
            return jsonify({"error": "Invalid API key"}), 403
        
        if api_key.requests_used >= api_key.request_limit:
            return jsonify({"error": "Monthly quota exceeded"}), 429

        # Increment usage
        api_key.requests_used += 1
        db.session.commit()

        return f(*args, **kwargs)
    return decorated_function
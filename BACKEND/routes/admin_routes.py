from flask import Blueprint, jsonify
from models.user import User
from db import get_db

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['GET'])
def list_users():
    try:
        users_coll = get_db()['users']
        users = list(users_coll.find({}, {'password_hash': 0}))
        users_out = []
        for u in users:
            users_out.append({
                'id': str(u['_id']),
                'email': u.get('email'),
                'name': u.get('name'),
                'created_at': u.get('created_at').isoformat() if u.get('created_at') else None
            })
        return jsonify({'success': True, 'users': users_out}), 200
    except Exception as e:
        print(f"[ERROR] Listing users failed: {e}")
        return jsonify({'success': False, 'error': 'Failed to list users'}), 500


@admin_bp.route('/uploads', methods=['GET'])
def list_uploads():
    try:
        history_coll = get_db()['history']
        uploads = list(history_coll.find({}).sort('created_at', -1).limit(100))
        uploads_out = []
        for h in uploads:
            uploads_out.append({
                'id': str(h.get('_id')),
                'title': h.get('title') or h.get('filename') or 'PDF',
                'user_id': str(h.get('user_id')) if h.get('user_id') else None,
                'created_at': h.get('created_at').isoformat() if h.get('created_at') else None
            })
        return jsonify({'success': True, 'uploads': uploads_out}), 200
    except Exception as e:
        print(f"[ERROR] Listing uploads failed: {e}")
        return jsonify({'success': False, 'error': 'Failed to list uploads'}), 500

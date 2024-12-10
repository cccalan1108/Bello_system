from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager

admin_users = Blueprint("admin_users", __name__)

@admin_users.route('/admin/users', methods=['GET'])
def get_all_users():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        search = request.args.get('search', '')
        
        db = DatabaseManager()
        users, total = db.get_all_users(page, limit, search)
        
        return jsonify({
            'status': 'success',
            'users': users,
            'total': total
        })
        
    except Exception as e:
        print(f"Error getting users: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_users.route('/admin/users/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    try:
        db = DatabaseManager()
        basic_info = db.get_user_basic_info(user_id)
        profile_info = db.get_user_profile_info(user_id)
        
        if basic_info:
            return jsonify({
                'status': 'success',
                'basic_info': basic_info,
                'profile_info': profile_info
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '找不到該用戶'
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

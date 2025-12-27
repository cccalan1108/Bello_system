from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager
from jwt_utils import require_admin

admin_users = Blueprint("admin_users", __name__)

@admin_users.route('/admin/users', methods=['GET', 'OPTIONS'])
@require_admin
def get_all_users():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        search = request.args.get('search', '')
        
        db = DatabaseManager()
        # 如果 search 是空字串，轉為 None
        search_param = search if search else None
        users, total = db.get_all_users(page, limit, search_param)
        
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

@admin_users.route('/admin/users/<int:user_id>', methods=['GET', 'OPTIONS'])
@require_admin
def get_user_details(user_id):
    if request.method == 'OPTIONS':
        return '', 204
        
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

@admin_users.route('/admin/users/<int:user_id>', methods=['DELETE', 'OPTIONS'])
@require_admin
def delete_user(user_id):
    """刪除用戶（管理員功能）"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # 防止管理員刪除自己
        current_user_id = request.current_user.get('user_id')
        if current_user_id == user_id:
            return jsonify({
                'status': 'error',
                'message': '無法刪除自己的帳號'
            }), 400
        
        db = DatabaseManager()
        
        # 檢查用戶是否存在
        basic_info = db.get_user_basic_info(user_id)
        if not basic_info:
            return jsonify({
                'status': 'error',
                'message': '找不到該用戶'
            }), 404
        
        # 執行刪除
        success = db.delete_user(user_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '用戶已成功刪除'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '刪除用戶失敗'
            }), 500
            
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager

admin_remove_user = Blueprint("admin_remove_user", __name__)

@admin_remove_user.route('/admin/remove-user-from-meeting', methods=['POST', 'OPTIONS'])
def handle_remove_user():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        meeting_id = data.get('meeting_id')
        user_id = data.get('user_id')
        
        if not meeting_id or not user_id:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數'
            }), 400
            
        db = DatabaseManager()
        success = db.remove_user_from_meeting(meeting_id, user_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '成功移除用戶'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '移除用戶失敗'
            }), 400
            
    except Exception as e:
        print(f"Error in remove_user: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
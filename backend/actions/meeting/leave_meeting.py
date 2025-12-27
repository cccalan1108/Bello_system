from flask import Blueprint, request, jsonify
from DB_utils import DatabaseManager
from jwt_utils import require_auth

leave_meeting = Blueprint("leave_meeting", __name__)

@leave_meeting.route('/leave-meeting', methods=['POST', 'OPTIONS'])
@require_auth
def handle_leave_meeting():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        # 從 JWT token 獲取 user_id
        user_id = request.current_user['user_id']
        meeting_id = data.get('meeting_id')
        
        if not user_id or not meeting_id:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數'
            }), 400
            
        # 檢查是否為創辦人
        db = DatabaseManager()
        meeting = db.get_meeting(meeting_id)
        if meeting and meeting.get('holder_id') == user_id:
            return jsonify({
                'status': 'error',
                'message': '創辦人不能退出聚會,請取消聚會'
            }), 400
            
        success = db.leave_meeting(user_id, meeting_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '成功退出聚會'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '退出聚會失敗'
            }), 400
            
    except Exception as e:
        print(f"Error in leave_meeting: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
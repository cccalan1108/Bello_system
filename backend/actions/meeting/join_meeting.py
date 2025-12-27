from flask import Blueprint, request, jsonify
from DB_utils import DatabaseManager
from jwt_utils import require_auth

join_meeting = Blueprint("join_meeting", __name__)
db_manager = DatabaseManager()

@join_meeting.route('/join-meeting', methods=['POST', 'OPTIONS'])
@require_auth
def join_meeting_route():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json()
        # 從 JWT token 獲取 user_id，而不是從請求數據
        user_id = request.current_user['user_id']
        meeting_id = data.get('meeting_id')
        password = data.get('password')  # 取得使用者輸入的密碼

        if not user_id or not meeting_id:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數'
            }), 400

        # 檢查聚會是否可加入
        if not db_manager.check_meeting_availability(meeting_id):
            return jsonify({
                'status': 'error',
                'message': '該聚會已滿或已結束'
            }), 400

        # 檢查用戶是否已在聚會中
        if db_manager.is_user_in_meeting(user_id, meeting_id):
            return jsonify({
                'status': 'error',
                'message': '您已經在這個聚會中了'
            }), 400

        # 驗證聚會密碼
        if db_manager.meeting_has_password(meeting_id):
            if not db_manager.verify_meeting_password(meeting_id, password):
                return jsonify({
                    'status': 'error',
                    'message': '密碼錯誤'
                }), 401

        # 加入聚會
        if db_manager.join_meeting(user_id, meeting_id):
            return jsonify({
                'status': 'success',
                'message': '成功加入聚會'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '加入聚會失敗'
            }), 500

    except Exception as e:
        print(f"Error in join_meeting: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
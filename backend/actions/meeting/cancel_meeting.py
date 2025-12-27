from flask import Blueprint, request, jsonify
from DB_utils import DatabaseManager
from jwt_utils import require_auth

cancel_meeting = Blueprint("cancel_meeting", __name__)

@cancel_meeting.route('/cancel-meeting', methods=['POST', 'OPTIONS'])
@require_auth
def handle_cancel_meeting():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        meeting_id = data.get('meeting_id')
        
        if not meeting_id:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數'
            }), 400
            
        db = DatabaseManager()
        success = db.cancel_meeting(meeting_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '成功取消聚會'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '取消聚會失敗'
            }), 400
            
    except Exception as e:
        print(f"Error in cancel_meeting: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager
from jwt_utils import require_admin

admin_cancel_meeting = Blueprint("admin_cancel_meeting", __name__)

@admin_cancel_meeting.route('/admin/cancel-meeting', methods=['POST', 'OPTIONS'])
@require_admin
def handle_admin_cancel_meeting():
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
        success = db.admin_cancel_meeting(meeting_id)
        
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
        print(f"Error in admin_cancel_meeting: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

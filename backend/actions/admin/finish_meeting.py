from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager
from jwt_utils import require_admin

admin_finish_meeting = Blueprint("admin_finish_meeting", __name__)

@admin_finish_meeting.route('/admin/finish-meeting', methods=['POST', 'OPTIONS'])
@require_admin
def handle_admin_finish_meeting():
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
        success = db.finish_meeting(meeting_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '成功結束聚會'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '結束聚會失敗'
            }), 400
            
    except Exception as e:
        print(f"Error in finish_meeting: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
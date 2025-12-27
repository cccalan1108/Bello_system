from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager
from jwt_utils import require_admin

admin_meetings = Blueprint("admin_meetings", __name__)

@admin_meetings.route('/admin/meetings', methods=['GET', 'OPTIONS'])
@require_admin
def get_all_meetings():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        db = DatabaseManager()
        meetings = db.get_all_meetings_admin()
        
        if meetings is not None:
            return jsonify({
                'status': 'success',
                'meetings': meetings
            })
        
        return jsonify({
            'status': 'error',
            'message': '獲取聚會列表失敗'
        }), 500
        
    except Exception as e:
        print(f"Error getting all meetings: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

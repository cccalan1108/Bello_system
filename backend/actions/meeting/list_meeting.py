from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager

list_meeting = Blueprint("list_meeting", __name__)

@list_meeting.route('/list-meeting', methods=['GET'])
def handle_list_meeting():
    try:
        # 從 query string 獲取 user_id
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': '缺少用戶ID'
            }), 400
            
        db = DatabaseManager()
        meetings = db.get_available_meetings(user_id)
        
        if meetings is not None:
            return jsonify({
                'status': 'success',
                'meetings': meetings
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '獲取聚會列表失敗'
            }), 500
            
    except Exception as e:
        print(f"Error in list_meeting: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager
from jwt_utils import require_auth

my_meetings = Blueprint("my_meetings", __name__)

@my_meetings.route('/my-meetings/<int:user_id>', methods=['GET'])
@require_auth
def get_my_meetings(user_id):
    # 驗證請求的 user_id 與 token 中的 user_id 一致
    if request.current_user['user_id'] != user_id:
        return jsonify({
            'status': 'error',
            'message': '無權限訪問'
        }), 403
    try:
        db = DatabaseManager()
        meetings = db.get_user_meetings(user_id)
        
        return jsonify({
            'status': 'success',
            'meetings': meetings
        })
        
    except Exception as e:
        print(f"Error in get_my_meetings: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 
from flask import Blueprint, jsonify
from DB_utils import DatabaseManager

my_meetings = Blueprint("my_meetings", __name__)

@my_meetings.route('/my-meetings/<int:user_id>', methods=['GET'])
def get_my_meetings(user_id):
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
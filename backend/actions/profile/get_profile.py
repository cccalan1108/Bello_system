from flask import Blueprint, jsonify
from DB_utils import DatabaseManager

get_profile = Blueprint("get_profile", __name__)

@get_profile.route('/user-profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    try:
        db = DatabaseManager()
        basic_info = db.get_user_basic_info(user_id)
        profile_info = db.get_user_profile_info(user_id)
        print(profile_info)
        if basic_info:
            return jsonify({
                'status': 'success',
                'basic_info': basic_info,
                'profile_info': profile_info
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '獲取用戶資料失敗'
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

from flask import Blueprint, request, jsonify
from DB_utils import DatabaseManager

update_profile = Blueprint("update_profile", __name__)

@update_profile.route('/update-profile', methods=['POST'])
def update_user_profile():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        updates = data.get('updates', [])

        print(f"Received update request for user {user_id}: {updates}")

        if not user_id or not updates:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數'
            }), 400

        db = DatabaseManager()
        success = True
        
        for update in updates:
            field = update.get('field')
            value = update.get('value')
            print(f"Updating field {field} with value {value}")
            if not db.update_user_detail(field, value, user_id):
                print(f"Failed to update field {field}")
                success = False
                break

        if success:
            print("Update successful")
            return jsonify({
                'status': 'success',
                'message': '更新成功'
            })
        else:
            print("Update failed")
            return jsonify({
                'status': 'error',
                'message': '更新失敗'
            }), 500

    except Exception as e:
        print(f"Error during update: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

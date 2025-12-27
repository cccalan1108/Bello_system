from flask import Blueprint, request, jsonify
from DB_utils import DatabaseManager
from jwt_utils import require_auth

sns_management = Blueprint("sns_management", __name__)

@sns_management.route('/add-sns', methods=['POST', 'OPTIONS'])
@require_auth
def add_sns():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    try:
        data = request.get_json()
        # 從 JWT token 獲取 user_id
        user_id = request.current_user['user_id']
        platform = data.get('platform')
        sns_id = data.get('sns_id')

        if not all([user_id, platform, sns_id]):
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數'
            }), 400

        db = DatabaseManager()
        if db.add_sns_detail(user_id, platform, sns_id):
            return jsonify({
                'status': 'success',
                'message': '新增成功'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '新增失敗'
            }), 500

    except Exception as e:
        print(f"Error in add_sns: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '系統錯誤'
        }), 500

@sns_management.route('/sns-accounts/<int:user_id>', methods=['GET'])
@require_auth
def get_sns_accounts(user_id):
    # 驗證請求的 user_id 與 token 中的 user_id 一致
    if request.current_user['user_id'] != user_id:
        return jsonify({
            'status': 'error',
            'message': '無權限訪問'
        }), 403
    try:
        db = DatabaseManager()
        accounts = db.get_sns_details(user_id)
        return jsonify({
            'status': 'success',
            'sns_accounts': accounts
        })
    except Exception as e:
        print(f"Error in get_sns_accounts: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取社交媒體帳號失敗'
        }), 500

@sns_management.route('/remove-sns', methods=['POST', 'OPTIONS'])
@require_auth
def remove_sns():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    try:
        data = request.get_json()
        # 從 JWT token 獲取 user_id
        user_id = request.current_user['user_id']
        platform = data.get('platform')

        if not all([user_id, platform]):
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數'
            }), 400

        db = DatabaseManager()
        if db.remove_sns_detail(user_id, platform):
            return jsonify({
                'status': 'success',
                'message': '刪除成功'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '刪除失敗'
            }), 500

    except Exception as e:
        print(f"Error in remove_sns: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '系統錯誤'
        }), 500
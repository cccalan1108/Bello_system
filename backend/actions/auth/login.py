from flask import Blueprint, request, jsonify
from DB_utils import DatabaseManager
from jwt_utils import generate_token

login = Blueprint("login", __name__)

@login.route('/login', methods=['POST'])
def login_route():
    try:
        account = request.form.get('account')
        password = request.form.get('password')
        
        db = DatabaseManager()
        result = db.verify_login(account, password)
        
        if result.get('status') == 'success':
            user = result.get('user')
            
            # 生成 JWT token
            token = generate_token(
                user_id=user['user_id'],
                role=user['role'],
                user_name=user['user_name']
            )
            
            return jsonify({
                'status': 'success',
                'user': user,
                'token': token,
                'message': '登入成功'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '帳號或密碼錯誤'
            }), 401
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
        
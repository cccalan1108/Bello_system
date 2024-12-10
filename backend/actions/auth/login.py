from flask import Blueprint, request, jsonify
from DB_utils import DatabaseManager

login = Blueprint("login", __name__)

@login.route('/login', methods=['POST'])
def login_route():
    try:
        account = request.form.get('account')
        password = request.form.get('password')
        
        db = DatabaseManager()
        result = db.verify_login(account, password)
        
        if result.get('status') == 'success':
            return jsonify({
                'status': 'success',
                'user': result.get('user'),
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
        
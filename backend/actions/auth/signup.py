from flask import Blueprint, request, jsonify
from datetime import datetime
from DB_utils import DatabaseManager

ADMIN_AUTH_CODE = "belloadmin"

signUp = Blueprint("signup", __name__)

@signUp.route('/signup', methods=['POST'])
def signup_route():
    try:
        data = request.get_json()
        print(data)
        account = data.get('account')
        password = data.get('password')
        user_name = data.get('user_name')
        user_nickname = data.get('user_nickname')
        nationality = data.get('nationality')
        city = data.get('city')
        phone = data.get('phone')
        email = data.get('email')
        sex = data.get('sex')
        birthday = data.get('birthday')
        admin_auth_code = data.get('admin_auth_code')
        
        # 基本驗證
        if not all([account, password, user_name, user_nickname, nationality,
                   city, phone, email, sex, birthday]):
            print("缺少必要欄位:", {
                'account': account,
                'password': password,
                'user_name': user_name,
                'user_nickname': user_nickname,
                'nationality': nationality,
                'city': city,
                'phone': phone,
                'email': email,
                'sex': sex,
                'birthday': birthday
            })
            return jsonify({
                'status': 'error',
                'message': '請填寫所有必要欄位'
            }), 400
            
        db = DatabaseManager()
        
        # 檢查帳號是否已存在
        if db.check_account_exists(account):
            return jsonify({
                'status': 'error',
                'message': '此帳號已被註冊'
            }), 400
            
        # 創建用戶並設置角色
        user_id = db.create_user(
            account=account,
            password=password,
            user_name=user_name,
            user_nickname=user_nickname,
            nationality=nationality,
            city=city,
            phone=phone,
            email=email,
            sex=sex,
            birthday=birthday,
            register_time=datetime.now()
        )
        print(user_id)
        if user_id:
            # 根據驗證碼設置角色
            role = 'Admin' if admin_auth_code == ADMIN_AUTH_CODE else 'User'
            if db.set_user_role(user_id, role):
                return jsonify({
                    'status': 'success',
                    'message': '註冊成功！'
                })
        
        return jsonify({
            'status': 'error',
            'message': '註冊失敗'
        }), 500
            
    except Exception as e:
        print(f"註冊錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

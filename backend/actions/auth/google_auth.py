from flask import Blueprint, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from DB_utils import DatabaseManager
from jwt_utils import generate_token
from config import Config
from datetime import datetime

google_auth = Blueprint("google_auth", __name__)

@google_auth.route('/auth/google', methods=['POST'])
def google_login():
    """
    處理 Google OAuth 登入
    前端傳送 Google credential (ID token)，後端驗證並創建/登入用戶
    """
    try:
        data = request.get_json()
        credential = data.get('credential')
        
        if not credential:
            return jsonify({
                'status': 'error',
                'message': '缺少 Google credential'
            }), 400
        
        # 驗證 Google ID token
        try:
            idinfo = id_token.verify_oauth2_token(
                credential, 
                google_requests.Request(), 
                Config.GOOGLE_CLIENT_ID
            )
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': f'Google token 驗證失敗: {str(e)}'
            }), 401
        
        # 從 Google 獲取用戶資訊
        google_id = idinfo['sub']
        email = idinfo.get('email', '')
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')
        given_name = idinfo.get('given_name', '')  # 名字
        family_name = idinfo.get('family_name', '')  # 姓氏
        locale = idinfo.get('locale', '')  # 地區設定
        
        db = DatabaseManager()
        
        # 檢查用戶是否已存在（透過 Google ID 或 Email）
        user = db.get_user_by_google_id(google_id)
        
        if not user:
            # 檢查是否有相同 email 的用戶（可能是用一般方式註冊的）
            user = db.get_user_by_email(email)
            
            if user:
                # 更新現有用戶的 Google ID 和頭像
                db.link_google_account(user['user_id'], google_id, picture)
            else:
                # 創建新的 Google 用戶，傳入更多資訊
                user_id = db.create_google_user(
                    google_id=google_id,
                    email=email,
                    user_name=name,
                    avatar_url=picture,
                    given_name=given_name,
                    family_name=family_name,
                    locale=locale
                )
                
                if not user_id:
                    return jsonify({
                        'status': 'error',
                        'message': '創建用戶失敗'
                    }), 500
                
                # 設置用戶角色
                db.set_user_role(user_id, 'User')
                
                # 獲取新創建的用戶資訊
                user = db.get_user_by_google_id(google_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': '無法獲取用戶資訊'
            }), 500
        
        # 生成 JWT token
        token = generate_token(
            user_id=user['user_id'],
            role=user['role'],
            user_name=user['user_name']
        )
        
        return jsonify({
            'status': 'success',
            'user': {
                'user_id': user['user_id'],
                'user_name': user['user_name'],
                'nickname': user['user_nickname'],
                'email': user['email'],
                'role': user['role'],
                'avatar_url': user.get('avatar_url', '')
            },
            'token': token,
            'message': '登入成功'
        })
        
    except Exception as e:
        print(f"Google 登入錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@google_auth.route('/auth/google/client-id', methods=['GET'])
def get_google_client_id():
    """
    獲取 Google Client ID（供前端使用）
    """
    client_id = Config.GOOGLE_CLIENT_ID
    if not client_id:
        return jsonify({
            'status': 'error',
            'message': 'Google OAuth 未配置'
        }), 500
    
    return jsonify({
        'status': 'success',
        'client_id': client_id
    })


import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# JWT 密鑰（從環境變數讀取）
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'bello-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))  # Token 24 小時後過期


def generate_token(user_id, role, user_name):
    """
    生成 JWT token
    
    Args:
        user_id: 用戶 ID
        role: 用戶角色 (User/Admin)
        user_name: 用戶名稱
    
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'user_name': user_name,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token):
    """
    驗證 JWT token
    
    Args:
        token: JWT token 字符串
    
    Returns:
        dict: 如果驗證成功，返回 payload；如果失敗，返回 None
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token 已過期
    except jwt.InvalidTokenError:
        return None  # Token 無效


def get_token_from_request():
    """
    從請求頭中獲取 token
    
    Returns:
        str: token 字符串，如果不存在則返回 None
    """
    # 從 Authorization header 獲取
    auth_header = request.headers.get('Authorization')
    if auth_header:
        # 格式: "Bearer <token>"
        parts = auth_header.split(' ')
        if len(parts) == 2 and parts[0] == 'Bearer':
            return parts[1]
    
    # 也可以從 query parameter 獲取（備用方案）
    token = request.args.get('token')
    if token:
        return token
    
    return None


def require_auth(f):
    """
    裝飾器：要求用戶已登入
    
    使用方式:
        @require_auth
        def my_route():
            # user_id 和 role 可以從 g.current_user 獲取
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 跳過 OPTIONS 請求（CORS preflight）
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
            
        token = get_token_from_request()
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': '缺少認證 token，請先登入'
            }), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({
                'status': 'error',
                'message': 'Token 無效或已過期，請重新登入'
            }), 401
        
        # 將用戶信息存儲到 request 對象中，方便後續使用
        request.current_user = {
            'user_id': payload['user_id'],
            'role': payload['role'],
            'user_name': payload['user_name']
        }
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """
    裝飾器：要求用戶是管理員
    
    使用方式:
        @require_admin
        def admin_route():
            pass
    """
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        # 跳過 OPTIONS 請求（CORS preflight）
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
            
        if request.current_user['role'] != 'Admin':
            return jsonify({
                'status': 'error',
                'message': '需要管理員權限'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


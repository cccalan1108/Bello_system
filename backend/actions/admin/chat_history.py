from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager

admin_chat_history = Blueprint("admin_chat_history", __name__)

@admin_chat_history.route('/admin/chat-history', methods=['POST', 'OPTIONS'])
def get_chat_history():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        user1_id = data.get('user1_id')
        user2_id = data.get('user2_id')
        limit = data.get('limit', 20)
        
        if not user1_id or not user2_id:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數'
            }), 400
            
        db = DatabaseManager()
        messages = db.get_user_chat_history(user1_id, user2_id, limit)
        
        if messages is not None:
            return jsonify({
                'status': 'success',
                'messages': messages
            })
        
        return jsonify({
            'status': 'error',
            'message': '獲取聊天記錄失敗'
        }), 500
        
    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

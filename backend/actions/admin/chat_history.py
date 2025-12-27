from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager
from jwt_utils import require_admin

admin_chat_history = Blueprint("admin_chat_history", __name__)

@admin_chat_history.route('/admin/all-private-chats', methods=['GET', 'OPTIONS'])
@require_admin
def get_all_private_chats():
    """獲取所有私人聊天對話列表"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        db = DatabaseManager()
        chats, total = db.get_all_private_chat_conversations(page, limit)
        
        return jsonify({
            'status': 'success',
            'conversations': chats,
            'total': total
        })
        
    except Exception as e:
        print(f"Error getting all private chats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@admin_chat_history.route('/admin/chat-history', methods=['POST', 'OPTIONS'])
@require_admin
def get_chat_history():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        user1_id = data.get('user1_id')
        user2_id = data.get('user2_id')
        limit = data.get('limit', 50)
        
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

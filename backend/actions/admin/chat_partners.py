from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager
from jwt_utils import require_admin

admin_chat_partners = Blueprint("admin_chat_partners", __name__)

@admin_chat_partners.route('/admin/chat-partners/<user_id>', methods=['GET', 'OPTIONS'])
@require_admin
def get_chat_partners(user_id):
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        db = DatabaseManager()
        partners = db.get_user_chat_partners(user_id)
        
        if partners is not None:
            return jsonify({
                'status': 'success',
                'partners': partners
            })
        
        return jsonify({
            'status': 'error',
            'message': '獲取聊天對象列表失敗'
        }), 500
        
    except Exception as e:
        print(f"Error getting chat partners: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

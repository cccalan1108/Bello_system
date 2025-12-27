from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager
from jwt_utils import require_admin

admin_meeting_chat = Blueprint("admin_meeting_chat", __name__)

@admin_meeting_chat.route('/admin/all-meeting-chats', methods=['GET', 'OPTIONS'])
@require_admin
def get_all_meeting_chats():
    """獲取所有有聊天記錄的聚會列表"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        db = DatabaseManager()
        meetings, total = db.get_all_meeting_chat_list(page, limit)
        
        return jsonify({
            'status': 'success',
            'meetings': meetings,
            'total': total
        })
        
    except Exception as e:
        print(f"Error getting all meeting chats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@admin_meeting_chat.route('/admin/meeting-chat/<meeting_id>', methods=['GET', 'OPTIONS'])
@require_admin
def get_meeting_chat(meeting_id):
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        db = DatabaseManager()
        
        # 獲取聚會資訊
        meeting_info = db.get_meeting_info(meeting_id)
        if not meeting_info:
            return jsonify({
                'status': 'error',
                'message': '找不到該聚會'
            }), 404
            
        # 獲取聚會聊天記錄
        messages = db.get_meeting_chat_history(meeting_id)
        
        return jsonify({
            'status': 'success',
            'meeting_info': meeting_info,
            'messages': messages or []
        })
        
    except Exception as e:
        print(f"Error getting meeting chat: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

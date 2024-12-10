from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager

meeting_chat = Blueprint("meeting_chat", __name__)

@meeting_chat.route('/meeting-chat/<meeting_id>', methods=['GET', 'OPTIONS'])
def get_meeting_chat(meeting_id):
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        db = DatabaseManager()
        messages = db.get_meeting_chat_history(meeting_id)
        
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
        print(f"Error getting meeting chat: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@meeting_chat.route('/meeting-chat/send', methods=['POST', 'OPTIONS'])
def send_meeting_message():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        meeting_id = data.get('meeting_id')
        sender_id = data.get('sender_id')
        content = data.get('content')
        
        if not all([meeting_id, sender_id, content]):
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數'
            }), 400
            
        db = DatabaseManager()
        message_id = db.save_meeting_message(meeting_id, sender_id, content)
        
        if message_id:
            return jsonify({
                'status': 'success',
                'message_id': message_id
            })
            
        return jsonify({
            'status': 'error',
            'message': '發送訊息失敗'
        }), 500
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
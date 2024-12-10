from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager

chat_search = Blueprint("chat_search", __name__)

@chat_search.route('/search-users', methods=['GET'])
def search_users():
    try:
        query = request.args.get('query', '')
        current_user = request.args.get('current_user')
        
        if not query or not current_user:
            return jsonify({
                'status': 'success',
                'users': []
            })
            
        db = DatabaseManager()
        users = db.search_chat_users(query, current_user)
        
        return jsonify({
            'status': 'success',
            'users': users
        })
        
    except Exception as e:
        print(f"Error searching users: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

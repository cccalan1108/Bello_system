from flask import Blueprint, jsonify, request
from DB_utils import DatabaseManager
from jwt_utils import require_auth

friendship = Blueprint("friendship", __name__)

@friendship.route('/friends', methods=['GET'])
@require_auth
def get_friends():
    """獲取好友列表"""
    try:
        user_id = request.current_user['user_id']
        db = DatabaseManager()
        friends = db.get_friends_list(user_id)
        
        return jsonify({
            'status': 'success',
            'friends': friends
        })
        
    except Exception as e:
        print(f"Error getting friends: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@friendship.route('/friends/requests', methods=['GET'])
@require_auth
def get_friend_requests():
    """獲取待處理的好友請求"""
    try:
        user_id = request.current_user['user_id']
        db = DatabaseManager()
        
        pending_requests = db.get_pending_friend_requests(user_id)
        sent_requests = db.get_sent_friend_requests(user_id)
        
        return jsonify({
            'status': 'success',
            'pending_requests': pending_requests,
            'sent_requests': sent_requests
        })
        
    except Exception as e:
        print(f"Error getting friend requests: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@friendship.route('/friends/add', methods=['POST'])
@require_auth
def send_friend_request():
    """發送好友請求"""
    try:
        user_id = int(request.current_user['user_id'])
        data = request.get_json()
        friend_id = data.get('friend_id')
        
        if not friend_id:
            return jsonify({
                'status': 'error',
                'message': '缺少好友ID'
            }), 400
        
        # 確保 friend_id 是整數
        try:
            friend_id = int(friend_id)
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'message': '無效的好友ID'
            }), 400
        
        if user_id == friend_id:
            return jsonify({
                'status': 'error',
                'message': '不能加自己為好友'
            }), 400
        
        db = DatabaseManager()
        result = db.send_friend_request(user_id, friend_id)
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': result['message']
            })
        else:
            print(f"Failed to send friend request: {result.get('message', 'Unknown error')}")
            return jsonify({
                'status': 'error',
                'message': result.get('message', '發送好友請求失敗')
            }), 400
        
    except Exception as e:
        import traceback
        print(f"Error sending friend request: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'發送好友請求時發生錯誤: {str(e)}'
        }), 500

@friendship.route('/friends/accept', methods=['POST'])
@require_auth
def accept_friend_request():
    """接受好友請求"""
    try:
        user_id = int(request.current_user['user_id'])
        data = request.get_json()
        friend_id = data.get('friend_id')
        
        if not friend_id:
            return jsonify({
                'status': 'error',
                'message': '缺少好友ID'
            }), 400
        
        friend_id = int(friend_id)
        
        db = DatabaseManager()
        success = db.accept_friend_request(user_id, friend_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '已接受好友請求'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '接受好友請求失敗'
            }), 400
        
    except Exception as e:
        print(f"Error accepting friend request: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@friendship.route('/friends/reject', methods=['POST'])
@require_auth
def reject_friend_request():
    """拒絕好友請求"""
    try:
        user_id = int(request.current_user['user_id'])
        data = request.get_json()
        friend_id = data.get('friend_id')
        
        if not friend_id:
            return jsonify({
                'status': 'error',
                'message': '缺少好友ID'
            }), 400
        
        friend_id = int(friend_id)
        
        db = DatabaseManager()
        success = db.reject_friend_request(user_id, friend_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '已拒絕好友請求'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '拒絕好友請求失敗'
            }), 400
        
    except Exception as e:
        print(f"Error rejecting friend request: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@friendship.route('/friends/remove', methods=['POST'])
@require_auth
def remove_friend():
    """刪除好友"""
    try:
        user_id = int(request.current_user['user_id'])
        data = request.get_json()
        friend_id = data.get('friend_id')
        
        if not friend_id:
            return jsonify({
                'status': 'error',
                'message': '缺少好友ID'
            }), 400
        
        friend_id = int(friend_id)
        
        db = DatabaseManager()
        success = db.remove_friend(user_id, friend_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '已刪除好友'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '刪除好友失敗'
            }), 400
        
    except Exception as e:
        print(f"Error removing friend: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@friendship.route('/friends/status/<int:other_user_id>', methods=['GET'])
@require_auth
def check_friendship_status(other_user_id):
    """檢查與指定用戶的好友狀態"""
    try:
        user_id = int(request.current_user['user_id'])
        other_user_id = int(other_user_id)
        db = DatabaseManager()
        friendship_data = db.check_friendship_status(user_id, other_user_id)
        
        return jsonify({
            'status': 'success',
            'friendship_status': friendship_data.get('status', 'none'),
            'is_friend': friendship_data.get('is_friend', False)
        })
        
    except Exception as e:
        print(f"Error checking friendship status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@friendship.route('/friends/search', methods=['GET'])
@require_auth
def search_users_for_friend():
    """搜尋用戶以添加好友"""
    try:
        user_id = request.current_user['user_id']
        query = request.args.get('query', '')
        
        if not query:
            return jsonify({
                'status': 'success',
                'users': []
            })
        
        db = DatabaseManager()
        users = db.search_users_for_friend(query, user_id)
        
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

@friendship.route('/online-status', methods=['POST'])
@require_auth
def update_online_status():
    """更新在線狀態"""
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        is_online = data.get('is_online', True)
        
        db = DatabaseManager()
        success = db.update_online_status(user_id, is_online)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '在線狀態已更新'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '更新在線狀態失敗'
            }), 400
        
    except Exception as e:
        print(f"Error updating online status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@friendship.route('/user-status/<int:target_user_id>', methods=['GET'])
@require_auth
def get_user_status(target_user_id):
    """獲取指定用戶的在線狀態"""
    try:
        db = DatabaseManager()
        status = db.get_user_online_status(target_user_id)
        
        return jsonify({
            'status': 'success',
            **status
        })
        
    except Exception as e:
        print(f"Error getting user status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@friendship.route('/friends/user-profile/<int:target_user_id>', methods=['GET'])
@require_auth
def get_user_public_profile(target_user_id):
    """獲取指定用戶的公開個人資料"""
    try:
        db = DatabaseManager()
        profile = db.get_user_public_profile(target_user_id)
        
        if profile:
            return jsonify({
                'status': 'success',
                'profile': profile
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '找不到該用戶'
            }), 404
        
    except Exception as e:
        print(f"Error getting user profile: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


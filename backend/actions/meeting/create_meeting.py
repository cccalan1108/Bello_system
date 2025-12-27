import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from flask import Blueprint, request, jsonify
from DB_utils import DatabaseManager
from jwt_utils import require_auth

create_meeting = Blueprint('create_meeting', __name__)

class CreateMeetingAction:
    MEETING_TYPES = ['午餐', '咖啡/下午茶', '晚餐', '喝酒', '語言交換']
    LANGUAGES = ['中文', '台語', '客語', '原住民語', '英文', '日文', '韓文', 
                 '法文', '德文', '西班牙文', '俄文', '阿拉伯文', '泰文', '越南文', '印尼文']

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def exec(self, holder_id=None):
        try:
            data = request.get_json()
            print("Received data:", data)
            
            # 如果提供了 holder_id（從 JWT token），使用它
            if holder_id:
                data['holder_id'] = holder_id
            
            # 直接傳遞整個 data 字典
            success = self.db_manager.create_meeting(data)
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': '聚會建立成功'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': '建立聚會失敗'
                }), 400
                
        except Exception as e:
            print(f"TypeError in create_meeting: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

# 初始化數據庫管理器
db_manager = DatabaseManager()

# 建立 CreateMeetingAction 實例
create_meeting_action = CreateMeetingAction(db_manager)

# 註冊路由
@create_meeting.route('/create-meeting', methods=['POST'])
@require_auth
def create_meeting_route():
    # 從 JWT token 中獲取 user_id
    holder_id = request.current_user['user_id']
    return create_meeting_action.exec(holder_id=holder_id)

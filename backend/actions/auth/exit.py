from flask import Blueprint, jsonify

exit = Blueprint("exit", __name__)

@exit.route('/exit', methods=['POST'])
def exit_route():
    try:
        return jsonify({
            'status': 'success',
            'message': '登出成功'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 

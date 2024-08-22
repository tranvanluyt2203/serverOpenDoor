from flask import jsonify

def error_response(message, status_code):
    return jsonify({
        'success': False,
        'error': {
            'code': status_code,
            'message': message
        }
    }), status_code

def success_response(data=None, message="Operation successful", status_code=200):
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def list_response(items, total_count=None, page=None, per_page=None):
    response = {
        'success': True,
        'data': items
    }
    if total_count is not None:
        response['total_count'] = total_count
    if page is not None:
        response['page'] = page
    if per_page is not None:
        response['per_page'] = per_page
    return jsonify(response), 200
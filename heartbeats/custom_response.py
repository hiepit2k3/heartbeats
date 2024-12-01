from rest_framework.response import Response

class CustomResponse(Response):
    def __init__(self, data=None, status=None, message=None, success=True, **kwargs):
        response_data = {
            'success': success,
            'message': message or 'Operation completed',
            'data': data,
        }
        super().__init__(response_data, status=status, **kwargs)

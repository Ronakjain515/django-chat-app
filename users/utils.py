from utility import messages
from rest_framework import status
from .models import BlackListedToken
from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import RefreshToken


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Update the structure of the response data.
    if response is not None:
        customized_response = dict()
        customized_response['error'] = []

        for key, value in response.data.items():
            error = key
            customized_response['status_code'] = response.status_code
            customized_response['error'] = error
            customized_response['data'] = None
            customized_response['message'] = value

        response.data = customized_response

    return response


class ResponseInfo(object):
    """
    Class for setting how API should send response.
    """

    def __init__(self, user=None, **args):
        self.response = {
            "status_code": args.get('status', 200),
            "error": args.get('error', None),
            "data": args.get('data', []),
            "message": [args.get('message', 'Success')]
        }


def get_tokens_for_user(user_name):
    """
    function to creates and returns JWT token in response
    """
    refresh = RefreshToken.for_user(user_name)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class IsTokenValid(BasePermission):
    """
    Class for validating if the token is present in the blacklisted token list.
    """

    def has_permission(self, request, view):
        """
        Function for checking if the caller of this function has
         permission to access particular API.
        """
        is_allowed_user = True
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            key, token = auth_header.split(' ')
            if key == 'Bearer':
                try:
                    is_blacklisted = BlackListedToken.objects.get(token=token)
                    if is_blacklisted:
                        is_allowed_user = False
                except BlackListedToken.DoesNotExist:
                    is_allowed_user = True
                    if not request.user.status == "ACTIVE":
                        self.message = "Your account has been deleted. Please contact your admin"
                        is_allowed_user = False
        else:
            is_allowed_user = False
        return is_allowed_user


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            "status_code": status.HTTP_200_OK,
            "error": None,
            "data": [{
                'links': {
                    'total_pages': self.page.paginator.num_pages,
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.page.paginator.count,
                'results': data
            }],
            "message": [messages.SUCCESS]
        })

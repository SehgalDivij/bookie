from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(http_method_names=['GET'])
def base_url(request):
    """
    Base url to replace index call.
    :param request:
    :return:
    """
    return Response(
        data={
            "message": "Welcome"
        },
        status=status.HTTP_200_OK
    )

# __author__='gzh'

import json

from rest_framework import status
from rest_framework.response import Response

from common.custom_exception import PushError
from libs.push_service.site_push import infopush


def station_msg_push(station_id):
    try:
        resp = infopush(station_id)
    except Exception as e:
        raise PushError("11"+str(e))

    else:
        resp = json.loads(resp.content.decode('utf-8'))
        if not resp['status']:
            raise PushError('msg push fail')
        else:
            return Response({}, status=status.HTTP_200_OK)

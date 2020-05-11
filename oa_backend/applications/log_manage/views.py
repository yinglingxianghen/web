from rest_framework import viewsets

from libs.datetimes import str_to_date, datetime_delta
from .models import OperateLog
from .serializers import OperateLogSerializer, PersonalLogSerializer


# Create your views here.
class SystemLogViewSet(viewsets.ModelViewSet):
    queryset = OperateLog.objects.all()
    serializer_class = OperateLogSerializer

    def get_queryset(self):
        kwargs = self.request.GET
        query_params = {}
        from_date = kwargs.get("from_date", None)
        to_date = kwargs.get("to_date", None)
        username = kwargs.get("username", None)
        action = kwargs.get("action", None)
        if from_date:
            query_params.update({"operationtime__gte": str_to_date(from_date)})
        if to_date:
            to_date = datetime_delta(str_to_date(to_date), days=1)
            query_params.update({"operationtime__lte": to_date})
        if username:
            query_params.update({"user__last_name": username})
        if action:
            query_params.update({"action": action})
        return OperateLog.objects.all().filter(**query_params).order_by("-operationtime")

    def check_permissions(self, request):
        super(SystemLogViewSet, self).check_permissions(request)
        if not request.user.has_perm("log_manage.view_system-log"):
            self.permission_denied(request)


class PersonalLogViewSet(viewsets.ModelViewSet):
    queryset = OperateLog.objects.all()
    serializer_class = PersonalLogSerializer

    def get_queryset(self):
        kwargs = self.request.GET
        query_params = {"user_id": self.request.user.id}
        from_date = kwargs.get("from_date", None)
        to_date = kwargs.get("to_date", None)
        action = kwargs.get("action", None)
        if from_date:
            query_params.update({"operationtime__gte": str_to_date(from_date)})
        if to_date:
            to_date = datetime_delta(str_to_date(to_date), days=1)
            query_params.update({"operationtime__lte": to_date})
        if action:
            query_params.update({"action": action})
        return OperateLog.objects.all().filter(**query_params).order_by("-operationtime")

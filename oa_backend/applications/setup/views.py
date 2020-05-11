# Create your views here.
import boto3
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from applications.log_manage.models import OperateLog
from applications.production_manage.models import DataBaseInfo
from applications.setup.models import SiteReceptionGroup
from applications.setup.permissions import SiteReceptionGroupPermission
from applications.setup.serializers import CliIndustrySerializer
from applications.setup.serializers import SiteReceptionGroupSerializer
from applications.workorder_manage.models import Industry
from libs.hash import decrypt, get_md5
from libs.image import image_resize
from libs.mysql_helper import Connection


class CliIndustrySet(viewsets.ModelViewSet):
    queryset = Industry.objects.all().order_by('-id').prefetch_related('company_info')
    serializer_class = CliIndustrySerializer

    def is_unique(self, industry):
        industry_list = Industry.objects.all().values_list('industry', flat=True)
        if industry in industry_list:
            return 0
        else:
            return 1

    def create(self, request, *args, **kwargs):
        industry = request.data.get('industry', '').strip()
        if industry:
            if self.is_unique(industry):
                Industry.objects.create(industry=industry)
                OperateLog.create_log(request)
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response({'error': '该行业已存在'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '参数错误，无行业名'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        industry = request.data.get('industry', '').strip()
        instance = self.get_object()

        if industry:
            if industry == instance.industry:
                return Response(status=status.HTTP_200_OK)
            elif self.is_unique(industry):
                instance.industry = industry
                instance.save()
                OperateLog.create_log(request)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'error': '该行业已存在'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '参数错误，无行业名'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        site_num = instance.company_info.count()
        if not site_num:
            instance.delete()
            OperateLog.create_log(request)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "有站点在该行业，不可删除"}, status=status.HTTP_400_BAD_REQUEST)


class SiteReceptionGroupView(ModelViewSet):
    """站点接待组接口的统一入口"""
    queryset = SiteReceptionGroup.objects.all()
    serializer_class = SiteReceptionGroupSerializer
    permission_classes = [SiteReceptionGroupPermission]

    def get_queryset(self):
        title = self.request.GET.get("title", None)
        manager = self.request.GET.get("manager", None)
        company_id = self.request.GET.get("company_id", None)
        params = dict()
        if title:
            params["title"] = title
        if manager:
            params["manager"] = manager
        if company_id:
            params["site__company_id"] = company_id
        return SiteReceptionGroup.objects.all().filter(**params)

def reception_groups(request):
    """小能的客服组保存在bj-v4的t2d_syssetting表中，对应site_id为kf_8008
    从中获取到接待组的id和名称，返回给前端
    """
    db_info = DataBaseInfo.objects.get(grid__grid_name="bj-v4", db_name="kf")
    conn = Connection(database="kf", host=db_info.db_address, user=db_info.db_username,
                      password=decrypt(db_info.db_pwd), port=int(db_info.db_port))
    sql = "SELECT name, id FROM t2d_syssetting WHERE siteid='kf_8008'"
    reception_groups = conn.query(sql)
    conn.close()
    return JsonResponse(reception_groups, safe=False)


@csrf_exempt
def avatar_upload(request):
    """头像上传接口，上传jpeg图片，返回该图片的url"""
    if not request.method == "POST":
        return JsonResponse({"error": "request method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    cli = boto3.client(**settings.BAISHANYUN_CONFIGS)  # 获得客户端会话对象

    file = request.FILES['file']
    assert isinstance(file, UploadedFile)  # 获取到的文件信息应为一个UploadedFile对象

    file_type = file.name.split(".")[-1]
    if file_type not in ("jpg", "jpeg", "png"):
        return JsonResponse({"error": "文件格式不合法，目前只支持jpeg, jpg, png"}, status=status.HTTP_400_BAD_REQUEST)
    # 图片压缩，统一为280 * 280, jpeg格式
    data = image_resize(
        data=file.read(),
        size=settings.AVATAR_SIZE,
    )
    key = get_md5(data)
    cli.put_object(
        ACL='public-read',  # 公共可读
        Bucket='minioss',  # 固定
        Key=f"oa/{key}.jpeg",  # 文件保存在oa目录下
        ContentType=f'image/jpeg',
        Body=data
    )
    url = f'http://s2.i.qingcdn.com/minioss/oa/{key}.jpeg'
    return HttpResponse(url)


def help_center(request):
    if not request.method == "GET":
        return JsonResponse({"error": "request method not allowed"})
    site_id = request.GET.get("siteid", "")
    user_id = request.GET.get("userid", "")
    user_id = "_".join(user_id.split("_ISME9754_T2D_"))
    site_reception_obj = SiteReceptionGroup.objects.filter(site__company_id=site_id).first()
    if not site_reception_obj:
        return JsonResponse({"error": "Invalid site_id"}, status=status.HTTP_400_BAD_REQUEST)
    data = {
        "company_name": site_reception_obj.site.open_station.company_info.company_name,
        "site_id": site_id,
        "reception_group_id": site_reception_obj.group_id,
        "user_id": user_id,
        "avatar": site_reception_obj.avatar,
        "manager": site_reception_obj.manager,
        "phone_number": site_reception_obj.phone_number,
        "email": site_reception_obj.email,
        "url": site_reception_obj.url,
        "desc": site_reception_obj.desc,
    }
    return render(request, "help_center.html", data)

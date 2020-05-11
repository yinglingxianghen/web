# -*- coding:utf-8 -*-
import json
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q


from .models import CourseOrg, CityDict, Teacher
from .forms import UserAskForm
from courses.models import Course
from operation.models import UserFavorite


class OrgView(View):
    """
    课程机构列表功能
    """
    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()

        # 提取热门机构
        hot_orgs = all_orgs.order_by("-click_nums")[:3]

        # 城市
        all_citys = CityDict.objects.all()

        # 机构搜索
        serach_keywords = request.GET.get('keywords', "")
        if serach_keywords:
            all_orgs = all_orgs.filter(
                Q(name__icontains=serach_keywords) | Q(desc__icontains=serach_keywords))

        # 取出筛选城市
        city_id = request.GET.get('city', "")
        if city_id:
            # 筛选出当前城市的结果集
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 类别筛选
        category = request.GET.get('ct', "")
        if category:
            # 筛选出当前城市的结果集
            all_orgs = all_orgs.filter(category=category)

        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-courses_nums")

        org_nums = all_orgs.count()

        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_orgs, 5, request=request)

        orgs = p.page(page)

        current_nav = 'org'
        return render(request, 'org-list.html', {
            "all_orgs": orgs,
            "all_citys": all_citys,
            "org_nums": org_nums,
            "city_id": city_id,
            "category": category,
            "hot_orgs": hot_orgs,
            "sort": sort,
            'current_nav': current_nav,
        })


# 用户添加咨询课程表单提交
class AddUserAskView(View):
    def post(self, request):
        user_ask_form = UserAskForm(request.POST)
        res = dict()
        if user_ask_form.is_valid():
            user_ask_form.save(commit=True)
            res['status'] = 'success'
        else:
            res['status'] = 'fail'
            res['msg'] = '添加出错'
        return HttpResponse(json.dumps(res), content_type='application/json')


# 机构首页
class OrgHomeView(View):
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        current_page = "home"
        course_org.click_nums += 1
        course_org.save()
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        # 有外键的地方都可以这样用，通过外键取出数据
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


# 机构介绍页
class OrgDescView(View):
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        current_page = "desc"
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        # 有外键的地方都可以这样用，通过外键取出数据
        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,

        })


# 机构课程页
class OrgCourseView(View):
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        current_page = "course"
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        # 有外键的地方都可以这样用，通过外键取出数据
        all_courses = course_org.course_set.all()
        return render(request, 'org-detail-course.html', {
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


# 机构教师页
class OrgTeacherView(View):
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        current_page = "teacher"
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        # 有外键的地方都可以这样用，通过外键取出数据
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', {
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,

        })


# 用户收藏，用户取消收藏
class AddFavView(View):
    # 用户收藏、取消收藏 课程机构
    # def set_fav_nums(self, fav_type, fav_id, num=1):
    #     if fav_type == 1:
    #         course = Course.objects.get(id=fav_id)
    #         course.fav_nums += num
    #         course.save()
    #     elif fav_type == 2:
    #         course_org = CourseOrg.objects.get(id=fav_id)
    #         course_org.fav_nums += num
    #         course_org.save()
    #     elif fav_type == 3:
    #         teacher = Teacher.objects.get(id=fav_id)
    #         teacher.fav_nums += num
    #         teacher.save()
    def post(self, request):
        fav_id = int(request.POST.get('fav_id', 0))
        fav_type = int(request.POST.get('fav_type', 0))
        res = dict()
        if not request.user.is_authenticated():
            res['status'] = 'fail'
            res['msg'] = '用户未登录'
            return HttpResponse(json.dumps(res), content_type='application/json')
        # 查询收藏记录
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=fav_id, fav_type=fav_type)
        if exist_records:
            exist_records.delete()
            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()

            elif int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()

            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()

            # self.set_fav_nums(fav_type, fav_id, -1)
            res['status'] = 'success'
            res['msg'] = '收藏'
        else:
            user_fav = UserFavorite()
            if fav_id and fav_type:
                user_fav.user = request.user
                user_fav.fav_id = fav_id
                user_fav.fav_type = fav_type
                user_fav.save()

                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()

                # self.set_fav_nums(fav_type, fav_id, 1)
                res['status'] = 'success'
                res['msg'] = '已收藏'
            else:
                res['status'] = 'fail'
                res['msg'] = '收藏出错'
        return HttpResponse(json.dumps(res), content_type='application/json')


# 课程讲师列表页
class TeacherListView(View):
    def get(self, request):
        all_teachers = Teacher.objects.all()

        # 教师搜索
        serach_keywords = request.GET.get('keywords', "")
        if serach_keywords:
            all_teachers = all_teachers.filter(name__icontains=serach_keywords)

        sort = request.GET.get('sort', "")
        if sort:
            if sort == "hot":
                all_teachers = all_teachers.order_by("-click_nums")

        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]

        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_teachers, 1, request=request)

        teachers = p.page(page)


        return render(request, "teachers-list.html", {
            'all_teachers': teachers,
            'sorted_teacher': sorted_teacher,
            'sort': sort,
        })


# 讲师详情页
class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher.click_nums += 1
        teacher.save()

        all_course = Course.objects.filter(teacher=teacher)
        has_teacher_faved = False
        if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
            has_teacher_faved = True

        has_org_faved = False
        if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
            has_org_faved = True

        # 讲师排行
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]

        return render(request, "teacher-detail.html", {
            'teacher': teacher,
            'all_course': all_course,
            'sorted_teacher': sorted_teacher,
            'has_teacher_faved': has_teacher_faved,
            'has_org_faved': has_org_faved,
        })



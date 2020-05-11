from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import auth
from .models import *
from .forms import UploadFileForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .mypager import MyPager
from .forms import RegisterForm
from .utils import MyPaginator
# Create your views here.
def log(request):
    return render(request, 'languang.html')
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            bbs_user = BBS_User.objects.get(user__username=username)
        except (KeyError, BBS_User.DoesNotExist):
            return render(request, 'login.html', {'login_err':"用户名或密码错误！"})
        else:
            user = auth.authenticate(username=username, password=password)
            #assert(False)
            if user is not None:
                #authentication pass
                auth.login(request, user)

                category_list = Category.objects.all()
                post_list = Post.objects.all()
                return render(request, 'index.html', {'user': user, 'bbs_user': bbs_user, 'category_list': category_list, 'post_list': post_list})
            else:
                return render(request, 'login.html', {'login_err':'用户名或密码错误！'})
    else:
        return render(request, 'login.html')

def index(request):
    category_list = Category.objects.all()
    posts = Post.objects.all().order_by('created_date')
    current_page  = request.GET.get('page', 1)
    if current_page:
        current_page = int(current_page)
    paginator = MyPaginator(current_page, 11, posts, 10)
    start, end = paginator.show_page_num()
    if current_page >= 1:
        post_list = paginator.page(current_page)
    elif not current_page :
        post_list = paginator.page(1)
    elif current_page > paginator.num_pages:
        post_list = paginator.page(paginator.num_pages)
    #bbs_user = BBS_User.objects.get(user=request.user)
    user = request.user
    if user.is_authenticated():
        bbs_user = BBS_User.objects.filter(user=request.user)
        if bbs_user:
            bbs_user = bbs_user[0]
        else:
            bbs_user = None
    else:
        bbs_user = None

    return render(request, 'index.html', {
        'category_list': category_list,
        'post_list':post_list,
        'page_range': range(start,end+1),
        'current_page': int(current_page),
        'paginator': paginator,

        'bbs_user':bbs_user})

def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    category_list = Category.objects.all()
    comments = post.comment_set.all()

    if request.user.is_authenticated():
        bbs_user = BBS_User.objects.filter(user=request.user)[0]
    else:
        bbs_user = None
    return render(request, 'post_detail.html', {
        'post': post,
        'category_list': category_list,
        'bbs_user': bbs_user,
        'comments': comments,
    })


def logout(request):
    #bbs_user = get_object_or_404(BBS_User, user=request.user)
    #category_list = Category.objects.all()
    #post_list = Post.objects.all()
    auth.logout(request)
    return redirect('/index/')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print(form.errors.as_data())
        if form.is_valid():
            username = form.cleaned_data['username']
            user = BBS_User.objects.filter(user__username=username)

            if user:
                error_msg = '该用户名已被注册'
                return render(request, 'register.html', {'form': form, 'error_msg': error_msg})
            password = form.cleaned_data.get('password')
            password_confirm = form.cleaned_data.get('password_confirm')
            if password != password_confirm:
                error_msg = '请输入相同的密码!'
                return render(request, 'register.html', {'form': form, 'error_msg':error_msg})
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            sex = form.cleaned_data.get('sex')
            head_img = request.FILES.get('head_img')
            user = User.objects.create_user(username=username, password=password, email=email)
            print(user)
            BBS_User.objects.create(user=user,
                phone = phone,
                sex = sex,
                head_img = head_img)
            return redirect('/login/')
        else:
            return render(request, 'register.html', {'form': form})
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form':form})


def publish(request):
    category_list = Category.objects.all()
    if request.user.is_authenticated():
        #bbs_user = BBS_User.objects.filter(user=request.user)
        bbs_user = BBS_User.objects.filter(user=request.user)[0]
        if bbs_user:
            return render(request, 'publish.html', {'category_list': category_list, 'bbs_user': bbs_user})
        else:
            return redirect('/index/')
    else:
        return redirect('/index/')


def submit_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        cate = Category.objects.get(name=category)
        content = request.POST.get('content')
        summary = request.POST.get('summary')
        author = BBS_User.objects.get(user=request.user)
        myfile = request.FILES.getlist("myfile")
        for file in myfile:
            detination = 'D:/' + file.name
            with open(detination,'wb+') as f :
                for chunk in file.chunks():
                    f.write(chunk)
        Post.objects.create(author=author, title=title, category=cate, content=content, summary=summary)
        return redirect('/index/')
    else:
        return render(request, 'publish.html')

def category(request,category_id):
    post_list = Post.objects.filter(category__id=category_id)
    user = request.user
    print(user)

    #posts = Post.objects.all().order_by('created_date')
    current_page = request.GET.get('page', 1)
    if current_page:
        current_page = int(current_page)
    paginator = MyPaginator(current_page, 11, post_list, 10)
    start, end = paginator.show_page_num()
    if current_page >= 1:
        post_list = paginator.page(current_page)
    elif not current_page:
        post_list = paginator.page(1)
    elif current_page > paginator.num_pages:
        post_list = paginator.page(paginator.num_pages)
    if user.is_authenticated():
        bbs_user = BBS_User.objects.filter(user=request.user)[0]
    else:
        bbs_user = None
    category_list = Category.objects.all()
    cate_id = int(category_id)
    return render(request, 'index.html', { 'page_range': range(start, end + 1),
        'current_page': int(current_page),
        'paginator': paginator,'bbs_user': bbs_user, 'cate_id':cate_id, 'category_list':category_list, 'post_list': post_list})


def add_comment(request, post_id):
    content = request.POST.get('content')
    bbs_user = BBS_User.objects.filter(user=request.user)[0]
    post = Post.objects.get(pk=post_id)
    category_list = Category.objects.all()
    comment = Comment.objects.create(
        comment_content =content,
        creator = bbs_user,
        post = post,
    )
    comments = post.comment_set.all().order_by('date')

    return render(request, 'post_detail.html', {
        'post':post,
        'comments':comments,
        'category_list': category_list,
        'bbs_user': bbs_user,
    })


def bbs_user_detail(request, user_id):
    user = BBS_User.objects.filter(pk=user_id)
    return HttpResponse('welcome')

def file_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['uploadfile']
            with open('D:/'+file.name, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        else:
            return render(request, 'uploadfileform.html', {'form': form})
    else:
        form = UploadFileForm()
        return render(request, 'uploadfileform.html', {'form':form})

def comment_content_reply(request):
    '''
    评论回复类
    :param request:
    :return:
    '''
    creator = BBS_User.objects.get(user=request.user)
    post_id = request.POST.get('post_id')
    parent_content_id = request.POST.get('comment_content_id')
    comment_content = request.POST.get('comment_content_reply', None)
    #print(creator,111111,parent_content_id,222222,comment_content,333333,post_id)

    Comment.objects.create(creator=creator, post_id=post_id, comment_content=comment_content,
                           parent_comment_id=parent_content_id)

    return redirect('/post_detail/%s' % post_id)



# @login_required
# def post_review(request,post_id):
#     '''
#     评论类
#     :param request:
#     :param post_id:
#     :return:
#     '''
#     creator = BBS_User.objects.get(user=request.user)
#     comment_content =request.POST.get('comment_content',None)
#     Comment.objects.create(creator=creator, post_id=post_id, comment_content=comment_content)
#
#     # p_c = Comment.objects.get(pk=1)
#     # print(type( p_c),p_c.post.id)
#
#     return redirect('/post_detail/%s' % post_id )

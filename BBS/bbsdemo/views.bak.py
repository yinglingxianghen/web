from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import auth
from bbs_demo.models import *
from bbs_demo.forms import UploadFileForm

# Create your views here.
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
    post_list = Post.objects.all()
    
    return render(request, 'index.html', {'category_list': category_list, 'post_list':post_list})

def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    category_list = Category.objects.all()
    comments = post.comment_set.all()
    if request.user.is_authenticated():
        bbs_user = BBS_User.objects.filter(user=request.user)
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
    return HttpResponse('please register')

def publish(request):
    category_list = Category.objects.all()
    if request.user.is_authenticated():
        bbs_user = BBS_User.objects.filter(user=request.user)
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
        cate = Category.objects.filter(name=category)
        content = request.POST.get('content')
        summary = request.POST.get('summary')
        author = BBS_User.objects.filter(user=request.user)
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
    bbs_user = BBS_User.objects.filter(user=request.user)
    category_list = Category.objects.all()
    cate_id = int(category_id)
    return render(request, 'index.html', {'bbs_user': bbs_user, 'cate_id':cate_id, 'category_list':category_list, 'post_list': post_list})


def add_comment(request, post_id):
    content = request.POST.get('content')
    bbs_user = BBS_User.objects.filter(user=request.user)
    post = Post.objects.get(pk=post_id)
    category_list = Category.objects.all()
    comment = Comment.objects.create(
        comment_content =content,
        creator = bbs_user,
        post = post,
    )
    comments = post.comment_set.all().order_by('-date')

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
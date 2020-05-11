from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.log, name='log'),
    url(r'^login/$', views.login, name='login'),
    url(r'^index/$', views.index, name='index'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^publish/$', views.publish, name='publish'),
    url(r'^submit_post/$', views.submit_post, name='submit_post'),
    url(r'^category/(\d+)/$', views.category, name='category'),
    url(r'^post_detail/(\d+)/$', views.post_detail, name='post_detail'),
    url(r'^bbs_user_detail/(\d+)/$', views.bbs_user_detail, name='bbs_user_detail'),
    url(r'^add_comment/(\d+)/$', views.add_comment, name='add_comment'),
    url(r'^file_upload/$', views.file_upload, name='file_upload'),
    url(r'^comment_content_reply/$', views.comment_content_reply,name='comment_content_reply')
]
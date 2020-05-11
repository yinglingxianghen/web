
from django import template
from django.utils.html import mark_safe


register = template.Library()

@register.simple_tag
def ret_str(margin_left, k_comment_content, k_post_id, k_id):
    return '''<form action="/comment_content_reply/" method="post">
    <div class="comment" style="margin-left:%spx; font-size: 18px">%s
    <ul class="nav">
    <li class="dropdown">
    <a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false" style="height:50px;width:50px;padding:0 100px 0 100px;font-size:1px;color:red"> 回复</a>
    <ol class="dropdown-menu">
    <li>
    <input type="hidden" name="post_id" value="%d">
    <input type="hidden" name="comment_content_id" value="%d">
    <textarea cols="100" rows="2" required name="comment_content_reply"></textarea>
    <button style="height:50px;width:40px;color:blue" type="submit">回复</button></li></ol></li></ul></div></form>''' % (margin_left, k_comment_content, k_post_id, k_id)

@register.simple_tag
def build_comment_tree(comment_list):
    #---开始生成评论字典---#
    comment_dic = {}
    for comment_obj in comment_list:
        if comment_obj.parent_comment is None:
            comment_dic[comment_obj] = {}
        else:
            search_parent_comment(comment_dic,comment_obj)
    html = ""
    # ---生成评论字典结束---#

    # ---开始生成评论HTML---#
    for k,v in comment_dic.items():
        margin_left = 0
        html += ret_str(margin_left, k.comment_content, k.post.id, k.id)
        if v:
            html += generate_html(v,margin_left + 25)
    return mark_safe(html)
    # ---生成评论HTML结束---#

def generate_html(sub_comment_dic,margin_left):
    '''
    递归生成 html 标签
    :param sub_comment_dic:
    :param margin_left:
    :return:
    '''
    html = ""
    for k,v in sub_comment_dic.items():
        html += ret_str(margin_left, k.comment_content, k.post.id, k.id)
        if v:
            html += generate_html(v, margin_left + 25)
    return html


def search_parent_comment(comment_dic,comment_obj):
    '''
    递归获取 评论数据 生成字典
    :param comment_dic:
    :param comment_obj:
    :return:
    '''
    for k,v in comment_dic.items():
        if k == comment_obj.parent_comment:
            comment_dic[k][comment_obj] = {}
        else:
            search_parent_comment(comment_dic[k], comment_obj)


# coding=utf-8
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def generate_comment_html(sub_comment_dic, margin_left):
    html = ""
    # 遍历子评论字典
    for k, v in sub_comment_dic.items():
        # 子评论第一层
        html += "<div style='margin-left:%spx' class='comment-node'>" % margin_left + k.comment_content + "</div>"
        # 如果下面还有子节点，递归继续加
        if v:
            html += generate_comment_html(v, margin_left + 15)
    return html


# 递归查找父节点
def tree_search(comment_dic, comment_obj):
    for k, v in comment_dic.items():
        # 如果这个字典的k等于comment_obj的parent_comment，那么comment_obj的父节点就找到了。
        if k == comment_obj.parent_comment:
            # 找到的话，把自己插入到父节点下面，同时留个口，以防自己下面还有子节点。
            comment_dic[k][comment_obj] = {}
            # 找到，且插入完成，返回
            return
        else:
            # 没找到，往下一层递归查找。
            tree_search(comment_dic[k], comment_obj)

@register.simple_tag
def build_comment_tree(comment_list):
    # 评论树空字典
    comment_dic = {}

    # 循环遍历该comment_list
    for comment_obj in comment_list:
        # 如果comment没有parent_comment，那么它作为根节点构造一个评论树中的一棵树。
        if comment_obj.parent_comment is None:
            comment_dic[comment_obj] = {}
        else:
            # 如果有parent_comment，递归查找它的父节点。
            tree_search(comment_dic, comment_obj)

    # 循环过后，所有comment归位，评论树正确建立。
    # 接下来构造一个具有层级关系的html，传给前台，让前台正确显示comment层级关系。
    html = "<div class='comment-bos'>"
    # 思路就是从构建好的comment_dic字典中，从父节点开始递归拼接html字符串，最后一个子节点字典的value是空了，表示遍历完了。
    margin_left = 0
    for k, v in comment_dic.items():
        # 第一层html
        html += "<div class='comment-node'>" + k.comment_content + "</div>"
        # 通过递归把k的儿子都加上
        html += generate_comment_html(v, margin_left + 15)
    html += "</div>"
    return mark_safe(html)





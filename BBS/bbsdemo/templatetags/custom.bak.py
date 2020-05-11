from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def generate_comment_html(sub_comment_dic, margin_left):
    html = ""
    for k,v in sub_comment_dic.items():
        html += "<div class='comment-node' style='margin-left:%spx'>" % margin_left + k.comment_content + "</div>"
        if v:
            html += generate_comment_html(v, margin_left + 15)
    return html


def search_parent_comment(comment_dic,comment_obj):
    for k,v in comment_dic.items():
        if k == comment_obj.parent_comment:
            comment_dic[k][comment_obj] = {}
            return
        else:
            search_parent_comment(comment_dic[k], comment_obj)


@register.simple_tag
def build_comment_tree(comment_list):
    comment_dic = {}
    for comment_obj in comment_list:
        if comment_obj.parent_comment is None:
            comment_dic[comment_obj] = {}
        else:
			search_parent_comment(comment_dic, comment_obj)
    html = "<div class='comment-bos'>"
    margin_left = 0

    for k,v in comment_dic.items():
        html += "<div class='comment-node'>" + k.comment_content + "</div>"
        html += generate_comment_html(v, margin_left + 15)
    html += "</div>"
    return mark_safe(html)




#coding=utf-8
"""
    06/07/2017,19:07,2017
    BY DoraZhang
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class TreeData():
    #获取变量树
    treeArray = []
    def getChildren(id=0):
        jsonArray = []
        for obj in treeArray:
            if obj["parentid"] == id:
                x = getChildren(obj["id"])
                if len(x) != 0:
                    jsonArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"], "nodes": x})
                else:
                    jsonArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"]})

        return jsonArray

    treeview = models.Variable.objects.all()
    for t in treeview:
        treeNode = {'id': t.nid, 'parentid': t.parentid, 'name': t.zname, 'aliasn': t.aliasname}
        treeArray.append(treeNode)
    treeData = getChildren()
    #   treeData = [{"text": "Node 1"}]

    #获取机组列表
    jzArray = []
    def getJzChildren(id=0):
        jArray = []
        for obj in jzArray:
            if obj["parentid"] == id:
                x = getJzChildren(obj["id"])
                if len(x) != 0:
                    jArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"], "nodes": x})
                else:
                    jArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"]})

        return jArray

    #   获取机组名称
    jz = models.Jzvariable.objects.all()
    for t in jz:
        jnode = {'id': t.jid, 'parentid': t.parentid, 'name': t.jzname, 'aliasn': t.aliasname}
        jzArray.append(jnode)
    jzData = getJzChildren()

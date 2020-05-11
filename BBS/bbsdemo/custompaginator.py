from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

class CustomPaginator(Paginator):
    def  __init__(self, current_page, max_pager_num,*args, **kwagrs):
        """
            :param current_page: 当前页
            :param max_pager_num:最多显示的页码个数
            :param args:
            :param kwargs:
            :return:
            """
        self.current_page = int(current_page)
        self.max_pager_num = max_pager_num
        super(CustomPaginator, self).__init__(*args, **kwagrs)

    def page_num_range(self):
        # 当前页面
        # self.current_page
        # 总页数
        # self.num_pages
        # 最多显示的页码个数
        # self.max_pager_num
        #特殊情况
        if self.num_pages < self.max_pager_num:
            return range(1, self.num_pages + 1)

        part = int(self.max_pager_num / 2)
        if self.current_page - part < 1:
            return range(1, self.max_pager_num + 1)

        if self.current_page + part > self.num_pages:
            return range(self.num_pages + 1 - self.max_pager_num, self.num_pages + 1)
        return range(self.current_page - part, self.current_page + part + 1)

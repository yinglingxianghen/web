from django.core.paginator import Paginator

class MyPager(Paginator):
    def __init__(self, current_page, max_pager_num, *args, **kwargs ):
        self.current_page = int(current_page)
        self.max_pager_num = max_pager_num

        super(MyPager,self).__init__(*args, **kwargs)

    def get_start_end(self):
        return self.show_page_num()

    def show_page_num(self):
        if self.max_pager_num > self.num_pages:
            start = 1
            end = self.num_pages
            return start, end

        part = self.max_pager_num // 2
        if self.current_page <= part + 1:
            start = 1
            end = self.max_pager_num
            return start, end

        if self.current_page + part > self.num_pages:
            start = self.num_pages - self.max_pager_num + 1
            end = self.num_pages
            return start, end


        start = self.current_page - part
        end = self.current_page + part -1
        return start, end



import os
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from shop.models import Category,Product,Categoryproperty,Supplier,Categorypropertyvalue,Productproperty,Ad,Saleproperty
from account.models import UserFav
from comments.models import Tag,Comments,Commentspic
from coupons.models import Coupon,CouponRedemption
from orders.models import Order,OrderItem
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
import datetime
from shop.cache_manager import setcache,getcache
from django.template.loader import render_to_string
import codecs
import pickle
from django.conf import settings

HTML_DIR=os.path.join(settings.BASE_DIR, 'templates/html')
# Create your views here.
def globe_context(request):
    top_categories = Category.objects.filter(parent__isnull=True)
    categories = Category.objects.exclude(parent__isnull=True)

    ad_list = Ad.objects.all()
    context = {
        'categories': categories,
        'top_categories': top_categories,
        'ad_list': ad_list,
    }

    return context


def index(request):
    # 首页表态化，取当天时间构造文件名
    todays = datetime.date.today()
    indexhtml = 'index_{}.html'.format(todays)
    index_html = os.path.join(HTML_DIR, indexhtml)
    #检查是否已生成静态化首页
    if not os.path.exists(index_html) :

        if request.user:
            user = request.user

        supply_list = Supplier.objects.all()
        # 手机通讯相关数据id=1 为手机通讯
        category_phone2= Category.objects.filter(parent=1)
        category_phonechild = getchild(category_phone2)

        products_phone = Product.objects.filter(category__in = category_phonechild ).order_by('saleproperty')
        hot_phone = products_phone.filter(saleproperty=1)
        saleproperty_phone = Saleproperty.objects.filter(category=1).order_by('id')
        suppply_list_phone = supply_list.filter(category__in = category_phonechild)[0:6]

       # 电脑数码相关数据# id=2 为电脑数码
        category_computer2 = Category.objects.filter(parent=2)[0:4]
        category_computerchild = getchild(category_computer2)
        products_computer = Product.objects.filter(category__in=category_computerchild).order_by('saleproperty')
        # hot_computer = products_computer.filter(saleproperty=1)  # 精选热卖
        saleproperty_computer = Saleproperty.objects.filter(category=2).order_by('id')
        # 家用电器相关数据# id=3 为家用电器
        category_dianqi2 = Category.objects.filter(parent=3)[0:4]
        category_dianqichild = getchild(category_dianqi2)
        products_dianqi = Product.objects.filter(category__in=category_dianqichild).order_by('saleproperty')
        # hot_dianqi = products_dianqi.filter(saleproperty=1)  # 精选热卖
        saleproperty_dianqi = Saleproperty.objects.filter(category=3).order_by('id')
        # 服饰鞋包相关数据# id=4 为服饰鞋包
        category_cloth2 = Category.objects.filter(parent=4)[0:4]
        category_clothchild = getchild(category_cloth2)
        products_cloth = Product.objects.filter(category__in=category_clothchild).order_by('saleproperty')
        # hot_cloth = products_cloth.filter(saleproperty=1)  # 精选热卖
        saleproperty_cloth = Saleproperty.objects.filter(category=4).order_by('id')
        # 家居家装相关数据# id=5 家居家装
        category_jiaju2 = Category.objects.filter(parent=5)[0:10]
        category_jiajuchild = getchild(category_jiaju2)
        products_jiaju = Product.objects.filter(category__in=category_jiajuchild).order_by('saleproperty')
        # hot_jiaju = products_jiaju.filter(saleproperty=1)# 精选热卖
        saleproperty_jiaju = Saleproperty.objects.filter(category=5).order_by('id')

        # 优惠券
        coupon_list = Coupon.objects.filter(is_active=1).filter(expiration_date__gt=todays)[0:5]

        # 畅销商品
        ids = []
        bestsale_productids = OrderItem.objects.all().values('product_id').annotate(total=Count('product_id')).order_by(
            '-total')[0:6]
        for productids in bestsale_productids:
            ids.append(productids['product_id'])
        bestsale_product = Product.objects.filter(id__in=ids)

        content = render_to_string('shop/index.html', locals())
        # with open(index_html,'w') as static_file:
        with  codecs.open(index_html, 'w', encoding='utf-8') as static_file:
            static_file.write(content)
    return render(request, index_html, locals())

    # return render(request ,'shop/index.html',locals())

def getchild(categorylist):
    pid=[]
    #以分类的id作为父id,构造父id 列表
    for category in categorylist:
        pid.append(category.id)
    #由parent__in=pid取出所有的子类
    return  Category.objects.filter(parent__in=pid)


def category(request):
    topid =  request.GET.get('topid')
    seccateid =  request.GET.get('seccateid')
    thirdid =  request.GET.get('thirdid')
    selcatename =  request.GET.get('selcatename')

    categoryproperty =Categoryproperty.objects.all()

    brands_list = Supplier.objects.all()

    if thirdid:
        product_list = Product.objects.filter(category=thirdid)
        categoryproperty_list = Categoryproperty.objects.filter(category=thirdid)
        if categoryproperty_list:
            propertyvalue_list = Categorypropertyvalue.objects.filter(categoryproperty__in=categoryproperty_list)
        brands_list = brands_list.filter(category=thirdid)
    elif  seccateid:
        product_list = Product.objects.filter(category__parent=seccateid)
        brands_list = brands_list.filter(category__parent=seccateid)
    elif topid:
        product_list = Product.objects.filter(category__parent__parent=topid)
        brands_list = brands_list.filter(category__parent__parent=topid)

    propertyvalueid = request.GET.get('propertyvalueid')
        # 已选分类属性
    selected_list = []
    if propertyvalueid:
        # 构造list
        valueidlist = list(propertyvalueid.split(','))
        property_product = []
        i = 0
        # 分类扩展属性值表
        cateproperty_list = Categorypropertyvalue.objects.filter(id__in=valueidlist)
        print(cateproperty_list)
        for cateproperty in cateproperty_list:
            # 已选分类属性列表
            selected_list.append({'id': cateproperty.id, "name": cateproperty.valuename,
                                  'categoryproperty': cateproperty.categoryproperty.displayname,
                                  'cateid': cateproperty.categoryproperty.id})
        # 将含有此属性的商品id查询出来
        property_productids = Productproperty.objects.all().filter(categorypropertyvalue__in=cateproperty_list).values_list('product', flat=True)

        # 根据查询出的商品id查询商品信息
        products_list = product_list.filter(id__in=property_productids)


    #如选了品牌
    brandid = request.GET.get('brandid')
    if brandid:
        product_list = product_list.filter(supplier=brandid)
        brands = brands_list.get(id=brandid)
        #品牌已选
        brand_selectednamme = brands.name
        brand_selected = True
    #排序
    orderby = request.GET.get('orderby')
    if orderby:
        product_list = product_list.order_by(orderby)

    products_count = product_list.count()
    # 进行分页
    page = request.GET.get('page')
    pagesize = 8
    curr_url = request.get_full_path()
    nPos = curr_url.find('&page')
    if nPos > 0:
        curr_url = request.get_full_path()[0:nPos]
    else:
        curr_url = request.get_full_path()
    # 取第page页数据
    if page == None:
        page = 1
    else:
        page = int(page)
    # 分页
    product_list, pages = getpage(product_list, page, pagesize)

    return render(request, 'shop/category.html', locals())



'''
#### Paginator类实例对象

- 方法__init__(列表,int)：返回分页对象，第一个参数为列表数据，第二个参数为每页数据的条数。
- 属性count：返回对象总数。
- 属性num_pages：返回页面总数。
- 属性page_range：返回页码列表，从1开始，例如[1, 2, 3, 4]。
- 方法page(m)：返回Page类实例对象，表示第m页的数据，下标以1开始。

#### Page类实例对象

- 调用Paginator对象的page()方法返回Page对象，不需要手动构造。
- 属性object_list：返回当前页对象的列表。
- 属性number：返回当前是第几页，从1开始。
- 属性paginator：当前页对应的Paginator对象。
- 方法has_next()：如果有下一页返回True。
- 方法has_previous()：如果有上一页返回True。
- 方法len()：返回当前页面对象的个数。
'''
#分页
def getpage(objectlist,page=1,pagesize=10):
    paginator = Paginator(objectlist, pagesize)  # 每页10条
    #pages = range(1)
    #page = request.GET.get('page')
    try:
        if page==1:
            contacts = paginator.page(1)
            num_pages = paginator.num_pages
            pages = range(1, num_pages + 1)
        else:
            contacts = paginator.page(page)  # contacts为Page对象！
            # 页码处理
            # 如果分页之后页码超过5页，最多在页面上只显示5个页码：当前页前2页，当前页，当前页后2页
            # 1) 分页页码小于5页，显示全部页码
            # 2）当前页属于1-3页，显示1-5页
            # 3) 当前页属于后3页，显示后5页
            # 4) 其他请求，显示当前页前2页，当前页，当前页后2页
            num_pages = paginator.num_pages
            if num_pages < 5:
                # 1-num_pages
                pages = range(1, num_pages + 1)
            elif page <= 3:
                pages = range(1, 6)
            elif num_pages - page <= 2:
                # num_pages-4, num_pages
                pages = range(num_pages - 4, num_pages + 1)
            else:
                # page-2, page+2
                pages = range(page - 2, page + 3)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return contacts,pages

def product_detail(request):
    id = request.GET.get('productid')
    product = get_object_or_404(Product, id=id, available=True)
    # 此店家销售排行
    bestsale_product = OrderItem.objects.filter(product__store=product.store).annotate(
        total=Count('product_id')).order_by('-total')[0:5]
    # 此店家收藏排行
    userfav_list = UserFav.objects.filter(products__store=product.store).annotate(
        total=Count('products_id')).order_by('-total')[0:5]
    # 优惠券
    coupon_list = []
    # 指定商品优惠券type=1
    coupon_list = Coupon.objects.filter(type=1).filter(is_active=1).filter(product=product).filter(
        expiration_date__gt=datetime.datetime.now())
    # 全场优惠券type=2
    coupon_allproduct = Coupon.objects.filter(type=2).filter(is_active=1).filter(
        expiration_date__gt=datetime.datetime.now())
    if coupon_allproduct:
        coupon_list = (coupon_list | coupon_allproduct)[0:2]
    comments_list = Comments.objects.filter(product=id)
    comments_count = comments_list.count()
    # 进行分页
    page = request.GET.get('page')
    curr_url = request.get_full_path()
    nPos = curr_url.find('&page')
    if nPos > 0:
        curr_url = request.get_full_path()[0:nPos]
    else:
        curr_url = request.get_full_path()
    # 取第page页数据
    if page == None:
        page = 1
    else:
        page = int(page)
    comments_list, pages = getpage(comments_list, page, 10)
    tag_list = Tag.objects.filter(comments__product=id).annotate(commentsnum=Count('comments'))

    return render(request, 'shop/product_detail.html', locals())

def hotsale_list(request):
    pass

#淘实惠
def goodbuy(request):
    # 淘实惠 pname='淘实惠'
    saleproperty_ids = Saleproperty.objects.filter(pname='淘实惠').values('id')
    #设置保存到缓存的key
    goodbuy_key = 'goodbuy'
    #根据key，从缓存中读数据
    goodbuy_list = getcache(goodbuy_key)
    if goodbuy_list:
        #如有数据，反序列化为对象
        goodbuy_list = pickle.loads(goodbuy_list)
    elif goodbuy_list is None:
        #如没有数据，从数据库中读取
        goodbuy_list = Product.objects.filter(saleproperty_id__in=saleproperty_ids).order_by('-id')
        #并将数据序列化后保存到缓存
        setcache(goodbuy_key, pickle.dumps(goodbuy_list), 60 * 60)


    # 进行分页
    page = request.GET.get('page')
    pagesize = 8
    curr_url = request.get_full_path()
    nPos = curr_url.find('?page')
    if nPos > 0:
        curr_url = request.get_full_path()[0:nPos]
    else:
        curr_url = request.get_full_path()
    # 取第page页数据
    if page == None:
        page = 1
    else:
        page = int(page)
    #对数据列表进行分页
    goodbuy_products,pages = getpage(goodbuy_list, page, pagesize)

    return render(request, 'shop/goodbuy_list.html', locals())

#畅销商品
def hotsale_list(request):
    ids = []
    bestsale_productids = OrderItem.objects.all().values('product_id').annotate(total=Count('product_id')).order_by(
        '-total')
    for productids in bestsale_productids:
        ids.append(productids['product_id'])

    # 设置保存到缓存的key
    bestsale_key = 'bestsale'
    # 根据key，从缓存中读数据
    bestsale_list = getcache(bestsale_key)
    if bestsale_list:
        # 如有数据，反序列化为对象
        bestsale_list = pickle.loads(bestsale_list)
    elif bestsale_list is None:
        # 如没有数据，从数据库中读取
        bestsale_list = Product.objects.filter(id__in=ids)
        # 并将数据序列化后保存到缓存
        setcache(bestsale_key, pickle.dumps(bestsale_list), 60 * 60)

    # 进行分页
    page = request.GET.get('page')
    pagesize = 20
    curr_url = request.get_full_path()
    nPos = curr_url.find('?page')
    if nPos > 0:
        curr_url = request.get_full_path()[0:nPos]
    else:
        curr_url = request.get_full_path()
    # 取第page页数据
    if page == None:
        page = 1
    else:
        page = int(page)

    bestsale_product,pages = getpage(bestsale_list, page, pagesize)

    return render(request, 'shop/hotsale.html', locals())

def getbestsale_products(cateids):
    ids = []
    # 设置保存到缓存的key
    bestsale_product_key = 'bestsale_product'
    # 根据key，从缓存中读数据
    bestsale_product = getcache(bestsale_product_key)
    if bestsale_product:
        # 如有数据，反序列化为对象
        bestsale_product = pickle.loads(bestsale_product)
    elif bestsale_product is None:
        # 如没有数据，从数据库中读取
        bestsale_product = OrderItem.objects.filter(product__category__in=cateids).annotate(
            total=Count('product_id')).order_by('-total')[0:5]
        # 并将数据序列化后保存到缓存
        setcache(bestsale_product_key, pickle.dumps(bestsale_product), 60 * 60)

    return bestsale_product


#手机通讯
def mobile_list(request):
    # 手机通讯相关数据id=1 为手机通讯
    category_phone2 = Category.objects.filter(parent=1)[0:4]
    category_phonechild = getchild(category_phone2)
    products_phone = Product.objects.filter(category__in=category_phonechild).order_by('saleproperty')  #
    hot_phone = products_phone.filter(saleproperty=1)  # 精选热卖
    saleproperty_phone = Saleproperty.objects.filter(category=1).order_by('id')

    bestsale_productlist = getbestsale_products(category_phonechild)
    # 手机通讯品牌
    brands_list = Supplier.objects.filter(category__parent__parent=1)

    return render(request, 'shop/mobile_list.html', locals())


#电脑数码
def computer_list(request):
    # 电脑数码相关数据# id=2 为电脑数码
    category_computer2 = Category.objects.filter(parent=2)[0:4]
    category_computerchild = getchild(category_computer2)
    products_computer = Product.objects.filter(category__in=category_computerchild).order_by('saleproperty')
    hot_computer = products_computer.filter(saleproperty=1)  # 精选热卖
    saleproperty_computer = Saleproperty.objects.filter(category=2).order_by('id')

    bestsale_productlist = getbestsale_products(category_computerchild)

    return render(request, 'shop/computer_list.html', locals())

from django.shortcuts import render
import datetime
from coupons.models import Coupon,CouponRedemption

#领券中心
def coupon_list(request):

    # coupon_list = CouponRedemption.objects.filter(status=1)
    todays = datetime.date.today()
    coupon_list = Coupon.objects.filter(is_active=1).filter(expiration_date__gt=todays)
    if request.method == 'POST':
        if request.user.id:
            id = request.POST.get('coupanid')
            if id :
                coup = CouponRedemption.objects.get(coupon=id)
                coup.user= request.user
                coup.getdate = datetime.datetime.now()
                coup.save()
                msg = u'领券成功'
        else:
            msg = u'没有登录，请先登录'
    return render(request, 'coupon/coupon.html', locals())

from django import forms
from django.core.validators import RegexValidator,ValidationError

class UploadFileForm(forms.Form):
    filename = forms.CharField(max_length=64)
    test = forms.CharField(required=True)
    uploadfile = forms.FileField()
    initial = forms.CharField(initial='请输入')



class RegisterForm(forms.Form):
    username = forms.CharField(required='用户名不能为空', max_length=64,label='用户名')
    password = forms.CharField(widget=forms.PasswordInput, required='密码不能为空',max_length=32,min_length=8,label='密码')
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required='密码不能为空',
        max_length=32,
        min_length=8,
        label = '密码确认'
    )
    email = forms.EmailField(required='邮箱不能为空', label='邮箱')
    phone = forms.CharField(required='手机号码不能为空',max_length=11,error_messages={
                                 'phone_err': '手机号码格式有误',
                             },
                             validators=[
                                 RegexValidator(regex='1[3578][0-9]{9}', message='手机号码格式有误',
                                                code='phone_err')
                             ],label = '手机号码')
    sex = forms.CharField(label='性别',widget=forms.Select(choices=(
        ('male', '男'),
        ('female', '女'),
    )))
    head_img = forms.ImageField(required=False,label='头像')


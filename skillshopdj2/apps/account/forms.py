# -*- coding:utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField(label=u'帐号',)
    password = forms.CharField(label=u'密码',widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(label=u'帐号', )
    password = forms.CharField(label=u'密码', widget=forms.PasswordInput)
    #password2 = forms.CharField(label=u'重输密码', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo','grender','address','moible')
class PasswordchangeForm(forms.Form):
    old_password = forms.CharField(label=u"原密码", widget=forms.PasswordInput)
    new_password1 = forms.CharField(label=u"新密码", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=u"新密码再输入", widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordchangeForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['二次输入的密码不一样，请重输入！'])
        return password2


    def save(self, commit=True):
        """
        Saves the new password.
        """
        self.user.set_password(self.cleaned_data["new_password2"])
        if commit:
            self.user.save()
        return self.user
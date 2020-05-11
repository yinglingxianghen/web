
from __future__ import unicode_literals

from django.db import models


class Personalizedthreshold(models.Model):
    jzname = models.CharField(max_length=100)
    zname = models.CharField(max_length=100)
    aliasname = models.CharField(max_length=100, blank=True, null=True)
    threshold = models.IntegerField()
    activepower = models.IntegerField(db_column='activePower')  # Field name made lowercase.
    rotatespeed1 = models.IntegerField(db_column='rotateSpeed1')  # Field name made lowercase.
    rotatespeed2 = models.IntegerField(db_column='rotateSpeed2')  # Field name made lowercase.
    rotatespeed3 = models.IntegerField(db_column='rotateSpeed3')  # Field name made lowercase.
    starttime = models.CharField(db_column='startTime', max_length=100, blank=True, null=True)  # Field name made lowercase.
    endtime = models.CharField(db_column='endTime', max_length=100, blank=True, null=True)  # Field name made lowercase.
    datanum = models.IntegerField()
    userid = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PersonalizedThreshold'


class Allxfsvariable(models.Model):
    fieldname = models.CharField(max_length=50)
    comments = models.CharField(max_length=100, blank=True, null=True)
    parentid = models.IntegerField()
    optimal_value = models.CharField(max_length=15000)

    class Meta:
        managed = False
        db_table = 'allxfsVariable'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Bivarvariable(models.Model):
    jzname = models.CharField(max_length=100)
    rotatespeed = models.IntegerField(db_column='rotateSpeed')  # Field name made lowercase.
    load = models.IntegerField()
    activepower = models.IntegerField(db_column='activePower')  # Field name made lowercase.
    zname1 = models.CharField(max_length=100)
    aliasname1 = models.CharField(max_length=100, blank=True, null=True)
    zname2 = models.CharField(max_length=100)
    aliasname2 = models.CharField(max_length=100, blank=True, null=True)
    mic = models.FloatField()
    bivarr = models.FloatField()
    coef = models.FloatField()
    intercept = models.FloatField()
    score = models.FloatField()
    distthre = models.FloatField(db_column='distThre')  # Field name made lowercase.
    datanum = models.IntegerField()
    starttime = models.CharField(db_column='startTime', max_length=100, blank=True, null=True)  # Field name made lowercase.
    userid = models.CharField(max_length=100, blank=True, null=True)
    endtime = models.CharField(db_column='endTime', max_length=100, blank=True, null=True)  # Field name made lowercase.
    fengmic = models.CharField(max_length=100, blank=True, null=True)
    fengr = models.CharField(max_length=100, blank=True, null=True)
    fengcoef = models.CharField(max_length=100, blank=True, null=True)
    fengintercept = models.CharField(max_length=100, blank=True, null=True)
    fengscore = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bivarVariable'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Healthmodel(models.Model):
    modelpath = models.CharField(db_column='modelPath', max_length=50)  # Field name made lowercase.
    minvalue = models.FloatField()
    maxvalue = models.FloatField()
    createtime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'healthModel'


class Jzvariable(models.Model):
    jid = models.AutoField(primary_key=True)
    parentid = models.IntegerField()
    jzname = models.CharField(unique=True, max_length=100)
    aliasname = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jzvariable'


class Middlevariable(models.Model):
    fieldname = models.CharField(max_length=50)
    comments = models.CharField(max_length=100, blank=True, null=True)
    parentid = models.IntegerField()
    optimal_value = models.FloatField()
    gbl = models.IntegerField(db_column='GBL')  # Field name made lowercase.
    gbh = models.IntegerField(db_column='GBH')  # Field name made lowercase.
    hecl = models.IntegerField(db_column='HECL')  # Field name made lowercase.
    hech = models.IntegerField(db_column='HECH')  # Field name made lowercase.
    contractl = models.IntegerField(db_column='contractL')  # Field name made lowercase.
    contracth = models.IntegerField(db_column='contractH')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'middleVariable'


class Modelresult(models.Model):
    userid = models.CharField(max_length=100)
    starttime = models.CharField(max_length=100, blank=True, null=True)
    endtime = models.CharField(max_length=100, blank=True, null=True)
    datanum = models.IntegerField(blank=True, null=True)
    univarfields = models.CharField(max_length=2000)
    bivarfields = models.CharField(max_length=2000)
    bivarmainfield = models.CharField(max_length=100)
    multifields = models.CharField(max_length=2000)
    monitfields = models.CharField(max_length=2000)
    id = models.IntegerField(primary_key=True)
    jzname = models.CharField(max_length=100, blank=True, null=True)
    monitperiod = models.CharField(max_length=100, blank=True, null=True)
    multinum = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'modelResult'


class Monitorvariable(models.Model):
    jzname = models.CharField(max_length=100)
    rotatespeed = models.IntegerField(db_column='rotateSpeed')  # Field name made lowercase.
    load = models.IntegerField()
    activepower = models.IntegerField(db_column='activePower')  # Field name made lowercase.
    zname = models.CharField(max_length=100)
    aliasname = models.CharField(max_length=100, blank=True, null=True)
    min_val = models.FloatField()
    mid_val = models.FloatField()
    max_val = models.FloatField()
    alert_val = models.FloatField()
    mean = models.FloatField()
    std = models.FloatField()
    timeinterval = models.IntegerField(db_column='timeInterval')  # Field name made lowercase.
    userid = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'monitorVariable'


class Multivarvariable(models.Model):
    jzname = models.CharField(max_length=100)
    rotatespeed = models.IntegerField(db_column='rotateSpeed')  # Field name made lowercase.
    load = models.IntegerField()
    activepower = models.IntegerField(db_column='activePower')  # Field name made lowercase.
    fieldpair = models.CharField(max_length=200, blank=True, null=True)
    modelname = models.CharField(db_column='modelName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    userid = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'multivarVariable'


class User(models.Model):
    uid = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=40)
    uname = models.CharField(unique=True, max_length=40)
    sex = models.IntegerField()
    updatetime = models.DateTimeField()
    createtime = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'


class Variable(models.Model):
    nid = models.AutoField(primary_key=True)
    parentid = models.IntegerField()
    zname = models.CharField(max_length=100)
    aliasname = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'variable'


class Variabletype(models.Model):
    tubeid = models.IntegerField()
    fieldname = models.CharField(max_length=50)
    datatype = models.CharField(max_length=20)
    comments = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=30, blank=True, null=True)
    fieldtype = models.CharField(max_length=30, blank=True, null=True)
    parentid = models.IntegerField()
    optimal_value = models.FloatField()

    class Meta:
        managed = False
        db_table = 'variableType'


class Xfsvariable(models.Model):
    fieldname = models.CharField(max_length=50)
    comments = models.CharField(max_length=100, blank=True, null=True)
    parentid = models.IntegerField()
    optimal_value = models.FloatField()

    class Meta:
        managed = False
        db_table = 'xfsVariable'
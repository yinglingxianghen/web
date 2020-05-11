#coding=utf-8
"""
    12/08/17,17:00,2017
    BY DoraZhang
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from sklearn import svm
from sklearn.externals import joblib
import numpy as np
import math
import time


def timeslice(t):
    ts = time.mktime(time.strptime(t, '%Y-%m-%d %H%M%S'))
    # for t in ts.gettime():
    #     timeseries.append(t[0:13] + ':' + t[13:15] + ':' + t[15:17])
    # ts = t.replace('-','').replace(' ', '')[8:]
    #return time.strftime('%H:%M:%S',time.strptime(t, '%Y-%m-%d %H%M%S'))
    return ts

def getFeature(x, y):
    positive = True
    sample = []
    # 以后可以替换成我们的个性化阈值
    threshold = 300
    sample.append(x.max() - x.min())
    sample.append(y.max() - y.min())
    if ((x.max() - x.min()) > threshold or (y.max() - y.min()) > threshold):
        positive = False
    return positive, sample


def readfile(file_name):
    csvfile = open(file_name)
    csv_reader = csv.reader(csvfile)
    x = []
    for row in csv_reader:
        x.append(float(row[0]))
    csvfile.close()
    return x


def getSamples(var1, var2):
    num_one_circle = 256
    # path = os.getcwd();
    # path = os.path.join(path,"decomp_417")
    # # path = '../decomp_417'
    # time_file = open(os.path.join(path,'times.txt'),'r')

    time_file = open("data/decomp_417/times.txt", 'r')

    X_train = []
    X_outliers = []
    X_all = []
    time_series = []
    while True:
        time_str = time_file.readline().strip()
        if not time_str:
            break
        time_series.append(timeslice(time_str))

        x = readfile("data/decomp_417/" + var1 + time_str + ".csv")
        y = readfile("data/decomp_417/" + var2 + time_str + ".csv")

        n_samples = len(x) // num_one_circle
        x = np.array(x)
        y = np.array(y)
        # print "time:"+ time_str+",x.min:"+ str(x.min())+",x.max:"\
        # +str(x.max())+",y.min:"+str(y.min())+",y.max:"+str(y.max())

        for i in range(1):
            positive, sample = getFeature(x[i * num_one_circle: (i + 1) * num_one_circle - 1], \
                                          y[i * num_one_circle: (i + 1) * num_one_circle - 1])
            if positive:
                X_train.append(sample)
            else:
                X_outliers.append(sample)
            X_all.append(sample)

    time_file.close()

    X_train = np.array(X_train)
    X_outliers = np.array(X_outliers)
    # print len(time_series), X_train.shape, X_outliers.shape
    return X_train, X_outliers, X_all, time_series


def train(X_train, nu, gamma):
    # fit the model
    clf = svm.OneClassSVM(nu=nu, kernel="rbf", gamma=gamma)
    clf.fit(X_train)
    sv_num = len(clf.support_)

    pred_train = clf.predict(X_train)
    n_error_train = pred_train[pred_train == -1].size

    # save the model
    joblib.dump(clf, "train_model.m")


def sigmoid(samples):
    y = [(1 if x > 0 else round(2 / (1 + 2 * math.exp(-x)), 4)) for x in samples]
    return np.array(y)


def score(samples):
    clf = joblib.load("train_model.m")
    clf.decision_function(samples)
    return sigmoid(samples)


def gettridata(X_train):
    # X_train = np.array(sorted(x_train, key=lambda x: x[0]))
    X_train = np.array(X_train)
    xxx = X_train[:, 0]
    yyy = X_train[:, 1]
    clf = joblib.load("train_model.m")
    Z = clf.decision_function(np.c_[xxx, yyy])
    sc = sigmoid(Z)
    # print sc

    return xxx.ravel(), yyy.ravel(), Z.ravel(), sc

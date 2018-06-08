## 环境

> Python 环境： 3.6

1. 系统依赖软件

        sudo apt-get install python-matplotlib ipython ipython-notebook

        sudo apt-get install python-pandas python-sympy python-nose

2. python机器学习库

        直接 pip install -r requirement.txt  即可

## 运行

        ipython TFIDF_Log.py

## 说明

+ 可以先训练模型把模型实例序列化到文本中，下次直接读入文本的实例，避免每次执行程序都要再训练一次（确实比较慢）。
+ REG.txt存放正则匹配表达式，并含有分类行
+ badqueries.txt和goodqueries.txt存放模型一的训练集
+ testdata1_bad和testdata1_good存放模型一的测试集
+ 测试结果存放在TP,FN,FP,TN各变量中，可在ipython界面中输入查看

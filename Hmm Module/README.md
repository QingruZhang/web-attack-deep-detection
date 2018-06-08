## 环境

> Python 环境： 3.6

1. 系统依赖软件

        sudo apt-get install python-matplotlib ipython ipython-notebook

        sudo apt-get install python-pandas python-sympy python-nose

2. python机器学习库

        hmmlearn模块win版本已存放在hmmlearn，hmmlearn-0.2.1.dist-info文件夹中

## 运行

        ipython 
        run HmmModel
        run Detector2

## 说明

+ HmmModel是利用标记好的训练集Hmmtrainset训练得到
+ HmmModel训练好的模型存放在model_profile_output中
+ HmmModel_grouptrain直接使用日志流量训练，作为初期的实验，其训练的结果以分组的方式存放在Model中，分组结果存放在id_group中
+ Detector2执行测试集的测试，测试样本为训练集Hmmtrainset，测试集hmmTestSet，脚本文件中的file变量可更改测试集
+ 其他模块包含功能依赖函数
+ id_done.txt保存以训练好模型的id
+ GetSqlData.py完成从服务器数据库提取数据并归一数据格式，并将归一化的数据用json保存,如文件夹中的weblog0407_data.json
+ pickle保存测试训练的模型集合
+ Model保存测试训练的单个模型
+ model_profile_output保存训练集训练的模型

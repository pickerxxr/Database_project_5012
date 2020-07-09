import os

count = 3 #最大检测次数，即第一次检测不存在则安装，会有安装失败的情况，就会再来一次

while count:
    try:
        import hashlib
        print('hashlib模块已安装')
        break
    except:
        print ('hashlib模块未安装,现在准备开始安装')
        os.system('pip install hashlib')
        count -= 1
        continue

count = 3
while count:
    try:
        import matplotlib
        print('matplotlib模块已安装')
        break
    except:
        print ('matplotlib模块未安装,现在准备开始安装')
        os.system('pip install matplotlib')
        count -= 1
        continue

count = 3
while count:
    try:
        import numpy
        print('numpy模块已安装')
        break
    except:
        print ('numpy模块未安装,现在准备开始安装')
        os.system('pip install numpy')
        count -= 1
        continue

count = 3
while count:
    try:
        import PyQt5
        print('PyQt5模块已安装')
        break
    except:
        print ('PyQt5模块未安装,现在准备开始安装')
        os.system('pip install PyQt5')
        count -= 1
        continue

count = 3
while count:
    try:
        import pyodbc
        print('pyodbc模块已安装')
        break
    except:
        print ('pyodbc模块未安装,现在准备开始安装')
        os.system('pip install pyodbc')
        count -= 1
        continue

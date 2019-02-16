# -*- coding: utf-8 -*
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
import shlex
import datetime
import subprocess
import time

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def login():
    result = False
    if request.method == 'POST':
        ssid = request.form['ssid']
        psk = request.form['password']

        # have a bug, wpa_cli command just check psk have 8 word.
        result = connect_wifi(ssid, psk)
        if result:
            return render_template('conn_succeed.html', result=result)

    return render_template('login.html', result=result)


@app.route('/clear', methods=['POST', 'GET'])
def clear():
    if request.method == 'POST':
        if clear_cache():
            return render_template('clear_succeed.html')
    return render_template('login.html')


def connect_wifi(ssid, psk):
    cmdstring = 'sh /usr/lib/Airprint_Hub/connect_wifi.sh ' + ssid + ' ' + psk
    result_cmd = execute_command(cmdstring)
    return result_cmd == 'OK\n'


def clear_cache():
    cmdstr = 'sh /usr/lib/Airprint_Hub/clear_cache.sh'
    result_cmd = execute_command(cmdstr)
    return result_cmd == 'OK\n'


def execute_command(cmdstring, cwd=None, timeout=None, shell=True):
    """执行一个SHELL命令
        封装了subprocess的Popen方法, 支持超时判断，支持读取stdout和stderr
        参数:
      cwd: 运行命令时更改路径，如果被设定，子进程会直接先更改当前路径到cwd
      timeout: 超时时间，秒，支持小数，精度0.1秒
      shell: 是否通过shell运行
    Returns: return_code
    Raises: Exception: 执行超时
    """
    if shell:
        cmdstring_list = cmdstring
    else:
        cmdstring_list = shlex.split(cmdstring)
    if timeout:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

    # 没有指定标准输出和错误输出的管道，因此会打印到屏幕上；
    sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=shell,
                           bufsize=4096)

    # subprocess.poll()方法：检查子进程是否结束了，如果结束了，设定并返回码，放在subprocess.returncode变量中
    while sub.poll() is None:
        time.sleep(0.1)
        if timeout:
            if end_time <= datetime.datetime.now():
                raise Exception("Timeout：%s" % cmdstring)

    return str(sub.stdout.read().decode("GBK"))


if __name__ == '__main__':
    app.debug = True
    app.run('192.168.222.1', 80)

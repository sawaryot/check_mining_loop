"""
事前チェック
・すでに本バッチが起動しているか確認
・GPU使用率ログバッチ起動確認
・ゲームが起動しているか確認(apex,dbd)
・GPU使用率が十分低いか確認

実行
・マイニング実行

"""
import subprocess
import csv
import time
from collections import defaultdict, namedtuple
import os
import sys
import psutil
import datetime
import re
import math

import subprocess
from subprocess import PIPE

loop_cnt = 0
CHECK_MINUTES = 1
WAIT_TIME = 2

def exec_subproc(cmd_file, cmd_file_sec):
    os.chdir(cmd_file)
    #os.system(cmd_file_sec)

    try:
        # サブプロセスをスタート
        proc = subprocess.Popen(cmd_file_sec, shell=True, stdout=PIPE, stderr=PIPE, text=True)
    except ZeroDivisionError as e:
        print('subproc error')
        print(e)

# 適当に100000カウンタ用意
# 100000 * 1分 = 500000 / 60分 = 8333時間 / 24 = 347日
while loop_cnt < 2:

    # 実行されていなければ実行する
    #cmd_file = "C:\Users\owner\Desktop\program\auto_mining\auto_mining.bat"
    #os.system(cmd_file)

    gpu_check_cnt = 0

    # 5分間(1分 * 5回)GPU使用率が高くなければマイニングを実行する
    #for i in range(4):
    dict_pids = {
        p.info["name"]
        for p in psutil.process_iter(attrs=["name"])
    }

    # GPU使用率ロガープログラムが実行されていることをチェック
    if 'nvidia-smi.exe' not in dict_pids:
        print('GPU使用率ロガープログラムが実行されていません。実行して８分間待ちます')
        # 実行されていなければGPU使用率ロガープログラムを実行してから8分待つ
        cmd_file = r"C:\Users\owner\Desktop\program\auto_mining"
        os.chdir(cmd_file)
        cmd_file = r"nvidia-smi --query-gpu=timestamp,utilization.gpu --format=csv -l 1 > C:\Users\owner\Desktop\program\auto_mining\gpu_log.csv -l 60"
        os.system(cmd_file)
        # 8分間timesleep()
        time.sleep(300)
    else:
        print('gpu使用率ロガーは実行されています')

    # GPU使用率ファイルを読み込む
    csv_file = open("./gpu_log.csv", "r", encoding="ms932", errors="", newline="" )
    #リスト形式
    #f = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    #辞書形式
    f = csv.DictReader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    
    #log_dict = defaultdict(lambda: defaultdict())
    for row in f:
        #rowはdictionary
        #row["column_name"] or row.get("column_name")で必要な項目を取得することができる
        print(row)
        record_time     = row["timestamp"]
        record_time = re.sub('\..*', '', record_time)
        utilization_gpu = row["utilization.gpu [%]"]
        utilization_gpu = int(utilization_gpu.strip(' %'))
        print('record_time:')
        print(record_time)
        print('utilization_gpu:')
        print(utilization_gpu)

        #mining_flag = True
        dt_now = datetime.datetime.now()
        target_date = datetime.datetime.strptime(record_time, '%Y/%m/%d %H:%M:%S')
        diff = dt_now - target_date

        diff_minutes = math.floor(diff.seconds / 60)
        diff_hours = math.floor(diff_minutes / 60)
        
        # 現在時刻との差分が7分以内であるかチェック
        if diff.days == 0 and diff_hours == 0 and diff_minutes < 8:

            if utilization_gpu < 50:
                #mining_flag = False
                gpu_check_cnt = gpu_check_cnt + 1

    # 直近５分間はGPU使用率が20%以内だったら
    if gpu_check_cnt >= 5:

        print('直近５分間はGPU使用率が50%以内')
        mining_flag = True

        # 5分間timesleep() test用なので削除して
        #time.sleep(300)
        #continue

        # マイニングプログラムが実行されていた場合はマイニングフラグをFalse
        if 'PhoenixMiner.exe' in dict_pids:
            print('PhoenixMiner.exe executed')
            mining_flag = False

        # APEXまたはDBDが立ち上がっていたらマイニング停止
        cmd = 'tasklist | findstr "apex DeadByDaylight"'
        #cmd = 'tasklist | findstr "cmd"'
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

        proc_name = ''
        for line in proc.stdout:
            proc_name = line

        print(proc_name)
        if proc_name != '':
            mining_flag = False

        # マイニングフラグがFalseなら5分待ってスキップ
        if mining_flag == False:
            print('mining_flagがFalseです。５分間待ってスキップ')
            # 5分間timesleep()
            time.sleep(300)           
            continue

        # 以下サブプロセスで実行
        # 5回連続(5分)でGPU使用が20%以下だったのでマイニング開始
        cmd_file = r"C:\Users\owner\Desktop\mining\PhoenixMiner_5.5c_Windows"
        #os.chdir(cmd_file)
        cmd_file_sec = r"C:\Users\owner\Desktop\mining\PhoenixMiner_5.5c_Windows\start_miner.bat"
        #os.system(cmd_file)
        exec_subproc(cmd_file,cmd_file_sec)

    else:
        print('gpu_check_cnt:')
        print(gpu_check_cnt)
        print('直近５分間GPU使用率が20%以内ではなかったのでマイニングは実行されませんでした')
        
    print('end')
    # 5分間timesleep()
    time.sleep(300)

    loop_cnt = loop_cnt + 1

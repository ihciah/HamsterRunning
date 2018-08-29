# -*- coding: utf-8 -*-

from influxdb import InfluxDBClient
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from requests_toolbelt import MultipartEncoder
import numpy as np
import requests
import time
from datetime import date

dbAddr = "127.0.0.1"
dbPort = 8086
dbName = "hamster"
dbUserName = "admin"
dbPassword = ""
token = "YOUR_TOKEN"
tmpFilePath = "/tmp/plot.jpg"


def send_weibo(text, image=False):
    url = "https://api.weibo.com/2/statuses/share.json"
    content = text + " https://weibo.com/cangshucangshu"
    if image:
        postContent = MultipartEncoder(fields={
            "access_token": token,
            "status": content,
            "pic": ("image.jpg", open(tmpFilePath, 'rb'))
        })
        r = requests.post(url, postContent, headers={'Content-Type': postContent.content_type})
    else:
        postContent = {
            "access_token": token,
            "status": content
        }
        r = requests.post(url, postContent)
    result = r.json()
    if "id" in result:
        return 0
    if "error_code" in result:
        return result["error_code"]
    return -1


def send_weibo_retry(text, image):
    sent = -1
    retry = 0
    while sent != 0 and retry < 3:
        sent = send_weibo(text, image)
        time.sleep(1)
        retry += 1


def plot(y):
    plt.style.use('ggplot')
    plt.figure(figsize=(10, 5))
    plt.title("Hamster Bob,Charlie,Dave's Running Log - %s" % date.isoformat(date.today()))
    plt.xlim((1, len(y)))
    plt.xlabel("Time")
    plt.ylabel("Round")
    plt.plot(np.arange(1, 1 + len(y)), np.array(y), '-', label="Hourly")
    stmp = 0
    for i in range(len(y)):
        y[i] += stmp
        stmp = y[i]
    plt.plot(np.arange(1, 1 + len(y)), np.array(y), '-', label="Sum")
    plt.legend()
    plt.grid(True)
    plt.savefig(tmpFilePath)


def update():
    client = InfluxDBClient(dbAddr, dbPort, dbUserName, dbPassword, dbName)
    lastDay = list(client.query('select sum(round) from round where time > now() - 24h group by time(1h) fill(0)')['round'])[-24:]
    if len(lastDay) == 24:
        y = [point['sum'] for point in lastDay]
        plot(y)
        send_weibo_retry(u"仓鼠运动", True)


if __name__ == "__main__":
    update()

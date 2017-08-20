from app import _celery
from app.models import XauusdSequencial
import itchat
from itchat.content import TEXT
import matplotlib.pyplot as plt
from config import PLOT_DIR, WEEK_SECONDS, DAY_SECONDS, FOUR_HOUR_SECONDS
import time
from datetime import datetime
import os
import numpy as np


@itchat.msg_register(TEXT)
def simple_reply(msg):
    # week/day/4hour
    msg_send = '%s: %s - %s' % (msg['Type'], msg['Text'], msg['FromUserName'])
    print(msg_send)
    if msg['Text'] == '周':
        ed_timestamp = time.time()
        st_timestamp = ed_timestamp - WEEK_SECONDS
        send_plot(st_timestamp, ed_timestamp)
    elif msg['Text'] == '日':
        ed_timestamp = time.time()
        st_timestamp = ed_timestamp - DAY_SECONDS
        send_plot(st_timestamp, ed_timestamp)
    elif msg['Text'] == '4小时':
        ed_timestamp = time.time()
        st_timestamp = ed_timestamp - FOUR_HOUR_SECONDS
        send_plot(st_timestamp, ed_timestamp)
    else:
        itchat.send(msg_send, toUserName='filehelper')


@_celery.task
def start_itchat():
    itchat.auto_login()
    itchat.run()


def send_plot(start_timestamp, end_timestamp):
    rs = XauusdSequencial.query.filter((XauusdSequencial.id <= end_timestamp)
                                       & (XauusdSequencial.id >= start_timestamp))
    # datetime.fromtimestamp(start_time), price, fxpro, average, dukscopy, ftroanda, fxcm, myfxbook, saxobank
    x, y1, y2, y3 = [], [], [], []
    for row in rs:
        x.append(datetime.fromtimestamp(int(row.id)))
        y1.append(row.price)
        y2.append(row.fxpro)
        y3.append([row.average, row.dukscopy, row.ftroanda, row.fxcm, row.myfxbook, row.saxobank])
    y3 = np.array(y3)

    # plot 1 for price
    fig, ax = plt.subplots()
    ax.plot(x, y1)
    fig.autofmt_xdate()
    plt.ylabel('Price($)')
    plt.grid(True)
    img_path = os.path.join(PLOT_DIR, '%s_1.png' % str(time.time()))
    plt.savefig(img_path)
    itchat.send_image(img_path, toUserName='filehelper')

    # plot 2 for fxpro
    fig, ax = plt.subplots()
    ax.plot(x, y2)
    ax.axhline(30, linestyle='--', color='r')  # horizontal lines
    ax.axhline(70, linestyle='--', color='r')  # horizontal lines
    ax.set_ylim(0, 100)
    fig.autofmt_xdate()
    plt.ylabel('fxpro(%)')
    plt.grid(True)
    ticklines = ax.get_xticklines() + ax.get_yticklines()
    gridlines = ax.get_xgridlines() + ax.get_ygridlines()
    for line in ticklines:
        line.set_linewidth(3)
    for line in gridlines:
        line.set_linestyle('--')
    img_path = os.path.join(PLOT_DIR, '%s_2.png' % str(time.time()))
    plt.savefig(img_path)
    itchat.send_image(img_path, toUserName='filehelper')

    # plot 3 for other indices
    # y3 columns is: average, dukscopy, ftroanda, fxcm, myfxbook, saxobank
    fig, ax = plt.subplots()
    ax.plot(x, y3[:, 0], label="average")
    ax.plot(x, y3[:, 1], label="dukscopy")
    # ax.plot(x, y3[:, 2], label="ftroanda")
    # ax.plot(x, y3[:, 3], label="fxcm")
    # ax.plot(x, y3[:, 4], label="myfxbook")
    # ax.plot(x, y3[:, 5], label="saxobank")
    ax.legend(loc='upper right')
    ax.axhline(30, linestyle='--', color='r')  # horizontal lines
    ax.axhline(70, linestyle='--', color='r')  # horizontal lines
    ax.set_ylim(0, 100)
    fig.autofmt_xdate()
    plt.ylabel('other indices(%)')
    plt.grid(True)
    ticklines = ax.get_xticklines() + ax.get_yticklines()
    gridlines = ax.get_xgridlines() + ax.get_ygridlines()
    for line in ticklines:
        line.set_linewidth(3)
    for line in gridlines:
        line.set_linestyle('--')
    img_path = os.path.join(PLOT_DIR, '%s_3.png' % str(time.time()))
    plt.savefig(img_path)
    itchat.send_image(img_path, toUserName='filehelper')
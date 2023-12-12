import paho.mqtt.client as mqtt
import time

from sscma.micro.client import Client
from sscma.micro.device import Device
from sscma.micro.const import *
import serial
import threading
import time
import logging
import cv2
import base64
import numpy as np


logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)


# 定义代理服务器和主题
broker_address = "192.168.199.230"
rx_topic = "sscma/v0/grove_we2_360779f5/tx"
tx_topic = "sscma/v0/grove_we2_360779f5/rx"

# 连接成功时的回调


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(rx_topic)

# 收到消息时的回调


def on_message(client, tclient, msg):
    tclient.recieve_handler(msg.payload)


def monitor_handler(msg):

    if "image" in msg:
        jpeg_bytes = base64.b64decode(msg["image"])

        # Convert the bytes into a numpy array
        nparr = np.frombuffer(jpeg_bytes, np.uint8)

        # Decode the image array using OpenCV
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Display the image
        cv2.imshow('Base64 Image', img)
        cv2.waitKey(1)
        msg.pop("image")
        
    print(msg)


def main():

    client = mqtt.Client()
    client.username_pw_set("user", "user")
    client.on_connect = on_connect
    client.on_message = on_message

    # 连接到代理服务器
    client.connect(broker_address, 1883, 60)

    # 保持连接
    client.loop_start()

    tclient = Client(lambda msg: client.publish(tx_topic, msg), debug=1)

    client.user_data_set(tclient)

    device = Device(tclient, debug=1)
    device.on_monitor = monitor_handler

    
    i = 60
    while True:
        if not device.status & DeviceStatus.INVOKING:
            print("Waiting for invoke...")
            device.invoke(-1, False ,True)
            device.tscore = 70
        print("model:{}".format(device.model))
        # device.tscore = i
        # device.tiou = i
        # i = i + 1
        # if i > 100:
        #     i = 30

        time.sleep(2)

    # 断开连接
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()

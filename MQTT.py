import paho.mqtt.client as mqtt
import numpy as np
import cv2
import time
import functools


##############Cấu hình MQTT trên máy tính#####################
# Cấu hình MQTT Broker
mqtt_server = "bf9e78d9019447609bada8c1a9b76912.s1.eu.hivemq.cloud"  # Thay bằng hostname của bạn
mqtt_port = 8883  # Cổng cho TLS
mqtt_user = "test_MQQT"  # Thay bằng username của bạn
mqtt_password = "123ABC456abc"  # Thay bằng password của bạn
topic_subscribe = "sendToPC"  # Topic để nhận tin nhắn
topic_publish = "sendfromPC"  # Topic để gửi tin nhắn

# Tạo MQTT client
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)  # Cấu hình username và password
client.tls_set()  # Kích hoạt kết nối TLS/SSL
#Tạo biến
cam_value = 0

# Hàm xử lý khi kết nối thành công
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to HiveMQ!")
        client.subscribe(topic_subscribe)  # Đăng ký vào topic
        client.subscribe("esp/1/1")
        client.subscribe("esp/2/1")
        client.subscribe("esp/3/1")
        client.subscribe("esp/3/2")
        client.subscribe("esp/3/3")
        client.subscribe("esp/3/4")
        client.subscribe("esp/3/5")
        client.subscribe("esp/3/6")
    else:
        print(f"Failed to connect with code {rc}")

# Hàm xử lý khi nhận tin nhắn
def on_message(client, userdata, msg):
 
    try:
        fire_detected = 0
        if msg.topic == topic_subscribe_cam_1:
            get_picture(image_path_cam_1, fire_detected, msg.payload)
        # Gọi module phát hiện lửa
        #fire_detected = detect_fire(image_path) # giá trị fire detected trả về 1 nếu là có lửa, 0 là ko có lửa
        #client.publish(topic_publish, fire_detected)
        if msg.topic == topic_subscribe_cam_2:
            get_picture(image_path_cam_2, fire_detected, msg.payload)
    # Này là mới xử lí một cam thôi, đến sau sẽ test hai cam
        cam_value = fire_detected
        message = msg.payload.decode()
        input_topic = msg.topic
        print(f"Received message: {message} on topic {input_topic}")

            mdnh = f"{cam_value}{message}"
            if mdnh != '000':
                floorr = input_topic[4]
                zone = input_topic[6]
                output_topic = f"lap/{floorr}/{zone}"
                client.publish(output_topic, mdnh)
                print(f"Published messenge: {mdnh} on topic {output_topic}")

    except Exception as e:
        print(f"Error processing message from topic {msg.topic}: {e}")

# Gắn cam_value vào userdata
client.user_data_set(cam_value)


# Gắn hàm callback
client.on_connect = on_connect
client.on_message = on_message

# Kết nối đến HiveMQ broker
print("Connecting to HiveMQ...")
client.connect(mqtt_server, mqtt_port)

# Vòng lặp chính
client.loop_start()

# Gửi tin nhắn (publish)
while True:
    message = "Hello from Python MQTT client!"
    client.publish(topic_publish, message)
    print(f"Published: {message}")
    input("Press Enter to send another message...")  # Chờ input để gửi tiếp

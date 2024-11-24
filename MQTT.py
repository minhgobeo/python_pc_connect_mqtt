import paho.mqtt.client as mqtt

# Cấu hình MQTT Broker
mqtt_broker = "bf9e78d9019447609bada8c1a9b76912.s1.eu.hivemq.cloud"  # Thay bằng hostname của bạn
mqtt_port = 8883  # Cổng cho TLS
mqtt_user = "test_MQQT"  # Thay bằng username của bạn
mqtt_password = "123ABC456abc"  # Thay bằng password của bạn
topic_subscribe = "takePicture"  # Topic để nhận tin nhắn
topic_publish = "sendfromPC"  # Topic để gửi tin nhắn

# Hàm xử lý khi kết nối thành công
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to HiveMQ!")
        client.subscribe(topic_subscribe)  # Đăng ký vào topic
    else:
        print(f"Failed to connect with code {rc}")

# Hàm xử lý khi nhận tin nhắn
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

# Tạo MQTT client
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)  # Cấu hình username và password
client.tls_set()  # Kích hoạt kết nối TLS/SSL

# Gắn hàm callback
client.on_connect = on_connect
client.on_message = on_message

# Kết nối đến HiveMQ broker
print("Connecting to HiveMQ...")
client.connect(mqtt_broker, mqtt_port)

# Vòng lặp chính
client.loop_start()

# Gửi tin nhắn (publish)
while True:
    message = "Hello from Python MQTT client!"
    client.publish(topic_publish, message)
    print(f"Published: {message}")
    input("Press Enter to send another message...")  # Chờ input để gửi tiếp

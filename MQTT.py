import paho.mqtt.client as mqtt
import numpy as np
import cv2
import tensorflow as tf
import time
import functools
###############Load model xử lý ảnh####################
# Load the model
model = tf.keras.models.load_model("fire_detection_model_transfer_learning.keras")

def detect_fire(image_path, threshold=0.6):
    # Read the image from file
    frame = cv2.imread(image_path)

    if frame is None:
        print(f"Error: Unable to load image {image_path}")
        return False

    # Resize and prepare the frame for model input
    preprocess_frame = cv2.cvtColor(cv2.resize(frame, (224, 224)), cv2.COLOR_BGR2RGB)  # Convert to RGB
    preprocess_frame = np.expand_dims(preprocess_frame, axis=0)  # Add batch dimension

    # Prediction
    prediction = model.predict(preprocess_frame)
    print(f"Prediction: {prediction[0]}")
    print(f"Fire probability: {prediction[0][0]}")

    # Check if fire is detected based on the threshold
    if prediction[0][0] >= threshold:
        return 1
    else:
        return 0

# Path to the image
image_path = "received_image.jpg"  # Replace with the path to your image

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

# Biến
cam_value = 0 #chỉnh sau

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
        if msg.topic == topic_subscribe:
            # Dữ liệu nhận được là chuỗi byte từ ESP32-CAM
            print("Receiving picture data...")
            image_data = msg.payload  # Binary image data
            # Giải mã thành mảng numpy

            nparr = np.frombuffer(image_data, np.uint8)
            # Chuyển đổi thành hình ảnh
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is not None:
                print("Image received and decoded!")
                # Hiển thị hình ảnh
                # Lưu ảnh ra file nếu cần
                cv2.imwrite("received_image.jpg", img)
            else:
                print("Failed to decode image.")
        # Gọi module phát hiện lửa
        fire_detected = detect_fire(image_path) # giá trị fire detected trả về 1 nếu là có lửa, 0 là ko có lửa
        client.publish(topic_publish, fire_detected)
    # Này là mới xử lí một cam thôi, đến sau sẽ test hai cam
        cam_value = userdata
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

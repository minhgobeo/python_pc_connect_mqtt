
import paho.mqtt.client as mqtt
import numpy as np
import cv2
import tensorflow as tf
import time
import functools
###############Load model xử lý ảnh####################
# Load the model
# Load the TFLite model
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("Model loaded successfully!")

def detect_fire(image_path, threshold=0.6):
    # Read the image from file
    frame = cv2.imread(image_path)

    if frame is None:
        print(f"Error: Unable to load image {image_path}")
        return False

    # Resize and prepare the frame for model input
    preprocess_frame = cv2.cvtColor(cv2.resize(frame, (224, 224)), cv2.COLOR_BGR2RGB)  # Convert to RGB
    preprocess_frame = np.expand_dims(preprocess_frame, axis=0)  # Add batch dimension
    preprocess_frame = preprocess_frame.astype(np.float32)  # Ensure the input is float32

    # Set the tensor
    interpreter.set_tensor(input_details[0]['index'], preprocess_frame)

    # Run the model
    interpreter.invoke()

    # Get the prediction
    prediction = interpreter.get_tensor(output_details[0]['index'])
    print(f"Prediction: {prediction[0]}")
    print(f"Fire probability: {prediction[0][0]}")

    # Check if fire is detected based on the threshold
    if prediction[0][0] >= threshold:
        return 1
    else:
        return 0
##############Hàm xử lý chuỗi binary từ hình ảnh#####################
def get_picture(image_path, fire_detected, image_data):
    #if msg.topic == topic_subscribe:
    # image_data = msg.payload
    # Dữ liệu nhận được là chuỗi byte từ ESP32-CAM
    print("Receiving picture data...")
    # Binary image data
    # Giải mã thành mảng numpy
    nparr = np.frombuffer(image_data, np.uint8)
    # Chuyển đổi thành hình ảnh
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is not None:
        print("Image received and decoded!")
        # Hiển thị hình ảnh
        # Lưu ảnh ra file nếu cần
        cv2.imwrite(image_path, img)
        fire_detected = detect_fire(image_path)  # giá trị fire detected trả về 1 nếu là có lửa, 0 là ko có lửa
        return fire_detected
    else:
        print("Failed to decode image.")
        return 0

# Đường dẫn ta image
image_path_cam_1 = "received_image.jpg"  # Replace with the path to your image
image_path_cam_2 = "received_image_1.jpg"

##############Cấu hình MQTT trên máy tính#####################
# Cấu hình MQTT Broker
mqtt_server = "4838f20abef342ccba6a129cecb3ebe8.s1.eu.hivemq.cloud"  # Thay bằng hostname của bạn
mqtt_port = 8883  # Cổng cho TLS
mqtt_user = "testaccount"  # Thay bằng username của bạn
mqtt_password = "Test12345"  # Thay bằng password của bạn
topic_subscribe_cam_1 = "cam/3/5"  # Topic để nhận dữ lieu tu cam
topic_subscribe_cam_2 = "cam/3/6"  # Topic để nhận dữ lieu tu cam
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
        client.subscribe(topic_subscribe_cam_1)  # Đăng ký vào topic
        client.subscribe(topic_subscribe_cam_2)
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
    global output_topic_cam_1
    global mdnh_cam_1
    global output_topic_cam_2
    global mdnh_cam_2
    #global fire_detected
    try:
        flag = 0
        fire_detected = 0
        if msg.topic == "esp/3/5" :
            message = msg.payload.decode()
            input_topic = msg.topic
            print(f"Received message: {message} on topic {input_topic}")

            mdnh_cam_1 = f"{message}"
            floorr = input_topic[4]
            zone = input_topic[6]
            output_topic_cam_1 = f"lap/{floorr}/{zone}"

            flag = 1;

        if msg.topic == "esp/3/6":
            message = msg.payload.decode()
            input_topic = msg.topic
            print(f"Received message: {message} on topic {input_topic}")

            mdnh_cam_2 = f"{message}"
            floorr = input_topic[4]
            zone = input_topic[6]
            output_topic_cam_2 = f"lap/{floorr}/{zone}"

            flag = 1;

        if msg.topic == topic_subscribe_cam_1:
            fire_detected = get_picture(image_path_cam_1, fire_detected, msg.payload)
            mdnh_cam_1 = f"{fire_detected}{mdnh_cam_1}"

            client.publish(output_topic_cam_1, mdnh_cam_1)
            print(f"Published messenge: {mdnh_cam_1} on topic {output_topic_cam_1}")
            flag = 1
        # Gọi module phát hiện lửa
        #fire_detected = detect_fire(image_path) # giá trị fire detected trả về 1 nếu là có lửa, 0 là ko có lửa
        #client.publish(topic_publish, fire_detected)
        if msg.topic == topic_subscribe_cam_2:
            fire_detected = get_picture(image_path_cam_2, fire_detected, msg.payload)

            mdnh_cam_2 = f"{fire_detected}{mdnh_cam_2}"

            client.publish(output_topic_cam_2, mdnh_cam_2)
            print(f"Published messenge: {mdnh_cam_2} on topic {output_topic_cam_2}")
            flag = 1

        if flag == 0:
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

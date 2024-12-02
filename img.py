import cv2
import numpy as np
import tensorflow as tf

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
        return True
    else:
        return False

# Path to the image
image_path = "received_image.jpg"  # Replace with the path to your image

# Detect fire in the image
fire_detected = detect_fire(image_path)

if fire_detected:
    print("Warning: Fire detected!")
    # Optionally, save the image with a fire warning annotation
    frame = cv2.imread(image_path)
    height, width, _ = frame.shape
    cv2.rectangle(frame, (50, 50), (width - 50, height - 50), (0, 0, 255), 2)
    cv2.putText(frame, "Warning: Fire detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.imwrite("fire_detected_image.jpg", frame)  # Save the annotated image
    print("Annotated image saved as fire_detected_image.jpg")
else:
    print("No fire detected.")
from flask import Flask, Response, request
from flask_cors import CORS
import threading
import time
import cv2
import tensorflow as tf
import mediapipe as mp
import pyttsx3

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from the frontend

# Initialize the detection thread
detection_thread = None
detection_running = False

# Initialize pyttsx3 for text-to-speech with a female voice
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Index 1 is typically a female voice, adjust if needed

# Load the model
model_path = "exported_model/gesture_recognizer.task"

# Initialize Mediapipe Gesture Recognizer
BaseOptions = mp.tasks.BaseOptions
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
Image = mp.Image
ImageFormat = mp.ImageFormat

# Correctly initialize the base options and recognizer options
base_options = BaseOptions(model_asset_path=model_path)
options = GestureRecognizerOptions(base_options=base_options)
recognizer = GestureRecognizer.create_from_options(options)

# List to store detected gestures
detected_gestures = []
current_label = None
label_start_time = None

def detect_gestures():
    global detection_running, detected_gestures, current_label, label_start_time
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        detection_running = False
        return

    while detection_running:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Convert the image from BGR to RGB as mediapipe uses RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the RGB frame to a Mediapipe Image object
        mp_image = mp.Image(image_format=ImageFormat.SRGB, data=rgb_frame)

        # Perform gesture recognition
        recognition_result = recognizer.recognize(mp_image)

        # Initialize gesture_label and score
        gesture_label = ""
        score = 0.0

        # Check if any gestures are detected
        if recognition_result.gestures and recognition_result.gestures[0]:
            gesture = recognition_result.gestures[0][0]
            gesture_label = gesture.category_name
            score = gesture.score
            print(f"Detected gesture: {gesture_label} with confidence {score:.2f}")

            # Check if the label has changed or has been held for more than 3 seconds
            current_time = time.time()
            if current_label != gesture_label:
                current_label = gesture_label
                label_start_time = current_time
            elif current_time - label_start_time >= 3:
                detected_gestures.append(gesture_label)
                current_label = None  # Reset current label to allow detecting the next sign

        # Display the label on the video frame
        cv2.putText(frame, f"{gesture_label} ({score:.2f})", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Display the list of detected gestures on the frame
        y0, dy = 30, 30
        for i, sign in enumerate(detected_gestures):
            y = y0 + i * dy
            cv2.putText(frame, sign, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Display the resulting frame
        cv2.imshow('Gesture Recognition', frame)

        # Check for key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            detection_running = False
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/start', methods=['POST'])
def start_detection():
    global detection_thread, detection_running
    if not detection_running:
        detection_running = True
        detection_thread = threading.Thread(target=detect_gestures)
        detection_thread.start()
        return {"status": "Detection started"}, 200
    else:
        return {"status": "Detection already running"}, 400

@app.route('/stop', methods=['POST'])
def stop_detection():
    global detection_running
    if detection_running:
        detection_running = False
        if detection_thread is not None:
            detection_thread.join()
        return {"status": "Detection stopped"}, 200
    else:
        return {"status": "Detection not running"}, 400

@app.route('/gestures', methods=['GET'])
def get_gestures():
    global detected_gestures
    return {"gestures": detected_gestures}, 200

@app.route('/speak', methods=['POST'])
def speak_gestures():
    global detected_gestures
    print(f"Speaking: {detected_gestures}")
    
    # Join all the words into a single sentence
    sentence = ' '.join(detected_gestures)

    # Speak each word with a small pause between them
    for word in detected_gestures:
        engine.say(word)
        engine.startLoop(False)
        engine.iterate()
        time.sleep(0.3)  # Add a small pause between words
        engine.endLoop()
    
    # Clear the list after speaking
    detected_gestures = []
    
    return {"status": "Spoken"}, 200


if __name__ == '__main__':
    app.run(debug=True)

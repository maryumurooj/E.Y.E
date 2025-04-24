import cv2
import tensorflow as tf
import mediapipe as mp
import pyttsx3
import time

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

# Open the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# List to store detected gestures
detected_gestures = []
current_label = None
label_start_time = None

while True:
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
        break
    elif key == ord('s'):
        # Concatenate the detected gestures into a sentence
        sentence = ' '.join(detected_gestures)
        print(f"Speaking: {sentence}")
        # Use pyttsx3 to speak the sentence with pauses
        words = sentence.split()
        for word in words:
            engine.say(word)
            engine.runAndWait()
            time.sleep(0.05)  # Add a 0.05-second pause between words
        # Clear the list after speaking
        detected_gestures = []

# When everything is done, release the capture and close any open windows
cap.release()
cv2.destroyAllWindows()

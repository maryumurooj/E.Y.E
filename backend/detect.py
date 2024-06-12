import cv2
import tensorflow as tf
import mediapipe as mp
import pyttsx3
# Initialize pyttsx3 for text-to-speech with a female voice
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Index 1 is typically a female voice, adjust if needed
# Dictionary to track last spoken times for each label
last_spoken_time = {label: 0 for label in class_labels.values()}
label_duration = 5  # Duration in seconds for each label


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

        # Display the label on the video frame
        cv2.putText(frame, f"{gesture_label} ({score:.2f})", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Display the resulting frame
    cv2.imshow('Gesture Recognition', frame)

    # Break the loop if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture and close any open windows
cap.release()
cv2.destroyAllWindows()

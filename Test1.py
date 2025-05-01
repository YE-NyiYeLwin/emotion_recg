import cv2
import numpy as np
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from keras.optimizers import Adam

# Load the pre-trained model for emotion recognition
model = load_model("fer2013_mini_XCEPTION.102-0.66.hdf5", compile=False)

# Recompile the model with a new optimizer (if necessary)
model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

# Define emotion categories
emotion_labels = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

# Initialize webcam
cap = cv2.VideoCapture(0)


# Function to preprocess the face image
def preprocess_face(face):
    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    face = cv2.resize(face, (64, 64))
    face = face.astype("float32") / 255.0
    face = img_to_array(face)
    face = np.expand_dims(face, axis=0)
    return face


while True:
    # Read frame from webcam
    ret, frame = cap.read()

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Load OpenCV's pre-trained face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    # Loop through detected faces
    for x, y, w, h in faces:
        # Extract the face from the frame
        face = frame[y : y + h, x : x + w]

        # Preprocess the face
        face_preprocessed = preprocess_face(face)

        # Predict emotion
        emotion_prediction = model.predict(face_preprocessed)
        max_index = np.argmax(emotion_prediction[0])
        emotion_label = emotion_labels[max_index]

        # Draw rectangle around the face and label the emotion
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            frame,
            emotion_label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2,
        )

    # Display the frame
    cv2.imshow("Emotion Recognition", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()

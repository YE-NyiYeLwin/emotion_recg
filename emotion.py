import cv2
from fer import FER
import matplotlib.pyplot as plt
import requests

# url = "https://api.ai21.com/studio/v1/j2-ultra/chat"

# payload = {
#     "numResults": 1,
#     "temperature": 0.7,
#     "messages": [
#         {
#             "text": "I chose to take the safe route instead of the risky one. Emotion: Neutral I ignored a quest to help an NPC. Emotion: Sad I collected coins instead of power-ups. Emotion: Happy I prioritized speedrunning over exploring the map. Emotion: Angry I engaged in combat with enemies. Emotion: Fear I spent resources freely rather than saving them. Emotion: Happy I customized my character for appearance over functionality. Emotion: Happy I solved puzzles using trial and error rather than strategy. Emotion: Surprised I made morally questionable decisions. Emotion: Neutral I avoided risky jumps in favor of safe ones. Emotion: Neutral Based on these choices and emotions, can you generate a personality report that describes my key personality traits? Write it as an essay report, rather than bullet points. Just describe my personality. Do not include the actions I did that reflect my personality trait, only mention the personality traits. Do not mention the actions.",
#             "role": "user",
#         }
#     ],
#     "system": "You are an AI assistant for generating personality assessment reports. Your responses should be informative and concise.",
# }
# headers = {
#     "accept": "application/json",
#     "content-type": "application/json",
#     "Authorization": "Bearer DDRPPVJWLRaDm9U3pXP6crGjivmIOVly",
# }

# response = requests.post(url, json=payload, headers=headers)

# print(response.text)


def capture_and_detect_emotion():
    # Initialize webcam
    cap = cv2.VideoCapture(0)

    # Initialize emotion detector
    emotion_detector = FER(mtcnn=True)

    print("Press 'c' to capture an image and detect emotion, or 'q' to quit.")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Display the frame
        cv2.imshow("Webcam", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("c"):
            # Detect emotions in the captured frame
            result = emotion_detector.detect_emotions(frame)
            if result:
                # Get the dominant emotion
                dominant_emotion = max(
                    result[0]["emotions"], key=result[0]["emotions"].get
                )
                print(f"Detected emotion: {dominant_emotion}")

                # Display the image with detected emotion
                plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                plt.title(f"Detected Emotion: {dominant_emotion}")
                plt.axis("off")
                plt.show()
            else:
                print("No face detected in the image.")
        elif key == ord("q"):
            break

    # Release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    capture_and_detect_emotion()

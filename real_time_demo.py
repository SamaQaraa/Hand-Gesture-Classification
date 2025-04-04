import cv2
import mediapipe as mp
import numpy as np
import joblib  # For loading the trained SVM model

# Load the trained SVM model
svm_model = joblib.load("svm_winner.pkl")

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Start video capture
cap = cv2.VideoCapture(0)

# Get frame width and height
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Define codec and create VideoWriter object to save the video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
out = cv2.VideoWriter("output.mp4", fourcc, 30, (frame_width, frame_height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a mirrored effect
    frame = cv2.flip(frame, 1)

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Extract (x, y, z) coordinates
            landmarks = np.array([(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark])

            # Normalize: Recenter based on wrist position (landmark 0)
            wrist_x, wrist_y, wrist_z = landmarks[0]
            landmarks[:, 0] -= wrist_x  
            landmarks[:, 1] -= wrist_y  

            # Scale only x and y using the mid-finger tip (landmark 12)
            mid_finger_x, mid_finger_y, _ = landmarks[12] 
            scale_factor = np.sqrt(mid_finger_x**2 + mid_finger_y**2)
            landmarks[:, 0] /= scale_factor  
            landmarks[:, 1] /= scale_factor  

            # Flatten the features for SVM
            features = landmarks.flatten().reshape(1, -1)

            # Predict using SVM
            prediction = svm_model.predict(features)[0]

            # Draw landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Display the prediction on the frame
            cv2.putText(frame, f'Prediction: {prediction}', (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # Write the flipped frame to the video file
    out.write(frame)

    # Show the flipped frame
    cv2.imshow("Hand Gesture Recognition", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
out.release()  # Ensure video is saved properly
cv2.destroyAllWindows()

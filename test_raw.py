import cv2
import mediapipe as mp
import math

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

print("Starting Camera... Press 'q' to exit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the image horizontally for a mirror effect
    frame = cv2.flip(frame, 1)
    # Convert BGR image to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        # Get coordinates for Ears and Shoulders
        landmarks = results.pose_landmarks.landmark
        
        # Landmark indices: Left Shoulder (11), Right Shoulder (12), Left Ear (7), Right Ear (8)
        l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y
        r_sh = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
        l_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR].y
        r_ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR].y

        # Calculate averages for stability
        avg_sh = (l_sh + r_sh) / 2
        avg_ear = (l_ear + r_ear) / 2

        # Posture Logic: Vertical distance between ears and shoulders
        # Normalized coordinates range from 0 (top) to 1 (bottom)
        distance = avg_sh - avg_ear

        status = "GOOD POSTURE"
        color = (0, 255, 0) # Green

        # If the distance is too small, the head is dropping (slouching)
        if distance < 0.12: # Threshold based on typical laptop distance
            status = "SLOUCHING DETECTED!"
            color = (0, 0, 255) # Red

        # Draw visual cues on the frame
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        cv2.putText(frame, status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow('EyeCare Raw Engine', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
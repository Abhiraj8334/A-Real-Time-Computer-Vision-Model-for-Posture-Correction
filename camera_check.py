import cv2
import sys

print("--- SYSTEM CHECK ---")
print(f"Python Version: {sys.version}")
print("Checking for camera...")

# CAP_DSHOW is for Windows. It helps bypass slow camera initialization.
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Could not open camera at Index 0. Trying Index 1...")
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if cap.isOpened():
    print("SUCCESS: Camera is now active!")
    print("Press any key on your keyboard to close the window.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
            
        cv2.imshow("Check", frame)
        
        # This keeps the window open until you press a key
        if cv2.waitKey(1) != -1:
            break
else:
    print("FATAL ERROR: No camera found on this device.")

cap.release()
cv2.destroyAllWindows()
print("--- TEST ENDED ---")
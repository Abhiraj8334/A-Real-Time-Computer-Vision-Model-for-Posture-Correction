import sys
import os

import sys
import os

# Fix working directory for PyInstaller executable
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    os.chdir(os.path.dirname(sys.executable))

# Imports
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk, ImageDraw, ImageFont
from urllib.request import urlopen
import io
import mediapipe as mp
import traceback
import winsound
import time
import ctypes  # For bringing window to foreground

# Initialize AI Brain
try:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    
    # Add face mesh for eye detection
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
except Exception as e:
    print(f"Error initializing MediaPipe: {e}")
    traceback.print_exc()
    pose = None
    face_mesh = None
    mp_drawing = None
    mp_drawing_styles = None

class PostureCorrectionApp(ctk.CTk):
    # single __init__ defined below
    def __init__(self):
        super().__init__()
        self.title("Posture Correction System")
        self.geometry("1200x800")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#0a0a0a")
        
        # Bring window to foreground
        try:
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            ctypes.windll.user32.ShowWindow(hwnd, 0)  # Hide console
        except:
            pass
        
        self.attributes('-topmost', True)  # Make window always on top
        self.after_idle(self.attributes, '-topmost', False)
        
        # Create main container with 2 columns
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # === SIDEBAR (LEFT COLUMN) ===
        self.sidebar = ctk.CTkFrame(self, fg_color="#1a1a1a", width=250)
        self.sidebar.grid(row=0, column=0, sticky="nswe", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        
        # Sidebar title
        title = ctk.CTkLabel(self.sidebar, text="POSTURE\nCORRECTION", font=("Arial", 22, "bold"), 
                    text_color="#00D4FF", justify="center")
        title.pack(pady=30, padx=20)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(self.sidebar, text="STATUS:\nIDLE", text_color="white", 
                                        font=("Arial", 11, "bold"), justify="center")
        self.status_label.pack(pady=20, padx=15, fill="x")
        
        # Start/Stop button
        self.start_btn = ctk.CTkButton(self.sidebar, text="START MONITOR", command=self.toggle_monitor, 
                                       height=50, font=("Arial", 12, "bold"), fg_color="#3B8ED0",
                                       text_color="white")
        self.start_btn.pack(pady=15, padx=15, fill="x")

        # Posture guidance text
        self.posture_text = ctk.CTkLabel(self.sidebar, text="Good posture:\n- Sit upright\n- Keep shoulders relaxed\n- Keep head centered", font=("Arial", 11), justify="left")
        self.posture_text.pack(pady=10, padx=10, fill="x")

        self.distance_text = ctk.CTkLabel(self.sidebar, text="Recommended distance:\n- Keep monitor 50-70 cm away\n- Top of screen at eye level", font=("Arial", 11), justify="left")
        self.distance_text.pack(pady=10, padx=10, fill="x")
        
        # === MAIN CONTENT (RIGHT COLUMN) ===
        self.main_frame = ctk.CTkFrame(self, fg_color="#0a0a0a")
        self.main_frame.grid(row=0, column=1, sticky="nswe", padx=0, pady=0)
        self.main_frame.grid_propagate(True)
        
        # Video display label
        self.video_label = ctk.CTkLabel(self.main_frame, text="", fg_color="#0a0a0a", text_color="white")
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Show initial instruction text
        self.show_instruction_text()
        
        # Camera and state
        self.cap = None
        self.is_monitoring = False
        self.last_alert_time = 0  # Track last alert time to avoid spamming

    def calculate_eye_closure_ratio(self, face_landmarks):
        """Calculate eye closure ratio (0 = open, 1 = closed)"""
        # Eye landmarks indices for left and right eyes
        # Left eye: 33, 160, 158, 133, 153, 144
        # Right eye: 263, 387, 386, 362, 382, 381
        
        left_eye_points = [33, 160, 158, 133, 153, 144]
        right_eye_points = [263, 387, 386, 362, 382, 381]
        
        def calculate_distance(p1, p2):
            return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**0.5
        
        def eye_aspect_ratio(eye_indices):
            # Get the eye landmarks
            landmarks = [face_landmarks[i] for i in eye_indices]
            
            # Vertical distances
            vertical_1 = calculate_distance(landmarks[1], landmarks[5])
            vertical_2 = calculate_distance(landmarks[2], landmarks[4])
            
            # Horizontal distance
            horizontal = calculate_distance(landmarks[0], landmarks[3])
            
            # Eye aspect ratio
            if horizontal > 0:
                ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
            else:
                ear = 0
            
            return ear
        
        left_ear = eye_aspect_ratio(left_eye_points)
        right_ear = eye_aspect_ratio(right_eye_points)
        avg_ear = (left_ear + right_ear) / 2.0
        
        return avg_ear

    def show_instruction_text(self):
        """Display instruction text in the main area"""
        # Create a dark image
        img = Image.new('RGB', (900, 600), color=(10, 10, 10))
        draw = ImageDraw.Draw(img)
        
        # Draw text
        text = "POSTURE CORRECTION SYSTEM\n\nPress START MONITOR\nto begin posture detection"
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # Center text
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (img.width - text_width) // 2
        text_y = (img.height - text_height) // 2
        
        draw.text((text_x, text_y), text, fill=(0, 212, 255), font=font)
        
        # Convert to PhotoImage and display
        self.instr_photo_image = ImageTk.PhotoImage(img)
        self.video_label.configure(image=self.instr_photo_image, text="")

    def toggle_monitor(self):
        if not self.is_monitoring:
            # Open camera with Windows-specific settings
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if self.cap.isOpened():
                self.is_monitoring = True
                self.start_btn.configure(text="STOP MONITOR", fg_color="#E74C3C")
                self.status_label.configure(text="STATUS:\nMONITORING")
                self.update_frame()
            else:
                self.video_label.configure(text="❌ CAMERA ERROR", text_color="#E74C3C")
        else:
            self.is_monitoring = False
            if self.cap: 
                self.cap.release()
            self.start_btn.configure(text="START MONITOR", fg_color="#3B8ED0")
            self.status_label.configure(text="STATUS:\nIDLE", text_color="white")
            self.show_instruction_text()

    def update_frame(self):
        if self.is_monitoring and pose and mp_drawing:
            ret, frame = self.cap.read()
            if ret:
                try:
                    frame = cv2.flip(frame, 1)  # Mirror effect
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # AI Logic - Pose Detection
                    results = pose.process(rgb_frame)
                    
                    # Eye closure detection
                    eyes_closed = False
                    if face_mesh:
                        face_results = face_mesh.process(rgb_frame)
                        if face_results.multi_face_landmarks:
                            face_landmarks = face_results.multi_face_landmarks[0].landmark
                            eye_closure_ratio = self.calculate_eye_closure_ratio(face_landmarks)
                            print(f"Eye Closure Ratio: {eye_closure_ratio:.3f}")
                            
                            # If eye closure ratio < 0.15, eyes are closed
                            if eye_closure_ratio < 0.15:
                                eyes_closed = True
                    
                    if results.pose_landmarks:
                        # Draw skeleton on frame
                        mp_drawing.draw_landmarks(
                            rgb_frame,
                            results.pose_landmarks,
                            mp_pose.POSE_CONNECTIONS,
                            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                        )
                        # Posture Detection - Slouching and Forward Head Detection
                        landmarks = results.pose_landmarks.landmark
                        # Landmark indices: Left Ear (7), Right Ear (8), Left Shoulder (11), Right Shoulder (12), Nose (0)
                        left_ear = landmarks[7]
                        right_ear = landmarks[8]
                        left_shoulder = landmarks[11]
                        right_shoulder = landmarks[12]
                        nose = landmarks[0]
                        
                        # Calculate average positions
                        avg_ear_y = (left_ear.y + right_ear.y) / 2
                        avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
                        avg_shoulder_x = (left_shoulder.x + right_shoulder.x) / 2
                        
                        # Vertical distance between shoulder and ear (positive = ear below shoulder = good)
                        vertical_distance = avg_shoulder_y - avg_ear_y
                        
                        # Horizontal distance: how far head is forward from shoulder
                        horizontal_distance = abs(nose.x - avg_shoulder_x)
                        
                        # Debug output
                        print(f"Vertical: {vertical_distance:.3f}, Horizontal: {horizontal_distance:.3f}, Eyes Closed: {eyes_closed}")
                        
                        # Detection logic: 
                        # Slouching: vertical distance < 0.15 (head too close to shoulder)
                        # Forward Head: horizontal distance > 0.15 (head too far forward)
                        is_slouching = (vertical_distance < 0.15) or (horizontal_distance > 0.15)
                        
                        # Alert based on priority: Eyes Closed > Slouching > Good
                        if eyes_closed:
                            self.status_label.configure(text="STATUS:\nEYES CLOSED!", text_color="#FF00FF")
                            # Play alert sound (only every 2 seconds)
                            current_time = time.time()
                            if current_time - self.last_alert_time > 2:
                                winsound.Beep(1500, 500)  # Higher pitch, longer duration
                                self.last_alert_time = current_time
                        elif is_slouching:
                            self.status_label.configure(text="STATUS:\nSLOUCHING ⚠", text_color="#E74C3C")
                            # Play alert sound (only every 2 seconds to avoid spam)
                            current_time = time.time()
                            if current_time - self.last_alert_time > 2:
                                winsound.Beep(1000, 300)  # 1000 Hz, 300ms duration
                                self.last_alert_time = current_time
                        else:
                            self.status_label.configure(text="STATUS:\nGOOD ✓", text_color="#2ECC71")
                    
                    # Convert and display frame
                    img = Image.fromarray(rgb_frame)
                    photo = ImageTk.PhotoImage(img)
                    self.video_label.configure(image=photo, text="")
                    self.video_label.photo = photo  # Keep a reference
                    
                except Exception as e:
                    print(f"Error processing frame: {e}")
                    traceback.print_exc()
            
            # Schedule next frame update (30ms = ~33 fps)
            if self.is_monitoring:
                self.after(30, self.update_frame)

if __name__ == "__main__":
    app = PostureCorrectionApp()
    app.mainloop()
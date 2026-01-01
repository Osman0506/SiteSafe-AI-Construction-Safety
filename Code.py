import cv2
import threading
import time
import os
import datetime
import numpy as np
from ultralytics import YOLO

# --- CONFIGURATION ---
MODEL_PATH = 'best.pt'  # Will load your new brain here later
CONF_THRESHOLD = 0.40   # Sensitivity
PERSISTENCE_THRESHOLD = 5 # Frames to wait before triggering alarm (Anti-Flicker)

# PRO COLOR PALETTE
C_BG = (15, 15, 15)        # Deep Black-Gray
C_PANEL = (40, 40, 40)     # Sidebar
C_SAFE = (0, 255, 128)     # Spring Green
C_DANGER = (0, 50, 255)    # Alert Red
C_TEXT_MAIN = (255, 255, 255)
C_TEXT_DIM = (150, 150, 150)

# Class Mapping (Update these if your new model changes names!)
UNSAFE_CLASSES = ['No-Helmet', 'No-Vest', 'no_helmet', 'no_vest', 'head', 'person']
SAFE_CLASSES = ['Helmet', 'Vest', 'Hardhat', 'helmet', 'vest']

# Global State
last_beep_time = 0
BEEP_COOLDOWN = 3.0
event_log = []
violation_counter = 0 # Tracks how many frames a violation has persisted

# --- AUDIO SYSTEM (Non-Blocking) ---
def play_alarm():
    def run():
        # Mac system sound (Sosumi is distinct and sharp)
        os.system('afplay /System/Library/Sounds/Sosumi.aiff')
    t = threading.Thread(target=run)
    t.start()

# --- GRAPHICS ENGINE ---
def draw_tech_bracket(img, x1, y1, x2, y2, color, label, conf):
    # 1. Draw "Bracket" Corners (The Sci-Fi Look)
    line_len = min(int((x2-x1)*0.2), int((y2-y1)*0.2))
    t = 2 # Thickness
    
    # Top Left
    cv2.line(img, (x1, y1), (x1 + line_len, y1), color, t)
    cv2.line(img, (x1, y1), (x1, y1 + line_len), color, t)
    # Top Right
    cv2.line(img, (x2, y1), (x2 - line_len, y1), color, t)
    cv2.line(img, (x2, y1), (x2, y1 + line_len), color, t)
    # Bottom Left
    cv2.line(img, (x1, y2), (x1 + line_len, y2), color, t)
    cv2.line(img, (x1, y2), (x1, y2 - line_len), color, t)
    # Bottom Right
    cv2.line(img, (x2, y2), (x2 - line_len, y2), color, t)
    cv2.line(img, (x2, y2), (x2, y2 - line_len), color, t)

    # 2. Confidence Bar (Mini "Health Bar" above box)
    bar_width = int((x2 - x1) * conf)
    cv2.rectangle(img, (x1, y1 - 10), (x1 + bar_width, y1 - 8), color, -1)

    # 3. Label with Background
    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.rectangle(img, (x1, y1 - 30), (x1 + w + 10, y1 - 12), color, -1)
    cv2.putText(img, label, (x1 + 5, y1 - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)

def draw_sidebar(dashboard, h, w, sidebar_w, status, color_overall, fps):
    sb_x = w 
    
    # Background
    cv2.rectangle(dashboard, (sb_x, 0), (sb_x + sidebar_w, h), C_BG, -1)
    
    # Header
    cv2.rectangle(dashboard, (sb_x, 0), (sb_x + sidebar_w, 80), C_PANEL, -1)
    cv2.putText(dashboard, "SITESAFE", (sb_x + 20, 45), cv2.FONT_HERSHEY_TRIPLEX, 1.0, C_TEXT_MAIN, 1, cv2.LINE_AA)
    cv2.putText(dashboard, "ENTERPRISE v3.0", (sb_x + 20, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.4, C_TEXT_DIM, 1, cv2.LINE_AA)
    
    # FPS Counter (Tech Flex)
    cv2.putText(dashboard, f"FPS: {int(fps)}", (sb_x + sidebar_w - 80, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_SAFE, 1)

    # Status Block
    cv2.rectangle(dashboard, (sb_x + 20, 100), (sb_x + sidebar_w - 20, 180), color_overall, -1)
    cv2.putText(dashboard, "SYSTEM STATUS", (sb_x + 30, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1, cv2.LINE_AA)
    cv2.putText(dashboard, status, (sb_x + 28, 160), cv2.FONT_HERSHEY_TRIPLEX, 1.1, (0,0,0), 2, cv2.LINE_AA)

    # Event Log
    cv2.putText(dashboard, "LIVE EVENT LOG", (sb_x + 20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_TEXT_MAIN, 1, cv2.LINE_AA)
    cv2.line(dashboard, (sb_x + 20, 230), (sb_x + sidebar_w - 20, 230), C_PANEL, 2)

    y_log = 260
    for log_entry in reversed(event_log):
        # Dim old logs
        color = C_DANGER if "VIOLATION" in log_entry else C_TEXT_DIM
        cv2.putText(dashboard, log_entry, (sb_x + 20, y_log), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
        y_log += 25

# --- MAIN APP ---
def main():
    global last_beep_time, event_log, violation_counter

    # 1. Boot Sequence (Fake Loading Screen)
    print("Initializing SiteSafe v3.0...")
    time.sleep(1) # Dramatic pause

    # Load Model
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ WARNING: '{MODEL_PATH}' not found. Using standard YOLO for UI demo.")
        model = YOLO('yolov8n.pt') # Fallback so code runs
    else:
        model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    
    SIDEBAR_WIDTH = 320
    prev_frame_time = 0
    new_frame_time = 0

    while True:
        success, frame = cap.read()
        if not success: break
            
        # Resize for dashboard fit
        frame = cv2.resize(frame, (960, 720))
        h, w, _ = frame.shape
        
        # Calculate FPS
        new_frame_time = time.time()
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time

        # Canvas Setup
        dashboard = np.zeros((h, w + SIDEBAR_WIDTH, 3), dtype=np.uint8)
        
        # Inference
        results = model(frame, stream=True, verbose=False)
        
        any_unsafe = False
        frame_detections = []

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_name = model.names[int(box.cls[0])]
                conf = float(box.conf[0])
                
                if conf < CONF_THRESHOLD: continue

                # Logic Check
                is_unsafe = cls_name in UNSAFE_CLASSES
                
                if is_unsafe:
                    any_unsafe = True
                    color = C_DANGER
                    label = f"{cls_name} {int(conf*100)}%"
                    frame_detections.append(f"VIOLATION: {cls_name}")
                else:
                    color = C_SAFE
                    label = f"{cls_name} {int(conf*100)}%"

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                draw_tech_bracket(frame, x1, y1, x2, y2, color, label, conf)

        # --- STABILITY LOGIC (The "Anti-Flicker") ---
        status_text = "SECURE"
        status_color = C_SAFE

        if any_unsafe:
            violation_counter += 1
        else:
            violation_counter = 0

        # Only trigger alarm if violation persists for X frames
        if violation_counter > PERSISTENCE_THRESHOLD:
            status_text = "BREACH"
            status_color = C_DANGER
            
            # Update Log (Debounced)
            curr_time = datetime.datetime.now().strftime("%H:%M:%S")
            log_msg = f"[{curr_time}] {frame_detections[0]}"
            if len(event_log) == 0 or log_msg != event_log[-1]:
                event_log.append(log_msg)
                if len(event_log) > 10: event_log.pop(0)

            # Audio Alarm
            if time.time() - last_beep_time > BEEP_COOLDOWN:
                play_alarm()
                last_beep_time = time.time()

        # Combine Video + Sidebar
        dashboard[0:h, 0:w] = frame
        draw_sidebar(dashboard, h, w, SIDEBAR_WIDTH, status_text, status_color, fps)

        cv2.imshow('SiteSafe v3.0 Enterprise', dashboard)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
import cv2
import time
import math as m
import mediapipe as mp
import argparse
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def findDistance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points."""
    return m.sqrt((x2 - x1)*2 + (y2 - y1)*2)

def findAngle(x1, y1, x2, y2, x3, y3):
    """Calculate angle between three points (in degrees)."""
    # Calculate vectors
    v1 = (x1 - x2, y1 - y2)
    v2 = (x3 - x2, y3 - y2)
    
    # Calculate dot product and magnitudes
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    mag_v1 = m.sqrt(v1[0]*2 + v1[1]*2)
    mag_v2 = m.sqrt(v2[0]*2 + v2[1]*2)
    
    # Calculate angle in radians and convert to degrees
    angle_rad = m.acos(dot_product / (mag_v1 * mag_v2))
    angle_deg = m.degrees(angle_rad)
    
    return angle_deg
#code tht perfetctly checks aloignment

def sendWarning(message):
    """Send a voice warning."""
    print("ALERT:", message)
    try:
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        print("Voice alert failed:", e)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Front View Posture Monitor with MediaPipe')
    parser.add_argument('--video', type=str, default=0, help='Path to input video file (default: webcam)')
    parser.add_argument('--shoulder-threshold', type=int, default=30, help='Threshold for shoulder alignment (pixels)')
    parser.add_argument('--ear-shoulder-threshold', type=int, default=20, help='Threshold for ear-shoulder alignment (pixels)')
    parser.add_argument('--time-threshold', type=int, default=30, help='Time threshold for alerts (seconds)')
    parser.add_argument('--alert-cooldown', type=int, default=60, help='Minimum time between alerts (seconds)')
    return parser.parse_args()


def main():
    args = parse_arguments()
    sendWarning("Voice engine test: posture monitor is starting.")
    
    # Initialize frame counters and timers
    good_frames = 0
    bad_frames = 0
    last_alert_time = 0
    
    # Font and colors
    font = cv2.FONT_HERSHEY_SIMPLEX
    green = (0, 255, 0)
    red = (0, 0, 255)
    blue = (255, 0, 0)
    white = (255, 255, 255)
    yellow = (0, 255, 255)
    
    # Initialize MediaPipe Pose
    pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    
    # Initialize video capture
    cap = cv2.VideoCapture(args.video if args.video != '0' else 0)
    if not cap.isOpened():
        print("Error: Could not open video source")
        return
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps is None or m.isnan(fps):
        fps = 30  # fallback

    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
        
        # Get frame dimensions
        h, w = image.shape[:2]
        
        # Convert to RGB and process
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        
        if results.pose_landmarks:
            # Get landmarks
            landmarks = results.pose_landmarks.landmark
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # Get key points (convert normalized coordinates to pixel values)
            left_ear = (int(landmarks[mp_pose.PoseLandmark.LEFT_EAR].x * w), 
                        int(landmarks[mp_pose.PoseLandmark.LEFT_EAR].y * h))
            right_ear = (int(landmarks[mp_pose.PoseLandmark.RIGHT_EAR].x * w), 
                         int(landmarks[mp_pose.PoseLandmark.RIGHT_EAR].y * h))
            left_shoulder = (int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * w), 
                             int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * h))
            right_shoulder = (int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w), 
                              int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h))
            nose = (int(landmarks[mp_pose.PoseLandmark.NOSE].x * w), 
                    int(landmarks[mp_pose.PoseLandmark.NOSE].y * h))
            
            # Calculate mid points
            mid_ear = ((left_ear[0] + right_ear[0]) // 2, (left_ear[1] + right_ear[1]) // 2)
            mid_shoulder = ((left_shoulder[0] + right_shoulder[0]) // 2, 
                            (left_shoulder[1] + right_shoulder[1]) // 2)
            
            # Calculate metrics
            # 1. Shoulder alignment (vertical difference)
            shoulder_diff = abs(left_shoulder[1] - right_shoulder[1])
            
            # 2. Head forward posture (horizontal difference between ear and shoulder)
            ear_shoulder_diff = mid_ear[0] - mid_shoulder[0]
            
            # 3. Head tilt (difference between ear heights)
            head_tilt = abs(left_ear[1] - right_ear[1])
            
            # Draw reference lines and points
            cv2.line(image, (0, mid_shoulder[1]), (w, mid_shoulder[1]), blue, 1)  # Shoulder line
            cv2.line(image, (mid_ear[0], 0), (mid_ear[0], h), blue, 1)  # Ear vertical line
            cv2.circle(image, left_shoulder, 8, yellow, -1)
            cv2.circle(image, right_shoulder, 8, yellow, -1)
            cv2.circle(image, mid_ear, 8, white, -1)
            
            # Check posture conditions
            posture_good = True
            messages = []
            
            # Shoulder alignment check
            if shoulder_diff > args.shoulder_threshold:
                posture_good = False
                messages.append(f"Uneven shoulders ({shoulder_diff}px)")
                cv2.putText(image, f"Shoulders uneven: {shoulder_diff}px", (10, 30), font, 0.7, red, 2)
                cv2.line(image, left_shoulder, right_shoulder, red, 2)
            else:
                cv2.putText(image, f"Shoulders aligned: {shoulder_diff}px", (10, 30), font, 0.7, green, 2)
                cv2.line(image, left_shoulder, right_shoulder, green, 2)
            
            # Forward head posture check
            if ear_shoulder_diff > args.ear_shoulder_threshold:
                posture_good = False
                messages.append(f"Forward head posture ({ear_shoulder_diff}px)")
                cv2.putText(image, f"Head forward: {ear_shoulder_diff}px", (10, 60), font, 0.7, red, 2)
                cv2.line(image, mid_ear, (mid_shoulder[0], mid_ear[1]), red, 2)
            else:
                cv2.putText(image, f"Head aligned: {ear_shoulder_diff}px", (10, 60), font, 0.7, green, 2)
                cv2.line(image, mid_ear, (mid_shoulder[0], mid_ear[1]), green, 2)
            
            # Head tilt check
            if head_tilt > 20:  # 20px threshold for head tilt
                posture_good = False
                messages.append(f"Head tilted ({head_tilt}px)")
                cv2.putText(image, f"Head tilt: {head_tilt}px", (10, 90), font, 0.7, red, 2)
                cv2.line(image, left_ear, right_ear, red, 2)
            else:
                cv2.line(image, left_ear, right_ear, green, 2)
            
            # Update frame counters

            if posture_good:
                good_frames += 1
                bad_frames = 0
            else:
                bad_frames += 1
                good_frames = 0
            
            # Calculate time in current posture
            bad_time = bad_frames / fps if fps else 0
            good_time = good_frames / fps if fps else 0
            
            
            # Display time information
            if posture_good:
                cv2.putText(image, f"Good posture: {good_time:.1f}s", (10, h-20), font, 0.7, green, 2)
            else:
                cv2.putText(image, f"Bad posture: {bad_time:.1f}s", (10, h-20), font, 0.7, red, 2)
            
            # Send voice alert if needed
            current_time = time.time()
            if bad_time > args.time_threshold and messages and (current_time - last_alert_time > args.alert_cooldown):
                print("Triggering voice alert NOW!")
                natural_message = "Hey, "
                if "Uneven shoulders" in ", ".join(messages):
                    natural_message += "your shoulders seem uneven"
                if "Forward head posture" in ", ".join(messages):
                    if "Uneven shoulders" in ", ".join(messages):
                        natural_message += " and your head is leaning forward"
                    else:
                        natural_message += "your head is leaning forward"
                if "Head tilted" in ", ".join(messages):
                    if "Uneven shoulders" in ", ".join(messages) or "Forward head posture" in ", ".join(messages):
                        natural_message += " and your head seems tilted"
                    else:
                        natural_message += "your head seems tilted"
                natural_message += ". Please adjust your posture."
                sendWarning(natural_message)

                last_alert_time = current_time

        
        # Display image
        cv2.imshow('Front View Posture Analysis', image)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
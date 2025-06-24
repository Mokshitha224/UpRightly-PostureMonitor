This is a fork of https://github.com/alxkh18/UpRightly-PostureMonitor. Original project by Mokshitha and Alekhya.
I contributed to design, coding, and documentation.

# 🧍‍♂️ UpRightly – Front View Posture Analysis using MediaPipe

This project is a real-time posture monitoring tool using MediaPipe Pose, OpenCV, and pyttsx3 for voice alerts. Unlike most posture monitoring systems that rely on side-view cameras to analyze spine alignment, this tool works with a front-facing webcam, making it easier and more accessible for everyday use — especially on laptops.

---

## 📸 Features
📸 Front-view webcam posture analysis

🧠 Uses MediaPipe Pose to track body landmarks

## 🧠 How It Works (Front View Advantage)
Traditional posture monitoring systems rely on side-view cameras to track spine curvature, which often requires careful positioning and more physical space.

This project takes a front-facing approach, making it easier to deploy with webcams or laptop cameras. Instead of directly analyzing the spine, it uses three key visual cues from the front to assess posture quality in real-time:

🧍‍♂️ Shoulder Alignment:
Tracks the vertical difference between shoulders. If one is higher than the other, it indicates slouching or leaning sideways. A significant difference triggers a posture alert.

🧍‍♂️ Forward Head Posture:
Measures the horizontal distance between ear and shoulder midpoints. A large offset suggests the head is too far forward, signaling poor posture.

🧍‍♂️ Head Tilt:
Compares ear heights. A noticeable height difference signals a head tilt, indicating fatigue or poor ergonomics.

🔔 Voice Alerts:
If posture issues persist beyond a set time, voice alerts are triggered, spaced out to avoid repetition.

## 🧾 Calculates:
Shoulder alignment – vertical difference between left and right shoulders

Forward head posture – horizontal offset between ears and shoulders (explained below 👇)

Head tilt – height difference between ears

⏱️ Tracks how long good/bad posture is held

🔊 Sends voice alerts when poor posture is maintained too long
---


Key Dependencies:
-opencv-python
-mediapipe
-pyttsx3
-argparse

## 🛠️ Setup

-Clone the repository
git clone https://github.com/your-username/posture-monitor.git
cd posture-monitor

-Install dependencies
pip install -r requirements.txt

-Run the app▶️
1. Using Webcam (default):

python app.py
#can give parameters
python app.py --shoulder-threshold 50 --ear-shoulder-threshold 15 --time-threshold 5 --alert-cooldown 9

2. Using a Video File:

python app.py --video posture-monitor/video.mp4 

## ⚙️ Arguments

Argument                    | Description                                               | Default

--video                     | Path to input video file                                  | 0 (webcam)
--shoulder-threshold        | Vertical pixel difference for shoulder misalignment       | 30
--ear-shoulder-threshold    | Horizontal pixel offset between ears and shoulders        | 20
--time-threshold            | Time (in seconds) of bad posture before alert triggers    | 30
--alert-cooldown            | Cooldown time (in seconds) between two voice alerts       | 60


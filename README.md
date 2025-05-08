# MediaPipe X-Plane 11 Controller

This project uses **MediaPipe** to detect hand gestures and control the **X-Plane 11 flight simulator**. Hand gestures are mapped to flight controls such as throttle, elevator, and aileron, enabling intuitive and real-time control of the simulator.

## Features
- **Real-time hand gesture detection** using MediaPipe.
- **Flight control mapping** for throttle, pitch, and roll.
- Intuitive interface for controlling X-Plane 11 using hand gestures.

## Requirements
To run this project, you need the following:
- Python 3.x
- OpenCV
- MediaPipe
- XPlaneConnect

## Installation
Follow these steps to set up and run the project:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mediapipe-xplane-controller.git
   cd mediapipe-xplane-controller


Usage
Start the script: Run the visual_control_v3.py file.
Place your hand in front of the camera:
Left hand: Open your left hand to control pitch and roll.
Right hand: Open your right hand to control throttle.
Adjust your gestures: The script will map your hand movements to the flight controls in X-Plane 11.
How It Works
The left hand controls the pitch (up/down) and roll (left/right) of the aircraft.
The right hand controls the throttle (engine power).
The script uses MediaPipe to detect hand landmarks and calculates control values based on the positions of the fingers.
File Structure
visual_control_v3.py: Main script for hand gesture detection and X-Plane control.
README.md: Documentation for the project.
LICENSE: License file for the project.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
MediaPipe for hand tracking.
XPlaneConnect for X-Plane communication.
OpenCV for image processing.
Troubleshooting
Camera not detected: Ensure your webcam is connected and accessible.
X-Plane not responding: Verify that X-Plane Connect is properly installed and running.
Performance issues: Close other applications using the camera or reduce the resolution in the script.
Contributing
Contributions are welcome! If you'd like to improve this project, feel free to fork the repository and submit a pull request.

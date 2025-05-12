import xpc
import cv2
import mediapipe as mp

class XPlaneManualControl:
    """
    Handles communication with X-Plane simulator to send control inputs.
    """
    def __init__(self):
        self.vehicle = xpc.XPlaneConnect()
        print("Connected to X-Plane")

    def send_controls(self, elevator, aileron, rudder, throttle):
        """
        Sends control inputs to the X-Plane simulator.
        :param elevator: Elevator control (-1.0 to 1.0)
        :param aileron: Aileron control (-1.0 to 1.0)
        :param rudder: Rudder control (-1.0 to 1.0)
        :param throttle: Throttle control (0.0 to 1.0)
        """
        ctrl = [elevator, aileron, rudder, throttle]
        self.vehicle.sendCTRL(ctrl)
        print(f"Controls sent: Elevator={elevator}, Aileron={aileron}, Rudder={rudder}, Throttle={throttle}")

controller = XPlaneManualControl()
 
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

width , height = 1280 , 720

def FingerPoints(hand):
    """
    Extracts finger positions from the detected hand landmarks.
    :param hand: MediaPipe hand landmarks object.
    :return: Dictionary containing finger positions for left and right hands.
    """
    hand_index = hand.multi_hand_landmarks
    hands = {"right":None,"left":None}
    
    for idx , hand_landmarks in enumerate(hand_index):
        
        try:
          fingers = {
                      "index_top": [None,8],
                      "index_bottom": [None,5],
                      "middle_top": [None,12],
                      "middle_bottom": [None,9],
                      "ring_top": [None,16],
                      "ring_bottom": [None,13],
                      "pinky_top": [None,20],
                      "pinky_bottom": [None,17],
                      "wrist" : [None,0]
                      }
          
          for point in fingers.keys():
             num = fingers[point][1]
             landmark = (results.multi_hand_landmarks[idx].landmark[num].x,results.multi_hand_landmarks[idx].landmark[num].y)
             landmark_xy = int(width * landmark[0]) , int(height * landmark[1])
             fingers[point][0] = landmark_xy

          if hand.multi_handedness[idx].classification[0].label == "Right":
            hands["right"] = fingers
          else:
            hands["left"] = fingers

        except:
          pass
        
    return hands

def Fist(fingers):
    """
    Determines whether the hand is in a fist (closed) or open position.
    :param fingers: Dictionary containing finger positions.
    :return: "Close" if fist is detected, "Open" otherwise.
    """
    if fingers != None:
       
        x_error = abs(fingers["middle_top"][0][0] - fingers["wrist"][0][0])
        y_error = abs(fingers["middle_top"][0][1] - fingers["wrist"][0][1])
        sum_top = ((x_error**2 + y_error**2)**(0.5))

        x_error = abs(fingers["middle_bottom"][0][0] - fingers["wrist"][0][0])
        y_error = abs(fingers["middle_bottom"][0][1] - fingers["wrist"][0][1])
        sum_bottom = ((x_error**2 + y_error**2)**(0.5))

        if sum_bottom > sum_top:
            return "Close"
        else:
            return "Open"
    else:
       return None
    
def ThrottleRange(image , fingers):
    """
    Calculates the throttle value based on finger positions.
    :param image: The current video frame.
    :param fingers: Dictionary containing finger positions.
    :return: Throttle value (0.0 to 1.0).
    """
    if fingers != None:
        y_error = abs(fingers["middle_top"][0][1] - fingers["middle_bottom"][0][1])
        x_error = abs(fingers["middle_top"][0][0] - fingers["middle_bottom"][0][0])

        error1 = ((x_error**2 + y_error**2)**(0.5))

        y_error1 = abs(fingers["middle_bottom"][0][1] - fingers["wrist"][0][1])
        x_error1 = abs(fingers["middle_bottom"][0][0] - fingers["wrist"][0][0])

        error2 = ((x_error1**2 + y_error1**2)**(0.5)) - 50

        throttle = error1 / error2
        cv2.putText(image, f"Throttle : {throttle:.2f}", (fingers["middle_bottom"][0][0] - 50, fingers["middle_bottom"][0][1] + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        return throttle
    else:
       return None
    
    
def Pitch_Roll(fingers):
   """
    Calculates the pitch and yaw values based on finger positions.
    :param fingers: Dictionary containing finger positions.
    :return: Pitch and yaw values.
    """
   pitch_roll_x = width // 4
   pitch_roll_y = height // 2 

   if fingers != None:
      cv2.circle(image,(int(fingers["middle_bottom"][0][0]),int(fingers["middle_bottom"][0][1])),30,(255,0,0),3)
      
      roll = pitch_roll_x - fingers["middle_bottom"][0][0] 
      pitch = pitch_roll_y - fingers["middle_bottom"][0][1]

   else:
        return None ,None

   return roll ,pitch
    

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

Throttle ,Pitch , Roll = 0 , 0 , 0

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  
  
  while cap.isOpened():
    
    success, image = cap.read()
    image = cv2.flip(image, 1)
    if not success:
      print("Ignoring empty camera frame.")
      continue

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      fingers = FingerPoints(results)
      fingers_right ,fingers_left = fingers["right"] , fingers["left"]

      try:
         if Fist(fingers_left) == "Open":
            pitch_roll_x = width // 4
            pitch_roll_y = height // 2    
            size = 20    
            cv2.rectangle(image,(pitch_roll_x - size , pitch_roll_y - size),(pitch_roll_x + size ,pitch_roll_y + size),(255,0,0),2)
            Pitch , Roll = Pitch_Roll(fingers_left)
      except:
         Pitch , Roll = 0 , 0

      try:
         if Fist(fingers_right) == "Open":
            Throttle = ThrottleRange(image,fingers_right)
         else:
            Throttle = 0
      except:
         pass
         
      elevator1=Roll / 250
      aileron1 = Pitch / 300
      throttle1=Throttle

      controller.send_controls(
            elevator = -1*(Roll / 250) , 
            aileron = -1*(Pitch / 300),
            throttle = Throttle , 
            rudder = 0
            )
      
      cv2.putText(image, f"Elevator {elevator1:.2} |  Aileron {aileron1:.2f} | Throttle {throttle1:.2f}", (100, 650), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
   
    image = cv2.resize(image, (width//2, height//2))
    cv2.imshow('MediaPipe X-Plane 11 Controller',image)

    if cv2.waitKey(5) & 0xFF == 27:
      break

cap.release()
    

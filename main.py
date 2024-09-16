import cv2
import numpy as np
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Video Feed
cap = cv2.VideoCapture(0)

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 


# Curl Counter Varibales
counter = 0
stage = None


# Setup mediapipe instance
with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose:
   while cap.isOpened():
      ret, frame = cap.read()
           
      # Recolor image to RGB
      image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      image.flags.writeable = False
      
      # Make Detection
      reults = pose.process(image)

      # Recolor back to RGB
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

      # Extract Landmarks
      try:
         landmarks = reults.pose_landmarks.landmark

         shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
         elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
         wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
         ## shoulder_2 = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
         ## elbow_2 = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
         ## wrist_2 = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
         # prinkt(landarks)

         # Calculate angle
         angle = calculate_angle(shoulder, elbow, wrist)
        ## angle_2 = calculate_angle(shoulder_2, elbow_2, wrist_2)
         # print(angle)

         # Visualize angle
         cv2.putText(image, str(angle), 
                           tuple(np.multiply(elbow, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    
                                
         ##cv2.putText(image, str(angle_2), 
         ##                  tuple(np.multiply(elbow_2, [640, 480]).astype(int)), 
         ##                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                                
         
         # Curl counter logic
         ## The 160 degree DOWN thresholds gives you leeway in case the person don't get a perfect 180 degree staright arm.
         ## The 30 degree UP thresholds ensures a rep that doesn't go all the way up is counted.
         if angle > 160:
            stage = 'down'
         if angle < 30 and stage == 'down':
            stage = 'up'
            counter += 1
            # print(counter) 
         
      except:
         pass   

      # Render Curl Counter
      # Setup Status Box
      cv2.rectangle(image, (0,0), (300,73), (245,117,16), -1)


      # Rep data
      ## The REP data section holds the title and counter.
      cv2.putText(image, 'REPS', (15,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
      cv2.putText(image, str(counter), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)


      # Stage data
      ## The STAGE data section holds the title and stage state (e.g. UP & DOWN).
      cv2.putText(image, 'STAGE', (65,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
      cv2.putText(image, stage, (60,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
                                                          
                                
      # Render Detections
      mp_drawing.draw_landmarks(image, reults.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness = 2, circle_radius = 2),
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness = 2, circle_radius = 2))

     # print(reults)
      
      cv2.imshow("Mediapipe Feed", image)
      if cv2.waitKey(10) & 0xFF == ord('k'):
         break
cap.release()
cv2.destroyAllWindows()

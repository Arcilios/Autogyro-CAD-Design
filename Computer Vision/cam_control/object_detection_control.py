import cv2
import numpy as np
import time
import serial
from ultralytics import YOLO

# ------------------ Pan Controller (FS90R) ------------------
class PanController:
    def __init__(self, base_speed=92, min_speed=60, max_speed=120):
        self.base_speed = base_speed
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.last_error = 0
        self.integral = 0

    def sigmoid_pid(self, error, Ki=0.005, Kd=0.01, dt=0.1, max_output=10):
        derivative = (error - self.last_error) / dt
        p_term = 6 * (1 / (1 + np.exp(-error / 40)) - 0.5)
        output = p_term + Ki * self.integral + Kd * derivative
        output = np.clip(output, -max_output, max_output)
        self.integral += error * dt
        self.last_error = error
        return int(np.clip(self.base_speed + output, self.min_speed, self.max_speed))

# ------------------ Tilt Controller (MG90S) ------------------
class TiltController:
    def __init__(self, angle=90, min_angle=60, max_angle=120):
        self.angle = angle
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.last_error = 0
        self.integral = 0

    def sigmoid_pid(self, error, Ki=0.005, Kd=0.01, dt=0.1, max_output=4):
        derivative = (error - self.last_error) / dt
        p_term = 6 * (1 / (1 + np.exp(-error / 40)) - 0.5)
        output = p_term + Ki * self.integral + Kd * derivative
        output = np.clip(output, -max_output, max_output)
        self.integral += error * dt
        self.last_error = error
        self.angle += output
        self.angle = np.clip(self.angle, self.min_angle, self.max_angle)
        return int(self.angle)

# ------------------ Camera & Detection ------------------
def videoCapture(cam_num=1):
    cap = cv2.VideoCapture(cam_num, cv2.CAP_DSHOW)
    cap.set(3, 320)
    cap.set(4, 240)
    time.sleep(1)
    return cap

def object_detection(frame, model, min_conf=0.8):
    results = model(frame)[0]
    centers = [(int((x1 + x2) / 2), int((y1 + y2) / 2))
               for x1, y1, x2, y2, conf, cls in results.boxes.data.tolist()
               if int(cls) == 0 and conf >= min_conf]
    if centers:
        x_obj, y_obj = map(int, np.mean(centers, axis=0))
        return x_obj, y_obj
    return None, None

# ------------------ Main Loop ------------------
if __name__ == "__main__":
    model = YOLO("yolov8n.pt")
    pan_ctrl = PanController()
    tilt_ctrl = TiltController()
    ser = serial.Serial("COM17", 9600, timeout=1)
    cap = videoCapture()
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        x_obj, y_obj = object_detection(frame, model)
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2

        if x_obj is not None:
            dx = -(x_obj - cx)
            dy = y_obj - cy
            dx = np.clip(dx, -100, 100)
            dy = np.clip(dy, -100, 100)

            pan = pan_ctrl.sigmoid_pid(dx)
            tilt = tilt_ctrl.sigmoid_pid(dy)

            if frame_id % 2 == 0:
                ser.write(f"P{pan}T{tilt}\n".encode())

            print(f"🎯 dx={dx}, dy={dy} | Pan={pan}, Tilt={tilt}")
            cv2.drawMarker(frame, (cx, cy), (255, 0, 255), cv2.MARKER_CROSS, 20, 2)
            cv2.circle(frame, (x_obj, y_obj), 5, (0, 255, 0), -1)
        else:
            print("No person detected.")

        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_id += 1

    cap.release()
    ser.close()
    cv2.destroyAllWindows()

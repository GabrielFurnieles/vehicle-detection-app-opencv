import math
import pandas as pd
from dataclasses import dataclass
import numpy as np
import ultralytics
from ultralytics import YOLO
import cv2


class VehicleTracker:

    # Dict to store tracked objects
    tracked_objects = {}

    # load yolov8 model
    model = YOLO('yolov8n.pt')


    def track_video(self, cap:cv2.VideoCapture, roi_mask:np.array):

        cv2.namedWindow('Object detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Object detection', 600, 400)

        # ROI mask
        # Convert the image to grayscale
        gray = cv2.cvtColor(roi_mask, cv2.COLOR_BGR2GRAY)

        # Create a binary mask by thresholding
        _, binary_mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        binary_mask = cv2.merge([binary_mask] * 3)

        num_frame = 1
        ret = True
        # read frames
        while ret:
            ret, frame = cap.read()

            if ret:
                # Apply ROI mask
                roi_masked_frame = cv2.bitwise_and(frame, binary_mask)

                # track objects
                results = self.model.track(roi_masked_frame, persist=True, classes=[2,3,5,7])
                self.process_results(results[0], num_frame)

                # plot results
                frame_ = results[0].plot()

                # visualize
                cv2.imshow('Object detection', frame_)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

                num_frame += 1
        
        vehicle_data = self.store_datafraframe()

        # return object count adn vehicle_data
        return results[0].boxes.id[-1], vehicle_data

    def __get_direction(self, p1,p2):
        x1, y1 = p1
        x2, y2 = p2
        # Compute the angle using arctan2 (result in rad)
        angle_rad = math.atan2(y2 - y1, x2 - x1)

        return math.degrees(angle_rad)

    def process_results(self, results:ultralytics.engine.results.Results, frame):
        if results.boxes.id is not None:
            for i,id_ in enumerate(results.boxes.id.numpy().astype(int)):
                # Compute centroid
                xyxy = results.boxes.xyxy.numpy()[i]
                cx = (xyxy[0] + xyxy[2]) / 2
                cy = (xyxy[1] + xyxy[3]) / 2

                # Store into info into dicts
                if self.tracked_objects.get(id_):
                    self.tracked_objects[id_]['end_frame'] = frame
                    self.tracked_objects[id_]['end_point'] = (cx,cy)
                else:
                    self.tracked_objects[id_] = {
                        'id': id_,
                        'class': results.boxes.cls.numpy()[i].astype(int),
                        'origin_point':(cx,cy),
                        'origin_frame': frame,
                        'end_point': (cx,cy),
                        'end_frame': frame,
                        'direction': None
                    }

    def store_datafraframe(self):
        # Build dataframe from tracked objects
        df = pd.DataFrame(self.tracked_objects.values())

        if df.shape[0] == 0:
            print('No vehicles found')
            return None

        # Direction
        df['direction'] = df.apply(lambda row: self.__get_direction(row['origin_point'], row['end_point']), axis=1)

        # Distance in km travelled by the object

        # Speed of the object in kph
        # fps = cap.get(cv2.CAP_PROP_FPS)

        return df
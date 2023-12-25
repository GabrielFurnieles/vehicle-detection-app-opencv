import math
import pandas as pd
from collections import deque
from dataclasses import dataclass

@dataclass
class ObjectTrack():
    id:int
    origin_point:tuple
    origin_frame:int
    end_point:tuple
    end_frame:int


class EuclideanDistTracker:

    def __init__(self, distance=40, history_frames=15):
        self.tracked_objects = []
        #self.first_center_points = {}
        #self.last_center_points = {}
        self.center_points_window = deque(maxlen=history_frames)
        self.id_count = 0
        self.distance = distance

    def update(self, objects_rect, num_frame):
        # Objects boxes and id
        objects_bbs_ids = []

        # Window frame
        actual_window_frame = []
        
        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            
            # Find out if that object was detected already
            same_object_detected = False

            for window_frame in self.center_points_window:
                for tracked_object in window_frame: 
                    pt = tracked_object.end_point
                    dist = math.hypot(cx - pt[0], cy - pt[1])

                # for id, pt in window_frame.items():
                #     dist = math.hypot(cx - pt[0], cy - pt[1])

                    # If distance between tracked centroid is small then they are the same object
                    if dist < self.distance:
                        objects_bbs_ids.append([x, y, w, h, tracked_object.id])
                        
                        tracked_object.end_point = (cx,cy)
                        tracked_object.end_frame = num_frame

                        actual_window_frame.append(tracked_object)

                        # actual_window_frame[id] = (cx,cy)
                        # self.last_center_points[id] = (cx,cy)
                        
                        same_object_detected = True
                        break
            
            # New object is detected we assign the ID to that object
            if not same_object_detected:
                new_object = ObjectTrack(
                    id = self.id_count,
                    origin_point=(cx,cy),
                    origin_frame=num_frame,
                    end_point=(cx,cy),
                    end_frame=num_frame,
                )
                actual_window_frame.append(new_object)
                self.tracked_objects.append(new_object)
                
                # actual_window_frame[self.id_count] = (cx,cy)
                # self.first_center_points[self.id_count] = (cx,cy)

                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1
        
        self.update_window(actual_window_frame)
        
        return objects_bbs_ids


    def update_window(self, window_frame):
        self.center_points_window.append(window_frame)

    
    # def compute_speed(self):
    #     # Get first detected centroid for every vehicle
    #     ids = list(self.first_center_points.keys())
    #     origin_coordinates = list(self.first_center_points.values())

    #     # Get last detected centroid for every vehicle
    #     end_coordinates = [self.last_center_points.get(i) for i in ids]
    #     origin_frame = 
    #     end_frame = 

    #     # Create DataFrame
    #     # SE NECESITA GUARDAR EL NUM DE FRAME PARA CALCULAR EL TIEMPO TRANSCURRIDO
    #     self.df = pd.DataFrame({'ID': ids, 
    #                             'ORIGIN_frame':origin_frame,'ORIGIN_coords': origin_coordinates, 
    #                             'END_frame':end_frame, 'END': end_coordinates})

    #     # Compute distance
    #     self.df['DISTANCE(m)'] = 

    #     # Compute speed
    #     self.df['SPEED(m/s)'] = 

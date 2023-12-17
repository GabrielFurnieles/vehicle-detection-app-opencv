import math
from collections import deque

class EuclideanDistTracker:

    def __init__(self, distance=30, history_frames=15):
        self.center_points_history ={}
        self.center_points_window = deque(maxlen=history_frames)
        self.id_count = 0
        self.distance = distance

    def update(self, objects_rect):
        # Objects boxes and ids
        objects_bbs_ids = []

        # Window frame
        actual_window_frame = {}
        
        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            
            # Find out if that object was detected already
            same_object_detected = False

            for window_frame in self.center_points_window:
                for id, pt in window_frame.items():
                    dist = math.hypot(cx - pt[0], cy - pt[1])

                    if dist < self.distance:
                        objects_bbs_ids.append([x, y, w, h, id])
                        actual_window_frame[id] = (cx,cy)
                        same_object_detected = True
                        break
            
            # New object is detected we assign the ID to that object
            if same_object_detected is False:
                actual_window_frame[self.id_count] = (cx,cy)
                self.center_points_history[self.id_count] = (cx,cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1
        
        self.update_window(actual_window_frame)
        
        return objects_bbs_ids


    def update_window(self, window_frame):
        self.center_points_window.append(window_frame)
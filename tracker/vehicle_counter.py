import cv2
import numpy as np
from .euclidean_distance_tracker import *


def vehicle_counter2(cap, roi_mask, px2km_ratio):

    cv2.namedWindow('Object detection', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Object detection', 600, 400)

    # Check if camera opened successfully
    if (cap.isOpened() == False):
        print(cap)
        raise RuntimeError("Error opening video file")

    # Create tracker object
    tracker = EuclideanDistTracker()

    # Create Cascade classifiers for cars and buses
    car_cascade = cv2.CascadeClassifier('tracker/haars_cars.xml')
    bus_cascade = cv2.CascadeClassifier('tracker/haars_bus_front.xml')

    num_frame = 0
    while True:
        # Read cap
        ret,frame = cap.read()

        # Exit if no frame
        if not ret:
            break

        num_frame += 1

        # Apply ROI mask
        roi_masked_frame = cv2.bitwise_and(frame, roi_mask)

        # Convert the frame to the Lab color space (more robust)
        lab_img = cv2.cvtColor(roi_masked_frame, cv2.COLOR_BGR2Lab)

        # Separate the Lab channels
        l_channel, a_channel, b_channel = cv2.split(lab_img)

        # Apply gaussian blur to reduce noise
        blur = cv2.GaussianBlur(l_channel,(5,5),0)
        
        # 1. Object detection
        cars = car_cascade.detectMultiScale(blur, 1.05, 5)
        buses = bus_cascade.detectMultiScale(blur, 1.05, 5)
        detections = list(cars) + list(buses)

        # 2. Object Tracking
        boxes_ids = tracker.update(detections,num_frame)
        for box_id in boxes_ids:
            x, y, w, h, id = box_id
            cv2.putText(frame, str(id), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)


        cv2.rectangle(frame, (10, 2), (100,20), (255,255,255), -1)
        cv2.putText(frame, str(cap.get(cv2.CAP_PROP_POS_FRAMES)), (15, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5 , (0,0,0))
        
        # Display image
        cv2.imshow('Object detection', frame)

        chd = cv2.waitKey(1)
        # Exit if q is pressed
        if chd == ord('q'):
            break

    # 3. Get vehicle data
    df = vehicle_data(tracker, cap, px2km_ratio)
            
    return tracker.id_count, df


def vehicle_data(tracker, cap, px2km_ratio):
    # Build dataframe from tracked objects
    df = pd.DataFrame(tracker.tracked_objects)

    if df.shape[0] == 0:
        print('No vehicles founded')
        return None

    # Distance in km travelled by the object
    df['distance(km)'] = df.apply(
        lambda row: np.linalg.norm(
            np.array(row['end_point']) - np.array(row['origin_point'])
        ), 
        axis=1
    ) * px2km_ratio

    # Speed of the object in kph
    fps = cap.get(cv2.CAP_PROP_FPS)
    df['speed(kph)'] = df['distance(km)'] / ((df['end_frame'] - df['origin_frame']) / fps)

    return df


def vehicle_counter(cap, roi_mask):

    cv2.namedWindow('Object detection', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Object detection', 600, 400)

    cv2.namedWindow('Segmentation', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Segmentation', 600, 400)

    # Check if camera opened successfully
    if (cap.isOpened()== False):
        raise RuntimeError("Error opening video file")

    # Create tracker object
    tracker = EuclideanDistTracker()

    # Create background substraction
    backSub = cv2.createBackgroundSubtractorMOG2(history=1000, detectShadows=True)

    while True:
        # Read cap
        ret,frame = cap.read()

        # Exit if no frame
        if not ret:
            break

        # Apply ROI mask
        roi_masked_frame = cv2.bitwise_and(frame, roi_mask)

        # Convert the frame to the Lab color space (more robust)
        lab_img = cv2.cvtColor(roi_masked_frame, cv2.COLOR_BGR2Lab)

        # Separate the Lab channels
        l_channel, a_channel, b_channel = cv2.split(lab_img)

        # Subtract background
        fgmask = backSub.apply(l_channel)

        # Apply gaussian blur to reduce noise
        blur_mask = cv2.GaussianBlur(fgmask,(5,5),0)

        # Segment by binary threshold
        _, th1 = cv2.threshold(blur_mask,220,255,cv2.THRESH_BINARY)

        # Find contours
        contours, _ = cv2.findContours(th1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        # 1. Calculate area and remove small elements
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 400 and area < 10000:
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append([x, y, w, h])

        # 2. Object Tracking
        boxes_ids = tracker.update(detections)
        for box_id in boxes_ids:
            x, y, w, h, id = box_id
            cv2.putText(frame, str(id), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)


        cv2.rectangle(frame, (10, 2), (100,20), (255,255,255), -1)
        cv2.putText(frame, str(cap.get(cv2.CAP_PROP_POS_FRAMES)), (15, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5 , (0,0,0))
        
        # Display image
        cv2.imshow('Object detection', frame)
        cv2.imshow('Segmentation', th1)

        chd = cv2.waitKey(1)
        # Exit if q is pressed
        if chd == ord('q'):
            break
            
    return tracker.id_count


import cv2
from .euclidean_distance_tracker import *

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


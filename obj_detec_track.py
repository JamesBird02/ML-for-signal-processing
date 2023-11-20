import numpy as np
import cv2 as cv

cap = cv.VideoCapture('cars.mp4')

# Create a background subtractor object with KNN method

background_subtract = cv.createBackgroundSubtractorKNN(history=400, dist2Threshold=500.0, detectShadows=True)


# Initialize variables for MeanShift tracking
track_window = None
roi_hist = None
term_crit = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply background subtraction to get foreground mask
    fgmask = background_subtract.apply(frame)

    #remove noise
    fgmask = cv.morphologyEx(fgmask, cv.MORPH_OPEN, np.ones((4, 4), np.uint8))

    _, fgmask = cv.threshold(fgmask, 254, 255, cv.THRESH_BINARY)

    # Find contours of the detected objects
    contours, _ = cv.findContours(fgmask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Filter contours based on area to identify potential cars
    filtered_contours = []
    for contour in contours:
        area = cv.contourArea(contour)
        if area > 2100:  # Adjusted for object size, may be different for other videos and may be able to adjust this automatically
            filtered_contours.append(contour)
            

    # Draw rectangles around the objects
    for contour in filtered_contours:
        x, y, w, h = cv.boundingRect(contour)
        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Use the first detected contour for tracking
        if track_window is None:
            track_window = (x, y, w, h)

            # Set up the Region of interest for tracking
            roi = frame[y:y+h, x:x+w]
            hsv_roi = cv.cvtColor(roi, cv.COLOR_BGR2HSV)
            mask = cv.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
            roi_hist = cv.calcHist([hsv_roi], [0], mask, [180], [0, 180])
            cv.normalize(roi_hist, roi_hist, 0, 255, cv.NORM_MINMAX)

            # Set up termination criteria for meanshift tracking
            term_crit = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)

    # Perform meanshift tracking if the initial window is set
    if track_window is not None:
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        dst = cv.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)

        # Apply meanshift to get the new location
        ret, track_window = cv.meanShift(dst, track_window, term_crit)

        # Draw rectangle around the tracked area
        x, y, w, h = track_window
        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

    cv.imshow('Frame', frame)
    cv.imshow('Background Subtraction Frame', fgmask)
    k = cv.waitKey(30) & 0xFF
    if k == 27:
        break

cv.destroyAllWindows()
cap.release()

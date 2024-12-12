import numpy as np
import cv2
import time

def create_background(cap, num_frames=30):
    print("Capturing background. Move out of the frame.")
    backgrounds = []
    for i in range(num_frames):
        ret, frame = cap.read()
        if ret:
            backgrounds.append(frame)
        else:
            print(f"Failed to capture background frame {i+1}/{num_frames}")
        time.sleep(0.1)
    
    if backgrounds:
        return np.mean(backgrounds, axis=0).astype(np.uint8)
    else:
        raise ValueError("Couldn't capture any frames for background")

def create_mask(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8), iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3,3), np.uint8), iterations=1)
    return mask

def apply_cloak_effect(frame, mask, background):
    mask_inv = cv2.bitwise_not(mask)
    fg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    bg = cv2.bitwise_and(background, background, mask=mask)
    return cv2.add(fg, bg)

def main():
    print("OpenCV version:", cv2.__version__)
    
    # Try multiple camera indices
    camera_indices = [0, 1, 2]
    cap = None
    
    for index in camera_indices:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"Successfully opened camera at index {index}")
            break
    
    if not cap or not cap.isOpened():
        print("Error: Could not open camera. Please check your camera connections.")
        return

    try:
        background = create_background(cap)
    except ValueError as e:
        print(f"Error: {e}")
        cap.release()
        return

    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])

    print("Starting main loop. Press 'q' to exit")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            time.sleep(1)
            continue

        mask = create_mask(frame, lower_blue, upper_blue)
        result = apply_cloak_effect(frame, mask, background)

        cv2.imshow('Invisible cloak', result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
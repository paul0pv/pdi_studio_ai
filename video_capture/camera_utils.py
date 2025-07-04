import cv2


def list_available_cameras(max_index=5):
    available = []
    for index in range(max_index):
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            available.append(index)
        cap.release()
    return available

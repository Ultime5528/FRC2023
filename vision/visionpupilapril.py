import cv2
import pupil_apriltags

cap = cv2.VideoCapture(0)
detector = pupil_apriltags.Detector("tag16h5")


while True:
    ret, frame = cap.read()
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = detector.detect(gray_img)
    for tag in results:
        for i in range(4):
            corner = (int(tag.corners[i][0]), int(tag.corners[i][1]))
            if i < 3:
                next_corner = (int(tag.corners[i+1][0]), int(tag.corners[i+1][1]))
            else:
                next_corner = (int(tag.corners[0][0]), int(tag.corners[0][1]))
            cv2.line(frame, corner, next_corner, (0, 255, 0), 2)
            cv2.putText(frame, str(tag.tag_id), (int(tag.center[0]), int(tag.center[1])), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)

    cv2.imshow("camera capture", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



import cv2
import robotpy_apriltag

cap = cv2.VideoCapture(0)
detector = robotpy_apriltag.AprilTagDetector()
config = robotpy_apriltag.AprilTagDetector.Config()
# config.numThreads = 2
# config.quadDecimate = 15
detector.setConfig(config)
detector.addFamily("tag36h11")


def get_xy_from_point(point: robotpy_apriltag.AprilTagDetection.Point):
    return int(point.x), int(point.y)


while True:
    ret, frame = cap.read()
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = detector.detect(gray_img)
    # results = [x for x in results if x.getDecisionMargin() > 30]
    # if len(results) > 1:
    print(results)
    for tag in results:
        if tag.getDecisionMargin() > 60 and tag.getHamming() == 0:
            for i in range(4):
                corner = get_xy_from_point(tag.getCorner(i))
                if i < 3:
                    next_corner = get_xy_from_point(tag.getCorner(i+1))
                else:
                    next_corner = get_xy_from_point(tag.getCorner(0))
                cv2.line(frame, corner, next_corner, (0, 255, 0), 2)
                cv2.putText(frame, str(tag.getId()), get_xy_from_point(tag.getCenter()), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)

    cv2.imshow("camera capture", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



import numpy as np
import cv2 as cv

# 계산된 calibration data 로드
try:
    with np.load('data/calib_result.npz') as data:
        K = data['K']
        dist = data['dist']
except:
    print("Data open error - no calibration data")
    exit()

# 영상 파일
video_file = 'data/chessboard_video.mp4'
video = cv.VideoCapture(video_file)
if not video.isOpened():
    print("Video open error - cannot open video")
    exit(0)

map1, map2 = None, None

while True:
    valid, img = video.read()
    if not valid: break

    h, w = img.shape[:2]
    
    # 보정 맵 생성(1번만)
    if map1 is None:
        map1, map2 = cv.initUndistortRectifyMap(K, dist, None, None, (w, h), cv.CV_32FC1)

    # 왜곡 보정
    rectified = cv.remap(img, map1, map2, cv.INTER_LINEAR)

    # 원본과 보정본 합쳐서 출력
    combined = np.hstack((img, rectified))

    scale_percent = 0.4 # 40% 크기로 줄이기
    width = int(combined.shape[1] * scale_percent)
    height = int(combined.shape[0] * scale_percent)
    dim = (width, height)
    combined = cv.resize(combined, dim, interpolation=cv.INTER_AREA)

    cv.putText(combined, "Original", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    cv.putText(combined, "Rectified", (int(width/2) + 10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
    
    cv.imshow('Distortion Correction (ESC to quit)', combined)
    
    # Space: Pause / ESC: Exit
    key = cv.waitKey(10)
    if key == ord(' '):     
        key = cv.waitKey()
    if key == 27:           
        break

video.release()
cv.destroyAllWindows()
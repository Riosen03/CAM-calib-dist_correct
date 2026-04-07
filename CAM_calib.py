import numpy as np
import cv2 as cv

# 기본 정보
video_file = 'data/chessboard_video.mp4'  # 영상 파일명
board_pattern = (10, 7)      # 체스보드 가로/세로 십자교차 개수
board_cellsize = 0.025       # 체스보드 한 칸의 실제 크기 (m 단위)


# 영상 재생 및 프레임 추출
def select_img_from_video(video_file, board_pattern):
    video = cv.VideoCapture(video_file)
    if not video.isOpened():
        print("Video open error - cannot open video")
        exit(0)

    print("--- 조작키 ---")
    print("Space : 일시정지")
    print("(After space)Enter : 현재 프레임 저장")
    print("ESC : 영상 종료(선택 완료) 및 계산 시작")

    img_select = []

    while True:
        valid, img = video.read()
        if not valid:
            video.set(cv.CAP_PROP_POS_FRAMES, 0) # 영상 무한 반복
            continue

        display = img.copy()
        cv.putText(display, f'Selected : {len(img_select)}', (10, 30), 
                   cv.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), 2)
        cv.imshow('Camera Calibration', display)

        key = cv.waitKey(20) # 20ms 대기 (멈춤 방지)
        if key == ord(' '):  # Space
            complete, pts = cv.findChessboardCorners(img, board_pattern)
            cv.drawChessboardCorners(display, board_pattern, pts, complete)
            cv.putText(display, 'Reviewing... Enter to Save / Any key to skip', (10, 60), 
                       cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 255), 1)
            cv.imshow('Camera Calibration', display)
            
            sub_key = cv.waitKey()
            if sub_key == ord('\r') and complete: # Enter
                if complete:
                    img_select.append(img)
                    print(f"Image saved (saved num - {len(img_select)})")
                else :
                    print(f"Image select error - no {board_pattern} pattern chessboard")
                
        if key == 27: # ESC
            break

    cv.destroyAllWindows()
    return img_select



# main
images = select_img_from_video(video_file, board_pattern)

if len(images) > 0:
    print("\ncalculating calibration")
    gray_shape = cv.cvtColor(images[0], cv.COLOR_BGR2GRAY).shape[::-1]
    
    # 3D 준비
    obj_pts_single = [[c, r, 0] for r in range(board_pattern[1]) for c in range(board_pattern[0])]
    obj_points = [np.array(obj_pts_single, dtype=np.float32) * board_cellsize] * len(images)
    
    # 2D 추출
    img_points = [cv.findChessboardCorners(cv.cvtColor(i, cv.COLOR_BGR2GRAY), board_pattern)[1] for i in images]

    # 상수값 계산
    rms, K, dist, rvecs, tvecs = cv.calibrateCamera(obj_points, img_points, gray_shape, None, None)

    # 결과 출력
    print("\n[result]")
    print(f"RMS Error : {rms}")
    print(f"K Matrix :\n{K}")
    print(f"Distortion Coefficients : {dist.flatten()}")
    
    # 결과 저장
    np.savez('data/calib_result.npz', K=K, dist=dist)
else:
    print("Calibration error - no selected image")
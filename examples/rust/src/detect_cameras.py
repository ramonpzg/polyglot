import cv2

def list_cameras():
    """Find all available cameras"""
    print("🎥 Detecting available cameras...\n")

    available_cameras = []

    # Test camera indices 0-10
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Get camera info
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)

            print(f"✅ Camera {i}: {int(width)}x{int(height)} @ {fps}fps")
            available_cameras.append(i)

            # Try to read a frame to confirm it works
            ret, frame = cap.read()
            if ret:
                print(f"   -> Successfully read test frame")
            else:
                print(f"   -> Warning: Could not read frame")

            cap.release()
        else:
            # Try with different backend
            cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
            if cap.isOpened():
                print(f"✅ Camera {i}: Available with V4L2 backend")
                available_cameras.append(i)
                cap.release()

    if not available_cameras:
        print("❌ No cameras found!")
        print("\nTrying alternative methods...")

        # Try /dev/video* devices directly
        import os
        video_devices = [f for f in os.listdir('/dev') if f.startswith('video')]
        if video_devices:
            print(f"Found devices: {video_devices}")
            for device in video_devices:
                path = f'/dev/{device}'
                cap = cv2.VideoCapture(path)
                if cap.isOpened():
                    print(f"✅ {path} works!")
                    cap.release()

    return available_cameras

if __name__ == "__main__":
    cameras = list_cameras()
    if cameras:
        print(f"\n📸 Found {len(cameras)} camera(s): {cameras}")
        print(f"Use camera index: {cameras[0]}")
    else:
        print("\n💡 No cameras detected. You can use a video file instead!")

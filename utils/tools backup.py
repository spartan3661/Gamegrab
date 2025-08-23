from PySide6.QtGui import QImage
import pygetwindow as gw
import mss

# DEBUG
def screen_list():
    return gw.getAllTitles()

def capture_screen(screen):
    target_window = gw.getWindowsWithTitle(screen)[0]

    with mss.mss() as sct:
        monitor = {"top": target_window.top, 
                   "left": target_window.left, 
                   "width": target_window.right - target_window.left, 
                   "height": target_window.bottom - target_window.top}

        sct_img = sct.grab(monitor)
        qimg = QImage(
                    sct_img.rgb,
                    sct_img.width,
                    sct_img.height,
                    QImage.Format.Format_RGB888
                )
        
        return qimg.copy()

def main():
    # DEBUG
    capture_screen("TEVI")
    print(gw.getAllTitles())

if __name__ == "__main__":
    main()

import ctypes as C
from ctypes import c_int32, c_uint8, c_void_p, POINTER
from ctypes.wintypes import HWND as C_HWND
import numpy as np
import pygetwindow as gw
from PySide6.QtGui import QImage
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DLL_PATH = os.path.join(BASE_DIR, "cpp_backend", "wgc_core.dll")
print(DLL_PATH)
dll = C.CDLL(DLL_PATH)

class BGRAFrame(C.Structure):
    _fields_ = [
        ("data",   C.POINTER(c_uint8)),
        ("width",  c_int32),
        ("height", c_int32),
        ("stride", c_int32),
        ("size",   c_int32),
    ]

dll.wgc_capture_bgra.argtypes = [C_HWND, C.POINTER(BGRAFrame), c_int32]
dll.wgc_capture_bgra.restype  = c_int32
dll.wgc_free.argtypes = [c_void_p]
dll.wgc_free.restype  = None

def capture_hwnd_to_image(hwnd: int, timeout_ms=2000):
    frame = BGRAFrame()
    rc = dll.wgc_capture_bgra(C_HWND(hwnd), C.byref(frame), timeout_ms)
    if rc != 0:
        raise RuntimeError(f"capture failed rc={rc}")

    try:
        # Build a NumPy view over the unmanaged memory (stride-aware)
        # Use stride*height to include any padding, then slice to width*4.
        byte_count = frame.stride * frame.height
        buf = C.cast(frame.data, C.POINTER(c_uint8 * byte_count)).contents
        np_rowbuf = np.frombuffer(buf, dtype=np.uint8).reshape(frame.height, frame.stride)



        # Keep only the visible part (w*4). Make a deep copy so we can free the DLL buffer.
        np_bgra = np_rowbuf[:, :frame.width * 4].copy()
      
        # keep alpha

        qimg = QImage(
            np_bgra.data, frame.width, frame.height, frame.width * 4,
            QImage.Format.Format_ARGB32
        ).copy()  # deep copy



        # no alpha, RGB888
        #np_bgr = np_bgra.reshape(frame.height, frame.width, 4)[:, :, :3]       # BGRA -> BGR
        #qimg = QImage(np_bgr.data, frame.width, frame.height, frame.width * 3,
        #              QImage.Format.Format_BGR888).copy()

        return qimg
    finally:
        dll.wgc_free(frame.data)

# DEBUG
def screen_list():
    return gw.getAllTitles()

def capture_screen(screen):
    target_window = gw.getWindowsWithTitle(screen)[0]

    if not target_window:
        raise RuntimeError(f"No window matching: {target_window}")
    
    hwnd = target_window._hWnd

    return capture_hwnd_to_image(hwnd)

def main():
    # DEBUG
    print(gw.getAllTitles())
    qimg = capture_screen("TEVI")
    if not qimg.save("output.png"):
        print("Failed to save image")
    else:
        print("Saved capture to output.png")


if __name__ == "__main__":
    main()

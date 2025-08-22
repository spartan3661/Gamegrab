from PySide6.QtWidgets import QApplication, QMainWindow
from ui.home import Monitor
import sys

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("OCR")
window.resize(600, 600)
monitor = Monitor()

window.setCentralWidget(monitor)
window.show()
app.exec()


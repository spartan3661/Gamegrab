from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QComboBox, QMessageBox, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QCloseEvent, QPixmap, QResizeEvent, QImage, QMovie
from PySide6.QtCore import Qt, QThread
from utils.ocr import OCRWorker
from utils import tools
from functools import partial
from PySide6.QtCore import Signal
from .settings_dialog import SettingsDialog

class Monitor(QWidget):
    """
    Main GUI class
    """
    start_OCR_signal = Signal(QImage)

    def __init__(self):
        """
        Initialize the main display
        """       
        super().__init__()

        self.debug = True
        self.screenshot_taken = False
        self.original_image = QImage()
        self.ocr_image = QImage()

        self.ocr_running = False

        self.createWorkers()
        self.screen_menu = self.createComboBox()
        self.main_layout = self.createLayouts()  
        self.setLayout(self.main_layout)

    def createWorkers(self):
        """
        Create persistent worker thread running OCR
        """
        self.ocr_worker = OCRWorker()
        self.ocr_thread = QThread()

        self.ocr_worker.moveToThread(self.ocr_thread)

        self.start_OCR_signal.connect(self.ocr_worker.run_OCR)
        self.ocr_worker.result_ready.connect(self.process_OCR)

        self.ocr_thread.start()

    def createComboBox(self):
        """
        Create dropdown menu to choose windows
        """
        screen_menu = QComboBox()
        screens = tools.screen_list()
        for title in screens:
            if title.strip(): 
                screen_menu.addItem(title)
        return screen_menu
    
    
    def screen_grab(self):
        """
        Take a screenshot of the active window and pass it to OCRWorker
        """
        # NOTE: user must run screengrab once to run ocr. inform user in readme or disable ocr_button until screen_grab runs once
        # NOTE: must inform user in readme.txt to use borderless mode

        # enables ocr button
        self.ocr_button.setEnabled(True)

        # finds and captures a screenshot of a window
        screens = tools.screen_list()
        selected_title = self.screen_menu.currentText()


        if selected_title not in screens:
            QMessageBox.warning(self, "Warning", "Application Not Found or is Not in Borderless Window Mode!")
            self.screen_menu.clear()
            for title in screens:               # refreshes screen list when application not found
                if title.strip():
                    self.screen_menu.addItem(title)
            QMessageBox.information(self, "Window List Refreshed", "Please select an available application window.")
            return

        self.original_image = tools.capture_screen(selected_title)
        if self.original_image is None:
            QMessageBox.warning(self, "Warning", "Could Not Capture Window!")
            return    
        
        # process and display the image
        pixmap = QPixmap.fromImage(self.original_image)
        scaled_pixmap = pixmap.scaled(
            self.display_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.display_label.setPixmap(scaled_pixmap)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
    def rescale_pixmap(self):
        if self.original_image.isNull():
            return
        target = self.display_label.contentsRect().size()  # new layouted size
        if target.width() <= 0 or target.height() <= 0:
            return
        pm = QPixmap.fromImage(self.original_image)
        self.display_label.setPixmap(pm.scaled(
            target,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.rescale_pixmap()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Custom close event to close worker thread

        # IMPORTANT: user must run screengrab once to run ocr. inform user in readme or disable ocr_button until screen_grab runs once
        # IMPORTANT: must inform user in readme.txt to use borderless mode
        """
        self.ocr_thread.quit()
        self.ocr_thread.wait()
        self.ocr_worker.deleteLater()
        self.ocr_thread.deleteLater()

        return super().closeEvent(event)

    def createLayouts(self):
        """
        Create layouts, buttons and image display

        # IMPORTANT: user must run screengrab once to run ocr. inform user in readme or disable ocr_button until screen_grab runs once
        # IMPORTANT: must inform user in readme.txt to use borderless mode
        """

        take_screenshot_button = QPushButton()
        take_screenshot_button.setText("Screen grab")
        take_screenshot_button.clicked.connect(self.screen_grab)

        refresh_button = QPushButton()
        refresh_button.setText("Refresh")
        refresh_button.clicked.connect(self.refresh_screens)

        self.ocr_button = QPushButton()
        self.ocr_button.setText("OCR")

        self.ocr_button.clicked.connect(partial(self.run_OCR_button_clicked, self.ocr_button))
        self.ocr_button.setEnabled(False)
        self.ocr_button.setToolTip("Capture a screen first to enable OCR!")

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.screen_menu, stretch=2)
        button_layout.addWidget(take_screenshot_button, stretch=2)
        button_layout.addWidget(refresh_button, stretch=1)
        button_layout.addWidget(self.ocr_button, stretch=1)
        button_layout.addWidget(self.settings_button, stretch=0)

        self.display_label = QLabel()
        self.display_label.setMinimumSize(1, 1)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.display_label.setStyleSheet("background-color: #2E2E2E;")

        # load custom image
        """
        pixmap = QPixmap("assets/space1.png")
        scaled_pixmap = pixmap.scaled(
            self.display_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )       
        self.display_label.setPixmap(scaled_pixmap)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        """

 

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.display_label, stretch=1)

        return main_layout
    
    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
        
    def refresh_screens(self):
        """
        Refresh and display newly detected windows
        """
        screens = tools.screen_list()
        self.screen_menu.clear()
        for title in screens:
            if title.strip():
                self.screen_menu.addItem(title)

    def run_OCR_button_clicked(self, button):
        """
        Run OCR
        """
        button.setEnabled(False)                # prevent multiple concurrent triggers
        self.ocr_running = True
        self.start_OCR_signal.emit(self.original_image)

    def process_OCR(self, out_image):
        """
        Process OCR after receiving the results of OCRWorker
        """
        self.ocr_running = False

        # reenable ocr button
        self.ocr_button.setEnabled(True)

        self.ocr_image = out_image
        # TODO: add bounding box labels to image regions
        #self.display_label.setPixmap(QPixmap.fromImage(self.ocr_image))

        pixmap = QPixmap.fromImage(self.ocr_image)
        scaled_pixmap = pixmap.scaled(
            self.display_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.display_label.setPixmap(scaled_pixmap)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)



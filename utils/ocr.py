import easyocr
from PySide6.QtCore import QObject, Signal, Slot, Qt, QRect
from PySide6.QtGui import QImage, QPainter, QColor, QFont, QFontDatabase, QFontMetrics
from .translator import DeepLTranslator
import cv2
import numpy as np


class OCRWorker(QObject):
    """
    Persistent worker to annotate received QImage using EasyOCR

    Emits:
        result_ready (QImage): The image with bounding boxes drawn around detected text.
        finished (): Signal emitted when OCR processing is complete.
        running (): Optional signal indicating OCR is in progress.
    """
    finished = Signal()
    running = Signal()
    result_ready = Signal(QImage)


    def __init__(self):
        self.available_fonts = QFontDatabase().families()
        """
        Initialize the OCRWorker and load EasyOCR model
        OCR model initialized once for performance
        """
        super().__init__()
        self.reader = easyocr.Reader(['ja','en'])
        self.translator = DeepLTranslator()

    @Slot(QImage)
    def run_OCR(self, received_image: QImage):
        """
        Perform OCR on a received QImage and emit the annotated result.
        """

        """
        Alternate I/O Implementation
        result = self.reader.readtext('image.png')
        filtered = [res for res in result if res[2] > 0.9]
        original_image = cv2.imread('image.png')
        """
        # convert QImage to a format suitable for OCR and drawing
        received_image = received_image.convertToFormat(QImage.Format.Format_RGBA8888)
        qimage = received_image.copy()

        # convert to NumPy array for EasyOCR
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        image_arr = np.asarray(ptr, dtype=np.uint8).reshape((height, width, 4))

        ocr_image = cv2.cvtColor(image_arr, cv2.COLOR_RGBA2BGR)
        result = self.reader.readtext(ocr_image)

        texts = [text for _, text, _ in result]
        uniq_order = []
        seen = {}
        for t in texts:
            if t not in seen:
                seen[t] = len(uniq_order)
                uniq_order.append(t)
        # batch translate
        translated_uniq = self.translator.translate_many(uniq_order, target_lang="EN-US")
        translated_texts = [translated_uniq[seen[t]] for t in texts]

        # Paint on the qimage using QPainter
        painter = QPainter(qimage)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        font = QFont("Meiryo", 14)
        painter.setFont(font)

        # draw bounding box around detected text
        for (box, text, conf), translated in zip(result, translated_texts):
            top_left = tuple(map(int, box[0]))
            bottom_right = tuple(map(int, box[2]))
            x, y = top_left
            w = bottom_right[0] - x
            h = bottom_right[1] - y

            painter.setBrush(QColor(0, 0, 0, 200))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(x, y, w, h)

            font_size = 14
            font = QFont("Noto Sans JP" if "Noto Sans JP" in self.available_fonts else "Meiryo", font_size)
            metrics = QFontMetrics(font)

            # shrink font to fit the bounding box
            while (metrics.horizontalAdvance(translated) > w or metrics.height() > h) and font_size > 1:
                font_size -= 1
                font.setPointSize(font_size)
                metrics = QFontMetrics(font)

            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))

            text_rect = QRect(x, y, w, h)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter, translated)

        painter.end()

        self.result_ready.emit(qimage)
        self.finished.emit()
import easyocr
from PySide6.QtCore import QObject, Signal, Slot, Qt, QRect
from PySide6.QtGui import QImage, QPainter, QColor, QFont, QFontDatabase, QFontMetrics
from .translator import DeepLTranslator
import cv2
import torch
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
        if torch.cuda.is_available():
            self.reader = easyocr.Reader(['ja','en'], gpu=True)
        else:
            self.reader = easyocr.Reader(['ja','en'])
        self.translator = DeepLTranslator()

    def paintImage(self, input_image, result, translated_texts):
        qimage = input_image
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
        return qimage
    
    def run(self, image):
        result = self.reader.readtext(image, decoder='greedy', 
                                    text_threshold = 0.5, 
                                    batch_size=16,
                                    detail=1)
        return result
    
    def iou(self, box1, box2):
        x1_min, y1_min = min(p[0] for p in box1), min(p[1] for p in box1)
        x1_max, y1_max = max(p[0] for p in box1), max(p[1] for p in box1)
        x2_min, y2_min = min(p[0] for p in box2), min(p[1] for p in box2)
        x2_max, y2_max = max(p[0] for p in box2), max(p[1] for p in box2)

        inter_w = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
        inter_h = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
        inter = inter_w * inter_h
        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        area2 = (x2_max - x2_min) * (y2_max - y2_min)
        union = area1 + area2 - inter
        return inter / union if union > 0 else 0

    def merge_best_bbox(self, first_result, second_result):
        CONF_FLOOR = 0.4
        merged=[]
        filtered_original_result = [(box, txt, conf) for (box, txt, conf) in first_result if conf >= CONF_FLOOR]
        filtered_grey_result = [(box, txt, conf) for (box, txt, conf) in second_result if conf >= CONF_FLOOR]

        for candidate in filtered_original_result + filtered_grey_result:
            box, txt, conf = candidate
            keep = True
            for i, (m_box, m_txt, m_conf) in enumerate(merged):
                if self.iou(box, m_box) > 0.5:
                    if conf > m_conf:
                        merged[i] = candidate
                    keep = False
                    break
            if keep:
                merged.append(candidate)
        return merged
    
    @Slot(QImage)
    def run_OCR(self, received_image: QImage):
        """
        Perform OCR on a received QImage and emit the annotated result.
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
        grey_image_1_channel = cv2.cvtColor(image_arr, cv2.COLOR_RGBA2GRAY)
        ocr_image_grey = cv2.cvtColor(grey_image_1_channel, cv2.COLOR_GRAY2BGR)



        original_results = self.run(ocr_image)
        grey_results = self.run(ocr_image_grey)

        merged = self.merge_best_bbox(original_results, grey_results)

        texts = [text for _, text, _ in merged]
        uniq_order = []
        seen = {}

        for t in texts:
            if t not in seen:
                seen[t] = len(uniq_order)
                uniq_order.append(t)
        # batch translate
        translated_uniq = self.translator.translate_many(uniq_order, target_lang="EN-US")
        translated_texts = [translated_uniq[seen[t]] for t in texts]

        edited_image = self.paintImage(qimage, merged, translated_texts)

        self.result_ready.emit(edited_image)
        self.finished.emit()
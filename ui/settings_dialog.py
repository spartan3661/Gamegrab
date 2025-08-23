from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QWidget
)
from functools import partial
from PySide6.QtCore import Qt
from utils.key_ring import get_api_key, set_api_key, delete_api_key

class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.create_UI()

    def create_UI(self):
        self.setWindowTitle("Translation Settings")
        self.setModal(True)
        
        self.provider_box = QComboBox()
        self.provider_box.addItems(["DeepL", "Azure", "Google"])

        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_edit.setPlaceholderText("Enter API key for selected provider")
        
        self.create_buttons_and_layouts()

    def toggle_echo(self, show_button):
        self.key_edit.setEchoMode(
            QLineEdit.EchoMode.Normal 
            if self.key_edit.echoMode() == QLineEdit.EchoMode.Password 
            else QLineEdit.EchoMode.Password
        )
        show_button.setText("Hide" if self.key_edit.echoMode() == QLineEdit.EchoMode.Normal else "Show")

    def load_key(self):
        key = get_api_key(self.current_provider())
        if key:
            self.key_edit.setText(key)
            QMessageBox.information(self, "Loaded", "Key loaded from keyring.")
        else:
            QMessageBox.information(self, "Not Found", "No key stored for this provider.")

    def save_key(self):
        key = self.key_edit.text().strip()
        if not key:
            QMessageBox.warning(self, "Empty key", "Pease enter a key before saving.")
            return
        set_api_key(self.current_provider(), key)
        QMessageBox.information(self, "Saved", "Key saved to keyring.")

    def delete_key(self):
        delete_api_key(self.current_provider())
        self.key_edit.clear()
        QMessageBox.information(self, "Deleted", "Key deleted")

    def create_buttons_and_layouts(self):
        show_button = QPushButton("Show")   
        show_button.clicked.connect(partial(self.toggle_echo, show_button))

        load_button = QPushButton("Load")
        save_button = QPushButton("Save")
        delete_button = QPushButton("Delete")
        close_button = QPushButton("Close")
        
        load_button.setToolTip("Loads api key from keyring")

        load_button.clicked.connect(self.load_key)
        save_button.clicked.connect(self.save_key)
        delete_button.clicked.connect(self.delete_key)
        close_button.clicked.connect(self.accept)

        top = QVBoxLayout(self)
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Provider:"))
        row1.addWidget(self.provider_box, 1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("API Key:"))
        row2.addWidget(self.key_edit, 1)
        row2.addWidget(show_button)

        row3 = QHBoxLayout()
        row3.addStretch(1)
        row3.addWidget(load_button)
        row3.addWidget(save_button)
        row3.addWidget(delete_button)
        row3.addWidget(close_button)

        top.addLayout(row1)
        top.addLayout(row2)
        top.addLayout(row3)
        self.setLayout(top)
        self.resize(520, 140)

    def current_provider(self):
        return self.provider_box.currentText()
    

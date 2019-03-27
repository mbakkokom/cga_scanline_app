from typing import List

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, \
                            QPushButton
from PyQt5.QtCore import Qt


class ErrorListDrawer(QWidget):
    """
    `ErrorListDrawer` provides a mean of presenting a list of errors.
    """

    def __init__(self,
                 message: str,
                 errors: List[Exception],
                 parent: QWidget = None):
        super().__init__(parent, Qt.Drawer)
        self.message = message
        self.errors = errors

        self.initUI()

    def initUI(self):
        hl = QVBoxLayout(self)
        msg = QLabel(self.message, self)

        lst = QListWidget(self)
        for i in self.errors:
            lst.addItem(str(i))

        btn = QPushButton("&Ok", self)
        btn.clicked.connect(lambda: self.close())

        hl.addWidget(msg)
        hl.addWidget(lst)
        hl.addWidget(btn)

        self.setWindowModality(Qt.WindowModal)

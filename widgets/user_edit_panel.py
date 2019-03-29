from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout

from helpers.user_edit_tool_helper import UserEditToolHelper


class UserEditPanel(QWidget):
    def __init__(self, editHelper: UserEditToolHelper = None, parent=None):
        super().__init__(parent)
        self.editHelper = editHelper
        self.initUI()

    def initUI(self):
        self.setContentsMargins(0, 0, 0, 0)

        self.buttonLayout = QHBoxLayout(self)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.buttonLayout)

        self.newPointButton = QPushButton(
            "New Point", self
        )
        self.newPointButton.clicked.connect(
            self.editHelper.userRequestNewPoint
        )

        self.deletePointButton = QPushButton(
            "Delete", self
        )
        self.deletePointButton.clicked.connect(
            self.editHelper.userRequestDeletePoint
        )

        self.buttonLayout.addWidget(self.newPointButton)
        self.buttonLayout.addWidget(self.deletePointButton)

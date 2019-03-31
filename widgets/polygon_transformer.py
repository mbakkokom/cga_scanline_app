from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, \
    QLineEdit, QGridLayout, QPushButton
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from helpers.polygon_transformation_helper import \
    IDENTITY_MATRIX, getTranslationMatrix, getScalingMatrix, \
    getRotationMatrix, getSheeringMatrix, matmul33


class PolygonTransformer(QWidget):
    userAcknowledgedTransformation = pyqtSignal(tuple)  # Matix33

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self) -> None:
        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.WindowModal)

        self._mainLayout = QVBoxLayout(self)
        self.setLayout(self._mainLayout)

        # -- Translation
        self._translationGroupBox = QGroupBox("Translate", self)
        self._translationGroupBox.setCheckable(True)
        self._translationGroupBox.setChecked(False)

        self._translationLayout = QGridLayout(self)
        self._translationGroupBox.setLayout(self._translationLayout)

        self._translationXLabel = QLabel("X", self)
        self._translationXText = QLineEdit("0", self)
        # FIXME avoid infinity
        self._translationXText.setValidator(QDoubleValidator(self))

        self._translationLayout.addWidget(self._translationXLabel, 0, 0)
        self._translationLayout.addWidget(self._translationXText, 0, 1)

        self._translationYLabel = QLabel("Y", self)
        self._translationYText = QLineEdit("0", self)
        # FIXME avoid infinity
        self._translationYText.setValidator(QDoubleValidator(self))

        self._translationLayout.addWidget(self._translationYLabel, 1, 0)
        self._translationLayout.addWidget(self._translationYText, 1, 1)

        self._mainLayout.addWidget(self._translationGroupBox)

        # -- Scaling
        self._scalingGroupBox = QGroupBox("Scaling", self)
        self._scalingGroupBox.setCheckable(True)
        self._scalingGroupBox.setChecked(False)

        self._scalingLayout = QGridLayout(self)
        self._scalingGroupBox.setLayout(self._scalingLayout)

        self._scalingXLabel = QLabel("X", self)
        self._scalingXText = QLineEdit("1", self)
        # FIXME avoid infinity
        self._scalingXText.setValidator(QDoubleValidator(self))

        self._scalingLayout.addWidget(self._scalingXLabel, 0, 0)
        self._scalingLayout.addWidget(self._scalingXText, 0, 1)

        self._scalingYLabel = QLabel("Y", self)
        self._scalingYText = QLineEdit("1", self)
        # FIXME avoid infinity
        self._scalingYText.setValidator(QDoubleValidator(self))

        self._scalingLayout.addWidget(self._scalingYLabel, 1, 0)
        self._scalingLayout.addWidget(self._scalingYText, 1, 1)

        self._mainLayout.addWidget(self._scalingGroupBox)

        # -- Rotation
        self._rotationGroupBox = QGroupBox("Rotation", self)
        self._rotationGroupBox.setCheckable(True)
        self._rotationGroupBox.setChecked(False)

        self._rotationLayout = QGridLayout(self)
        self._rotationGroupBox.setLayout(self._rotationLayout)

        self._rotationThetaLabel = QLabel("θ", self)
        self._rotationThetaText = QLineEdit("0", self)
        # FIXME avoid infinity
        self._scalingXText.setValidator(QDoubleValidator(self))

        self._rotationLayout.addWidget(self._rotationThetaLabel, 0, 0)
        self._rotationLayout.addWidget(self._rotationThetaText, 0, 1)

        self._mainLayout.addWidget(self._rotationGroupBox)

        # -- Sheering
        self._sheeringGroupBox = QGroupBox("Sheering", self)
        self._sheeringGroupBox.setCheckable(True)
        self._sheeringGroupBox.setChecked(False)

        self._sheeringLayout = QGridLayout(self)
        self._sheeringGroupBox.setLayout(self._sheeringLayout)

        self._sheeringHLabel = QLabel("H", self)
        self._sheeringHText = QLineEdit("0", self)
        # FIXME avoid infinity
        self._sheeringHText.setValidator(QDoubleValidator(self))

        self._sheeringLayout.addWidget(self._sheeringHLabel, 0, 0)
        self._sheeringLayout.addWidget(self._sheeringHText, 0, 1)

        self._sheeringVLabel = QLabel("V", self)
        self._sheeringVText = QLineEdit("0", self)
        # FIXME avoid infinity
        self._sheeringVText.setValidator(QDoubleValidator(self))

        self._sheeringLayout.addWidget(self._sheeringVLabel, 1, 0)
        self._sheeringLayout.addWidget(self._sheeringVText, 1, 1)

        self._mainLayout.addWidget(self._sheeringGroupBox)

        # --
        self._applyButton = QPushButton("Apply", self)
        self._applyButton.clicked.connect(self.applyTransform)
        self._mainLayout.addWidget(self._applyButton)

    @pyqtSlot()
    def applyTransform(self) -> None:
        # produce transformation matrix
        matrix = IDENTITY_MATRIX

        if self._translationGroupBox.isChecked():
            x, y = self._translationXText.text(), self._translationYText.text()
            if len(x) > 0 and len(y) > 0:
                matrix = matmul33(
                    matrix,
                    getTranslationMatrix(
                        float(x),
                        float(y)
                    )
                )

        if self._scalingGroupBox.isChecked():
            x, y = self._scalingXText.text(), self._scalingYText.text()
            if len(x) > 0 and len(y) > 0:
                matrix = matmul33(
                    matrix,
                    getScalingMatrix(
                        float(x),
                        float(y)
                    )
                )

        if self._rotationGroupBox.isChecked():
            theta = self._rotationThetaText.text()
            if len(theta) > 0:
                matrix = matmul33(
                    matrix,
                    getRotationMatrix(
                        float(theta)
                    )
                )

        if self._sheeringGroupBox.isChecked():
            h, v = self._sheeringHText.text(), self._sheeringVText.text()
            if len(h) > 0 and len(v) > 0:
                matrix = matmul33(
                    matrix,
                    getSheeringMatrix(
                        float(h),
                        float(v)
                    )
                )

        self.close()
        self.userAcknowledgedTransformation.emit(matrix)

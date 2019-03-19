from PyQt5.QtWidgets import QWidget, QListWidget, QListWidgetItem, QMenu, \
                            QAction
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QPoint

from rasterizer.polygon_factory import PolygonFactory


class PolygonList(QListWidget):
    polygonsChanged = pyqtSignal()

    def __init__(self, polygonFactory: PolygonFactory = None,
                 parent: QWidget = None):
        super().__init__(parent)
        self.polygonFactory = polygonFactory

        self.initUI()

    def initUI(self) -> None:
        # -- setup list
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.customContextMenu)
        self.itemSelectionChanged.connect(self.itemSelectionChange)

        # -- context menu
        self._contextMenu = QMenu(self)

        self._contextMenuDelete = QAction("&Delete", self)
        self._contextMenuDelete.setEnabled(False)
        self._contextMenuDelete.setShortcut(Qt.Key_Backspace)  # OS binding?
        self._contextMenuDelete.triggered.connect(self.deleteSelectedPolygons)

        self._contextMenuMoveUp = QAction("Move &Up", self)
        self._contextMenuMoveUp.setEnabled(False)
        self._contextMenuMoveUp.setShortcut(Qt.CTRL | Qt.Key_Up)
        self._contextMenuMoveUp.triggered.connect(self.moveUpSelectedPolygons)

        self._contextMenuMoveDown = QAction("Move &Down", self)
        self._contextMenuMoveDown.setEnabled(False)
        self._contextMenuMoveDown.setShortcut(Qt.CTRL | Qt.Key_Down)
        self._contextMenuMoveDown.triggered.connect(
            self.moveDownSelectedPolygons
        )

        self._contextMenu.addActions([
            self._contextMenuDelete,
            self._contextMenuMoveUp,
            self._contextMenuMoveDown
        ])

        self.addActions([
            self._contextMenuDelete,
            self._contextMenuMoveUp,
            self._contextMenuMoveDown
        ])

    @pyqtSlot(QPoint)
    def customContextMenu(self, pos: QPoint):
        itm = self.itemAt(pos)
        if itm is not None:
            self.itemSelectionChange()
            self._contextMenu.exec(self.mapToGlobal(pos))

    @pyqtSlot()
    def itemSelectionChange(self) -> None:
        # FIXME cannot move up after have gone up and down again.
        sels = self.selectedIndexes()
        ln_ok = len(sels) > 0
        self._contextMenuDelete.setEnabled(ln_ok)
        self._contextMenuMoveUp.setEnabled(ln_ok and sels[0].row() > 0)
        self._contextMenuMoveDown.setEnabled(
            ln_ok and sels[-1].row() < self.model().rowCount() - 1
        )

    @pyqtSlot()
    def polygonsChange(self) -> None:
        self.clear()

        idx = 0
        for p in self.polygonFactory.polygons:
            itm = QListWidgetItem(p.__repr__(), self)
            # itm.setData(Qt.UserRole, idx)
            self.addItem(itm)
            idx += 1

    @pyqtSlot(bool)
    def deleteSelectedPolygons(self, checked: bool) -> None:
        deletes = []

        for i in self.selectedItems():
            idx = self.row(i)
            row = self.takeItem(idx)
            # idx = int(row.data(Qt.UserRole))
            deletes.append(self.polygonFactory.polygons[idx])
            del(row)

        for i in deletes:
            self.polygonFactory.polygons.remove(i)

        self.polygonsChanged.emit()
        # self.polygonsChange()

    @pyqtSlot(bool)
    def moveUpSelectedPolygons(self, checked: bool):
        selectedItems = self.selectedItems()

        if len(selectedItems) != 1:
            return

        sel = selectedItems[0]
        curIndex = self.row(sel)

        if curIndex <= 0:
            return

        cur = self.takeItem(curIndex)

        pIndex = curIndex - 1
        # prev = self.item(pIndex)
        # prev.setData(Qt.UserRole, curIndex)
        # cur.setData(Qt.UserRole, pIndex)

        self.insertItem(pIndex, cur)

        arr = self.polygonFactory.polygons
        arr.insert(pIndex, arr.pop(curIndex))

        self.setCurrentRow(pIndex)

        self.polygonsChanged.emit()
        # self.polygonsChange()

    @pyqtSlot(bool)
    def moveDownSelectedPolygons(self, checked: bool):
        selectedItems = self.selectedItems()

        if len(selectedItems) != 1:
            return

        cur = selectedItems[0]
        curIndex = self.row(cur)

        if curIndex >= self.model().rowCount() - 1:
            return

        nIndex = curIndex + 1
        prev = self.takeItem(nIndex)
        # prev.setData(Qt.UserRole, curIndex)
        # cur.setData(Qt.UserRole, nIndex)

        self.insertItem(curIndex, prev)

        arr = self.polygonFactory.polygons
        arr.insert(curIndex, arr.pop(nIndex))

        self.setCurrentRow(nIndex)

        self.polygonsChanged.emit()
        # self.polygonsChange()

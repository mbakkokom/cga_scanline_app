from PyQt5.QtWidgets import QWidget, QListWidget, QListWidgetItem, QMenu, \
                            QAction
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QPoint

from rasterizer.polygon_helper import PolygonHelper

from helpers.polygon_data_helper import PolygonDataHelper


class PolygonList(QListWidget):
    polygonsChanged = pyqtSignal()
    polygonEditingRequested = pyqtSignal(PolygonHelper)

    def __init__(self, polygonDataHelper: PolygonDataHelper,
                 parent: QWidget = None):
        super().__init__(parent)
        self.polygonDataHelper = polygonDataHelper
        self.polygonDataHelper.polygonChanged.connect(
            self.polygonPropertyChange
        )

        self.initUI()

    def initUI(self) -> None:
        # -- setup list
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.customContextMenu)
        self.itemSelectionChanged.connect(self.itemSelectionChange)

        # -- context menu
        self._contextMenu = QMenu(self)

        self._contextMenuInspect = QAction("In&spect", self)
        self._contextMenuInspect.setEnabled(False)
        self._contextMenuInspect.triggered.connect(
            self.inspectSelectedPolygons
        )

        self._contextMenuEdit = QAction("&Edit", self)
        self._contextMenuEdit.setEnabled(False)
        self._contextMenuEdit.triggered.connect(
            self.editSelectedPolygons
        )

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
            self._contextMenuInspect,
            self._contextMenuEdit,
            self._contextMenuDelete,
            self._contextMenuMoveUp,
            self._contextMenuMoveDown
        ])

        self.addActions([
            self._contextMenuInspect,
            self._contextMenuEdit,
            self._contextMenuDelete,
            self._contextMenuMoveUp,
            self._contextMenuMoveDown
        ])

        self.itemDoubleClicked.connect(self.showItemProperties)

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
        self._contextMenuInspect.setEnabled(ln_ok)
        self._contextMenuEdit.setEnabled(ln_ok)
        self._contextMenuDelete.setEnabled(ln_ok)
        self._contextMenuMoveUp.setEnabled(ln_ok and sels[0].row() > 0)
        self._contextMenuMoveDown.setEnabled(
            ln_ok and sels[-1].row() < self.model().rowCount() - 1
        )

    @pyqtSlot(PolygonHelper, bool)
    def polygonPropertyChange(self, poly: PolygonHelper, needRedraw: bool) \
            -> None:
        if needRedraw:
            self.polygonsChanged.emit()
        else:
            self.polygonsChange()

    @pyqtSlot()
    def polygonsChange(self) -> None:
        self.clear()

        idx = 0
        for p in self.polygonDataHelper.polygonFactory:
            itm = QListWidgetItem(p.__repr__(), self)
            # itm.setData(Qt.UserRole, idx)
            self.addItem(itm)
            idx += 1

    @pyqtSlot(bool)
    def inspectSelectedPolygons(self, checked: bool):
        for itm in self.selectedItems():
            self.showItemProperties(itm)

    @pyqtSlot(bool)
    def editSelectedPolygons(self, checked: bool):
        selectedItems = self.selectedItems()

        if len(selectedItems) != 1:
            return

        idx = self.row(selectedItems[0])

        if idx >= 0:
            poly = self.polygonDataHelper.getPolygon(idx)
            if poly is not None:
                self.polygonEditingRequested.emit(poly)

    @pyqtSlot(bool)
    def deleteSelectedPolygons(self, checked: bool) -> None:
        deletes = []

        for i in self.selectedItems():
            idx = self.row(i)
            row = self.takeItem(idx)
            # idx = int(row.data(Qt.UserRole))
            deletes.append(self.polygonDataHelper.polygonFactory[idx])
            del(row)

        for i in deletes:
            self.polygonDataHelper.removePolygon(i)

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

        arr = self.polygonDataHelper.polygonFactory
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

        arr = self.polygonDataHelper.polygonFactory
        arr.insert(curIndex, arr.pop(nIndex))

        self.setCurrentRow(nIndex)

        self.polygonsChanged.emit()
        # self.polygonsChange()

    @pyqtSlot(QListWidgetItem)
    def showItemProperties(self, item: QListWidgetItem):
        dlg = self.polygonDataHelper.getPropertiesWindowByIndex(
            self.row(item)
        )

        if dlg is not None:
            dlg.show()
            dlg.setFocus()

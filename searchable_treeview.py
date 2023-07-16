from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeView, QLineEdit
from PyQt5.QtCore import QSortFilterProxyModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class RecursiveSortFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, sourceRow, sourceParent):
        if self.filter_accepts_row_itself(sourceRow, sourceParent):
            return True
        if self.filter_accepts_any_parent(sourceRow, sourceParent):
            return True
        return self.filter_accepts_any_child(sourceRow, sourceParent)

    def filter_accepts_row_itself(self, sourceRow, sourceParent):
        return super(RecursiveSortFilterProxyModel, self).filterAcceptsRow(sourceRow, sourceParent)

    def filter_accepts_any_parent(self, sourceRow, sourceParent):
        parent = sourceParent
        while parent.isValid():
            if super(RecursiveSortFilterProxyModel, self).filterAcceptsRow(parent.row(), parent.parent()):
                return True
            parent = parent.parent()
        return False

    def filter_accepts_any_child(self, sourceRow, sourceParent):
        model = self.sourceModel()
        sourceIndex = model.index(sourceRow, self.filterKeyColumn(), sourceParent)
        if sourceIndex.isValid():
            rows = model.rowCount(sourceIndex)
            for i in range(rows):
                if self.filterAcceptsRow(i, sourceIndex):
                    return True
        return False


class TreeViewSearch(QWidget):
    def __init__(self):
        super().__init__()

        self.tree_view = QTreeView()
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.filter)

        self.model = self.create_model()
        self.proxy_model = RecursiveSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.tree_view.setModel(self.proxy_model)

        layout = QVBoxLayout()
        layout.addWidget(self.search_box)
        layout.addWidget(self.tree_view)

        self.setLayout(layout)

    def create_model(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Title'])

        items = ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']

        for item in items:
            parent = QStandardItem(item)
            child = QStandardItem(item + ' - Child')
            parent.appendRow([child])
            model.appendRow(parent)

        return model

    def filter(self, text):
        self.proxy_model.setFilterRegExp(text)
        self.proxy_model.setFilterKeyColumn(0)
        self.tree_view.expandAll()  # expand all branches
        if text == '':
            self.tree_view.collapseAll()  # if search is cleared, collapse all


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = TreeViewSearch()
    window.show()
    sys.exit(app.exec_())

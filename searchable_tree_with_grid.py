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
        model = self.sourceModel()
        for i in range(model.columnCount()):
            if super(RecursiveSortFilterProxyModel, self).filterAcceptsRow(sourceRow, sourceParent):
                return True
        return False

    def filter_accepts_any_parent(self, sourceRow, sourceParent):
        parent = sourceParent
        while parent.isValid():
            if super(RecursiveSortFilterProxyModel, self).filterAcceptsRow(parent.row(), parent.parent()):
                return True
            parent = parent.parent()
        return False

    def filter_accepts_any_child(self, sourceRow, sourceParent):
        model = self.sourceModel()
        sourceIndex = model.index(sourceRow, 0, sourceParent)
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
        model.setHorizontalHeaderLabels(['Title', 'Description', 'ID'])

        items = [('Item 1', 'Description 1', 'ID1'),
                 ('Item 2', 'Description 2', 'ID2'),
                 ('Item 3', 'Description 3', 'ID3'),
                 ('Item 4', 'Description 4', 'ID4'),
                 ('Item 5', 'Description 5', 'ID5')]

        for item in items:
            parent1 = QStandardItem(item[0])
            parent2 = QStandardItem(item[1])
            parent3 = QStandardItem(item[2])
            child1 = QStandardItem(item[0] + ' - Child')
            child2 = QStandardItem(item[1] + ' - Child')
            child3 = QStandardItem(item[2] + ' - Child')
            parent1.appendRow([child1, child2, child3])
            model.appendRow([parent1, parent2, parent3])

        return model

    def filter(self, text):
        self.proxy_model.setFilterRegExp(text)
        self.proxy_model.setFilterKeyColumn(-1)  # search all columns
        self.tree_view.expandAll()  # expand all branches
        if text == '':
            self.tree_view.collapseAll()  # if search is cleared, collapse all


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = TreeViewSearch()
    window.show()
    sys.exit(app.exec_())

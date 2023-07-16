from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeView, QLineEdit, QStyledItemDelegate, QStyle
from PyQt5.QtCore import QSortFilterProxyModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextDocument, QAbstractTextDocumentLayout
from PyQt5.QtCore import QModelIndex, QAbstractItemModel


class HighlightDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(HighlightDelegate, self).__init__(parent)
        self.parent = parent

    def paint(self, painter, option, index):
        model: QAbstractItemModel = index.model()
        filter_text = model.filterRegExp().pattern()

        # Draw selection background if the item is selected
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        # Set the document text
        document = QTextDocument()
        text = index.data(Qt.DisplayRole)
        if filter_text and filter_text in text:
            # Highlight the filter text with HTML
            document.setHtml(text.replace(filter_text, f"<span style='background-color: lightblue;'>{filter_text}</span>"))
        else:
            document.setPlainText(text)

        # Draw the document
        painter.save()
        painter.translate(option.rect.x(), option.rect.y())
        layout = QAbstractTextDocumentLayout.PaintContext()
        if option.state & QStyle.State_Selected:
            layout.palette.setColor(QPalette.Text, option.palette.color(QPalette.Active, QPalette.HighlightedText))
        document.documentLayout().draw(painter, layout)
        painter.restore()


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
        self.tree_view.setSelectionMode(QTreeView.ExtendedSelection)

        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.filter)

        self.model = self.create_model()
        self.proxy_model = RecursiveSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.tree_view.setModel(self.proxy_model)

        self.tree_view.setItemDelegate(HighlightDelegate(self.tree_view))

        self.tree_view.expanded.connect(self.resize_columns)

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

            for branch in range(2):
                branch1 = QStandardItem(f'{item[0]} - Branch {branch}')
                branch2 = QStandardItem(f'{item[1]} - Branch {branch}')
                branch3 = QStandardItem(f'{item[2]} - Branch {branch}')

                for subbranch in range(2):
                    subbranch1 = QStandardItem(f'{item[0]} - Branch {branch} - Subbranch {subbranch}')
                    subbranch2 = QStandardItem(f'{item[1]} - Branch {branch} - Subbranch {subbranch}')
                    subbranch3 = QStandardItem(f'{item[2]} - Branch {branch} - Subbranch {subbranch}')
                    branch1.appendRow([subbranch1, subbranch2, subbranch3])

                parent1.appendRow([branch1, branch2, branch3])
            model.appendRow([parent1, parent2, parent3])

        return model

    def filter(self, text):
        self.proxy_model.setFilterRegExp(text)
        self.proxy_model.setFilterKeyColumn(-1)
        self.tree_view.expandAll()
        if text == '':
            self.tree_view.collapseAll()

    def resize_columns(self):
        for i in range(self.proxy_model.columnCount()):
            self.tree_view.resizeColumnToContents(i)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = TreeViewSearch()
    window.show()
    sys.exit(app.exec_())

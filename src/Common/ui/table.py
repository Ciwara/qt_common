#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad


import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from .util import formatted_number

try:
    basestring
except NameError:
    # Python 3
    basestring = unicode = str
try:
    long
except NameError:
    long = int


class FlexibleTable(QTableWidget):
    pass


class FTableWidget(QTableWidget):
    SCROLL_WIDTH = 100

    def __init__(self, parent):
        QTableWidget.__init__(self, parent=parent)
        self._data = []
        self.hheaders = []  # horizontal headers
        self.vheaders = []  # vertical headers

        self._display_total = False
        self._column_totals = {}
        self._total_label = "TOTAL"

        self.stretch_columns = []
        self.display_hheaders = True
        self.display_vheaders = True
        self.align_map = {}
        self.display_fixed = False
        self.live_refresh = True
        self.sorter = False

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)

        self.cellClicked.connect(self.click_item)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # style au tr
        self.setStyleSheet("color: #2C2C2C;")
        self.setAlternatingRowColors(True)
        self.setAutoScroll(True)
        self.wc = self.width()
        self.hc = self.height()

    def dragMoveEvent(self, e):
        e.accept()

    def _display_fixed():
        def fget(self):
            return self._display_fixed

        def fset(self, value):
            self._display_fixed = value

        return locals()

    display_fixed = property(**_display_fixed())

    def _live_refresh():
        def fget(self):
            return self._live_refresh

        def fset(self, value):
            self._live_refresh = value

        return locals()

    live_refresh = property(**_live_refresh())

    def _sorter():
        def fset(self, value):
            self.setSortingEnabled(value)

        return locals()

    sorter = property(**_sorter())

    def display_hheaders():
        def fget(self):
            return self._display_hheaders

        def fset(self, value):
            self._display_hheaders = value

        def fdel(self):
            del self._display_hheaders

        return locals()

    display_hheaders = property(**display_hheaders())

    def display_vheaders():
        def fget(self):
            return self._display_vheaders

        def fset(self, value):
            self._display_vheaders = value

        def fdel(self):
            del self._display_vheaders

        return locals()

    display_vheaders = property(**display_vheaders())

    def stretch_columns():
        def fget(self):
            return self._stretch_columns

        def fset(self, value):
            self._stretch_columns = value

        def fdel(self):
            del self._stretch_columns

        return locals()

    stretch_columns = property(**stretch_columns())

    def data():
        def fget(self):
            return self._data

        def fset(self, value):
            self._data = value

        def fdel(self):
            del self._data

        return locals()

    data = property(**data())

    def align_map():
        def fget(self):
            return self._align_map

        def fset(self, value):
            self._align_map = value

        def fdel(self):
            del self._align_map

        return locals()

    align_map = property(**align_map())

    def _reset(self):
        for index in range(self.rowCount(), -1, -1):
            self.removeRow(index)

    def resizeEvent(self, event):
        """lancé à chaque redimensionnement de la fenêtre"""
        # trouve les dimensions du container
        self.wc = self.width()
        self.hc = self.height()
        if self.live_refresh:
            self.refresh()

    def refresh(self, resize=False):
        if not self.data:
            return

        # increase rowCount by one if we have to display total row
        rc = self.data.__len__()
        if self._display_total:
            rc += 1
        self.setRowCount(len(self.data))
        self.setColumnCount(len(self.hheaders))
        # self.setHorizontalHeaderLabels(self.hheaders)
        for col in range(len(self.hheaders)):
            self.setHorizontalHeaderItem(col, QTableWidgetItem(self.hheaders[col]))
        # self.setVerticalHeaderLabels(self.vheaders)
        for row in range(len(self.vheaders)):
            self.setVerticalHeaderItem(row, QTableWidgetItem(self.vheaders[row]))

        rowid = 0
        for row in self.data:
            colid = 0
            for item in row:
                # item is already a QTableWidgetItem, display it
                if isinstance(item, QTableWidgetItem):
                    self.setItem(rowid, colid, item)
                # item is QWidget, display it
                elif isinstance(item, QWidget):
                    self.setCellWidget(rowid, colid, item)
                # item is not ready for display, try to format it
                else:
                    ui_item = self._item_for_data(rowid, colid, item, row)

                    # new item is a QTableWidgetItem or QWidget
                    if isinstance(ui_item, QTableWidgetItem):
                        self.setItem(rowid, colid, ui_item)
                    elif isinstance(ui_item, QWidget):
                        self.setCellWidget(rowid, colid, ui_item)
                    # something failed, let's build a QTableWidgetItem
                    else:
                        self.setItem(
                            rowid,
                            colid,
                            QTableWidgetItem(
                                "%s" % ui_item,
                            ),
                        )
                colid += 1
            rowid += 1

        self._display_total_row()

        self.extend_rows()
        self.upd()

        # apply resize rules
        self.apply_resize_rules()

        # only resize columns at initial refresh
        if resize:
            self.resizeColumnsToContents()

    def apply_resize_rules(self):
        if self.display_fixed:
            return

        # set headers visibility according to our prop
        self.verticalHeader().setVisible(self.display_vheaders)
        self.horizontalHeader().setVisible(self.display_hheaders)

        self.max_width = self.wc

        # Pour l'horizontal
        # self.resize(self.max_width, self.size().height())

        contented_width = 0
        for ind in range(0, self.horizontalHeader().count()):
            contented_width += self.horizontalHeader().sectionSize(ind)
        self.verticalHeader().adjustSize()
        # get content-sized with of header
        if self.display_vheaders:
            vheader_width = self.verticalHeader().width()
        else:
            vheader_width = 0
        extra_width = self.max_width - contented_width - vheader_width

        # space filled-up.
        if extra_width:
            remaining_width = extra_width - vheader_width
            try:
                to_stretch = self.stretch_columns
                indiv_extra = int(remaining_width / len(to_stretch))
            except ZeroDivisionError:
                to_stretch = range(0, self.horizontalHeader().count())
                indiv_extra = int(remaining_width / len(to_stretch))
            except:
                indiv_extra = 0

            for colnum in to_stretch:
                self.horizontalHeader().resizeSection(
                    colnum, self.horizontalHeader().sectionSize(colnum) + indiv_extra
                )

        self.horizontalHeader().update()
        self.update()
        # HEIGHT
        rows_with_widgets = []
        for rowid in range(0, len(self.data)):
            for colid in range(0, len(self.data[rowid])):
                # if not isinstance(self.item(rowid, colid), QTableWidgetItem)
                # and not rowid in rows_with_widgets:
                if (
                    isinstance(self.item(rowid, colid), (QPushButton, None.__class__))
                    and not rowid in rows_with_widgets
                ):
                    rows_with_widgets.append(rowid)

    def extend_rows(self):
        """called after cells have been created/refresh.

        Use for adding/editing cells"""
        pass

    def upd(self):
        """called after cells have been created/refresh.

        Use for adding/editing cells"""
        pass

    def data():
        def fget(self):
            return self._data

        def fset(self, value):
            self._data = value

        def fdel(self):
            del self._data

        return locals()

    data = property(**data())

    def _item_for_data(self, row, column, data, context=None):
        if isinstance(data, (basestring, int, float)):
            if column in self.align_map.keys():
                widget = self.widget_from_align(self.align_map[column])
            else:
                widget = FlexibleReadOnlyWidget
            return widget(self._format_for_table(data))
        else:
            return QTableWidgetItem(self._format_for_table(data))

    def _item_for_data_(self, row, column, data, context=None):
        """returns QTableWidgetItem or QWidget to add to a cell"""
        return QTableWidgetItem(self._format_for_table(data))

    def widget_from_align(self, align):
        if align.lower() == "l":
            return FlexibleReadOnlyWidgetAL
        elif align.lower() == "r":
            return FlexibleReadOnlyWidgetAR
        else:
            return FlexibleReadOnlyWidget

    def _display_total_row(self, row_num=None):
        """adds the total row at end of table"""

        # display total row at end of table
        if self._display_total:
            if not row_num:
                row_num = self.data.__len__()

            # spans columns up to first data one
            # add label inside
            label_item = QTableWidgetItem("%s" % self._total_label)
            label_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.setItem(row_num, 0, label_item)
            self.setSpan(row_num, 0, 1, self._column_totals.keys()[0])
            # calculate total for each total column
            # if desired
            for index, total in self._column_totals.items():
                if not total:
                    total = sum([data[index] for data in self.data])
                item = QTableWidgetItem(self._format_for_table(total))
                self.setItem(row_num, index, item)

    def setDisplayTotal(self, display=False, column_totals={}, label=None):
        """ adds an additional row at end of table

        display: bool wheter of not to display the total row
        column_totals: an hash indexed by column number
                       providing data to display as total or None
                       to request automatic calculation
        label: text of first cell (spaned up to first index)
        Example call:
            self.setDisplayTotal(True, \
                                 column_totals={2: None, 3: None}, \
                                 label="TOTALS") """

        self._display_total = display
        self._column_totals = column_totals
        if label:
            self._total_label = label

    def _format_for_table(self, value):
        """formats input value for string in table widget

        override it to add more formats"""
        if isinstance(value, basestring):
            return value
        if isinstance(value, (int, float, long)):
            return formatted_number(value)
        elif isinstance(value, datetime.datetime):
            return value.strftime("%A %d/%m/%Y à %Hh:%Mmn")
        elif isinstance(value, datetime.date):
            return value.strftime("%A %d/%m/%Y")

        if value == None:
            return ""

        return "%s" % value

    def click_item(self, row, column, *args):
        pass


class FlexibleWidget(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super(FlexibleWidget, self).__init__(*args, **kwargs)

        self.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)

    def live_refresh(self):
        pass


class TotalsWidget(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super(TotalsWidget, self).__init__(*args, **kwargs)

        self.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        font = QFont()
        font.setBold(True)
        # font.setWeight(90)
        self.setFont(font)

        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)

    def live_refresh(self):
        pass


class FlexibleReadOnlyWidget(FlexibleWidget):
    def __init__(self, *args, **kwargs):
        super(FlexibleReadOnlyWidget, self).__init__(*args, **kwargs)

        self.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def live_refresh(self):
        pass


class FlexibleReadOnlyWidgetAL(FlexibleReadOnlyWidget):
    def __init__(self, *args, **kwargs):
        super(FlexibleReadOnlyWidgetAL, self).__init__(*args, **kwargs)
        self.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)


class FlexibleReadOnlyWidgetAR(FlexibleReadOnlyWidget):
    def __init__(self, *args, **kwargs):
        super(FlexibleReadOnlyWidgetAR, self).__init__(*args, **kwargs)
        self.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)


class EnterDoesTab(QWidget):
    def keyReleaseEvent(self, event):
        super(EnterDoesTab, self).keyReleaseEvent(event)
        if event.key() == Qt.Key_Return:
            self.focusNextChild()


class EnterTabbedQLabel(QLabel, EnterDoesTab):
    pass

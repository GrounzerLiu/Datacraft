from PySide6.QtCore import QSize, QRect, Qt, QPoint
from PySide6.QtWidgets import QLayout, QLayoutItem, QStyle, QSizePolicy


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, h_spacing=0, v_spacing=0):
        super().__init__(parent)
        self.h_space = h_spacing
        self.v_space = v_spacing
        self.item_list: list[QLayoutItem] = []
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item: QLayoutItem):
        self.item_list.append(item)

    def horizontal_spacing(self) -> int:
        if self.h_space >= 0:
            return self.h_space
        else:
            return self.__smart_spacing(QStyle.PixelMetric.PM_LayoutHorizontalSpacing)

    def vertical_spacing(self) -> int:
        if self.v_space >= 0:
            return self.v_space
        else:
            return self.__smart_spacing(QStyle.PixelMetric.PM_LayoutVerticalSpacing)

    def expandingDirections(self) -> Qt.Orientation:
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        height = self.__do_layout(QRect(0, 0, width, 0), True)
        return height

    def count(self) -> int:
        return len(self.item_list)

    def itemAt(self, index: int) -> QLayoutItem:
        if 0 <= index < len(self.item_list):
            return self.item_list[index]

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().left(), 2 * self.contentsMargins().top())
        return size

    def setGeometry(self, rect: QRect):
        super().setGeometry(rect)
        self.__do_layout(rect, False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def takeAt(self, index: int) -> QLayoutItem:
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)

    def __do_layout(self, rect: QRect, test_only: bool) -> int:
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(+left, +top, -right, -bottom)
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self.item_list:
            widget = item.widget()
            space_x = self.horizontal_spacing()
            if space_x == -1:
                space_x = widget.style().layoutSpacing(QSizePolicy.ControlType.PushButton,
                                                       QSizePolicy.ControlType.PushButton,
                                                       Qt.Orientation.Horizontal)
            space_y = self.vertical_spacing()
            if space_y == -1:
                space_y = widget.style().layoutSpacing(QSizePolicy.ControlType.PushButton,
                                                       QSizePolicy.ControlType.PushButton,
                                                       Qt.Orientation.Vertical)

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y += line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y() + bottom

    def __smart_spacing(self, pm: QStyle.PixelMetric) -> int:
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()
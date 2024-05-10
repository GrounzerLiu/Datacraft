import sys
from PySide6.QtCore import Qt, QEvent, QSize, Slot
from PySide6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, QMainWindow, QPushButton
from markdown2 import Markdown

from home import Ui_Home
from workshop import Ui_workShop
from tool import load_tool_list


class WorkshopWindow(QWidget):
    def __init__(self):
        super().__init__()
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        # self.setFixedSize(800, 100)

    def event(self, event):
        if event.type() == QEvent.Type.WindowDeactivate:
            self.hide()
        return super().event(event)


def init_home_ui(window: QMainWindow):
    home_ui = Ui_Home()
    home_ui.setupUi(window)
    tool_list = load_tool_list()
    model = QStandardItemModel()
    for tool in tool_list:
        if tool.icon is not None:
            icon = tool.icon
        else:
            icon = QIcon("icon/datacraft_icon.svg")
        standard_item = QStandardItem(icon, tool.name)
        standard_item.setEditable(False)
        model.appendRow(standard_item)
    home_ui.tooListView.setModel(model)
    home_ui.tooListView.setIconSize(QSize(32, 32))

    def on_tool_list_view_clicked(index):
        tool = tool_list[index.row()]
        markdown = f"""
# {tool.name}
###### 版本: {tool.version}
###### 作者: {tool.author}

***

{tool.description}
"""
        markdowner = Markdown()
        html = markdowner.convert(markdown)
        home_ui.manifestBrowser.setHtml(html)
        home_ui.manifestBrowser.setVisible(True)
        home_ui.line.setVisible(True)

    home_ui.tooListView.clicked.connect(on_tool_list_view_clicked)

    home_ui.manifestBrowser.setVisible(False)
    home_ui.line.setVisible(False)


def init_workshop_ui(window: WorkshopWindow):
    workshop_ui = Ui_workShop()
    workshop_ui.setupUi(window)

    tools = load_tool_list()

    def on_text_changed(text):
        model = QStandardItemModel()
        for tool in tools:
            if text in tool.name:
                if tool.icon is not None:
                    icon = tool.icon
                else:
                    icon = QIcon("icon/datacraft_icon.svg")
                standard_item = QStandardItem(icon, tool.name)
                standard_item.setEditable(False)
                model.appendRow(standard_item)
        workshop_ui.listView.setModel(model)
        workshop_ui.listView.setIconSize(QSize(32, 32))

    workshop_ui.lineEdit.textChanged.connect(on_text_changed)


def create_tray_icon():
    # 创建 QApplication 实例
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("DataCraft")

    # 创建系统托盘图标
    tray_icon = QSystemTrayIcon(QIcon("icon/datacraft_icon_64.png"), parent=None)

    # 创建一个菜单
    tray_menu = QMenu()
    # 创建一个显示动作
    show_action = QAction("显示")

    workshop = WorkshopWindow()
    init_workshop_ui(workshop)

    # 将动作连接到显示函数
    show_action.triggered.connect(workshop.show)
    # 将动作添加到菜单
    tray_menu.addAction(show_action)

    home_window = QMainWindow()
    init_home_ui(home_window)

    home_action = QAction("主页")
    home_action.triggered.connect(home_window.show)
    tray_menu.addAction(home_action)

    # 创建一个退出动作
    exit_action = QAction("退出")
    # 将动作连接到退出函数
    exit_action.triggered.connect(app.quit)
    # 将动作添加到菜单
    tray_menu.addAction(exit_action)

    # 将菜单设置到托盘图标
    tray_icon.setContextMenu(tray_menu)

    # 显示托盘图标
    tray_icon.show()

    # 运行应用程序
    sys.exit(app.exec())


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = SearchWindow()
#     ui = Ui_Search()
#     ui.setupUi(window)
#     window.show()
#     sys.exit(app.exec())
if __name__ == "__main__":
    create_tray_icon()

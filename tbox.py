import sys
import os
import json
import subprocess
import win32com.client
import winreg
import logging
import keyboard
import time
from PyQt5.QtCore import (
    Qt, QSize, QPropertyAnimation, 
    QEasingCurve, QModelIndex, QPoint,
    QSettings, QTimer, QAbstractNativeEventFilter
)
from PyQt5.QtGui import QFont, QIcon, QColor, QBrush, QMouseEvent, QKeySequence
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QFileDialog, QInputDialog,
    QSplitter, QTabWidget, QLabel, QMessageBox,
    QMenu, QAction, QLineEdit, QListWidgetItem,
    QFrame, QGraphicsDropShadowEffect, QDialog,
    QCheckBox, QKeySequenceEdit, QGroupBox,
    QFormLayout, QComboBox, QSystemTrayIcon,
    QShortcut, QTextEdit
)
from PyQt5.QtNetwork import QLocalSocket, QLocalServer
import win32con
import win32api
import win32gui
import ctypes
from ctypes import wintypes

CONFIG_FILE = "tool_manager_config.json"

STYLE_SHEET = """
/* 现代化纯白透明设计 */
QWidget, QMainWindow {
    background-color: rgba(255, 255, 255, 245);
    color: #2c3e50;
    font-family: 'Microsoft YaHei UI', 'Segoe UI', 'Arial';
    font-size: 14px;
    border: none;
    outline: none;
}

QMainWindow {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 rgba(255, 255, 255, 220),
                stop: 0.5 rgba(248, 250, 252, 230),
                stop: 1 rgba(241, 245, 249, 240));
}

/* 设置对话框样式 */
QDialog {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 rgba(255, 255, 255, 250),
                stop: 1 rgba(248, 250, 252, 250));
    border-radius: 12px;
}

QGroupBox {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(255, 255, 255, 180),
                stop: 1 rgba(248, 250, 252, 200));
    border: 2px solid rgba(226, 232, 240, 150);
    border-radius: 12px;
    margin-top: 20px;
    padding-top: 20px;
    font-weight: 600;
    font-size: 15px;
    color: #1e293b;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 0 10px;
    background-color: rgba(255, 255, 255, 200);
    border-radius: 6px;
}

QFormLayout {
    margin: 10px;
    spacing: 20px;
}

QFormLayout QLabel {
    min-width: 140px;
    font-weight: 500;
    color: #374151;
}

/* 现代化按钮样式 */
QPushButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(59, 130, 246, 220),
                stop: 1 rgba(37, 99, 235, 240));
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    min-width: 100px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(79, 150, 255, 240),
                stop: 1 rgba(59, 130, 246, 250));
    transform: translateY(-1px);
}

QPushButton:pressed {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(29, 78, 216, 240),
                stop: 1 rgba(30, 64, 175, 250));
}

/* 特殊按钮样式 */
QPushButton[class="success"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(34, 197, 94, 220),
                stop: 1 rgba(22, 163, 74, 240));
}

QPushButton[class="success"]:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(54, 217, 114, 240),
                stop: 1 rgba(34, 197, 94, 250));
}

QPushButton[class="danger"] {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(239, 68, 68, 220),
                stop: 1 rgba(220, 38, 38, 240));
}

QPushButton[class="danger"]:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(248, 113, 113, 240),
                stop: 1 rgba(239, 68, 68, 250));
}

QKeySequenceEdit {
    min-width: 220px;
    height: 36px;
    border: 2px solid rgba(226, 232, 240, 150);
    border-radius: 8px;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 200);
    font-size: 14px;
}

QKeySequenceEdit:focus {
    border-color: rgba(59, 130, 246, 200);
    background: rgba(255, 255, 255, 250);
}

QCheckBox {
    spacing: 8px;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
}

QCheckBox::indicator:unchecked {
    border: 2px solid rgba(209, 213, 219, 150);
    background: rgba(255, 255, 255, 200);
    border-radius: 4px;
}

QCheckBox::indicator:checked {
    border: 2px solid rgba(59, 130, 246, 200);
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 rgba(59, 130, 246, 220),
                stop: 1 rgba(37, 99, 235, 240));
    border-radius: 4px;
}

QCheckBox::indicator:checked:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 rgba(79, 150, 255, 240),
                stop: 1 rgba(59, 130, 246, 250));
}

/* 自定义标题栏样式 */
#titleBar {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(255, 255, 255, 230),
                stop: 0.5 rgba(248, 250, 252, 240),
                stop: 1 rgba(241, 245, 249, 250));
    border-bottom: 1px solid rgba(226, 232, 240, 120);
    height: 50px;
}

#titleLabel {
    color: #1e293b;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

#settingsButton, #minimizeButton, #maximizeButton {
    background: rgba(255, 255, 255, 100);
    color: #64748b;
    border: 1px solid rgba(226, 232, 240, 100);
    padding: 8px;
    border-radius: 6px;
    min-width: 36px;
    min-height: 36px;
}

#settingsButton:hover, #minimizeButton:hover, #maximizeButton:hover {
    background: rgba(241, 245, 249, 200);
    border-color: rgba(203, 213, 225, 150);
    color: #475569;
}

#settingsButton:pressed, #minimizeButton:pressed, #maximizeButton:pressed {
    background: rgba(226, 232, 240, 200);
}

#closeButton {
    background: rgba(255, 255, 255, 100);
    color: #64748b;
    border: 1px solid rgba(226, 232, 240, 100);
    padding: 8px;
    border-radius: 6px;
    min-width: 36px;
    min-height: 36px;
}

#closeButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(248, 113, 113, 200),
                stop: 1 rgba(239, 68, 68, 220));
    color: white;
    border-color: rgba(239, 68, 68, 150);
}

#closeButton:pressed {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(220, 38, 38, 220),
                stop: 1 rgba(185, 28, 28, 240));
}

/* 列表样式美化 */
QListWidget {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(255, 255, 255, 200),
                stop: 1 rgba(248, 250, 252, 220));
    border: 2px solid rgba(226, 232, 240, 120);
    border-radius: 12px;
    padding: 8px;
    margin: 8px;
    alternate-background-color: rgba(248, 250, 252, 150);
}

QListWidget::item {
    height: 48px;
    padding: 12px 16px;
    border-bottom: 1px solid rgba(226, 232, 240, 80);
    border-radius: 8px;
    margin: 2px 0;
}

QListWidget::item:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(241, 245, 249, 200),
                stop: 1 rgba(248, 250, 252, 220));
    border: 1px solid rgba(203, 213, 225, 100);
}

QListWidget::item:selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(219, 234, 254, 200),
                stop: 1 rgba(191, 219, 254, 220));
    color: #1e40af;
    border: 1px solid rgba(59, 130, 246, 150);
    font-weight: 600;
}

/* 搜索框美化 */
QLineEdit {
    border: 2px solid rgba(226, 232, 240, 120);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 15px;
    margin: 12px 0;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(255, 255, 255, 200),
                stop: 1 rgba(248, 250, 252, 220));
    color: #374151;
}

QLineEdit:focus {
    border-color: rgba(59, 130, 246, 180);
    background: rgba(255, 255, 255, 250);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 50);
}

QLineEdit::placeholder {
    color: #9ca3af;
    font-style: italic;
}

/* 选项卡美化 */
QTabWidget::pane {
    border: 2px solid rgba(226, 232, 240, 120);
    border-radius: 12px;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(255, 255, 255, 200),
                stop: 1 rgba(248, 250, 252, 220));
    margin-top: 8px;
}

QTabBar::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(241, 245, 249, 200),
                stop: 1 rgba(226, 232, 240, 220));
    border: 1px solid rgba(203, 213, 225, 120);
    color: #64748b;
    padding: 12px 24px;
    margin-right: 6px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(255, 255, 255, 240),
                stop: 1 rgba(248, 250, 252, 250));
    color: #1e40af;
    border-bottom-color: rgba(255, 255, 255, 240);
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(248, 250, 252, 220),
                stop: 1 rgba(241, 245, 249, 240));
    color: #475569;
}

/* 滚动条美化 */
QScrollBar:vertical {
    background: rgba(248, 250, 252, 150);
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(203, 213, 225, 180),
                stop: 1 rgba(156, 163, 175, 200));
    min-height: 40px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(156, 163, 175, 200),
                stop: 1 rgba(107, 114, 128, 220));
}

QScrollBar::add-line:vertical, 
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
}

/* 下拉框美化 */
QComboBox {
    border: 2px solid rgba(226, 232, 240, 120);
    border-radius: 8px;
    padding: 8px 16px;
    min-width: 140px;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(255, 255, 255, 200),
                stop: 1 rgba(248, 250, 252, 220));
    color: #374151;
    font-weight: 500;
}

QComboBox:hover {
    border-color: rgba(203, 213, 225, 150);
    background: rgba(255, 255, 255, 250);
}

QComboBox:focus {
    border-color: rgba(59, 130, 246, 180);
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 30px;
    border-left: 1px solid rgba(226, 232, 240, 120);
    border-radius: 0 8px 8px 0;
}

QComboBox QAbstractItemView {
    border: 2px solid rgba(226, 232, 240, 120);
    border-radius: 8px;
    background: rgba(255, 255, 255, 240);
    padding: 6px;
    outline: 0px;
    selection-background-color: rgba(219, 234, 254, 200);
    selection-color: #1e40af;
    color: #374151;
    margin: 4px 0;
}

QComboBox QAbstractItemView::item {
    height: 36px;
    padding: 0 12px;
    border-radius: 6px;
    margin: 1px;
}

QComboBox QAbstractItemView::item:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(241, 245, 249, 200),
                stop: 1 rgba(248, 250, 252, 220));
}

/* 菜单美化 */
QMenu {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(255, 255, 255, 250),
                stop: 1 rgba(248, 250, 252, 250));
    border: 2px solid rgba(226, 232, 240, 120);
    border-radius: 10px;
    padding: 6px;
}

QMenu::item {
    padding: 10px 20px;
    border: 1px solid transparent;
    border-radius: 6px;
    margin: 2px;
}

QMenu::item:selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(219, 234, 254, 200),
                stop: 1 rgba(191, 219, 254, 220));
    color: #1e40af;
    border-color: rgba(59, 130, 246, 100);
}

/* 主容器美化 */
#appContainer {
    border-radius: 16px;
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 rgba(255, 255, 255, 220),
                stop: 0.5 rgba(248, 250, 252, 240),
                stop: 1 rgba(241, 245, 249, 250));
    border: 1px solid rgba(226, 232, 240, 100);
}

/* 分割线美化 */
QSplitter::handle {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(226, 232, 240, 100),
                stop: 0.5 rgba(203, 213, 225, 120),
                stop: 1 rgba(226, 232, 240, 100));
    width: 2px;
    border-radius: 1px;
}

QSplitter::handle:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(59, 130, 246, 150),
                stop: 0.5 rgba(37, 99, 235, 180),
                stop: 1 rgba(59, 130, 246, 150));
}
"""

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TBox')

def resource_path(relative_path):
    """ 获取资源的绝对路径 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class TitleBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("titleBar")
        self.setFixedHeight(50)  # 增加标题栏高度
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)  # 增加左右边距
        
        # 应用图标
        self.iconLabel = QLabel()
        self.iconLabel.setFixedSize(24, 24)  # 增加图标大小
        icon = QIcon(resource_path("icon.png"))
        pixmap = icon.pixmap(24, 24)
        self.iconLabel.setPixmap(pixmap)
        
        # 标题
        self.titleLabel = QLabel("TBox")
        self.titleLabel.setObjectName("titleLabel")
        
        # 设置按钮
        self.settingsButton = QPushButton()
        self.settingsButton.setObjectName("settingsButton")
        self.settingsButton.setFixedSize(36, 36)  # 增加按钮大小
        self.settingsButton.setIcon(QIcon(resource_path("icons/settings.png")))
        self.settingsButton.setIconSize(QSize(18, 18))  # 增加图标大小
        self.settingsButton.clicked.connect(self.parent.show_settings)
        
        # 窗口控制按钮
        self.minimizeButton = QPushButton()
        self.minimizeButton.setObjectName("minimizeButton")
        self.minimizeButton.setFixedSize(36, 36)
        self.minimizeButton.setIcon(QIcon(resource_path("icons/minimize.png")))
        self.minimizeButton.setIconSize(QSize(18, 18))
        
        self.maximizeButton = QPushButton()
        self.maximizeButton.setObjectName("maximizeButton")
        self.maximizeButton.setFixedSize(36, 36)
        self.maximizeButton.setIcon(QIcon(resource_path("icons/maximize.png")))
        self.maximizeButton.setIconSize(QSize(18, 18))
        
        self.closeButton = QPushButton()
        self.closeButton.setObjectName("closeButton")
        self.closeButton.setFixedSize(36, 36)
        self.closeButton.setIcon(QIcon(resource_path("icons/close.png")))
        self.closeButton.setIconSize(QSize(18, 18))
        
        layout.addWidget(self.iconLabel)
        layout.addWidget(self.titleLabel)
        layout.addStretch()
        layout.addWidget(self.settingsButton)
        layout.addWidget(self.minimizeButton)
        layout.addWidget(self.maximizeButton)
        layout.addWidget(self.closeButton)
        
        # 设置按钮事件
        self.minimizeButton.clicked.connect(self.parent.showMinimized)
        self.maximizeButton.clicked.connect(self.toggleMaximize)
        self.closeButton.clicked.connect(self.parent.close)
        
        self.start = None
        
    def toggleMaximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximizeButton.setIcon(QIcon(resource_path("icons/maximize.png")))
        else:
            self.parent.showMaximized()
            self.maximizeButton.setIcon(QIcon(resource_path("icons/restore.png")))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.pos()
        return super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if self.start and event.buttons() == Qt.LeftButton:
            self.parent.move(self.parent.pos() + event.pos() - self.start)
        return super().mouseMoveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggleMaximize()
        return super().mouseDoubleClickEvent(event)

class EnvironmentSelectionDialog(QDialog):
    def __init__(self, parent=None, environments=None, env_details=None, title="选择环境"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(500, 400)
        self.setStyleSheet(STYLE_SHEET)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        
        # 设置窗口模态
        self.setModal(True)
        
        # 保存环境列表和详细信息
        self.environments = environments or []
        self.env_details = env_details or []
        self.selected_environment = None
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("请选择运行环境:")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # 主要内容区域
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # 左侧：环境列表
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        env_label = QLabel("环境列表:")
        env_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 5px;
            }
        """)
        left_layout.addWidget(env_label)
        
        self.env_list = QListWidget()
        self.env_list.setFixedWidth(200)
        self.env_list.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(255, 255, 255, 240),
                            stop: 1 rgba(248, 250, 252, 250));
                border: 2px solid rgba(226, 232, 240, 150);
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                font-weight: 500;
                color: #374151;
            }
            
            QListWidget::item {
                height: 40px;
                padding: 8px 12px;
                border-radius: 8px;
                margin: 2px 0;
                background: transparent;
                border: 1px solid transparent;
            }
            
            QListWidget::item:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                            stop: 0 rgba(241, 245, 249, 200),
                            stop: 1 rgba(248, 250, 252, 220));
                border: 1px solid rgba(203, 213, 225, 120);
                color: #1e293b;
                font-weight: 500;
            }
            
            QListWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                            stop: 0 rgba(219, 234, 254, 220),
                            stop: 1 rgba(191, 219, 254, 240));
                color: #1e40af;
                border: 1px solid rgba(59, 130, 246, 180);
                font-weight: 600;
            }
            
            QListWidget::item:selected:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                            stop: 0 rgba(219, 234, 254, 240),
                            stop: 1 rgba(191, 219, 254, 260));
                border: 1px solid rgba(59, 130, 246, 200);
                color: #1e40af;
                font-weight: 600;
            }
        """)
        
        # 添加环境到列表
        for env in self.environments:
            item = QListWidgetItem(env)
            item.setToolTip(f"环境: {env}")
            self.env_list.addItem(item)
        
        # 默认选择第一个环境
        if self.env_list.count() > 0:
            self.env_list.setCurrentRow(0)
            self.env_list.setFocus()
        
        # 双击选择环境
        self.env_list.itemDoubleClicked.connect(self.accept_selection)
        
        # 键盘事件处理
        self.env_list.keyPressEvent = self.list_key_press_event
        
        # 选择改变时更新详细信息
        self.env_list.currentItemChanged.connect(self.update_env_details)
        
        left_layout.addWidget(self.env_list)
        
        # 右侧：环境详细信息
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        details_label = QLabel("环境详细信息:")
        details_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 5px;
            }
        """)
        right_layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(255, 255, 255, 240),
                            stop: 1 rgba(248, 250, 252, 250));
                border: 2px solid rgba(226, 232, 240, 150);
                border-radius: 10px;
                padding: 12px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                color: #374151;
                line-height: 1.4;
            }
        """)
        right_layout.addWidget(self.details_text)
        
        # 添加左右布局到主布局
        content_layout.addLayout(left_layout)
        content_layout.addLayout(right_layout)
        layout.addLayout(content_layout)
        
        # 提示信息
        hint_label = QLabel("提示：双击环境名称或按回车键确认选择")
        hint_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6b7280;
                font-style: italic;
                margin-top: 5px;
            }
        """)
        layout.addWidget(hint_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(10)
        
        # 确定按钮
        self.ok_button = QPushButton("确定")
        self.ok_button.setFixedSize(100, 35)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(59, 130, 246, 220),
                            stop: 1 rgba(37, 99, 235, 240));
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(79, 150, 255, 240),
                            stop: 1 rgba(59, 130, 246, 250));
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(29, 78, 216, 240),
                            stop: 1 rgba(30, 64, 175, 250));
            }
        """)
        self.ok_button.clicked.connect(self.accept_selection)
        self.ok_button.setDefault(True)
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedSize(100, 35)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(156, 163, 175, 200),
                            stop: 1 rgba(107, 114, 128, 220));
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(156, 163, 175, 230),
                            stop: 1 rgba(107, 114, 128, 250));
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(75, 85, 99, 220),
                            stop: 1 rgba(55, 65, 81, 240));
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # 设置窗口居中
        self.center_on_parent()
        
        # 初始化详细信息显示
        self.update_env_details()
    
    def update_env_details(self):
        """更新环境详细信息显示"""
        current_item = self.env_list.currentItem()
        if not current_item:
            self.details_text.setHtml("<p style='color: #6b7280; font-style: italic;'>请选择一个环境查看详细信息</p>")
            return
        
        env_name = current_item.text()
        
        # 查找对应的环境详细信息
        env_info = None
        for env in self.env_details:
            if env.get("display_name") == env_name:
                env_info = env
                break
        
        if env_info:
            # 格式化环境信息
            details_html = f"""
            <div style='font-family: "Segoe UI", sans-serif; line-height: 1.6;'>
                <h3 style='color: #1e40af; margin-bottom: 15px; font-size: 16px;'>
                    🔧 {env_name}
                </h3>
                
                <div style='margin-bottom: 12px;'>
                    <strong style='color: #374151;'>📁 路径:</strong><br>
                    <span style='color: #6b7280; font-family: monospace; font-size: 12px; background: rgba(243, 244, 246, 0.8); padding: 2px 6px; border-radius: 4px;'>
                        {env_info.get("path", "未知")}
                    </span>
                </div>
                
                <div style='margin-bottom: 12px;'>
                    <strong style='color: #374151;'>📊 状态:</strong>
                    <span style='color: {"#10b981" if os.path.exists(env_info.get("path", "")) else "#ef4444"}; font-weight: 600;'>
                        {"✅ 可用" if os.path.exists(env_info.get("path", "")) else "❌ 不可用"}
                    </span>
                </div>
                
                <div style='margin-bottom: 12px;'>
                    <strong style='color: #374151;'>🏷️ 类型:</strong>
                    <span style='color: #6b7280;'>
                        {"Python 环境" if "python" in env_info.get("path", "").lower() else "Java 环境" if "java" in env_info.get("path", "").lower() else "其他环境"}
                    </span>
                </div>
                
                <div style='margin-bottom: 12px;'>
                    <strong style='color: #374151;'>📝 说明:</strong><br>
                    <span style='color: #6b7280; font-style: italic;'>
                        {env_info.get("description", "此环境用于运行相应类型的工具程序")}
                    </span>
                </div>
            </div>
            """
        else:
            details_html = f"""
            <div style='font-family: "Segoe UI", sans-serif; line-height: 1.6;'>
                <h3 style='color: #1e40af; margin-bottom: 15px; font-size: 16px;'>
                    🔧 {env_name}
                </h3>
                
                <div style='margin-bottom: 12px;'>
                    <span style='color: #6b7280; font-style: italic;'>
                        暂无详细信息
                    </span>
                </div>
            </div>
            """
        
        self.details_text.setHtml(details_html)
    
    def list_key_press_event(self, event):
        """处理列表的键盘事件"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.accept_selection()
        elif event.key() == Qt.Key_Escape:
            self.reject()
        else:
            # 调用原始的键盘事件处理
            QListWidget.keyPressEvent(self.env_list, event)
    
    def center_on_parent(self):
        """将对话框居中显示在父窗口上"""
        if self.parent():
            parent_rect = self.parent().geometry()
            dialog_rect = self.geometry()
            
            x = parent_rect.x() + (parent_rect.width() - dialog_rect.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - dialog_rect.height()) // 2
            
            self.move(x, y)
    
    def accept_selection(self):
        """接受当前选择的环境"""
        current_item = self.env_list.currentItem()
        if current_item:
            self.selected_environment = current_item.text()
            self.accept()
        else:
            QMessageBox.warning(self, "警告", "请先选择一个环境！")
    
    def get_selected_environment(self):
        """获取选择的环境"""
        return self.selected_environment


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setFixedSize(500, 450)  # 增加对话框大小
        self.setStyleSheet(STYLE_SHEET)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        
        # 保存原始设置值，用于检测变化
        self.original_startup = self.is_startup_enabled()
        self.original_hotkey = self.get_hotkey()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 启动设置
        startup_group = QGroupBox("启动设置")
        startup_layout = QFormLayout()
        startup_layout.setContentsMargins(15, 15, 15, 15)
        startup_layout.setSpacing(15)
        startup_layout.setLabelAlignment(Qt.AlignLeft)  # 左对齐标签
        
        self.startup_checkbox = QCheckBox("开机自动启动")
        self.startup_checkbox.setChecked(self.original_startup)
        self.startup_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                padding: 5px;
            }
        """)
        startup_layout.addRow("", self.startup_checkbox)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # 快捷键设置
        hotkey_group = QGroupBox("快捷键设置")
        hotkey_layout = QFormLayout()
        hotkey_layout.setContentsMargins(15, 15, 15, 15)
        hotkey_layout.setSpacing(15)
        hotkey_layout.setLabelAlignment(Qt.AlignLeft)  # 左对齐标签
        
        # 快捷键输入框容器
        hotkey_container = QHBoxLayout()
        hotkey_container.setSpacing(10)
        
        self.hotkey_edit = QKeySequenceEdit()
        self.hotkey_edit.setKeySequence(QKeySequence(self.original_hotkey))
        self.hotkey_edit.setMinimumWidth(200)  # 设置最小宽度
        
        # 测试按钮
        self.test_hotkey_btn = QPushButton("测试")
        self.test_hotkey_btn.setFixedWidth(60)
        self.test_hotkey_btn.setFixedHeight(32)
        self.test_hotkey_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(34, 197, 94, 200),
                            stop: 1 rgba(22, 163, 74, 220));
                font-size: 12px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(54, 217, 114, 230),
                            stop: 1 rgba(34, 197, 94, 240));
            }
        """)
        self.test_hotkey_btn.clicked.connect(self.test_hotkey)
        
        hotkey_container.addWidget(self.hotkey_edit)
        hotkey_container.addWidget(self.test_hotkey_btn)
        
        # 添加快捷键说明
        hotkey_info = QLabel("提示：建议使用 Ctrl+Alt+字母 组合")
        hotkey_info.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12px;
                font-style: italic;
                margin-top: 5px;
            }
        """)
        
        hotkey_widget = QWidget()
        hotkey_widget.setLayout(hotkey_container)
        
        hotkey_layout.addRow("显示/隐藏快捷键:", hotkey_widget)
        hotkey_layout.addRow("", hotkey_info)
        
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)
        button_layout.setSpacing(15)
        
        # 重置按钮
        reset_btn = QPushButton("重置")
        reset_btn.setFixedWidth(100)
        reset_btn.setFixedHeight(35)
        reset_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(156, 163, 175, 200),
                            stop: 1 rgba(107, 114, 128, 220));
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(156, 163, 175, 230),
                            stop: 1 rgba(107, 114, 128, 250));
            }
        """)
        reset_btn.clicked.connect(self.reset_settings)
        
        save_btn = QPushButton("保存")
        save_btn.setFixedWidth(120)
        save_btn.setFixedHeight(35)
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedWidth(120)
        cancel_btn.setFixedHeight(35)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_hotkey(self):
        settings = QSettings("TBox", "TBox")
        return settings.value("hotkey", "Ctrl+Alt+T")
    
    def is_startup_enabled(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, "TBox")
                return True
            except WindowsError:
                return False
            finally:
                winreg.CloseKey(key)
        except WindowsError:
            return False
    
    def set_startup(self, enabled):
        """设置开机启动"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_SET_VALUE)
            try:
                if enabled:
                    # 获取当前程序路径
                    exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
                    winreg.SetValueEx(key, "TBox", 0, winreg.REG_SZ, exe_path)
                    logger.info(f"已设置开机启动: {exe_path}")
                else:
                    try:
                        winreg.DeleteValue(key, "TBox")
                        logger.info("已取消开机启动")
                    except WindowsError:
                        pass  # 键不存在，忽略错误
                return True
            finally:
                winreg.CloseKey(key)
        except Exception as e:
            logger.error(f"设置开机启动失败: {str(e)}")
            return False
    
    def reset_settings(self):
        """重置设置到默认值"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要重置所有设置到默认值吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.startup_checkbox.setChecked(False)
            self.hotkey_edit.setKeySequence(QKeySequence("Ctrl+Alt+T"))
    
    def test_hotkey(self):
        """测试快捷键设置"""
        try:
            hotkey = self.hotkey_edit.keySequence().toString()
            if not hotkey or hotkey.strip() == "":
                QMessageBox.warning(self, "错误", "请先设置快捷键！")
                return
            
            # 显示测试提示
            reply = QMessageBox.question(
                self, "测试快捷键", 
                f"即将测试快捷键: {hotkey}\n\n点击确定后，请按下该快捷键组合进行测试。\n如果快捷键有效，将会显示确认消息。",
                QMessageBox.Ok | QMessageBox.Cancel
            )
            
            if reply != QMessageBox.Ok:
                return
            
            # 创建临时的快捷键处理器进行测试
            from PyQt5.QtCore import QTimer
            
            # 创建一个简单的测试回调
            def test_callback():
                QMessageBox.information(self, "测试成功", "快捷键响应正常！")
                if hasattr(self, 'test_handler'):
                    self.test_handler.cleanup()
            
            self.test_handler = GlobalHotkey(test_callback)
            
            # 尝试注册快捷键
            if self.test_handler.register_hotkey(hotkey):
                # 安装事件过滤器进行测试
                QApplication.instance().installNativeEventFilter(self.test_handler)
                
                # 设置定时器，10秒后自动清理测试
                self.test_timer = QTimer()
                self.test_timer.setSingleShot(True)
                self.test_timer.timeout.connect(self.cleanup_test)
                self.test_timer.start(10000)  # 10秒后清理
                
                QMessageBox.information(
                    self, "测试就绪", 
                    f"快捷键 '{hotkey}' 已就绪！\n请在10秒内按下该快捷键进行测试。"
                )
            else:
                QMessageBox.warning(
                    self, "测试失败", 
                    f"快捷键 '{hotkey}' 无法使用！\n可能已被其他程序占用，请尝试其他组合。"
                )
                
        except Exception as e:
            logger.error(f"测试快捷键时发生错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"测试快捷键时发生错误: {str(e)}")
    
    def cleanup_test(self):
        """清理测试用的快捷键"""
        try:
            if hasattr(self, 'test_handler'):
                QApplication.instance().removeNativeEventFilter(self.test_handler)
                self.test_handler.cleanup()
                delattr(self, 'test_handler')
            if hasattr(self, 'test_timer'):
                self.test_timer.stop()
                delattr(self, 'test_timer')
        except Exception as e:
            logger.warning(f"清理测试快捷键时发生错误: {str(e)}")
    
    def show_test_message(self):
        """显示测试消息"""
        QMessageBox.information(self, "快捷键测试", "快捷键响应正常！")
    
    def has_settings_changed(self):
        """检查设置是否发生变化"""
        current_startup = self.startup_checkbox.isChecked()
        current_hotkey = self.hotkey_edit.keySequence().toString()
        
        return (current_startup != self.original_startup or 
                current_hotkey != self.original_hotkey)
    
    def save_settings(self):
        try:
            # 检查设置是否发生变化
            if not self.has_settings_changed():
                QMessageBox.information(self, "提示", "设置没有变化，无需保存")
                return
            
            startup_enabled = self.startup_checkbox.isChecked()
            hotkey = self.hotkey_edit.keySequence().toString()
            
            # 验证快捷键格式
            if not hotkey or hotkey.strip() == "":
                QMessageBox.warning(self, "错误", "快捷键不能为空！")
                return
            
            # 保存开机启动设置
            if startup_enabled != self.original_startup:
                if not self.set_startup(startup_enabled):
                    QMessageBox.warning(self, "警告", "开机启动设置失败，但其他设置已保存")
                else:
                    if startup_enabled:
                        QMessageBox.information(self, "成功", "已启用开机自动启动")
                    else:
                        QMessageBox.information(self, "成功", "已取消开机自动启动")
            
            # 保存快捷键设置
            if hotkey != self.original_hotkey:
                settings = QSettings("TBox", "TBox")
                settings.setValue("hotkey", hotkey)
                logger.info(f"已保存快捷键设置: {hotkey}")
            
            self.accept()
            
        except Exception as e:
            logger.error(f"保存设置时发生错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"设置保存失败: {str(e)}")
    
    def closeEvent(self, event):
        """处理对话框关闭事件，检查未保存的更改"""
        try:
            # 清理测试用的快捷键
            self.cleanup_test()
            
            if self.has_settings_changed():
                reply = QMessageBox.question(
                    self, "未保存的更改", 
                    "设置已修改但未保存，确定要关闭吗？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    event.ignore()
                    return
            event.accept()
        except Exception as e:
            logger.error(f"关闭设置对话框时发生错误: {str(e)}")
            event.accept()


class HotkeyManager:
    """全局快捷键管理器，防止重复注册"""
    _instance = None
    _registered_hotkeys = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._registered_hotkeys = {}
            logger.info("初始化全局快捷键管理器")
    
    def is_registered(self, hotkey_sequence):
        """检查快捷键是否已注册"""
        return hotkey_sequence in self._registered_hotkeys
    
    def register_hotkey(self, hotkey_sequence, hotkey_id):
        """注册快捷键"""
        if hotkey_sequence in self._registered_hotkeys:
            logger.warning(f"快捷键 {hotkey_sequence} 已在管理器中注册")
            return False
        
        self._registered_hotkeys[hotkey_sequence] = hotkey_id
        logger.info(f"快捷键 {hotkey_sequence} 已注册到管理器，ID: {hotkey_id}")
        return True
    
    def unregister_hotkey(self, hotkey_sequence):
        """注销快捷键"""
        if hotkey_sequence in self._registered_hotkeys:
            hotkey_id = self._registered_hotkeys.pop(hotkey_sequence)
            logger.info(f"快捷键 {hotkey_sequence} 已从管理器中注销，ID: {hotkey_id}")
            return hotkey_id
        return None
    
    def cleanup_all(self):
        """清理所有注册的快捷键"""
        for hotkey_sequence, hotkey_id in self._registered_hotkeys.items():
            try:
                win32gui.UnregisterHotKey(None, hotkey_id)
                logger.info(f"清理快捷键: {hotkey_sequence}, ID: {hotkey_id}")
            except Exception as e:
                logger.warning(f"清理快捷键 {hotkey_sequence} 时发生错误: {str(e)}")
        
        self._registered_hotkeys.clear()
        logger.info("已清理所有快捷键")


class GlobalHotkey(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.hotkey_id = None
        self.registered = False
        self.current_hotkey = None
        self.hotkey_manager = HotkeyManager()
        
    def cleanup(self):
        """清理已注册的快捷键"""
        if self.registered and self.hotkey_id is not None and self.current_hotkey is not None:
            try:
                # 从管理器中注销
                self.hotkey_manager.unregister_hotkey(self.current_hotkey)
                
                # 从系统中注销
                result = win32gui.UnregisterHotKey(None, self.hotkey_id)
                if result != 0:
                    logger.info(f"成功注销快捷键 ID: {self.hotkey_id}")
                else:
                    error_code = win32api.GetLastError()
                    logger.warning(f"注销快捷键失败，错误代码: {error_code}")
                
                self.registered = False
                self.hotkey_id = None
                self.current_hotkey = None
            except Exception as e:
                logger.warning(f"注销快捷键时发生错误: {str(e)}")
                self.registered = False
                self.hotkey_id = None
                self.current_hotkey = None
        else:
            logger.info("快捷键未注册，无需清理")
        
    def register_hotkey(self, key_sequence):
        try:
            # 如果要注册的快捷键和当前相同，无需重复注册
            if self.registered and self.current_hotkey == key_sequence:
                logger.info(f"快捷键 {key_sequence} 已注册，无需重复注册")
                return True
            
            # 检查管理器中是否已注册
            if self.hotkey_manager.is_registered(key_sequence):
                logger.warning(f"快捷键 {key_sequence} 已被其他实例注册")
                return False
            
            # 先清理旧的快捷键
            self.cleanup()
            
            # 生成新的快捷键ID（使用时间戳确保唯一性）
            self.hotkey_id = int(time.time() * 1000) % 0xFFFF
            
            # 解析快捷键
            modifiers = 0
            key = 0
            
            # 将快捷键字符串转换为大写并分割
            key_parts = [part.strip().upper() for part in key_sequence.split("+")]
            logger.info(f"解析快捷键: {key_parts}")
            
            # 处理修饰键
            for part in key_parts[:-1]:  # 最后一个部分是实际按键
                if part == "CTRL":
                    modifiers |= win32con.MOD_CONTROL
                elif part == "ALT":
                    modifiers |= win32con.MOD_ALT
                elif part == "SHIFT":
                    modifiers |= win32con.MOD_SHIFT
                elif part == "WIN":
                    modifiers |= win32con.MOD_WIN
            
            # 处理实际按键
            last_key = key_parts[-1]
            if len(last_key) == 1:  # 字母键
                key = ord(last_key)
            elif last_key.startswith("F"):  # 功能键
                try:
                    key = getattr(win32con, f"VK_F{last_key[1:]}")
                except AttributeError:
                    raise Exception(f"不支持的功能键: {last_key}")
            else:
                raise Exception(f"不支持的按键: {last_key}")
            
            logger.info(f"注册快捷键 - ID: {self.hotkey_id}, 修饰键: {modifiers}, 按键: {key}")
            
            # 注册新的快捷键，尝试多次以处理ID冲突
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    result = win32gui.RegisterHotKey(None, self.hotkey_id, modifiers, key)
                    if result != 0:
                        # 注册到管理器
                        if self.hotkey_manager.register_hotkey(key_sequence, self.hotkey_id):
                            logger.info(f"成功注册快捷键 ID: {self.hotkey_id}")
                            self.registered = True
                            self.current_hotkey = key_sequence
                            return True
                        else:
                            # 管理器注册失败，注销系统快捷键
                            win32gui.UnregisterHotKey(None, self.hotkey_id)
                            raise Exception("快捷键管理器注册失败")
                    else:
                        error_code = win32api.GetLastError()
                        if error_code == 1409:  # ERROR_HOTKEY_ALREADY_REGISTERED
                            if attempt < max_retries - 1:
                                # 如果是ID冲突，尝试新的ID
                                self.hotkey_id = (self.hotkey_id + 1) % 0xFFFF
                                logger.warning(f"快捷键ID冲突，尝试新ID: {self.hotkey_id}")
                                continue
                            else:
                                raise Exception("快捷键已被其他程序占用，请选择其他快捷键")
                        else:
                            error_msg = win32api.FormatMessage(error_code)
                            raise Exception(f"注册快捷键失败 (错误代码: {error_code}): {error_msg}")
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"注册快捷键失败: {str(e)}")
                        return False
                    else:
                        logger.warning(f"注册快捷键失败，重试中: {str(e)}")
                        continue
            
            return False
            
        except Exception as e:
            logger.error(f"注册全局快捷键失败: {str(e)}")
            return False
    
    def nativeEventFilter(self, eventType, message):
        try:
            if eventType == "windows_generic_MSG":
                msg = ctypes.wintypes.MSG.from_address(message.__int__())
                if msg.message == win32con.WM_HOTKEY:
                    if msg.wParam == self.hotkey_id:
                        logger.info("检测到快捷键触发")
                        self.callback()
                        return True, 0
            return False, 0
        except Exception as e:
            logger.error(f"处理全局快捷键事件失败: {str(e)}")
            return False, 0

class ToolManagerApp(QMainWindow):
    def __init__(self):
        try:
            super().__init__(None, Qt.FramelessWindowHint)
            logger.info("初始化主窗口")
            
            # 设置窗口图标
            self.setWindowIcon(QIcon(resource_path("icon.png")))
            
            self.setWindowTitle("TBox")
            self.setGeometry(200, 200, 1200, 800)
            
            # 快捷键状态控制
            self.hotkey_enabled = True
            
            # 创建阴影效果
            self.shadow = QGraphicsDropShadowEffect(self)
            self.shadow.setBlurRadius(30)  # 增加模糊半径
            self.shadow.setColor(QColor(0, 0, 0, 100))  # 增加阴影透明度
            self.shadow.setOffset(0, 8)  # 增加阴影偏移
            
            # 创建容器部件，应用阴影效果
            self.container = QWidget(self)
            self.container.setObjectName("appContainer")
            self.container.setGraphicsEffect(self.shadow)
            
            # 设置主布局
            self.container_layout = QVBoxLayout(self.container)
            self.container_layout.setContentsMargins(0, 0, 0, 0)
            self.container_layout.setSpacing(0)
            
            # 添加自定义标题栏
            self.title_bar = TitleBar(self)
            self.container_layout.addWidget(self.title_bar)
            
            # 主内容区域
            self.main_content = QWidget()
            self.main_layout = QVBoxLayout(self.main_content)
            self.main_layout.setContentsMargins(25, 25, 25, 25)  # 增加边距
            self.main_layout.setSpacing(20)  # 增加间距
            self.container_layout.addWidget(self.main_content)
            
            # 设置容器为中央部件
            self.setCentralWidget(self.container)
            
            # 设置样式表
            self.setStyleSheet(STYLE_SHEET)
            
            self.setAttribute(Qt.WA_TranslucentBackground)
            
            self.environments = []
            self.categories = {}
            self.shortcut_dirs = []
            self.categories_order = []
            self.search_keyword = ""
            
            self.load_config()
            self.init_ui()
            self.setup_connections()
            self.fade_in_animation()
            
            # 设置定时器检查窗口状态
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.check_window_state)
            self.timer.start(100)  # 每100ms检查一次
            
            # 设置系统托盘
            self.setup_tray()
            
            # 设置全局快捷键
            self.setup_hotkey()
            
            logger.info("主窗口初始化完成")
            
        except Exception as e:
            logger.error(f"初始化主窗口时发生错误: {str(e)}")
            QMessageBox.critical(None, "错误", f"程序启动失败: {str(e)}")
            sys.exit(1)

    def setup_tray(self):
        try:
            logger.info("设置系统托盘")
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(resource_path("icon.png")))
            
            # 创建托盘菜单
            tray_menu = QMenu()
            
            show_action = QAction("显示", self)
            show_action.triggered.connect(self.show_window)
            tray_menu.addAction(show_action)
            
            settings_action = QAction("设置", self)
            settings_action.triggered.connect(self.show_settings)
            tray_menu.addAction(settings_action)
            
            tray_menu.addSeparator()
            
            quit_action = QAction("退出", self)
            quit_action.triggered.connect(self.quit_application)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
            # 托盘图标点击事件
            self.tray_icon.activated.connect(self.tray_icon_activated)
            logger.info("系统托盘设置完成")
            
        except Exception as e:
            logger.error(f"设置系统托盘时发生错误: {str(e)}")
            QMessageBox.warning(self, "警告", "系统托盘设置失败，程序将继续运行")
    
    def tray_icon_activated(self, reason):
        try:
            if reason == QSystemTrayIcon.Trigger:
                self.toggle_window()
        except Exception as e:
            logger.error(f"处理托盘图标点击时发生错误: {str(e)}")
    
    def show_window(self):
        try:
            self.showNormal()
            self.activateWindow()
            logger.info("显示主窗口")
        except Exception as e:
            logger.error(f"显示窗口时发生错误: {str(e)}")
    
    def quit_application(self):
        try:
            logger.info("退出应用程序")
            
            # 清理快捷键
            if hasattr(self, 'hotkey_handler'):
                try:
                    self.hotkey_handler.cleanup()
                    QApplication.instance().removeNativeEventFilter(self.hotkey_handler)
                    logger.info("已清理快捷键处理器")
                except Exception as e:
                    logger.warning(f"清理快捷键处理器时发生错误: {str(e)}")
            
            # 隐藏托盘图标
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
            
            # 停止定时器
            if hasattr(self, 'timer'):
                self.timer.stop()
            
            QApplication.quit()
            
        except Exception as e:
            logger.error(f"退出应用程序时发生错误: {str(e)}")
            sys.exit(1)
    
    def check_window_state(self):
        try:
            if not self.isActiveWindow() and self.isVisible():
                self.hide()
        except Exception as e:
            logger.error(f"检查窗口状态时发生错误: {str(e)}")
    
    def toggle_window(self):
        try:
            if self.isVisible():
                if self.isActiveWindow():
                    self.hide()
                    logger.info("隐藏主窗口")
                else:
                    self.activateWindow()
                    self.showNormal()
                    self.raise_()
                    logger.info("激活主窗口")
            else:
                self.showNormal()
                self.activateWindow()
                self.raise_()
                logger.info("显示主窗口")
        except Exception as e:
            logger.error(f"切换窗口状态时发生错误: {str(e)}")
    
    def closeEvent(self, event):
        try:
            logger.info("处理窗口关闭事件")
            self.hide()
            event.ignore()
        except Exception as e:
            logger.error(f"处理窗口关闭事件时发生错误: {str(e)}")
            event.accept()

    def show_settings(self):
        try:
            # 获取设置前的快捷键
            old_hotkey = QSettings("TBox", "TBox").value("hotkey", "Ctrl+Alt+T")
            
            # 禁用快捷键响应
            self.hotkey_enabled = False
            logger.info("设置对话框打开，已禁用快捷键响应")
            
            dialog = SettingsDialog(self)
            result = dialog.exec_()
            
            # 恢复快捷键响应
            self.hotkey_enabled = True
            logger.info("设置对话框关闭，已恢复快捷键响应")
            
            if result == QDialog.Accepted:
                # 获取设置后的快捷键
                new_hotkey = QSettings("TBox", "TBox").value("hotkey", "Ctrl+Alt+T")
                
                # 如果快捷键发生了变化，重新注册
                if old_hotkey != new_hotkey:
                    logger.info(f"快捷键已更改: {old_hotkey} -> {new_hotkey}")
                    
                    # 重新设置快捷键（会自动清除旧的绑定）
                    success = self.setup_hotkey()
                    if success:
                        QMessageBox.information(self, "成功", f"快捷键已更新为: {new_hotkey}")
                    else:
                        QMessageBox.warning(self, "警告", f"新快捷键设置失败，请尝试其他组合")
                        # 如果新快捷键设置失败，尝试恢复旧快捷键
                        settings = QSettings("TBox", "TBox")
                        settings.setValue("hotkey", old_hotkey)
                        self.setup_hotkey()
                
                logger.info("设置已应用")
            else:
                logger.info("用户取消了设置")
                
        except Exception as e:
            # 确保在异常情况下也能恢复快捷键响应
            self.hotkey_enabled = True
            logger.error(f"显示设置对话框时发生错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"设置处理失败: {str(e)}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.isMaximized():
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            
    def fade_in_animation(self):
        # 窗口淡入动画
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)  # 增加动画时长
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutQuart)  # 使用更优雅的缓动曲线
        self.anim.start()
        
        # 可选：添加缩放动画
        self.scale_anim = QPropertyAnimation(self, b"geometry")
        self.scale_anim.setDuration(500)
        current_geo = self.geometry()
        # 从稍小的尺寸开始
        start_geo = current_geo.adjusted(50, 50, -50, -50)
        self.scale_anim.setStartValue(start_geo)
        self.scale_anim.setEndValue(current_geo)
        self.scale_anim.setEasingCurve(QEasingCurve.OutQuart)
        self.scale_anim.start()

    def init_ui(self):
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("全局搜索工具（支持模糊匹配）...")
        self.main_layout.addWidget(self.search_input)
        
        splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(splitter)
        
        # 左侧分类面板
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # 分类搜索框容器
        category_search_container = QWidget()
        category_search_layout = QHBoxLayout(category_search_container)
        category_search_layout.setContentsMargins(0, 0, 0, 0)
        category_search_layout.setSpacing(5)
        
        self.category_search_input = QLineEdit()
        self.category_search_input.setPlaceholderText("搜索分类...")
        self.category_search_input.setStyleSheet("""
            QLineEdit {
                margin: 8px 0;
                padding: 8px 12px;
                font-size: 13px;
                border-radius: 8px;
            }
        """)
        
        # 清空搜索按钮
        self.clear_category_search_btn = QPushButton("×")
        self.clear_category_search_btn.setFixedSize(28, 28)
        self.clear_category_search_btn.setStyleSheet("""
            QPushButton {
                background: rgba(156, 163, 175, 150);
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 16px;
                font-weight: bold;
                margin: 8px 0;
            }
            QPushButton:hover {
                background: rgba(107, 114, 128, 180);
            }
            QPushButton:pressed {
                background: rgba(75, 85, 99, 200);
            }
        """)
        self.clear_category_search_btn.clicked.connect(self.clear_category_search)
        self.clear_category_search_btn.setVisible(False)  # 初始隐藏
        
        category_search_layout.addWidget(self.category_search_input)
        category_search_layout.addWidget(self.clear_category_search_btn)
        left_layout.addWidget(category_search_container)
        
        category_header = QWidget()
        header_layout = QHBoxLayout()
        
        # 分类标题和搜索结果统计
        self.category_title_label = QLabel("工具分类")
        self.category_title_label.setStyleSheet("""
            QLabel {
                font-weight: 600;
                font-size: 15px;
                color: #1e293b;
                margin: 0;
                padding: 0;
            }
        """)
        
        self.category_count_label = QLabel("")
        self.category_count_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #64748b;
                margin: 0;
                padding: 0 5px;
            }
        """)
        
        header_layout.addWidget(self.category_title_label)
        header_layout.addWidget(self.category_count_label)
        header_layout.addStretch()
        self.add_cat_btn = self.create_icon_button("", "#FFFFFF", "plus.png")
        self.del_cat_btn = self.create_icon_button("", "#FFFFFF", "delete.png")
        header_layout.addWidget(self.add_cat_btn)
        header_layout.addWidget(self.del_cat_btn)
        category_header.setLayout(header_layout)
        
        left_layout.addWidget(category_header)
        self.category_list = self.create_list_widget()
        self.category_list.setDragEnabled(True)
        self.category_list.setDragDropMode(QListWidget.InternalMove)
        self.category_list.model().rowsMoved.connect(self.update_category_order)
        left_layout.addWidget(self.category_list)
        
        # 右侧主面板
        right_panel = QTabWidget()
        
        # 工具管理
        tool_tab = QWidget()
        tool_layout = QVBoxLayout()
        tool_layout.addWidget(QLabel("工具列表"))
        self.tool_list = self.create_list_widget()
        self.tool_list.setContextMenuPolicy(Qt.CustomContextMenu)
        tool_layout.addWidget(self.tool_list)
        
        tool_btn_layout = QHBoxLayout()
        self.add_tool_btn = self.create_icon_button("添加工具", "rgba(59, 130, 246, 220)", "tool.png")
        self.del_tool_btn = self.create_icon_button("删除工具", "rgba(239, 68, 68, 220)", "delete.png")
        tool_btn_layout.addWidget(self.add_tool_btn)
        tool_btn_layout.addWidget(self.del_tool_btn)
        tool_layout.addLayout(tool_btn_layout)
        tool_tab.setLayout(tool_layout)
        
        # 快捷方式管理
        shortcut_tab = QWidget()
        shortcut_layout = QVBoxLayout()
        shortcut_layout.addWidget(QLabel("快捷方式"))
        self.shortcut_list = self.create_list_widget()
        shortcut_layout.addWidget(self.shortcut_list)
        
        sc_btn_layout = QHBoxLayout()
        self.add_sc_btn = self.create_icon_button("添加快捷方式", "rgba(59, 130, 246, 220)", "shortcut.png")
        self.del_sc_btn = self.create_icon_button("删除快捷方式", "rgba(239, 68, 68, 220)", "delete.png")
        sc_btn_layout.addWidget(self.add_sc_btn)
        sc_btn_layout.addWidget(self.del_sc_btn)
        shortcut_layout.addLayout(sc_btn_layout)
        shortcut_tab.setLayout(shortcut_layout)
        
        # 环境管理
        env_tab = QWidget()
        env_layout = QVBoxLayout()
        env_layout.addWidget(QLabel("环境配置"))
        self.env_list = self.create_list_widget()
        env_layout.addWidget(self.env_list)
        
        env_btn_layout = QHBoxLayout()
        self.add_env_btn = self.create_icon_button("添加环境", "rgba(59, 130, 246, 220)", "environment.png")
        self.del_env_btn = self.create_icon_button("删除环境", "rgba(239, 68, 68, 220)", "delete.png")
        env_btn_layout.addWidget(self.add_env_btn)
        env_btn_layout.addWidget(self.del_env_btn)
        env_layout.addLayout(env_btn_layout)
        env_tab.setLayout(env_layout)
        
        right_panel.addTab(tool_tab, QIcon(resource_path("icons/tool.png")), "工具")
        right_panel.addTab(shortcut_tab, QIcon(resource_path("icons/shortcut.png")), "快捷方式")
        right_panel.addTab(env_tab, QIcon(resource_path("icons/environment.png")), "运行环境")
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 750])
        
        self.load_data()

    def create_icon_button(self, text, color, icon_name):
        btn = QPushButton(text)
        
        # 根据颜色设置按钮类型
        if "220, 70, 70" in color or "239, 68, 68" in color:
            btn.setProperty("class", "danger")
        elif "34, 197, 94" in color or "22, 163, 74" in color:
            btn.setProperty("class", "success")
        
        # 设置图标
        icon_path = resource_path(f"icons/{icon_name}")
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(18, 18))
        
        # 设置按钮样式
        btn.setStyleSheet("""
            QPushButton {
                font-weight: 600;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 8px;
                min-height: 36px;
            }
        """)
        
        return btn

    def create_list_widget(self):
        list_widget = QListWidget()
        list_widget.setFont(QFont("Microsoft YaHei", 12))
        list_widget.setAlternatingRowColors(True)
        list_widget.setFocusPolicy(Qt.NoFocus)
        list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        return list_widget

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                data = json.load(f)
                self.categories_order = data.get("categories_order", list(data.get("categories", {}).keys()))
                self.categories = data.get("categories", {})
                self.environments = data.get("environments", [])
                self.shortcut_dirs = data.get("shortcuts", [])
        
        # 为现有分类创建目录
        self.create_category_directories()
    
    def create_category_directories(self):
        """为现有分类创建对应的目录"""
        try:
            for category_name in self.categories_order:
                category_dir = os.path.join(os.getcwd(), category_name)
                if not os.path.exists(category_dir):
                    os.makedirs(category_dir)
                    logger.info(f"为现有分类创建目录: {category_dir}")
        except Exception as e:
            logger.error(f"创建分类目录时发生错误: {str(e)}")
            QMessageBox.warning(None, "警告", f"创建分类目录时发生错误: {str(e)}")

    def save_config(self):
        data = {
            "categories_order": self.categories_order,
            "categories": self.categories,
            "environments": self.environments,
            "shortcuts": self.shortcut_dirs
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        self.category_list.clear()
        self.category_list.addItems(self.categories_order)
        
        # 初始化分类计数显示
        total_count = len(self.categories_order)
        self.category_count_label.setText(f"({total_count})")
        
        self.env_list.clear()
        self.env_list.addItems([e["display_name"] for e in self.environments])
        self.shortcut_list.clear()
        self.shortcut_list.addItems([s["display_name"] for s in self.shortcut_dirs])
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)
            self.update_tool_list()
    
    def filter_categories(self):
        """根据搜索关键词过滤分类列表"""
        search_text = self.category_search_input.text().strip().lower()
        
        # 根据搜索框内容显示/隐藏清空按钮
        self.clear_category_search_btn.setVisible(bool(search_text))
        
        self.category_list.clear()
        
        if not search_text:
            # 如果搜索框为空，显示所有分类
            self.category_list.addItems(self.categories_order)
            total_count = len(self.categories_order)
            self.category_count_label.setText(f"({total_count})")
        else:
            # 过滤匹配的分类
            filtered_categories = [
                category for category in self.categories_order
                if search_text in category.lower()
            ]
            self.category_list.addItems(filtered_categories)
            
            # 更新搜索结果统计
            result_count = len(filtered_categories)
            total_count = len(self.categories_order)
            if result_count == 0:
                self.category_count_label.setText(f"(0/{total_count})")
            else:
                self.category_count_label.setText(f"({result_count}/{total_count})")
            
            # 如果没有匹配结果，显示提示
            if not filtered_categories:
                no_result_item = QListWidgetItem("未找到匹配的分类")
                no_result_item.setFlags(Qt.NoItemFlags)  # 设置为不可选择
                no_result_item.setForeground(QBrush(QColor("#9ca3af")))
                self.category_list.addItem(no_result_item)
        
        # 如果有过滤结果，选择第一个
        if self.category_list.count() > 0 and self.category_list.item(0).flags() != Qt.NoItemFlags:
            self.category_list.setCurrentRow(0)
            self.update_tool_list()
        else:
            # 如果没有匹配的分类，清空工具列表
            self.tool_list.clear()
    
    def clear_category_search(self):
        """清空分类搜索"""
        self.category_search_input.clear()
        self.clear_category_search_btn.setVisible(False) # 隐藏清空按钮
        self.filter_categories()

    def update_category_order(self):
        self.categories_order = [self.category_list.item(i).text() for i in range(self.category_list.count())]
        self.save_config()

    def perform_search(self):
        self.search_keyword = self.search_input.text().strip().lower()
        self.update_tool_list()

    def update_tool_list(self):
        self.tool_list.clear()
        
        if self.search_keyword:
            for category in self.categories_order:
                for tool in self.categories.get(category, []):
                    if self.search_keyword in tool["display_name"].lower():
                        item = QListWidgetItem(tool["display_name"])
                        item.setData(Qt.UserRole, category)
                        item.setForeground(QBrush(QColor("#909399")))
                        item.setToolTip(f"分类：{category}")
                        self.tool_list.addItem(item)
        else:
            if current := self.category_list.currentItem():
                category = current.text()
                self.tool_list.addItems([t["display_name"] for t in self.categories.get(category, [])])

    def add_category(self):
        name, ok = QInputDialog.getText(self, "新建分类", "分类名称:")
        if ok and name:
            if name not in self.categories_order:
                try:
                    # 创建分类目录
                    category_dir = os.path.join(os.getcwd(), name)
                    if not os.path.exists(category_dir):
                        os.makedirs(category_dir)
                        logger.info(f"已创建分类目录: {category_dir}")
                    
                    # 添加到分类列表
                    self.categories_order.append(name)
                    self.categories[name] = []
                    self.category_list.addItem(name)
                    self.save_config()
                    
                    # 更新分类计数
                    self.filter_categories()
                    
                    QMessageBox.information(self, "成功", f"分类 '{name}' 已创建，同时创建了目录: {category_dir}")
                    
                except Exception as e:
                    logger.error(f"创建分类目录时发生错误: {str(e)}")
                    QMessageBox.warning(self, "警告", f"分类已创建，但创建目录失败: {str(e)}")
            else:
                QMessageBox.warning(self, "警告", "分类名称已存在！")

    def delete_category(self):
        if items := self.category_list.selectedItems():
            reply = QMessageBox.question(
                self, "确认删除", f"确定要删除 {len(items)} 个分类吗？\n注意：对应的目录也会被删除！",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                for item in items:
                    name = item.text()
                    try:
                        # 删除分类目录
                        category_dir = os.path.join(os.getcwd(), name)
                        if os.path.exists(category_dir):
                            # 检查目录是否为空
                            if os.listdir(category_dir):
                                # 目录不为空，询问是否强制删除
                                force_reply = QMessageBox.question(
                                    self, "目录不为空", 
                                    f"目录 '{category_dir}' 不为空，是否强制删除？\n这将删除目录中的所有文件！",
                                    QMessageBox.Yes | QMessageBox.No
                                )
                                if force_reply == QMessageBox.Yes:
                                    import shutil
                                    shutil.rmtree(category_dir)
                                    logger.info(f"已强制删除分类目录: {category_dir}")
                                else:
                                    logger.info(f"用户取消删除非空目录: {category_dir}")
                                    continue
                            else:
                                # 目录为空，直接删除
                                os.rmdir(category_dir)
                                logger.info(f"已删除空分类目录: {category_dir}")
                        
                        # 从分类列表中删除
                        self.categories_order.remove(name)
                        del self.categories[name]
                        self.category_list.takeItem(self.category_list.row(item))
                        
                    except Exception as e:
                        logger.error(f"删除分类目录时发生错误: {str(e)}")
                        QMessageBox.warning(self, "警告", f"删除分类 '{name}' 的目录时发生错误: {str(e)}")
                        # 即使目录删除失败，也继续删除分类
                        if name in self.categories_order:
                            self.categories_order.remove(name)
                        if name in self.categories:
                            del self.categories[name]
                        self.category_list.takeItem(self.category_list.row(item))
                
                self.save_config()
                self.update_tool_list()
                
                # 更新分类计数
                self.filter_categories()
                
                QMessageBox.information(self, "完成", "分类删除操作已完成")

    def add_tool(self):
        if not self.category_list.currentItem():
            QMessageBox.warning(self, "错误", "请先选择分类！")
            return

        path, _ = QFileDialog.getOpenFileName(self, "选择工具")
        if not path: return

        name, ok = QInputDialog.getText(self, "工具名称", "显示名称:")
        if ok and name:
            category = self.category_list.currentItem().text()
            self.categories[category].append({
                "path": path,
                "display_name": name
            })
            self.update_tool_list()
            self.save_config()

    def delete_tool(self):
        if items := self.tool_list.selectedItems():
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除 {len(items)} 个工具吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                category = self.category_list.currentItem().text()
                for item in items:
                    self.categories[category] = [
                        t for t in self.categories[category]
                        if t["display_name"] != item.text()
                    ]
                self.update_tool_list()
                self.save_config()

    def add_environment(self):
        path = QFileDialog.getExistingDirectory(self, "选择环境目录")
        if path:
            name, ok = QInputDialog.getText(self, "环境名称", "显示名称:")
            if ok and name:
                self.environments.append({
                    "path": path,
                    "display_name": name
                })
                self.env_list.addItem(name)
                self.save_config()

    def delete_environment(self):
        if items := self.env_list.selectedItems():
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除 {len(items)} 个环境吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                for item in items:
                    self.environments = [
                        e for e in self.environments
                        if e["display_name"] != item.text()
                    ]
                    self.env_list.takeItem(self.env_list.row(item))
                self.save_config()

    def add_shortcut(self):
        types = ["目录", "文件快捷方式"]
        type_choice, ok = QInputDialog.getItem(
            self, "选择类型", "请选择要添加的类型:", types, 0, False
        )
        if not ok: return

        path = ""
        if type_choice == "目录":
            path = QFileDialog.getExistingDirectory(self, "选择目录")
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "选择快捷方式", "", "Shortcuts (*.lnk);;All Files (*)"
            )
        
        if not path: return

        default_name = os.path.basename(path)
        if type_choice == "文件快捷方式":
            default_name = os.path.splitext(default_name)[0]
        
        name, ok = QInputDialog.getText(
            self, "快捷方式名称", "显示名称：", text=default_name
        )
        if ok and name:
            self.shortcut_dirs.append({
                "path": path,
                "display_name": name,
                "type": "dir" if type_choice == "目录" else "lnk"
            })
            self.shortcut_list.addItem(name)
            self.save_config()

    def delete_shortcut(self):
        if items := self.shortcut_list.selectedItems():
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除 {len(items)} 个快捷方式吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                for item in items:
                    self.shortcut_dirs = [
                        s for s in self.shortcut_dirs
                        if s["display_name"] != item.text()
                    ]
                    self.shortcut_list.takeItem(self.shortcut_list.row(item))
                self.save_config()

    def run_tool(self, item):
        if self.search_keyword:
            category = item.data(Qt.UserRole)
        else:
            if not (current := self.category_list.currentItem()):
                QMessageBox.warning(self, "错误", "请先选择分类！")
                return
            category = current.text()
        
        tool_name = item.text()
        tool = next(
            (t for t in self.categories[category] 
             if t["display_name"] == tool_name),
            None
        )
        if not tool:
            QMessageBox.warning(self, "错误", "找不到工具路径！")
            return
        
        tool_path = tool["path"]
        work_dir = os.path.dirname(tool_path)
        ext = os.path.splitext(tool_path)[1].lower()

        env_path = None
        if ext in ('.py', '.jar'):
            env_names = [e["display_name"] for e in self.environments]
            if not env_names:
                QMessageBox.warning(self, "错误", "请先添加运行环境！")
                return
            
            # 使用自定义的环境选择对话框
            env_dialog = EnvironmentSelectionDialog(
                parent=self,
                environments=env_names,
                env_details=self.environments,  # 传递完整的环境信息
                title="选择运行环境"
            )
            
            if env_dialog.exec_() == QDialog.Accepted:
                env_name = env_dialog.get_selected_environment()
                if not env_name:
                    return
                    
                env_path = next(
                    e["path"] for e in self.environments
                    if e["display_name"] == env_name
                )
            else:
                return

        cmd = self.build_command(tool_path, ext, env_path)
        self.execute_command(cmd, work_dir)

    def build_command(self, tool_path, ext, env_path=None):
        safe_tool_path = f'"{tool_path}"' if " " in tool_path else tool_path
        
        if ext == '.py':
            python_exe = os.path.join(env_path, "python.exe")
            safe_python = f'"{python_exe}"' if " " in python_exe else python_exe
            return f"{safe_python} {safe_tool_path}"
        
        elif ext == '.jar':
            java_exe = os.path.join(env_path, "java.exe")
            safe_java = f'"{java_exe}"' if " " in java_exe else java_exe
            return f"{safe_java} -jar {safe_tool_path}"
        
        else:
            return safe_tool_path

    def execute_command(self, command, work_dir):
        try:
            safe_work_dir = f'"{work_dir}"' if " " in work_dir else work_dir
            full_cmd = f'start "Tool Runner" cmd /k "cd /d "{work_dir}" && {command}"'
            subprocess.Popen(
                full_cmd,
                shell=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"执行失败: {str(e)}")

    def open_shortcut(self, item):
        shortcut = next(
            (s for s in self.shortcut_dirs 
             if s["display_name"] == item.text()),
            None
        )
        if not shortcut: return

        path = shortcut["path"]
        target_path = path

        try:
            if shortcut["type"] == "lnk":
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut_obj = shell.CreateShortCut(path)
                target_path = shortcut_obj.TargetPath

            if os.path.isdir(target_path):
                os.startfile(target_path)
            else:
                dir_path = os.path.dirname(target_path)
                if os.path.exists(dir_path):
                    os.startfile(dir_path)
                    if sys.platform == "win32":
                        subprocess.Popen(
                            f'explorer /select,"{target_path}"',
                            shell=True
                        )
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开失败: {str(e)}")

    def show_context_menu(self, pos):
        menu = QMenu()
        open_action = QAction("打开所在目录", self)
        open_action.triggered.connect(self.open_tool_directory)
        menu.addAction(open_action)
        menu.exec_(self.tool_list.mapToGlobal(pos))

    def open_tool_directory(self):
        if item := self.tool_list.currentItem():
            if self.search_keyword:
                category = item.data(Qt.UserRole)
            else:
                if not (current := self.category_list.currentItem()):
                    QMessageBox.warning(self, "错误", "请先选择分类！")
                    return
                category = current.text()
            
            tool = next(
                t for t in self.categories[category]
                if t["display_name"] == item.text()
            )
            path = os.path.dirname(tool["path"])
            os.startfile(path) if os.path.exists(path) else QMessageBox.warning(self, "错误", "路径不存在！")

    def setup_connections(self):
        self.search_input.textChanged.connect(self.perform_search)
        self.category_search_input.textChanged.connect(self.filter_categories)
        self.clear_category_search_btn.clicked.connect(self.clear_category_search)
        self.add_cat_btn.clicked.connect(self.add_category)
        self.del_cat_btn.clicked.connect(self.delete_category)
        self.category_list.currentItemChanged.connect(self.update_tool_list)
        self.add_tool_btn.clicked.connect(self.add_tool)
        self.del_tool_btn.clicked.connect(self.delete_tool)
        self.tool_list.itemDoubleClicked.connect(self.run_tool)
        self.tool_list.customContextMenuRequested.connect(self.show_context_menu)
        self.add_env_btn.clicked.connect(self.add_environment)
        self.del_env_btn.clicked.connect(self.delete_environment)
        self.add_sc_btn.clicked.connect(self.add_shortcut)
        self.del_sc_btn.clicked.connect(self.delete_shortcut)
        self.shortcut_list.itemDoubleClicked.connect(self.open_shortcut)

    def setup_hotkey(self):
        try:
            settings = QSettings("TBox", "TBox")
            hotkey = settings.value("hotkey", "Ctrl+Alt+T")
            logger.info(f"尝试设置快捷键: {hotkey}")
            
            # 如果已经有快捷键处理器，先完全清理
            if hasattr(self, 'hotkey_handler'):
                try:
                    # 移除旧的事件过滤器
                    QApplication.instance().removeNativeEventFilter(self.hotkey_handler)
                    # 清理旧的快捷键注册
                    self.hotkey_handler.cleanup()
                    logger.info("已完全清理旧的快捷键处理器")
                except Exception as e:
                    logger.warning(f"清理旧快捷键处理器时发生错误: {str(e)}")
                
                # 删除旧的处理器引用
                delattr(self, 'hotkey_handler')
            
            # 创建新的全局快捷键处理器
            self.hotkey_handler = GlobalHotkey(self.show_and_activate)
            
            # 注册全局快捷键
            if not self.hotkey_handler.register_hotkey(hotkey):
                logger.error("注册全局快捷键失败")
                # 尝试使用默认快捷键
                if hotkey != "Ctrl+Alt+T":
                    logger.info("尝试使用默认快捷键 Ctrl+Alt+T")
                    if self.hotkey_handler.register_hotkey("Ctrl+Alt+T"):
                        logger.info("成功使用默认快捷键")
                        # 更新设置
                        settings.setValue("hotkey", "Ctrl+Alt+T")
                        return True
                return False
            
            # 安装事件过滤器
            QApplication.instance().installNativeEventFilter(self.hotkey_handler)
            
            logger.info(f"成功设置快捷键: {hotkey}")
            return True
            
        except Exception as e:
            logger.error(f"设置快捷键时发生错误: {str(e)}")
            return False
    
    def show_and_activate(self):
        try:
            # 检查快捷键是否启用
            if not self.hotkey_enabled:
                logger.info("快捷键响应已禁用，忽略快捷键触发")
                return
                
            if self.isVisible():
                if self.isActiveWindow():
                    self.hide()
                    logger.info("隐藏主窗口")
                else:
                    self.activateWindow()
                    self.showNormal()
                    self.raise_()
                    logger.info("激活主窗口")
            else:
                self.showNormal()
                self.activateWindow()
                self.raise_()
                logger.info("显示主窗口")
        except Exception as e:
            logger.error(f"切换窗口状态时发生错误: {str(e)}")

    def cleanup(self):
        """清理资源"""
        try:
            # 清理全局快捷键
            if hasattr(self, 'hotkey_handler'):
                QApplication.instance().removeNativeEventFilter(self.hotkey_handler)
                self.hotkey_handler.cleanup()
                logger.info("已清理全局快捷键")
            
            # 清理快捷键管理器
            hotkey_manager = HotkeyManager()
            hotkey_manager.cleanup_all()
            
            # 清理系统托盘
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
                logger.info("已隐藏系统托盘图标")
            
            # 清理本地服务器
            if hasattr(self, 'server'):
                self.server.close()
                logger.info("已关闭本地服务器")
            
            logger.info("资源清理完成")
            
        except Exception as e:
            logger.error(f"清理资源时发生错误: {str(e)}")

if __name__ == "__main__":
    try:
        # 创建应用程序实例
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setQuitOnLastWindowClosed(False)
        
        # 设置应用程序信息
        app.setApplicationName("TBox")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("TBox")
        app.setOrganizationDomain("tbox.local")
        
        # 检查是否已有实例运行
        socket = QLocalSocket()
        socket.connectToServer("TBox")
        
        if socket.waitForConnected(500):
            logger.info("TBox已在运行，激活现有实例")
            socket.write(b"show")
            socket.waitForBytesWritten()
            socket.close()
            sys.exit(0)
        socket.close()
        
        # 创建本地服务器
        server = QLocalServer()
        server.listen("TBox")
        
        # 创建主窗口
        window = ToolManagerApp()
        
        # 注册退出处理
        def cleanup_on_exit():
            logger.info("程序退出，开始清理资源...")
            try:
                window.cleanup()
            except Exception as e:
                logger.error(f"清理资源时发生错误: {str(e)}")
            
            # 清理本地服务器
            try:
                server.close()
            except Exception as e:
                logger.error(f"关闭本地服务器时发生错误: {str(e)}")
        
        app.aboutToQuit.connect(cleanup_on_exit)
        
        # 运行应用程序
        exit_code = app.exec_()
        logger.info(f"应用程序退出，退出代码: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}")
        QMessageBox.critical(None, "错误", f"程序启动失败: {str(e)}")
        sys.exit(1)

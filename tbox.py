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
    QShortcut, QTextEdit, QStackedLayout, QAbstractItemView, QSpinBox
)
from PyQt5.QtNetwork import QLocalSocket, QLocalServer
import win32con
import win32api
import win32gui
import ctypes
from ctypes import wintypes
from PyQt5.QtWidgets import QSizePolicy

# 定义UnregisterHotKey函数
user32 = ctypes.windll.user32
UnregisterHotKey = user32.UnregisterHotKey
UnregisterHotKey.argtypes = [wintypes.HWND, wintypes.INT]
UnregisterHotKey.restype = wintypes.BOOL

# 导入统一样式配置
UNIFIED_STYLE = False  # 使用内置浅色主题

# Windows亚克力效果相关定义
DWM_BB_ENABLE = 0x00000001
DWM_BB_BLURREGION = 0x00000002
DWM_BB_TRANSITIONONMAXIMIZED = 0x00000004

class DWM_BLURBEHIND(ctypes.Structure):
    _fields_ = [
        ("dwFlags", wintypes.DWORD),
        ("fEnable", wintypes.BOOL),
        ("hRgnBlur", wintypes.HANDLE),
        ("fTransitionOnMaximized", wintypes.BOOL)
    ]

# 加载dwmapi.dll
try:
    dwmapi = ctypes.windll.dwmapi
    DwmEnableBlurBehindWindow = dwmapi.DwmEnableBlurBehindWindow
    DwmEnableBlurBehindWindow.argtypes = [wintypes.HWND, ctypes.POINTER(DWM_BLURBEHIND)]
    DwmEnableBlurBehindWindow.restype = wintypes.HRESULT
except:
    DwmEnableBlurBehindWindow = None

def enable_acrylic_effect(hwnd):
    """启用Windows亚克力效果"""
    if DwmEnableBlurBehindWindow is None:
        return False
    
    try:
        blur_behind = DWM_BLURBEHIND()
        blur_behind.dwFlags = DWM_BB_ENABLE
        blur_behind.fEnable = True
        blur_behind.hRgnBlur = None
        blur_behind.fTransitionOnMaximized = True
        
        result = DwmEnableBlurBehindWindow(hwnd, ctypes.byref(blur_behind))
        return result == 0  # S_OK
    except:
        return False

CONFIG_FILE = "tool_manager_config.json"

THEMES = {
    "浅色": {
        "bg": "#f0f4f8", "container": "#f0f4f8",
        "titlebar": "#ffffff", "titlebar_border": "#e2e8f0",
        "text": "#0f172a", "text_sub": "#334155", "text_muted": "#64748b",
        "card": "#ffffff", "card_border": "#e2e8f0", "card_hover": "#f8fafc",
        "card_border_hover": "#93c5fd",
        "list_bg": "#ffffff", "list_border": "#e2e8f0",
        "item_hover": "#f1f5f9", "item_sel": "#eff6ff", "item_sel_text": "#2563eb",
        "input_bg": "#ffffff", "input_border": "#e2e8f0",
        "btn_bg": "#ffffff", "btn_border": "#e2e8f0", "btn_text": "#374151", "btn_hover": "#f8fafc",
        "primary": "#3b82f6", "primary_hover": "#2563eb",
        "danger_bg": "#fff0f0", "danger_border": "#fca5a5", "danger_text": "#ef4444",
        "badge_bg": "#eff6ff", "badge_border": "#bfdbfe", "badge_text": "#2563eb",
        "bulk_bg": "#eff6ff", "bulk_border": "#bfdbfe",
        "scrollbar": "#cbd5e1", "scrollbar_hover": "#94a3b8", "sep": "#e2e8f0",
        "toast_bg": "#1e293b", "toast_border": "#334155",
        "run_btn": "#3b82f6", "run_btn_hover": "#2563eb",
        "open_btn": "#f1f5f9", "open_btn_border": "#e2e8f0", "empty_icon": "#94a3b8",
    },
    "深色": {
        "bg": "#0f1117", "container": "#0f1117",
        "titlebar": "#1a1d27", "titlebar_border": "#2d3148",
        "text": "#f1f5f9", "text_sub": "#cbd5e1", "text_muted": "#64748b",
        "card": "#1e2235", "card_border": "#2d3148", "card_hover": "#252840",
        "card_border_hover": "#4f6ef7",
        "list_bg": "#1a1d27", "list_border": "#2d3148",
        "item_hover": "#252840", "item_sel": "rgba(79,110,247,0.18)", "item_sel_text": "#818cf8",
        "input_bg": "#1e2235", "input_border": "#2d3148",
        "btn_bg": "#1e2235", "btn_border": "#2d3148", "btn_text": "#cbd5e1", "btn_hover": "#252840",
        "primary": "#4f6ef7", "primary_hover": "#3b5bdb",
        "danger_bg": "rgba(239,68,68,0.12)", "danger_border": "rgba(239,68,68,0.3)", "danger_text": "#f87171",
        "badge_bg": "rgba(79,110,247,0.15)", "badge_border": "rgba(79,110,247,0.3)", "badge_text": "#818cf8",
        "bulk_bg": "rgba(79,110,247,0.1)", "bulk_border": "rgba(79,110,247,0.25)",
        "scrollbar": "#2d3148", "scrollbar_hover": "#4f6ef7", "sep": "#2d3148",
        "toast_bg": "#1e2235", "toast_border": "#2d3148",
        "run_btn": "#4f6ef7", "run_btn_hover": "#3b5bdb",
        "open_btn": "#252840", "open_btn_border": "#2d3148", "empty_icon": "#475569",
    },
    "护眼绿": {
        "bg": "#e8f5e9", "container": "#e8f5e9",
        "titlebar": "#f1f8f1", "titlebar_border": "#c8e6c9",
        "text": "#1b3a1f", "text_sub": "#2e5c34", "text_muted": "#5a8a60",
        "card": "#f1f8f1", "card_border": "#c8e6c9", "card_hover": "#e8f5e9",
        "card_border_hover": "#66bb6a",
        "list_bg": "#f1f8f1", "list_border": "#c8e6c9",
        "item_hover": "#dcedc8", "item_sel": "#c8e6c9", "item_sel_text": "#2e7d32",
        "input_bg": "#f1f8f1", "input_border": "#c8e6c9",
        "btn_bg": "#f1f8f1", "btn_border": "#c8e6c9", "btn_text": "#2e5c34", "btn_hover": "#dcedc8",
        "primary": "#43a047", "primary_hover": "#2e7d32",
        "danger_bg": "#fff3e0", "danger_border": "#ffcc80", "danger_text": "#e65100",
        "badge_bg": "#dcedc8", "badge_border": "#a5d6a7", "badge_text": "#2e7d32",
        "bulk_bg": "#dcedc8", "bulk_border": "#a5d6a7",
        "scrollbar": "#a5d6a7", "scrollbar_hover": "#66bb6a", "sep": "#c8e6c9",
        "toast_bg": "#1b3a1f", "toast_border": "#2e5c34",
        "run_btn": "#43a047", "run_btn_hover": "#2e7d32",
        "open_btn": "#dcedc8", "open_btn_border": "#c8e6c9", "empty_icon": "#81c784",
    },
    "暖橙": {
        "bg": "#fff8f0", "container": "#fff8f0",
        "titlebar": "#ffffff", "titlebar_border": "#ffe0b2",
        "text": "#3e1f00", "text_sub": "#6d3a00", "text_muted": "#a0622a",
        "card": "#ffffff", "card_border": "#ffe0b2", "card_hover": "#fff3e0",
        "card_border_hover": "#ff9800",
        "list_bg": "#ffffff", "list_border": "#ffe0b2",
        "item_hover": "#fff3e0", "item_sel": "#ffe0b2", "item_sel_text": "#e65100",
        "input_bg": "#ffffff", "input_border": "#ffe0b2",
        "btn_bg": "#ffffff", "btn_border": "#ffe0b2", "btn_text": "#6d3a00", "btn_hover": "#fff3e0",
        "primary": "#f57c00", "primary_hover": "#e65100",
        "danger_bg": "#fce4ec", "danger_border": "#f48fb1", "danger_text": "#c62828",
        "badge_bg": "#fff3e0", "badge_border": "#ffcc80", "badge_text": "#e65100",
        "bulk_bg": "#fff3e0", "bulk_border": "#ffcc80",
        "scrollbar": "#ffcc80", "scrollbar_hover": "#ff9800", "sep": "#ffe0b2",
        "toast_bg": "#3e1f00", "toast_border": "#6d3a00",
        "run_btn": "#f57c00", "run_btn_hover": "#e65100",
        "open_btn": "#fff3e0", "open_btn_border": "#ffe0b2", "empty_icon": "#ffb74d",
    },
}

CURRENT_THEME = "浅色"
CURRENT_FONT_SIZE = 13

def build_style(theme_name=None, font_size=None):
    t = THEMES.get(theme_name or CURRENT_THEME, THEMES["浅色"])
    fs = font_size or CURRENT_FONT_SIZE
    return (
        "QWidget, QMainWindow {"
        f"background-color: {t['bg']}; color: {t['text']};"
        "font-family: 'Microsoft YaHei UI', 'Segoe UI', 'Arial';"
        f"font-size: {fs}px; font-weight: 600; border: none;}}"
        f"#appContainer {{background-color: {t['container']}; border-radius: 12px;}}"
        f"#titleBar {{background-color: {t['titlebar']}; border-bottom: 1px solid {t['titlebar_border']};"
        "border-top-left-radius: 12px; border-top-right-radius: 12px;}"
        f"#titleLabel {{color: {t['text']}; font-size: {fs}px; font-weight: 700;}}"
        "#settingsButton, #minimizeButton, #maximizeButton, #closeButton"
        "{background-color: transparent; border: none; border-radius: 6px; min-width: 28px; min-height: 28px;}"
        f"#settingsButton:hover, #minimizeButton:hover, #maximizeButton:hover {{background-color: {t['item_hover']};}}"
        f"#closeButton:hover {{background-color: {t['danger_bg']};}}"
        f"QLineEdit {{background-color: {t['input_bg']}; border: 1px solid {t['input_border']};"
        f"border-radius: 6px; padding: 6px 12px; color: {t['text']}; font-size: {fs}px; font-weight: 600;}}"
        f"QLineEdit:focus {{border-color: {t['primary']};}}"
        f"QListWidget {{background-color: {t['list_bg']}; border: 1px solid {t['list_border']};"
        "border-radius: 8px; padding: 4px; outline: 0;}"
        f"QListWidget::item {{border-radius: 6px; padding: 6px 10px; color: {t['text_sub']};"
        f"font-size: {fs}px; font-weight: 600;}}"
        f"QListWidget::item:hover {{background-color: {t['item_hover']}; color: {t['text']};}}"
        f"QListWidget::item:selected {{background-color: {t['item_sel']}; color: {t['item_sel_text']}; font-weight: 700;}}"
        f"QListWidget::item:selected:active {{background-color: {t['item_sel']}; color: {t['item_sel_text']};}}"
        "QTabWidget::pane {border: none; background-color: transparent;}"
        f"QTabBar::tab {{background-color: transparent; border: none; color: {t['text_muted']};"
        f"padding: 8px 16px; font-size: {fs}px; font-weight: 600;}}"
        f"QTabBar::tab:selected {{color: {t['primary']}; border-bottom: 2px solid {t['primary']}; font-weight: 700;}}"
        f"QTabBar::tab:hover {{color: {t['text']};}}"
        f"QPushButton {{background-color: {t['btn_bg']}; border: 1px solid {t['btn_border']};"
        f"border-radius: 6px; padding: 6px 14px; color: {t['btn_text']}; font-weight: 600; font-size: {fs}px;}}"
        f"QPushButton:hover {{background-color: {t['btn_hover']};}}"
        f"QPushButton:pressed {{background-color: {t['item_hover']};}}"
        f"QPushButton[class='primary'] {{background-color: {t['primary']}; border-color: {t['primary']}; color: #ffffff;}}"
        f"QPushButton[class='primary']:hover {{background-color: {t['primary_hover']}; border-color: {t['primary_hover']};}}"
        f"QPushButton[class='danger'] {{background-color: {t['danger_bg']}; border-color: {t['danger_border']}; color: {t['danger_text']};}}"
        f"QDialog {{background-color: {t['container']};}}"
        f"QGroupBox {{background-color: {t['card']}; border: 1px solid {t['card_border']};"
        f"border-radius: 8px; margin-top: 16px; padding-top: 16px; font-weight: 700; color: {t['text']}; font-size: {fs}px;}}"
        f"QGroupBox::title {{background: transparent; color: {t['text']};"
        "subcontrol-origin: margin; subcontrol-position: top left; left: 12px; padding: 0 8px; font-weight: 700;}"
        f"QLabel {{color: {t['text']}; background: transparent; font-weight: 600;}}"
        f"QCheckBox, QRadioButton {{color: {t['text_sub']}; font-weight: 600;}}"
        "QCheckBox::indicator {width: 16px; height: 16px; border-radius: 4px;}"
        f"QCheckBox::indicator:unchecked {{background-color: {t['input_bg']}; border: 1px solid {t['input_border']};}}"
        f"QCheckBox::indicator:checked {{background-color: {t['primary']}; border: 1px solid {t['primary']};}}"
        "QScrollArea {background: transparent; border: none;}"
        "QAbstractScrollArea::viewport {background: transparent;}"
        "QScrollBar:vertical {background: transparent; width: 6px; margin: 0;}"
        f"QScrollBar::handle:vertical {{background: {t['scrollbar']}; border-radius: 3px; min-height: 20px;}}"
        f"QScrollBar::handle:vertical:hover {{background: {t['scrollbar_hover']};}}"
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {height: 0;}"
        f"QWidget#toolsPanel {{background-color: {t['card']}; border: 1px solid {t['card_border']}; border-radius: 8px;}}"
        f"QFrame#bulkBar {{background-color: {t['bulk_bg']}; border: 1px solid {t['bulk_border']}; border-radius: 8px;}}"
        f"QComboBox {{background-color: {t['input_bg']}; border: 1px solid {t['input_border']};"
        f"border-radius: 6px; padding: 4px 10px; color: {t['text']}; font-size: {fs}px; font-weight: 600;}}"
        "QComboBox::drop-down {border: none; width: 20px;}"
        f"QComboBox QAbstractItemView {{background-color: {t['card']}; border: 1px solid {t['card_border']};"
        f"color: {t['text']}; selection-background-color: {t['item_sel']}; selection-color: {t['item_sel_text']};}}"
        f"QSpinBox {{background-color: {t['input_bg']}; border: 1px solid {t['input_border']};"
        f"border-radius: 6px; padding: 4px 8px; color: {t['text']}; font-size: {fs}px; font-weight: 600;}}"
    )

STYLE_SHEET = build_style()


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
        self.setFixedHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(8)

        # 应用图标
        self.iconLabel = QLabel()
        self.iconLabel.setFixedSize(24, 24)
        icon = QIcon(resource_path("icon.png"))
        pixmap = icon.pixmap(20, 20)
        self.iconLabel.setPixmap(pixmap)

        # 标题
        self.titleLabel = QLabel("TBox")
        self.titleLabel.setObjectName("titleLabel")

        layout.addWidget(self.iconLabel)
        layout.addWidget(self.titleLabel)
        layout.addStretch()

        BTN_W = 28
        # 设置按钮
        self.settingsButton = QPushButton()
        self.settingsButton.setObjectName("settingsButton")
        self.settingsButton.setFixedSize(BTN_W, BTN_W)
        self.settingsButton.setIcon(QIcon(resource_path("icons/settings.png")))
        self.settingsButton.setIconSize(QSize(16, 16))
        self.settingsButton.clicked.connect(self.parent.show_settings)

        # 窗口控制按钮
        self.minimizeButton = QPushButton()
        self.minimizeButton.setObjectName("minimizeButton")
        self.minimizeButton.setFixedSize(BTN_W, BTN_W)
        self.minimizeButton.setIcon(QIcon(resource_path("icons/minimize.png")))
        self.minimizeButton.setIconSize(QSize(16, 16))

        self.maximizeButton = QPushButton()
        self.maximizeButton.setObjectName("maximizeButton")
        self.maximizeButton.setFixedSize(BTN_W, BTN_W)
        self.maximizeButton.setIcon(QIcon(resource_path("icons/maximize.png")))
        self.maximizeButton.setIconSize(QSize(16, 16))

        self.closeButton = QPushButton()
        self.closeButton.setObjectName("closeButton")
        self.closeButton.setFixedSize(BTN_W, BTN_W)
        self.closeButton.setIcon(QIcon(resource_path("icons/close.png")))
        self.closeButton.setIconSize(QSize(16, 16))

        layout.addWidget(self.settingsButton, 0, Qt.AlignVCenter)
        layout.addWidget(self.minimizeButton, 0, Qt.AlignVCenter)
        layout.addWidget(self.maximizeButton, 0, Qt.AlignVCenter)
        layout.addWidget(self.closeButton, 0, Qt.AlignVCenter)

        self.minimizeButton.clicked.connect(self.parent.showMinimized)
        self.maximizeButton.clicked.connect(self.toggleMaximize)
        self.closeButton.clicked.connect(self.parent.close)

        self.start = None
        self.setAttribute(Qt.WA_StyledBackground, True)


        
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
        self.setFixedSize(600, 600)

        # 设置窗口图标
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        
        # 启用亚克力效果
        try:
            hwnd = self.winId().__int__()
            enable_acrylic_effect(hwnd)
        except:
            pass
        
        # 设置窗口模态
        self.setModal(True)
        
        # 保存环境列表和详细信息
        self.environments = environments or []
        self.env_details = env_details or []
        self.selected_environment = None
        
        # 创建主容器
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        
        # 创建阴影效果
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(40)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.shadow.setOffset(0, 10)
        self.central_widget.setGraphicsEffect(self.shadow)
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.central_widget)
        
        # 设置中央容器布局
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("请选择运行环境:")
        # title_label.setStyleSheet("""
        #     QLabel {
        #         font-size: 18px;
        #         font-weight: 600;
        #         color: #1a1a1a;
        #         margin-bottom: 10px;
        #         text-align: center;
        #     }
        # """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 主要内容区域
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # 左侧：环境列表
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        env_label = QLabel("环境列表:")
        # env_label.setStyleSheet("""
        #     QLabel {
        #         font-size: 14px;
        #         font-weight: 600;
        #         color: #1a1a1a;
        #         margin-bottom: 8px;
        #     }
        # """)
        left_layout.addWidget(env_label)
        self.env_list = QListWidget(self)
        self.env_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.env_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.env_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.env_list.setSpacing(10)
        self.env_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.env_list.setFixedWidth(200)
        # self.env_list.setStyleSheet("""
        #     QListWidget {
        #         background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        #                     stop: 0 rgba(255, 255, 255, 0.6),
        #                     stop: 1 rgba(248, 250, 252, 0.7));
        #         border: 1px solid rgba(255, 255, 255, 0.4);
        #         border-radius: 12px;
        #         padding: 8px;
        #         font-size: 14px;
        #         font-weight: 500;
        #         color: #1a1a1a;
        #     }
        #
        #     QListWidget::item {
        #         height: 40px;
        #         padding: 8px 12px;
        #         border-radius: 8px;
        #         margin: 2px 0;
        #         background: transparent;
        #         border: 1px solid transparent;
        #     }
        #
        #     QListWidget::item:hover {
        #         background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        #                     stop: 0 rgba(135, 206, 235, 0.2),
        #                     stop: 1 rgba(176, 224, 230, 0.3));
        #         border: 1px solid rgba(135, 206, 235, 0.4);
        #         color: #1a1a1a;
        #         font-weight: 500;
        #     }
        #
        #     QListWidget::item:selected {
        #         background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        #                     stop: 0 rgba(135, 206, 235, 0.4),
        #                     stop: 1 rgba(176, 224, 230, 0.5));
        #         color: #1a1a1a;
        #         border: 1px solid rgba(135, 206, 235, 0.6);
        #         font-weight: 600;
        #     }
        #
        #     QListWidget::item:selected:hover {
        #         background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        #                     stop: 0 rgba(135, 206, 235, 0.5),
        #                     stop: 1 rgba(176, 224, 230, 0.6));
        #         border: 1px solid rgba(135, 206, 235, 0.7);
        #         color: #1a1a1a;
        #         font-weight: 600;
        #     }
        # """)
        
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
        # details_label.setStyleSheet("""
        #     QLabel {
        #         font-size: 14px;
        #         font-weight: 600;
        #         color: #1a1a1a;
        #         margin-bottom: 8px;
        #     }
        # """)
        right_layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        # self.details_text.setStyleSheet("""
        #     QTextEdit {
        #         background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        #                     stop: 0 rgba(255, 255, 255, 0.6),
        #                     stop: 1 rgba(248, 250, 252, 0.7));
        #         border: 1px solid rgba(255, 255, 255, 0.4);
        #         border-radius: 12px;
        #         padding: 12px;
        #         font-size: 13px;
        #         font-family: 'Segoe UI', sans-serif;
        #         color: #1a1a1a;
        #         line-height: 1.4;
        #     }
        # """)
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
                color: #64748b;
                font-style: italic;
                margin-top: 5px;
                text-align: center;
            }
        """)
        hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)
        button_layout.setSpacing(15)
        
        # 确定按钮
        self.ok_button = QPushButton("确定")
        self.ok_button.setFixedSize(100, 35)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(255, 255, 255, 0.8),
                            stop: 1 rgba(248, 250, 252, 0.9));
                color: #1a1a1a;
                border: 1px solid rgba(34, 197, 94, 0.4);
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(34, 197, 94, 0.2),
                            stop: 1 rgba(74, 222, 128, 0.3));
                border-color: rgba(34, 197, 94, 0.6);
                color: #1a1a1a;
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
                            stop: 0 rgba(255, 255, 255, 0.8),
                            stop: 1 rgba(248, 250, 252, 0.9));
                color: #1a1a1a;
                border: 1px solid rgba(135, 206, 235, 0.4);
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(135, 206, 235, 0.2),
                            stop: 1 rgba(176, 224, 230, 0.3));
                border-color: rgba(135, 206, 235, 0.6);
                color: #1a1a1a;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # 设置窗口居中
        self.center_on_parent()
        
        # 初始化详细信息显示
        self.update_env_details()
        
        # 应用亚克力样式
        self.apply_acrylic_style()
    
    def apply_acrylic_style(self):
        """应用亚克力样式"""
        style = """
        """
        
        self.setStyleSheet(style)
    
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
                <h3 style='color: #f3f4f6; margin-bottom: 15px; font-size: 16px;'>
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
                <h3 style='color: #f3f4f6; margin-bottom: 15px; font-size: 16px;'>
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


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.resize(600, 500)  # 初始大小
        self.setMinimumSize(500, 400)  # 最小大小
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("SettingsDialog")
        
        # 设置窗口图标
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        
        # 保存原始设置值，用于检测变化
        self.original_startup = self.is_startup_enabled()
        self.original_hotkey = self.get_hotkey()
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)  # 减少边距
        layout.setSpacing(15)  # 减少间距
        
        # 标题
        title_label = QLabel("TBox 设置")
        layout.addWidget(title_label)

        # 启动设置组
        startup_group = QGroupBox("启动设置")
        startup_layout = QVBoxLayout()
        startup_layout.setContentsMargins(15, 15, 15, 15)
        startup_layout.setSpacing(8)

        self.startup_checkbox = QCheckBox("开机自动启动")
        self.startup_checkbox.setChecked(self.original_startup)

        startup_info = QLabel("启用后，TBox 将在系统启动时自动运行")
        startup_info.setStyleSheet("QLabel{font-style: italic;}")

        startup_layout.addWidget(self.startup_checkbox)
        startup_layout.addWidget(startup_info)
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)

        # 快捷键设置组
        hotkey_group = QGroupBox("快捷键设置")
        hotkey_layout = QVBoxLayout()
        hotkey_layout.setContentsMargins(15, 15, 15, 15)
        hotkey_layout.setSpacing(8)

        hotkey_label = QLabel("显示/隐藏快捷键:")

        self.hotkey_edit = QKeySequenceEdit()
        self.hotkey_edit.setKeySequence(QKeySequence(self.original_hotkey))
        self.hotkey_edit.setFixedHeight(36)

        hotkey_info = QLabel("提示：建议使用 Ctrl+Alt+字母 组合")
        hotkey_info.setStyleSheet("QLabel{font-style: italic;}")
        
        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addWidget(self.hotkey_edit)
        hotkey_layout.addWidget(hotkey_info)
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)

        # 外观设置组
        appear_group = QGroupBox("外观设置")
        appear_layout = QVBoxLayout()
        appear_layout.setContentsMargins(15, 15, 15, 15)
        appear_layout.setSpacing(10)

        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("配色主题:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText(CURRENT_THEME)
        self.theme_combo.setFixedWidth(120)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        appear_layout.addLayout(theme_row)

        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("字体大小:"))
        self.font_spin = QSpinBox()
        self.font_spin.setRange(10, 22)
        self.font_spin.setValue(CURRENT_FONT_SIZE)
        self.font_spin.setSuffix(" px")
        self.font_spin.setFixedWidth(80)
        font_row.addWidget(self.font_spin)
        font_row.addStretch()
        appear_layout.addLayout(font_row)

        appear_group.setLayout(appear_layout)
        layout.addWidget(appear_group)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 15, 0, 0)  # 减少上边距
        button_layout.setSpacing(10)
        
        # reset_btn = QPushButton("重置")
        # reset_btn.setFixedWidth(80)
        # reset_btn.setFixedHeight(32)
        # reset_btn.setStyleSheet("""
        #     QPushButton {
        #         background: white;
        #         color: #1a1a1a;
        #         border: 1px solid #ccc;
        #         border-radius: 4px;
        #         font-size: 12px;
        #         padding: 6px 12px;
        #     }
        #
        #     QPushButton:hover {
        #         background: #f0f0f0;
        #         border-color: #999;
        #     }
        # """)
        # reset_btn.clicked.connect(self.reset_settings)
        
        save_btn = QPushButton("保存")
        save_btn.setFixedSize(80, 32)
        save_btn.setProperty("class", "primary")
        save_btn.clicked.connect(self.save_settings)

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(80, 32)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
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
        current_theme = self.theme_combo.currentText()
        current_font = self.font_spin.value()
        return (current_startup != self.original_startup or
                current_hotkey != self.original_hotkey or
                current_theme != CURRENT_THEME or
                current_font != CURRENT_FONT_SIZE)
    
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
            hotkey_changed = False
            if hotkey != self.original_hotkey:
                settings = QSettings("TBox", "TBox")
                settings.setValue("hotkey", hotkey)
                logger.info(f"已保存快捷键设置: {hotkey}")
                hotkey_changed = True
            
            # 如果快捷键发生变化，通知主程序重新设置
            if hotkey_changed and hasattr(self.parent(), 'setup_hotkey'):
                try:
                    if self.parent().setup_hotkey():
                        QMessageBox.information(self, "成功", f"快捷键设置已更新为: {hotkey}")
                    else:
                        QMessageBox.warning(self, "警告", "快捷键设置已保存，但重新注册失败，请重启程序")
                except Exception as e:
                    logger.error(f"重新设置快捷键时发生错误: {str(e)}")
                    QMessageBox.warning(self, "警告", "快捷键设置已保存，但重新注册失败，请重启程序")

            # 保存并应用主题/字体
            global CURRENT_THEME, CURRENT_FONT_SIZE
            new_theme = self.theme_combo.currentText()
            new_font = self.font_spin.value()
            if new_theme != CURRENT_THEME or new_font != CURRENT_FONT_SIZE:
                CURRENT_THEME = new_theme
                CURRENT_FONT_SIZE = new_font
                settings = QSettings("TBox", "TBox")
                settings.setValue("theme", new_theme)
                settings.setValue("font_size", new_font)
                app = QApplication.instance()
                app.setStyleSheet(build_style(new_theme, new_font))
                app.setFont(QFont("Microsoft YaHei UI", new_font))

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
                UnregisterHotKey(None, hotkey_id)
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
                result = UnregisterHotKey(None, self.hotkey_id)
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
            
            # 先清理旧的快捷键
            self.cleanup()
            
            # 检查管理器中是否已注册（但允许重新注册）
            if self.hotkey_manager.is_registered(key_sequence):
                logger.info(f"快捷键 {key_sequence} 在管理器中存在，先清理")
                # 从管理器中移除旧的记录
                self.hotkey_manager.unregister_hotkey(key_sequence)
            
            # 尝试清理系统中可能存在的快捷键冲突
            # 使用一个范围内的ID进行清理
            for test_id in range(0x0000, 0x0100):  # 清理前256个ID
                try:
                    UnregisterHotKey(None, test_id)
                except:
                    pass  # 忽略不存在的快捷键
            
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
            max_retries = 10  # 增加重试次数
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
                            UnregisterHotKey(None, self.hotkey_id)
                            raise Exception("快捷键管理器注册失败")
                    else:
                        error_code = win32api.GetLastError()
                        if error_code == 1409:  # ERROR_HOTKEY_ALREADY_REGISTERED
                            if attempt < max_retries - 1:
                                # 尝试注销可能存在的快捷键
                                try:
                                    # 尝试注销当前ID的快捷键
                                    UnregisterHotKey(None, self.hotkey_id)
                                    logger.info(f"已注销ID {self.hotkey_id} 的快捷键")
                                except:
                                    pass
                                
                                # 尝试注销相同组合键的其他ID
                                for conflict_id in range(0x0000, 0xFFFF):
                                    try:
                                        UnregisterHotKey(None, conflict_id)
                                    except:
                                        pass
                                
                                # 生成新的ID
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

class EmptyStateWidget(QWidget):
    def __init__(self, title="当前分类暂无工具", subtitle="点击下方按钮添加你的第一个工具", button_text="添加工具", on_action=None, parent=None):
        super().__init__(parent)
        self.on_action = on_action
        self.setAttribute(Qt.WA_StyledBackground, True)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(12)
        root.setAlignment(Qt.AlignCenter)

        icon = QLabel("🧰")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("QLabel{font-size: 44px; color: #94a3b8;}")
        root.addWidget(icon)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet("QLabel{font-size: 15px; font-weight: 700; color: #1e293b;}")
        root.addWidget(title_lbl)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setWordWrap(True)
        sub_lbl.setStyleSheet("QLabel{font-size: 12px; color: #94a3b8;}")
        root.addWidget(sub_lbl)

        btn = QPushButton(button_text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton{
                background-color: #3b82f6;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 600;
                color: #ffffff;
                min-width: 120px;
                font-size: 13px;
            }
            QPushButton:hover{ background-color: #2563eb; }
            QPushButton:pressed{ background-color: #1d4ed8; }
        """)
        btn.clicked.connect(lambda: self.on_action() if self.on_action else None)
        root.addWidget(btn)

class ToolCardWidget(QWidget):
    """Grid tool card, theme-aware"""
    def __init__(self, title: str, subtitle: str, badge: str = "", on_run=None, on_open=None, parent=None):
        super().__init__(parent)
        self.on_run = on_run
        self.on_open = on_open

        fs = CURRENT_FONT_SIZE
        t = THEMES.get(CURRENT_THEME, THEMES["浅色"])
        btn_h = max(22, fs + 10)
        icon_sz = max(24, fs + 10)
        card_min_h = max(100, fs * 8)

        self.setObjectName("ToolCard")
        self.setMinimumHeight(card_min_h)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(6)

        # 顶部：图标行 + badge
        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        icon_lbl = QLabel("🔧")
        icon_lbl.setStyleSheet(f"QLabel{{font-size: {fs+4}px; background: transparent;}}")
        icon_lbl.setFixedSize(icon_sz, icon_sz)
        top_row.addWidget(icon_lbl)
        top_row.addStretch()

        if badge:
            badge_lbl = QLabel(badge)
            badge_lbl.setStyleSheet(f"""
                QLabel{{
                    background-color: {t['badge_bg']};
                    border: 1px solid {t['badge_border']};
                    padding: 1px 6px;
                    border-radius: 4px;
                    font-size: {max(9, fs-3)}px;
                    color: {t['badge_text']};
                    font-weight: 600;
                }}
            """)
            top_row.addWidget(badge_lbl)

        root.addLayout(top_row)

        # 工具名
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"QLabel{{font-size: {fs}px; font-weight: 700; color: {t['text']}; background: transparent;}}")
        title_lbl.setWordWrap(False)
        title_lbl.setMaximumWidth(160)
        root.addWidget(title_lbl)

        # 副标题（截断显示）
        cat_part = subtitle.split(" · ")[0] if " · " in subtitle else subtitle
        sub_lbl = QLabel(cat_part)
        sub_lbl.setStyleSheet(f"QLabel{{font-size: {max(9, fs-2)}px; color: {t['text_muted']}; background: transparent;}}")
        sub_lbl.setWordWrap(False)
        root.addWidget(sub_lbl)

        root.addStretch()

        # 底部按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        btn_row.setContentsMargins(0, 0, 0, 0)

        run_btn = QPushButton("运行")
        run_btn.setFixedHeight(btn_h)
        run_btn.setStyleSheet(f"""
            QPushButton{{
                background-color: {t['run_btn']};
                border: none;
                border-radius: 5px;
                color: #ffffff;
                font-size: {max(10, fs-1)}px;
                font-weight: 600;
                padding: 0 12px;
            }}
            QPushButton:hover{{ background-color: {t['run_btn_hover']}; }}
        """)
        run_btn.clicked.connect(lambda: self.on_run() if self.on_run else None)

        open_btn = QPushButton("📁")
        open_btn.setFixedSize(btn_h, btn_h)
        open_btn.setStyleSheet(f"""
            QPushButton{{
                background-color: {t['open_btn']};
                border: 1px solid {t['open_btn_border']};
                border-radius: 5px;
                font-size: {max(10, fs-1)}px;
                padding: 0;
            }}
            QPushButton:hover{{ background-color: {t['btn_hover']}; }}
        """)
        open_btn.setToolTip("打开目录")
        open_btn.clicked.connect(lambda: self.on_open() if self.on_open else None)

        btn_row.addWidget(run_btn, 1)
        btn_row.addWidget(open_btn)
        root.addLayout(btn_row)

        t = THEMES.get(CURRENT_THEME, THEMES["浅色"])
        self.setStyleSheet(f"""
            QWidget#ToolCard{{
                background-color: {t['card']};
                border: 1px solid {t['card_border']};
                border-radius: 8px;
            }}
            QWidget#ToolCard:hover{{
                border-color: {t['card_border_hover']};
                background-color: {t['card_hover']};
            }}
            QWidget#ToolCard[selected="true"]{{
                border: 1.5px solid {t['primary']};
                background-color: {t['item_sel']};
            }}
        """)
        self.setProperty("selected", False)



class Toast(QWidget):
    def __init__(self, parent, text, kind="info", duration_ms=2000):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground)

        bg = QFrame(self)
        bg.setObjectName("toastBg")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(bg)

        inner = QHBoxLayout(bg)
        inner.setContentsMargins(14, 10, 14, 10)
        inner.setSpacing(10)

        icon = QLabel("●")
        color = {
            "info": "rgba(59,130,246,0.95)",
            "success": "rgba(34,197,94,0.95)",
            "warning": "rgba(245,158,11,0.95)",
            "danger": "rgba(239,68,68,0.95)",
        }.get(kind, "rgba(59,130,246,0.95)")
        icon.setStyleSheet(f"QLabel{{color:{color}; font-size:14px;}}")
        inner.addWidget(icon)

        label = QLabel(text)
        label.setStyleSheet("QLabel{color:#e5e7eb; font-size:13px; font-weight:600;}")
        label.setWordWrap(True)
        inner.addWidget(label, 1)

        bg.setStyleSheet("""
            QFrame#toastBg{
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
        """)

        # 入场动画（淡入 + 上移一点点）
        self.setWindowOpacity(0.0)
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(160)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)
        self.timer.start(duration_ms)

    def fade_out(self):
        self.out_anim = QPropertyAnimation(self, b"windowOpacity")
        self.out_anim.setDuration(200)
        self.out_anim.setStartValue(1.0)
        self.out_anim.setEndValue(0.0)
        self.out_anim.finished.connect(self.close)
        self.out_anim.start()


class ToastManager:
    def __init__(self, host_window: QMainWindow):
        self.host = host_window

    def show(self, text, kind="info", duration_ms=2000):
        toast = Toast(self.host, text, kind=kind, duration_ms=duration_ms)
        toast.adjustSize()

        # 右下角位置（贴边留 20px）
        margin = 20
        host_geo = self.host.geometry()
        x = host_geo.x() + host_geo.width() - toast.width() - margin
        y = host_geo.y() + host_geo.height() - toast.height() - margin
        toast.move(x, y)
        toast.show()

class ToolManagerApp(QMainWindow):
    def add_card_item(self, list_widget, title, subtitle, badge, data, mode):
        card = ToolCardWidget(
            title=title,
            subtitle=subtitle,
            badge=badge,
            mode=mode
        )

        item = QListWidgetItem()
        item.setSizeHint(QSize(10, 78))
        item.setData(Qt.UserRole, mode)        # tool / env / shortcut
        item.setData(Qt.UserRole + 1, data)    # 原始数据 dict

        list_widget.addItem(item)
        list_widget.setItemWidget(item, card)

    def update_bulk_bar(self):
        n = len(self.tool_list.selectedItems())
        show = n > 0

        if hasattr(self, "bulk_bar"):
            self.bulk_bar.setVisible(show)
        if hasattr(self, "bulk_label"):
            self.bulk_label.setText(f"已选中 {n} 项")

        # 可选：选中时确保显示列表页
        if n > 0 and hasattr(self, "tools_stack"):
            self.tools_stack.setCurrentIndex(1)

    def update_bulk_bar_for(self, list_widget):
        n = len(list_widget.selectedItems())
        show = n > 0

        if hasattr(self, "bulk_bar"):
            self.bulk_bar.setVisible(show)
        if hasattr(self, "bulk_label"):
            self.bulk_label.setText(f"已选中 {n} 项")
    def update_shortcut_bulk_bar(self):
        self.update_bulk_bar_for(self.shortcut_list)

    def update_env_bulk_bar(self):
        self.update_bulk_bar_for(self.env_list)

    def sync_tool_card_selection_style(self):
        for i in range(self.tool_list.count()):
            it = self.tool_list.item(i)
            w = self.tool_list.itemWidget(it)
            if w is None:
                continue
            w.setProperty("selected", it.isSelected())
            w.style().unpolish(w)
            w.style().polish(w)
            w.update()

    def __init__(self):
        super().__init__()

        # 读取保存的主题/字体设置
        global CURRENT_THEME, CURRENT_FONT_SIZE
        _s = QSettings("TBox", "TBox")
        CURRENT_THEME = _s.value("theme", "浅色")
        CURRENT_FONT_SIZE = int(_s.value("font_size", 13))

        # 应用样式到整个 app（让所有子窗口/对话框都继承）
        _app = QApplication.instance()
        _app.setStyleSheet(build_style())
        _app.setFont(QFont("Microsoft YaHei UI", CURRENT_FONT_SIZE))
        
        # 读取窗口大小和位置
        self.restore_window_geometry()
        
        # 设置窗口属性
        self.setWindowTitle("工具管理器")
        self.setMinimumSize(900, 600)
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        
        # 初始化调整大小相关属性
        self.resizing = False
        self.resize_edge = None
        self.resize_start_pos = None
        self.resize_start_geometry = None
        self.edge_size = 5
        
        # 初始化拖拽相关属性
        self.dragging = False
        self.drag_start_pos = None
        self.drag_start_geometry = None
        
        # 创建主容器
        self.central_widget = QWidget()
        self.central_widget.setObjectName("appContainer")

        
        # 创建阴影效果
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.shadow.setOffset(0, 4)
        self.central_widget.setGraphicsEffect(self.shadow)

        # 设置中央窗口部件
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 12)
        self.main_layout.setSpacing(8)
        
        # 初始化数据属性
        self.environments = []
        self.categories = []
        self.shortcut_dirs = []
        self.categories_order = []
        self.search_keyword = ""
        
        # 初始化快捷键相关属性
        self.hotkey_enabled = True
        self.global_hotkey = None
        
        # 初始化界面
        self.init_ui()
        self.toast = ToastManager(self)
        
        # 加载配置
        self.load_config()
        self.toast = ToastManager(self)
        
        # 设置连接
        self.setup_connections()
        
        # 设置快捷键
        self.setup_hotkey()
        
        # 设置系统托盘
        self.setup_tray()
        
        # 加载数据
        self.load_data()
        
        # 窗口淡入动画
        self.fade_in_animation()
        self.tool_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # 可选：点空白取消多选更舒服
        self.tool_list.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.tool_list.itemSelectionChanged.connect(self.sync_tool_card_selection_style)


        # 启用亚克力效果
        self.enable_acrylic_effect()
    def show_tool_context_menu(self, pos):
        item = self.tool_list.itemAt(pos)
        if not item:
            return

        # 若右键点到的 item 没在选中集合里，先把它设为当前选中（符合常见交互）
        if not item.isSelected():
            self.tool_list.setCurrentItem(item)

        selected_items = self.tool_list.selectedItems()
        multi = len(selected_items) > 1

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
                color: #1e293b;
            }
            QMenu::item{ padding: 7px 14px; border-radius: 5px; color: #374151; }
            QMenu::item:selected{ background-color: #eff6ff; color: #2563eb; }
            QMenu::separator{ height: 1px; background: #e2e8f0; margin: 4px 8px; }
        """)

        if multi:
            act_move = menu.addAction(f"🗂 批量移动（{len(selected_items)}）…")
            act_del  = menu.addAction(f"🗑 批量删除（{len(selected_items)}）…")
            chosen = menu.exec_(self.tool_list.mapToGlobal(pos))
            if not chosen:
                return

            if chosen == act_move:
                self.batch_move_selected_tools()
            elif chosen == act_del:
                self.batch_delete_selected_tools()
            return

        # ---- 单选菜单（沿用你原来的）----
        category = item.data(Qt.UserRole)
        tool = item.data(Qt.UserRole + 1) or {}
        name = tool.get("display_name", "未命名工具")
        path = tool.get("path", "")

        act_run  = menu.addAction("▶ 运行")
        act_open = menu.addAction("📁 打开目录")
        act_copy = menu.addAction("📋 复制路径")
        menu.addSeparator()
        act_edit = menu.addAction("✏️ 编辑…")
        act_move = menu.addAction("🗂 移动到分类…")
        menu.addSeparator()
        act_del  = menu.addAction("🗑 删除")

        chosen = menu.exec_(self.tool_list.mapToGlobal(pos))
        if not chosen:
            return

        if chosen == act_run:
            tmp = QListWidgetItem(name)
            tmp.setData(Qt.UserRole, category)
            self.run_tool(tmp)

        elif chosen == act_open:
            try:
                d = os.path.dirname(path)
                if d and os.path.exists(d):
                    os.startfile(d)
                else:
                    QMessageBox.warning(self, "错误", "目录不存在或路径为空")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"打开失败: {e}")

        elif chosen == act_copy:
            QApplication.clipboard().setText(path or "")
            if hasattr(self, "toast"):
                self.toast.show("已复制路径", kind="success")

        elif chosen == act_edit:
            new_name, ok1 = QInputDialog.getText(self, "编辑工具", "显示名称：", text=name)
            if not ok1:
                return
            new_path, ok2 = QInputDialog.getText(self, "编辑工具", "路径：", text=path)
            if not ok2:
                return
            tool["display_name"] = (new_name.strip() or name)
            tool["path"] = new_path.strip()

            # 写回（按对象引用或 name+path 兜底）
            tools = self.categories.get(category, [])
            for t in tools:
                if t is tool or (t.get("display_name") == name and t.get("path") == path):
                    t.update(tool)
                    break

            if hasattr(self, "save_config"):
                self.save_config()
            if hasattr(self, "toast"):
                self.toast.show("工具已更新", kind="success")
            self.update_tool_list()

        elif chosen == act_move:
            self._move_one_tool(category, tool)

        elif chosen == act_del:
            self._delete_one_tool(category, tool, name=name, path=path)


        category = item.data(Qt.UserRole)
        tool = item.data(Qt.UserRole + 1) or {}
        name = tool.get("display_name", "未命名工具")
        path = tool.get("path", "")

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
                color: #1e293b;
            }
            QMenu::item{
                padding: 7px 14px;
                border-radius: 5px;
                color: #374151;
            }
            QMenu::item:selected{
                background-color: #eff6ff;
                color: #2563eb;
            }
            QMenu::separator{
                height: 1px;
                background: #e2e8f0;
                margin: 4px 8px;
            }
        """)

        act_run = menu.addAction("▶ 运行")
        act_open = menu.addAction("📁 打开目录")
        act_copy = menu.addAction("📋 复制路径")
        menu.addSeparator()
        act_edit = menu.addAction("✏️ 编辑…")
        act_move = menu.addAction("🗂 移动到分类…")
        menu.addSeparator()
        act_del = menu.addAction("🗑 删除")
        # 删除项更危险一点：可以加个红色提示（Qt 样式不太好单独染色，先保持一致）

        chosen = menu.exec_(self.tool_list.mapToGlobal(pos))
        if not chosen:
            return

        if chosen == act_run:
            tmp = QListWidgetItem(name)
            tmp.setData(Qt.UserRole, category)
            # 复用你的 run_tool（它内部会根据当前选中/或其他逻辑运行）
            self.run_tool(tmp)

        elif chosen == act_open:
            try:
                d = os.path.dirname(path)
                if d and os.path.exists(d):
                    os.startfile(d)
                else:
                    QMessageBox.warning(self, "错误", "目录不存在或路径为空")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"打开失败: {e}")

        elif chosen == act_copy:
            QApplication.clipboard().setText(path or "")
            if hasattr(self, "toast"):
                self.toast.show("已复制路径", kind="success")
            else:
                QMessageBox.information(self, "提示", "已复制路径")

        elif chosen == act_edit:
            # 最小可用编辑：编辑名称 & 路径（不依赖你原来的编辑弹窗）
            new_name, ok1 = QInputDialog.getText(self, "编辑工具", "显示名称：", text=name)
            if not ok1:
                return
            new_path, ok2 = QInputDialog.getText(self, "编辑工具", "路径：", text=path)
            if not ok2:
                return

            tool["display_name"] = new_name.strip() or name
            tool["path"] = new_path.strip()

            # 写回数据结构
            try:
                tools = self.categories.get(category, [])
                for t in tools:
                    if t is tool:
                        break
                    # 兜底：按原 name+path 匹配
                    if t.get("display_name") == name and t.get("path") == path:
                        t.update(tool)
                        break
            except Exception:
                pass

            if hasattr(self, "save_config"):
                self.save_config()
            if hasattr(self, "toast"):
                self.toast.show("工具已更新", kind="success")
            self.update_tool_list()

        elif chosen == act_move:
            cats = list(getattr(self, "categories_order", [])) or list(self.categories.keys())
            if not cats:
                return
            target, ok = QInputDialog.getItem(self, "移动到分类", "选择目标分类：", cats, editable=False)
            if not ok or not target or target == category:
                return

            # 从原分类移除
            src_list = self.categories.get(category, [])
            moved_tool = None
            for i, t in enumerate(list(src_list)):
                if t is tool or (t.get("display_name") == name and t.get("path") == path):
                    moved_tool = t
                    del src_list[i]
                    break

            if moved_tool is None:
                return

            # 加到目标分类
            self.categories.setdefault(target, []).append(moved_tool)

            if hasattr(self, "save_config"):
                self.save_config()
            if hasattr(self, "toast"):
                self.toast.show(f"已移动到：{target}", kind="success")

            # 让界面更符合直觉：切到目标分类
            for i in range(self.category_list.count()):
                if self.category_list.item(i).text() == target:
                    self.category_list.setCurrentRow(i)
                    break

            self.update_tool_list()

        elif chosen == act_del:
            # 删除确认：优先用你做过的 epic_confirm，否则用 QMessageBox
            ok = False
            if hasattr(self, "epic_confirm"):
                ok = self.epic_confirm("确认删除", f"确定要删除工具：{name} 吗？")
            else:
                ok = QMessageBox.question(self, "确认删除", f"确定要删除工具：{name} 吗？") == QMessageBox.Yes
            if not ok:
                return

            tools = self.categories.get(category, [])
            for i, t in enumerate(list(tools)):
                if t is tool or (t.get("display_name") == name and t.get("path") == path):
                    del tools[i]
                    break

            if hasattr(self, "save_config"):
                self.save_config()
            if hasattr(self, "toast"):
                self.toast.show("工具已删除", kind="success")
            self.update_tool_list()

    def batch_delete_selected_tools(self):
        items = self.tool_list.selectedItems()
        if not items:
            return

        names = []
        for it in items:
            tool = it.data(Qt.UserRole + 1) or {}
            names.append(tool.get("display_name", "未命名工具"))
        count = len(items)

        ok = False
        msg = f"确定要删除选中的 {count} 个工具吗？"
        if hasattr(self, "epic_confirm"):
            ok = self.epic_confirm("批量删除", msg)
        else:
            ok = QMessageBox.question(self, "批量删除", msg) == QMessageBox.Yes
        if not ok:
            return

        # 按分类分组删除，避免边删边遍历出错
        to_delete = {}
        for it in items:
            cat = it.data(Qt.UserRole)
            tool = it.data(Qt.UserRole + 1)
            if cat and tool:
                to_delete.setdefault(cat, []).append(tool)

        for cat, tools in to_delete.items():
            src = self.categories.get(cat, [])
            # 通过对象引用删除；若不是同一引用则按字段兜底
            for tool in tools:
                removed = False
                for i, t in enumerate(list(src)):
                    if t is tool:
                        del src[i]
                        removed = True
                        break
                if not removed:
                    dn = tool.get("display_name")
                    p = tool.get("path")
                    for i, t in enumerate(list(src)):
                        if t.get("display_name") == dn and t.get("path") == p:
                            del src[i]
                            break

        if hasattr(self, "save_config"):
            self.save_config()
        if hasattr(self, "toast"):
            self.toast.show(f"已删除 {count} 个工具", kind="success")
        self.update_tool_list()

    def batch_move_selected_tools(self):
        items = self.tool_list.selectedItems()
        if not items:
            return

        cats = list(getattr(self, "categories_order", [])) or list(self.categories.keys())
        if not cats:
            return

        target, ok = QInputDialog.getItem(self, "批量移动", "选择目标分类：", cats, editable=False)
        if not ok or not target:
            return

        # 收集要移动的 tool
        picked = []
        for it in items:
            cat = it.data(Qt.UserRole)
            tool = it.data(Qt.UserRole + 1)
            if cat and tool:
                picked.append((cat, tool))

        if not picked:
            return

        moved_count = 0
        for src_cat, tool in picked:
            if src_cat == target:
                continue
            src_list = self.categories.get(src_cat, [])
            moved_tool = None

            # 按引用删
            for i, t in enumerate(list(src_list)):
                if t is tool:
                    moved_tool = t
                    del src_list[i]
                    break

            # 兜底：按字段匹配
            if moved_tool is None:
                dn = tool.get("display_name")
                p = tool.get("path")
                for i, t in enumerate(list(src_list)):
                    if t.get("display_name") == dn and t.get("path") == p:
                        moved_tool = t
                        del src_list[i]
                        break

            if moved_tool is None:
                continue

            self.categories.setdefault(target, []).append(moved_tool)
            moved_count += 1

        if hasattr(self, "save_config"):
            self.save_config()
        if hasattr(self, "toast"):
            self.toast.show(f"已移动 {moved_count} 个工具 → {target}", kind="success")

        # 切到目标分类更符合直觉
        for i in range(self.category_list.count()):
            if self.category_list.item(i).text() == target:
                self.category_list.setCurrentRow(i)
                break

        self.update_tool_list()

    def _move_one_tool(self, category, tool):
        cats = list(getattr(self, "categories_order", [])) or list(self.categories.keys())
        if not cats:
            return
        target, ok = QInputDialog.getItem(self, "移动到分类", "选择目标分类：", cats, editable=False)
        if not ok or not target or target == category:
            return
        # 复用批量逻辑：构造一个临时选中集合
        self.categories.setdefault(target, [])
        src_list = self.categories.get(category, [])
        dn = tool.get("display_name")
        p = tool.get("path")
        for i, t in enumerate(list(src_list)):
            if t is tool or (t.get("display_name") == dn and t.get("path") == p):
                self.categories[target].append(t)
                del src_list[i]
                break
        if hasattr(self, "save_config"):
            self.save_config()
        if hasattr(self, "toast"):
            self.toast.show(f"已移动到：{target}", kind="success")
        self.update_tool_list()

    def _delete_one_tool(self, category, tool, name="", path=""):
        ok = False
        msg = f"确定要删除工具：{name or tool.get('display_name','未命名工具')} 吗？"
        if hasattr(self, "epic_confirm"):
            ok = self.epic_confirm("确认删除", msg)
        else:
            ok = QMessageBox.question(self, "确认删除", msg) == QMessageBox.Yes
        if not ok:
            return
        src = self.categories.get(category, [])
        dn = tool.get("display_name")
        p = tool.get("path")
        for i, t in enumerate(list(src)):
            if t is tool or (t.get("display_name") == dn and t.get("path") == p):
                del src[i]
                break
        if hasattr(self, "save_config"):
            self.save_config()
        if hasattr(self, "toast"):
            self.toast.show("工具已删除", kind="success")
        self.update_tool_list()



    def enable_acrylic_effect(self):
        pass  # 浅色主题不需要亚克力效果
    def epic_confirm(self, title: str, text: str) -> bool:
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(QMessageBox.Warning)
        yes = box.addButton("确认", QMessageBox.AcceptRole)
        no = box.addButton("取消", QMessageBox.RejectRole)
        box.setDefaultButton(no)
        # 暗色样式覆盖系统 MessageBox（先救急，后续可替换成自定义弹窗）
        box.setStyleSheet("""
            QMessageBox{background-color:#ffffff; color:#1e293b;}
            QLabel{color:#1e293b;}
            QPushButton{
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
                color: #374151;
            }
            QPushButton:hover{background-color: #e2e8f0;}
        """)
        box.exec_()
        return box.clickedButton() == yes

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
            self.save_window_geometry()
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
                # 字体/主题变化时刷新卡片
                self.update_tool_list()
                if hasattr(self, "update_env_list"):
                    self.update_env_list()
                if hasattr(self, "update_shortcut_list"):
                    self.update_shortcut_list()

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
            pos = event.pos()
            
            # 检查是否在标题栏区域
            if pos.y() < 50:  # 标题栏高度
                # 标题栏区域用于拖拽窗口
                self.dragging = True
                self.drag_start_pos = event.globalPos()
                self.drag_start_geometry = self.geometry()
                return
            
            # 检查是否在调整大小的边缘
            edge = self.get_resize_edge(pos)
            if edge:
                self.resizing = True
                self.resize_edge = edge
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
                self.set_resize_cursor(edge)
                return
            else:
                # 普通拖拽
                self.dragPos = event.globalPos()
                event.accept()
            
    def mouseMoveEvent(self, event):
        pos = event.pos()
        
        # 处理拖拽
        if hasattr(self, 'dragging') and self.dragging and event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.drag_start_pos
            new_pos = self.drag_start_geometry.topLeft() + delta
            self.move(new_pos)
            return
        
        # 处理调整大小
        if hasattr(self, 'resizing') and self.resizing and event.buttons() == Qt.LeftButton:
            self.handle_resize(event.globalPos())
            self.set_resize_cursor(self.resize_edge)
            return
        
        # 更新光标
        if not hasattr(self, 'resizing') or not self.resizing:
            self.update_cursor(pos)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 重置拖拽状态
            if hasattr(self, 'dragging'):
                self.dragging = False
            
            # 重置调整大小状态
            if hasattr(self, 'resizing'):
                self.resizing = False
                self.resize_edge = None
                self.setCursor(Qt.ArrowCursor)
            event.accept()
    
    def get_resize_edge(self, pos):
        """获取调整大小的边缘"""
        edge_size = 5  # 边缘检测大小
        width = self.width()
        height = self.height()
        
        # 排除标题栏区域（标题栏高度为50）
        title_bar_height = 50
        if pos.y() < title_bar_height:
            return None  # 标题栏区域不调整大小，只用于拖拽
        
        # 检测角落（优先级高于边缘）
        if pos.x() <= edge_size and pos.y() <= title_bar_height + edge_size:
            return "top-left"
        elif pos.x() >= width - edge_size and pos.y() <= title_bar_height + edge_size:
            return "top-right"
        elif pos.x() <= edge_size and pos.y() >= height - edge_size:
            return "bottom-left"
        elif pos.x() >= width - edge_size and pos.y() >= height - edge_size:
            return "bottom-right"
        
        # 检测边缘
        elif pos.y() <= title_bar_height + edge_size:
            return "top"
        elif pos.y() >= height - edge_size:
            return "bottom"
        elif pos.x() <= edge_size:
            return "left"
        elif pos.x() >= width - edge_size:
            return "right"
        
        return None
    
    def update_cursor(self, pos):
        """更新鼠标光标 - Windows标准方式"""
        edge = self.get_resize_edge(pos)
        if edge:
            if edge == "top-left":
                self.setCursor(Qt.SizeFDiagCursor)
            elif edge == "top-right":
                self.setCursor(Qt.SizeBDiagCursor)
            elif edge == "bottom-left":
                self.setCursor(Qt.SizeBDiagCursor)
            elif edge == "bottom-right":
                self.setCursor(Qt.SizeFDiagCursor)
            elif edge in ["left", "right"]:
                self.setCursor(Qt.SizeHorCursor)
            elif edge in ["top", "bottom"]:
                self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
    
    def handle_resize(self, global_pos):
        """处理调整大小 - 优化后的平滑调整"""
        if not self.resize_start_geometry:
            return
        
        delta_x = global_pos.x() - self.resize_start_pos.x()
        delta_y = global_pos.y() - self.resize_start_pos.y()
        
        # 获取起始几何信息
        start_geometry = self.resize_start_geometry
        min_width = self.minimumWidth()
        min_height = self.minimumHeight()
        
        # 计算新的几何信息
        new_x = start_geometry.x()
        new_y = start_geometry.y()
        new_width = start_geometry.width()
        new_height = start_geometry.height()
        
        # 根据调整边缘计算新的几何信息
        if self.resize_edge == "top-left":
            # 左上角：调整左边和上边
            new_width = max(min_width, start_geometry.width() - delta_x)
            new_height = max(min_height, start_geometry.height() - delta_y)
            new_x = start_geometry.right() - new_width
            new_y = start_geometry.bottom() - new_height
            
        elif self.resize_edge == "top-right":
            # 右上角：调整右边和上边
            new_width = max(min_width, start_geometry.width() + delta_x)
            new_height = max(min_height, start_geometry.height() - delta_y)
            new_y = start_geometry.bottom() - new_height
            
        elif self.resize_edge == "bottom-left":
            # 左下角：调整左边和下边
            new_width = max(min_width, start_geometry.width() - delta_x)
            new_height = max(min_height, start_geometry.height() + delta_y)
            new_x = start_geometry.right() - new_width
            
        elif self.resize_edge == "bottom-right":
            # 右下角：调整右边和下边
            new_width = max(min_width, start_geometry.width() + delta_x)
            new_height = max(min_height, start_geometry.height() + delta_y)
            
        elif self.resize_edge == "left":
            # 左边：只调整左边
            new_width = max(min_width, start_geometry.width() - delta_x)
            new_x = start_geometry.right() - new_width
            
        elif self.resize_edge == "right":
            # 右边：只调整右边
            new_width = max(min_width, start_geometry.width() + delta_x)
            
        elif self.resize_edge == "top":
            # 上边：只调整上边
            new_height = max(min_height, start_geometry.height() - delta_y)
            new_y = start_geometry.bottom() - new_height
            
        elif self.resize_edge == "bottom":
            # 下边：只调整下边
            new_height = max(min_height, start_geometry.height() + delta_y)
        
        # 应用新的几何信息
        self.setGeometry(new_x, new_y, new_width, new_height)

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

    def show_env_context_menu(self, pos):
        if not self.env_list.itemAt(pos):
            return
        menu = QMenu(self)
        act_open = QAction("打开目录", self)
        act_del = QAction("删除选中", self)
        act_open.triggered.connect(self.open_selected_env_dir)
        act_del.triggered.connect(self.delete_environment)
        menu.addAction(act_open)
        menu.addSeparator()
        menu.addAction(act_del)
        menu.exec_(self.env_list.mapToGlobal(pos))

    def open_selected_env_dir(self):
        it = self.env_list.currentItem()
        if not it:
            return
        env = it.data(Qt.UserRole + 1) or {}
        path = env.get("path", "")
        if path and os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.warning(self, "错误", "路径不存在！")
    def show_shortcut_context_menu(self, pos):
        if not self.shortcut_list.itemAt(pos):
            return
        menu = QMenu(self)
        act_open = QAction("打开", self)
        act_del = QAction("删除选中", self)
        act_open.triggered.connect(self.open_selected_shortcut)
        act_del.triggered.connect(self.delete_shortcut)
        menu.addAction(act_open)
        menu.addSeparator()
        menu.addAction(act_del)
        menu.exec_(self.shortcut_list.mapToGlobal(pos))

    def open_selected_shortcut(self):
        it = self.shortcut_list.currentItem()
        if not it:
            return
        sc = it.data(Qt.UserRole + 1) or {}
        name = sc.get("display_name", "")
        tmp = QListWidgetItem(name)
        self.open_shortcut(tmp)  # 复用你已有逻辑 :contentReference[oaicite:7]{index=7}

    def init_ui(self):
        # 创建自定义标题栏
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)

        # 搜索框 + 操作按钮行
        search_bar = QWidget()
        search_bar.setStyleSheet("QWidget{background: transparent;}")
        search_bar_layout = QHBoxLayout(search_bar)
        search_bar_layout.setContentsMargins(0, 0, 0, 0)
        search_bar_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  搜索工具...")
        search_bar_layout.addWidget(self.search_input, 1)

        btn_style_primary = "QPushButton{background:#3b82f6;border:none;border-radius:6px;color:#fff;font-weight:700;padding:0 14px;} QPushButton:hover{background:#2563eb;}"
        btn_style_normal  = "QPushButton{background:#fff;border:1px solid #e2e8f0;border-radius:6px;color:#000;font-weight:700;padding:0 14px;} QPushButton:hover{background:#f8fafc;}"

        # 工具按钮组
        self.tool_btn_group = QWidget()
        tg = QHBoxLayout(self.tool_btn_group)
        tg.setContentsMargins(0,0,0,0); tg.setSpacing(8)
        self.add_tool_btn = QPushButton("添加工具")
        self.add_tool_btn.setStyleSheet(btn_style_primary)
        self.del_tool_btn = QPushButton("删除工具")
        self.del_tool_btn.setStyleSheet(btn_style_normal)
        settings_btn_top = QPushButton("设置")
        settings_btn_top.setStyleSheet(btn_style_normal)
        settings_btn_top.clicked.connect(self.show_settings)
        tg.addWidget(self.add_tool_btn)
        tg.addWidget(self.del_tool_btn)
        tg.addWidget(settings_btn_top)

        # 快捷方式按钮组
        self.sc_btn_group = QWidget()
        sg = QHBoxLayout(self.sc_btn_group)
        sg.setContentsMargins(0,0,0,0); sg.setSpacing(8)
        self.add_sc_btn = QPushButton("添加快捷方式")
        self.add_sc_btn.setStyleSheet(btn_style_primary)
        self.del_sc_btn = QPushButton("删除快捷方式")
        self.del_sc_btn.setStyleSheet(btn_style_normal)
        sg.addWidget(self.add_sc_btn)
        sg.addWidget(self.del_sc_btn)
        self.sc_btn_group.setVisible(False)

        # 环境按钮组
        self.env_btn_group = QWidget()
        eg = QHBoxLayout(self.env_btn_group)
        eg.setContentsMargins(0,0,0,0); eg.setSpacing(8)
        self.add_env_btn = QPushButton("添加环境")
        self.add_env_btn.setStyleSheet(btn_style_primary)
        self.del_env_btn = QPushButton("删除环境")
        self.del_env_btn.setStyleSheet(btn_style_normal)
        eg.addWidget(self.add_env_btn)
        eg.addWidget(self.del_env_btn)
        self.env_btn_group.setVisible(False)

        search_bar_layout.addWidget(self.tool_btn_group)
        search_bar_layout.addWidget(self.sc_btn_group)
        search_bar_layout.addWidget(self.env_btn_group)
        self.main_layout.addWidget(search_bar)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle{background:#e2e8f0; width:1px;}")

        # 用一个容器包住 splitter，加左右边距
        content_wrapper = QWidget()
        content_wrapper.setStyleSheet("QWidget{background:transparent;}")
        cw_layout = QHBoxLayout(content_wrapper)
        cw_layout.setContentsMargins(12, 0, 12, 0)
        cw_layout.addWidget(splitter)
        self.main_layout.addWidget(content_wrapper, 1)

        # 搜索栏也加边距
        search_bar.setContentsMargins(12, 0, 12, 0)

        # 左侧分类面板
        left_panel = QWidget()
        left_panel.setFixedWidth(180)
        left_panel.setStyleSheet("QWidget{background:transparent;}")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(6)

        # 分类标题行
        cat_header = QHBoxLayout()
        self.category_title_label = QLabel("工具分类")
        self.category_title_label.setStyleSheet("QLabel{font-size:13px;font-weight:700;color:#1e293b;}")
        self.category_count_label = QLabel("")
        self.category_count_label.setStyleSheet("QLabel{font-size:12px;color:#94a3b8;}")
        cat_header.addWidget(self.category_title_label)
        cat_header.addWidget(self.category_count_label)
        cat_header.addStretch()

        self.add_cat_btn = QPushButton("+")
        self.add_cat_btn.setFixedSize(24, 24)
        self.add_cat_btn.setToolTip("添加新分类")
        self.add_cat_btn.setStyleSheet("""
            QPushButton{background:#f1f5f9;border:1px solid #e2e8f0;border-radius:5px;
                color:#374151;font-size:14px;font-weight:700;}
            QPushButton:hover{background:#e2e8f0;}
        """)
        self.del_cat_btn = QPushButton("−")
        self.del_cat_btn.setFixedSize(24, 24)
        self.del_cat_btn.setToolTip("删除选中分类")
        self.del_cat_btn.setStyleSheet("""
            QPushButton{background:#f1f5f9;border:1px solid #e2e8f0;border-radius:5px;
                color:#374151;font-size:14px;font-weight:700;}
            QPushButton:hover{background:#e2e8f0;}
        """)
        cat_header.addWidget(self.add_cat_btn)
        cat_header.addWidget(self.del_cat_btn)
        left_layout.addLayout(cat_header)

        # 分类搜索框
        self.category_search_input = QLineEdit()
        self.category_search_input.setPlaceholderText("搜索分类...")
        self.category_search_input.setFixedHeight(28)
        self.category_search_input.setStyleSheet("""
            QLineEdit{background:#fff;border:1px solid #e2e8f0;border-radius:5px;
                padding:2px 8px;font-size:12px;}
        """)
        left_layout.addWidget(self.category_search_input)

        # 清空搜索按钮（隐藏）
        self.clear_category_search_btn = QPushButton("×")
        self.clear_category_search_btn.setFixedSize(28, 28)
        self.clear_category_search_btn.setVisible(False)
        self.clear_category_search_btn.clicked.connect(self.clear_category_search)

        self.category_list = self.create_list_widget()
        self.category_list.setDragEnabled(True)
        self.category_list.setDragDropMode(QListWidget.InternalMove)
        self.category_list.model().rowsMoved.connect(self.update_category_order)
        self.category_list.setStyleSheet("""
            QListWidget{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:4px;}
            QListWidget::item{border-radius:5px;padding:5px 8px;color:#475569;font-size:13px;}
            QListWidget::item:hover{background:#f1f5f9;color:#1e293b;}
            QListWidget::item:selected{background:#eff6ff;color:#2563eb;font-weight:600;}
            QListWidget::item:selected:active{background:#eff6ff;color:#2563eb;}
        """)
        left_layout.addWidget(self.category_list, 1)

        # 右侧主面板
        right_panel = QTabWidget()
        right_panel.setStyleSheet("""
            QTabWidget::pane{border:none;background:transparent;}
            QTabBar::tab{background:transparent;border:none;color:#64748b;
                padding:8px 16px;font-size:13px;}
            QTabBar::tab:selected{color:#2563eb;border-bottom:2px solid #3b82f6;font-weight:600;}
            QTabBar::tab:hover{color:#1e293b;}
        """)

        # 工具管理 tab
        tool_tab = QWidget()
        tool_tab.setStyleSheet("QWidget{background:transparent;}")
        tool_layout = QVBoxLayout(tool_tab)
        tool_layout.setContentsMargins(0, 8, 0, 0)
        tool_layout.setSpacing(8)

        self.tool_list = self.create_list_widget()
        self.tool_list.setViewMode(QListWidget.IconMode)
        self.tool_list.setResizeMode(QListWidget.Adjust)
        self.tool_list.setWrapping(True)
        self.tool_list.setUniformItemSizes(False)
        self.tool_list.setStyleSheet("""
            QListWidget{background:transparent;border:none;}
            QListWidget::item{background:transparent;border:none;padding:4px;}
        """)
        self.tool_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tool_list.customContextMenuRequested.connect(self.show_tool_context_menu)

        self.empty_state = EmptyStateWidget(
            title="该分类下暂无工具",
            subtitle="你可以在此分类中添加、编辑和管理工具",
            button_text="添加工具",
            on_action=self.add_tool,
            parent=self
        )

        self.tools_stack = QStackedLayout()
        self.tools_stack.addWidget(self.empty_state)
        self.tools_stack.addWidget(self.tool_list)

        # 批量操作条
        self.bulk_bar = QFrame()
        self.bulk_bar.setObjectName("bulkBar")
        self.bulk_bar.setVisible(False)
        bulk_layout = QHBoxLayout(self.bulk_bar)
        bulk_layout.setContentsMargins(12, 8, 12, 8)
        bulk_layout.setSpacing(8)
        self.bulk_label = QLabel("已选中 0 项")
        self.bulk_label.setStyleSheet("QLabel{color:#2563eb;font-weight:700;}")
        self.btn_bulk_move = QPushButton("移动到分类")
        self.btn_bulk_delete = QPushButton("删除")
        self.btn_bulk_delete.setStyleSheet("""
            QPushButton{background:#fff0f0;border:1px solid #fca5a5;color:#ef4444;
                border-radius:5px;padding:4px 12px;font-weight:600;}
            QPushButton:hover{background:#fee2e2;}
        """)
        self.btn_bulk_clear = QPushButton("取消选择")
        bulk_layout.addWidget(self.bulk_label, 1)
        bulk_layout.addWidget(self.btn_bulk_move)
        bulk_layout.addWidget(self.btn_bulk_delete)
        bulk_layout.addWidget(self.btn_bulk_clear)
        self.tool_list.itemSelectionChanged.connect(self.update_bulk_bar)
        self.update_bulk_bar()
        self.btn_bulk_move.clicked.connect(self.batch_move_selected_tools)
        self.btn_bulk_delete.clicked.connect(self.batch_delete_selected_tools)
        self.btn_bulk_clear.clicked.connect(self.tool_list.clearSelection)

        tools_container = QWidget()
        tools_container.setLayout(self.tools_stack)
        tools_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tools_container.setObjectName("toolsPanel")
        tools_container.setAttribute(Qt.WA_StyledBackground, True)

        tool_layout.addWidget(self.bulk_bar)
        tool_layout.addWidget(tools_container, 1)

        # 快捷方式 tab
        shortcut_tab = QWidget()
        shortcut_tab.setStyleSheet("QWidget{background:transparent;}")
        shortcut_layout = QVBoxLayout(shortcut_tab)
        shortcut_layout.setContentsMargins(0, 8, 0, 0)
        shortcut_layout.setSpacing(8)
        self.shortcut_list = self.create_list_widget()
        self.shortcut_list.setViewMode(QListWidget.IconMode)
        self.shortcut_list.setResizeMode(QListWidget.Adjust)
        self.shortcut_list.setWrapping(True)
        self.shortcut_list.setUniformItemSizes(False)
        self.shortcut_list.setStyleSheet("QListWidget{background:transparent;border:none;} QListWidget::item{background:transparent;border:none;padding:4px;}")
        shortcut_layout.addWidget(self.shortcut_list)
        self.shortcut_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.shortcut_list.customContextMenuRequested.connect(self.show_shortcut_context_menu)
        self.shortcut_list.itemSelectionChanged.connect(self.update_shortcut_bulk_bar)

        # 环境 tab
        env_tab = QWidget()
        env_tab.setStyleSheet("QWidget{background:transparent;}")
        env_layout = QVBoxLayout(env_tab)
        env_layout.setContentsMargins(0, 8, 0, 0)
        env_layout.setSpacing(8)
        self.env_list = self.create_list_widget()
        self.env_list.setViewMode(QListWidget.IconMode)
        self.env_list.setResizeMode(QListWidget.Adjust)
        self.env_list.setWrapping(True)
        self.env_list.setUniformItemSizes(False)
        self.env_list.setStyleSheet("QListWidget{background:transparent;border:none;} QListWidget::item{background:transparent;border:none;padding:4px;}")
        env_layout.addWidget(self.env_list)
        self.env_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.env_list.customContextMenuRequested.connect(self.show_env_context_menu)
        self.env_list.itemSelectionChanged.connect(self.update_env_bulk_bar)

        right_panel.addTab(tool_tab, QIcon(resource_path("icons/tool.png")), "工具")
        right_panel.addTab(shortcut_tab, QIcon(resource_path("icons/shortcut.png")), "快捷方式")
        right_panel.addTab(env_tab, QIcon(resource_path("icons/environment.png")), "运行环境")

        def on_tab_changed(idx):
            self.tool_btn_group.setVisible(idx == 0)
            self.sc_btn_group.setVisible(idx == 1)
            self.env_btn_group.setVisible(idx == 2)

        right_panel.currentChanged.connect(on_tab_changed)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([180, 820])
        self.shortcut_list.itemSelectionChanged.connect(self.update_shortcut_bulk_bar)
        self.env_list.itemSelectionChanged.connect(self.update_env_bulk_bar)

        self.load_data()


    def update_env_list(self):
        self.env_list.clear()

        def add_env_card(env: dict):
            name = env.get("display_name", "未命名环境")
            path = env.get("path", "")
            badge = "ENV"
            subtitle = f"{badge} · {path}"

            def open_dir():
                try:
                    if os.path.exists(path):
                        os.startfile(path)
                    else:
                        QMessageBox.warning(self, "错误", "路径不存在！")
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"打开失败: {str(e)}")

            # 这里复用你现有的卡片组件
            card = ToolCardWidget(name, subtitle, badge=badge, on_run=open_dir, on_open=open_dir)

            lw_item = QListWidgetItem()
            lw_item.setSizeHint(QSize(200, max(110, CURRENT_FONT_SIZE * 9)))
            lw_item.setData(Qt.UserRole, "env")
            lw_item.setData(Qt.UserRole + 1, env)
            lw_item.setToolTip(subtitle)

            self.env_list.addItem(lw_item)
            self.env_list.setItemWidget(lw_item, card)
            #lw_item.setText(name)

        for env in getattr(self, "environments", []):
            add_env_card(env)

        # 如果你做了"卡片选中同步"，这里也调用一下
        if hasattr(self, "sync_env_card_selection_style"):
            self.sync_env_card_selection_style()


    def update_shortcut_list(self):
        self.shortcut_list.clear()

        def add_sc_card(sc: dict):
            name = sc.get("display_name", "未命名快捷方式")
            path = sc.get("path", "")
            t = sc.get("type", "dir")
            badge = "DIR" if t == "dir" else "LNK"
            subtitle = f"{badge} · {path}"

            def open_it():
                # 你已经有 open_shortcut(item)（它用 item.text() 查 display_name）:contentReference[oaicite:2]{index=2}
                # 这里用"临时 item"复用原逻辑，避免你重写一套
                tmp = QListWidgetItem(name)
                self.open_shortcut(tmp)

            card = ToolCardWidget(name, subtitle, badge=badge, on_run=open_it, on_open=open_it)

            lw_item = QListWidgetItem()
            lw_item.setSizeHint(QSize(200, max(110, CURRENT_FONT_SIZE * 9)))
            lw_item.setData(Qt.UserRole, "shortcut")
            lw_item.setData(Qt.UserRole + 1, sc)
            lw_item.setToolTip(subtitle)

            self.shortcut_list.addItem(lw_item)
            self.shortcut_list.setItemWidget(lw_item, card)
            #lw_item.setText(name)

        for sc in getattr(self, "shortcut_dirs", []):
            add_sc_card(sc)

        if hasattr(self, "sync_shortcut_card_selection_style"):
            self.sync_shortcut_card_selection_style()



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
        
        # 为分类按钮设置特殊样式
        if icon_name in ["plus.png","tool.png", "delete.png","shortcut.png","environment.png"]:
            #btn.setFixedSize(36, 36)
            # 不设置内联样式，让全局样式表生效
        #else:
            # 设置按钮样式
            btn.setStyleSheet("""
                QPushButton {
                    font-weight: 600;
                    font-size: 14px;
                    padding: 10px 20px;
                    border-radius: 8px;
                    min-height: 10px;
                }
            """)
        
        return btn

    def create_list_widget(self):
        list_widget = QListWidget()
        list_widget.setFont(QFont("Microsoft YaHei", 12))
        list_widget.setAlternatingRowColors(False)
        list_widget.setStyleSheet("QListWidget{background: transparent;} QListWidget::item{background: transparent;}")
        list_widget.setFocusPolicy(Qt.NoFocus)
        list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        list_widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        list_widget.setSpacing(8)
        return list_widget

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE,encoding="utf-8") as f:
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
        with open(CONFIG_FILE, "w",encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        self.category_list.clear()
        self.category_list.addItems(self.categories_order)
        
        # 初始化分类计数显示
        total_count = len(self.categories_order)
        self.category_count_label.setText(f"({total_count})")

        self.update_env_list()
        self.update_shortcut_list()
    
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
        # 清空
        self.tool_list.clear()

        def add_card(category: str, tool: dict):
            tool_name = tool.get("display_name", "未命名工具")
            tool_path = tool.get("path", "")
            ext = os.path.splitext(tool_path)[1].lower().replace(".", "").upper() or "TOOL"
            subtitle = f"{category} · {ext} · {tool_path}"

            def run():
                item = QListWidgetItem(tool_name)
                item.setData(Qt.UserRole, category)
                self.run_tool(item)

            def open_dir():
                try:
                    p = os.path.dirname(tool_path)
                    if os.path.exists(p):
                        os.startfile(p)
                    else:
                        QMessageBox.warning(self, "错误", "路径不存在！")
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"打开失败: {str(e)}")

            card = ToolCardWidget(tool_name, subtitle, badge=ext, on_run=run, on_open=open_dir)
            lw_item = QListWidgetItem()
            lw_item.setSizeHint(QSize(200, max(110, CURRENT_FONT_SIZE * 9)))
            lw_item.setData(Qt.UserRole, category)
            lw_item.setData(Qt.UserRole + 1, tool)
            lw_item.setToolTip(subtitle)

            self.tool_list.addItem(lw_item)
            self.tool_list.setItemWidget(lw_item, card)
            #lw_item.setText(tool_name)

            # 决定展示哪些工具：搜索优先，否则展示当前分类
        keyword = (getattr(self, "search_keyword", "") or "").strip().lower()

        if keyword:
            for category in getattr(self, "categories_order", []):
                for tool in self.categories.get(category, []):
                    if keyword in tool.get("display_name", "").lower():
                        add_card(category, tool)

        else:
            current = self.category_list.currentItem()
            if not current and self.category_list.count() > 0:
                self.category_list.setCurrentRow(0)
                current = self.category_list.currentItem()

            if current:
                category = current.text()
                for tool in self.categories.get(category, []):
                    add_card(category, tool)

        # 空状态切换
        if hasattr(self, "tools_stack"):
            has_items = self.tool_list.count() > 0
            self.tools_stack.setCurrentIndex(1 if has_items else 0)

        self.sync_tool_card_selection_style()

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

                    self.toast.show(f"已创建分类：{name}", kind="success")

                except Exception as e:
                    logger.error(f"创建分类目录时发生错误: {str(e)}")
                    QMessageBox.warning(self, "警告", f"分类已创建，但创建目录失败: {str(e)}")
            else:
                QMessageBox.warning(self, "警告", "分类名称已存在！")

    def delete_category(self):
        if items := self.category_list.selectedItems():
            reply = self.toast.show("分类删除完成", kind="success")
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
                self.update_env_list()
                self.save_config()

    def delete_environment(self):
        items = self.env_list.selectedItems()
        if not items:
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {len(items)} 个环境吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # ✅ 先收集要删的环境名（从 UserRole+1 拿 dict，别用 item.text()）
        to_del = set()
        for it in items:
            env = it.data(Qt.UserRole + 1)
            if isinstance(env, dict):
                to_del.add(env.get("display_name") or env.get("name"))
            else:
                # 兜底：如果你后面加了 setText(name)，这里也能用
                to_del.add(it.text())

        # ✅ 一次性更新数据源
        self.environments = [
            e for e in self.environments
            if (e.get("display_name") or e.get("name")) not in to_del
        ]

        # ✅ 最后只刷新一次
        self.update_env_list()
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
            self.update_shortcut_list()
            self.save_config()

    def delete_shortcut(self):
        items = self.shortcut_list.selectedItems()
        if not items:
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {len(items)} 个快捷方式吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        to_del = set()
        for it in items:
            sc = it.data(Qt.UserRole + 1)
            if isinstance(sc, dict):
                to_del.add(sc.get("display_name") or sc.get("name"))
            else:
                to_del.add(it.text())

        self.shortcut_dirs = [
            s for s in self.shortcut_dirs
            if (s.get("display_name") or s.get("name")) not in to_del
        ]

        self.update_shortcut_list()
        self.save_config()


    def run_tool(self, item):
        try:
            # --- 1) 类型保险 ---
            if not isinstance(self.categories, dict):
                self.categories = {}
            if not isinstance(self.environments, list):
                self.environments = []

            if self.search_keyword:
                category = item.data(Qt.UserRole)
            else:
                current = self.category_list.currentItem()
                if not current:
                    QMessageBox.warning(self, "错误", "请先选择分类！")
                    return
                category = current.text()

            tool_name = item.text().strip()
            if not tool_name:
                QMessageBox.warning(self, "错误", "无法获取工具名称（卡片项缺少 setText）")
                return

            tools = self.categories.get(category, [])
            tool = next((t for t in tools if t.get("display_name") == tool_name), None)
            if not tool:
                QMessageBox.warning(self, "错误", "找不到工具路径！")
                return

            tool_path = tool.get("path", "")
            if not tool_path:
                QMessageBox.warning(self, "错误", "工具路径为空！")
                return

            work_dir = os.path.dirname(tool_path)
            ext = os.path.splitext(tool_path)[1].lower()

            env_path = None
            if ext in ('.py', '.jar'):
                env_names = [e.get("display_name") for e in self.environments if isinstance(e, dict)]
                env_names = [n for n in env_names if n]
                if not env_names:
                    QMessageBox.warning(self, "错误", "请先添加运行环境！")
                    return

                env_dialog = EnvironmentSelectionDialog(
                    parent=self,
                    environments=env_names,
                    env_details=self.environments,
                    title="选择运行环境"
                )

                if env_dialog.exec_() != QDialog.Accepted:
                    return

                env_name = env_dialog.get_selected_environment()
                if not env_name:
                    return

                env_path = next((e.get("path") for e in self.environments
                                 if e.get("display_name") == env_name), None)
                if not env_path:
                    QMessageBox.warning(self, "错误", "环境路径无效！")
                    return

            cmd = self.build_command(tool_path, ext, env_path)
            self.execute_command(cmd, work_dir)

        except Exception as e:
            logger.exception("run_tool 崩溃")
            QMessageBox.critical(self, "运行失败", f"{type(e).__name__}: {e}")


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

    # def show_context_menu(self, pos):
    #     menu = QMenu()
    #     open_action = QAction("打开所在目录", self)
    #     open_action.triggered.connect(self.open_tool_directory)
    #     menu.addAction(open_action)
    #     menu.exec_(self.tool_list.mapToGlobal(pos))

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
        #self.tool_list.customContextMenuRequested.connect(self.show_context_menu)
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

    def set_resize_cursor(self, edge):
        """设置调整大小的光标 - Windows标准方式"""
        if edge == "top-left":
            self.setCursor(Qt.SizeFDiagCursor)
        elif edge == "top-right":
            self.setCursor(Qt.SizeBDiagCursor)
        elif edge == "bottom-left":
            self.setCursor(Qt.SizeBDiagCursor)
        elif edge == "bottom-right":
            self.setCursor(Qt.SizeFDiagCursor)
        elif edge in ["left", "right"]:
            self.setCursor(Qt.SizeHorCursor)
        elif edge in ["top", "bottom"]:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def restore_window_geometry(self):
        settings = QSettings("TBox", "TBox")
        geometry = settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1600, 800)
            self.move(200, 120)

    def save_window_geometry(self):
        settings = QSettings("TBox", "TBox")
        settings.setValue("window_geometry", self.saveGeometry())

    def closeEvent(self, event):
        try:
            self.save_window_geometry()
            self.hide()
            event.ignore()
        except Exception as e:
            logger.error(f"处理窗口关闭事件时发生错误: {str(e)}")
            event.accept()

if __name__ == "__main__":
    try:
        # 检查命令行参数
        force_restart = "--force-restart" in sys.argv or "-f" in sys.argv
        
        # 创建应用程序实例
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setQuitOnLastWindowClosed(False)
        app.setWindowIcon(QIcon(resource_path("icon.png"))) 
        
        # 设置应用程序信息
        app.setApplicationName("TBox")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("TBox")
        app.setOrganizationDomain("tbox.local")
        
        # 检查是否已有实例运行
        if not force_restart:
            socket = QLocalSocket()
            socket.connectToServer("TBox")
            
            if socket.waitForConnected(500):
                logger.info("TBox已在运行，激活现有实例")
                socket.write(b"show")
                socket.waitForBytesWritten()
                socket.close()
                sys.exit(0)
            socket.close()
        else:
            logger.info("强制重启模式，忽略现有实例检测")
        
        # 创建本地服务器
        server = QLocalServer()
        if not server.listen("TBox"):
            logger.warning("无法创建本地服务器，可能端口被占用")
            # 尝试删除可能存在的服务器文件
            try:
                import os
                server_file = os.path.join(os.environ.get('TEMP', ''), 'TBox')
                if os.path.exists(server_file):
                    os.remove(server_file)
                    logger.info("已删除旧的服务器文件")
                    if server.listen("TBox"):
                        logger.info("成功创建本地服务器")
                    else:
                        logger.error("仍然无法创建本地服务器")
                        sys.exit(1)
            except Exception as e:
                logger.error(f"清理服务器文件时发生错误: {str(e)}")
                sys.exit(1)
        
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
                # 删除服务器文件
                import os
                server_file = os.path.join(os.environ.get('TEMP', ''), 'TBox')
                if os.path.exists(server_file):
                    os.remove(server_file)
                    logger.info("已删除服务器文件")
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

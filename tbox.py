import sys
import os
import json
import subprocess
import win32com.client
import winreg
import logging
import keyboard
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
    QShortcut
)
from PyQt5.QtNetwork import QLocalSocket, QLocalServer
import win32con
import win32api
import win32gui
import ctypes
from ctypes import wintypes

CONFIG_FILE = "tool_manager_config.json"

STYLE_SHEET = """
/* 纯白透明设计 */
QWidget, QMainWindow {
    background-color: rgba(255, 255, 255, 240);
    color: #333333;
    font-family: 'Microsoft YaHei';
    font-size: 14px;
    border: none;
    outline: none;
}

QMainWindow {
    background-color: rgba(255, 255, 255, 200);
}

/* 设置对话框样式 */
QDialog {
    background-color: rgba(255, 255, 255, 240);
}

QGroupBox {
    background-color: rgba(255, 255, 255, 200);
    border: 1px solid rgba(200, 200, 200, 100);
    border-radius: 6px;
    margin-top: 15px;
    padding-top: 15px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
}

QFormLayout {
    margin: 0;
    spacing: 15px;
}

QFormLayout QLabel {
    min-width: 120px;
}

QPushButton {
    background-color: rgba(70, 130, 220, 200);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: rgba(70, 130, 220, 250);
}

QPushButton:pressed {
    background-color: rgba(50, 110, 200, 250);
}

QKeySequenceEdit {
    min-width: 200px;
    height: 30px;
    border: 1px solid rgba(200, 200, 200, 100);
    border-radius: 6px;
    padding: 5px;
}

QCheckBox {
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    border: 1px solid rgba(200, 200, 200, 100);
    background-color: white;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    border: 1px solid rgba(70, 130, 220, 200);
    background-color: rgba(70, 130, 220, 200);
    border-radius: 3px;
}

/* 自定义标题栏样式 */
#titleBar {
    background-color: rgba(255, 255, 255, 200);
    border-bottom: 1px solid rgba(200, 200, 200, 100);
    height: 40px;
}

#titleLabel {
    color: #333333;
    font-size: 14px;
    font-weight: bold;
}

#settingsButton, #minimizeButton, #maximizeButton {
    background-color: transparent;
    color: #666666;
    border: none;
    padding: 6px;
    border-radius: 3px;
    min-width: 30px;
    min-height: 30px;
}

#settingsButton:hover, #minimizeButton:hover, #maximizeButton:hover {
    background-color: rgba(230, 230, 230, 200);
}

#settingsButton:pressed, #minimizeButton:pressed, #maximizeButton:pressed {
    background-color: rgba(220, 220, 220, 200);
}

#closeButton {
    background-color: transparent;
    color: #666666;
    border: none;
    padding: 6px;
    border-radius: 3px;
    min-width: 30px;
    min-height: 30px;
}

#closeButton:hover {
    background-color: rgba(232, 17, 35, 200);
    color: white;
}

#closeButton:pressed {
    background-color: rgba(200, 15, 30, 250);
}

QListWidget {
    background-color: rgba(255, 255, 255, 200);
    border: 1px solid rgba(200, 200, 200, 100);
    border-radius: 6px;
    padding: 5px;
    margin: 5px;
    alternate-background-color: rgba(245, 245, 245, 200);
}

QListWidget::item {
    height: 40px;
    padding: 8px 12px;
    border-bottom: 1px solid rgba(200, 200, 200, 60);
}

QListWidget::item:hover {
    background-color: rgba(240, 240, 240, 200);
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: rgba(200, 220, 240, 200);
    color: #333333;
    border-radius: 4px;
    font-weight: bold;
}

QLineEdit {
    border: 1px solid rgba(200, 200, 200, 100);
    border-radius: 6px;
    padding: 8px;
    font-size: 14px;
    margin: 10px 0;
    background-color: rgba(255, 255, 255, 200);
}

QLineEdit:focus {
    border-color: rgba(100, 150, 255, 180);
}

QTabWidget::pane {
    border: 1px solid rgba(200, 200, 200, 100);
    border-radius: 6px;
    background-color: rgba(255, 255, 255, 200);
}

QTabBar::tab {
    background: rgba(240, 240, 240, 200);
    border: 1px solid rgba(200, 200, 200, 100);
    color: #333333;
    padding: 8px 20px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background: rgba(255, 255, 255, 220);
    color: rgba(70, 130, 220, 250);
    border-bottom-color: rgba(255, 255, 255, 220);
}

QScrollBar:vertical {
    background: rgba(240, 240, 240, 100);
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(180, 180, 180, 150);
    min-height: 30px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(160, 160, 160, 180);
}

QScrollBar::add-line:vertical, 
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
}

/* 环境选择框美化 */
QComboBox {
    border: 1px solid rgba(200, 200, 200, 100);
    border-radius: 6px;
    padding: 6px 12px;
    min-width: 120px;
    background: rgba(255, 255, 255, 200);
    color: #333333;
}

QComboBox:hover {
    border-color: rgba(180, 180, 180, 150);
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 24px;
    border-left: 1px solid rgba(200, 200, 200, 100);
    border-radius: 0 6px 6px 0;
}

QComboBox QAbstractItemView {
    border: 1px solid rgba(200, 200, 200, 100);
    border-radius: 6px;
    background: rgba(255, 255, 255, 220);
    padding: 4px;
    outline: 0px;
    selection-background-color: rgba(200, 220, 240, 200);
    selection-color: #333333;
    color: #333333;
    margin: 2px 0;
}

QComboBox QAbstractItemView::item {
    height: 30px;
    padding: 0 8px;
    border-radius: 4px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: rgba(240, 240, 240, 200);
}

QMenu {
    background-color: rgba(255, 255, 255, 240);
    border: 1px solid rgba(200, 200, 200, 100);
    border-radius: 6px;
}

QMenu::item {
    padding: 6px 24px 6px 20px;
    border: 1px solid transparent;
}

QMenu::item:selected {
    background-color: rgba(200, 220, 240, 200);
    color: #333333;
    border-radius: 4px;
}

#appContainer {
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 200);
}
"""

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tbox.log'),
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
        self.setFixedHeight(40)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        # 应用图标
        self.iconLabel = QLabel()
        self.iconLabel.setFixedSize(20, 20)
        icon = QIcon(resource_path("icon.png"))
        pixmap = icon.pixmap(20, 20)
        self.iconLabel.setPixmap(pixmap)
        
        # 标题
        self.titleLabel = QLabel("TBox")
        self.titleLabel.setObjectName("titleLabel")
        
        # 设置按钮
        self.settingsButton = QPushButton()
        self.settingsButton.setObjectName("settingsButton")
        self.settingsButton.setFixedSize(30, 30)
        self.settingsButton.setIcon(QIcon(resource_path("icons/settings.png")))
        self.settingsButton.setIconSize(QSize(16, 16))
        self.settingsButton.clicked.connect(self.parent.show_settings)
        
        # 窗口控制按钮
        self.minimizeButton = QPushButton()
        self.minimizeButton.setObjectName("minimizeButton")
        self.minimizeButton.setFixedSize(30, 30)
        self.minimizeButton.setIcon(QIcon(resource_path("icons/minimize.png")))
        self.minimizeButton.setIconSize(QSize(16, 16))
        
        self.maximizeButton = QPushButton()
        self.maximizeButton.setObjectName("maximizeButton")
        self.maximizeButton.setFixedSize(30, 30)
        self.maximizeButton.setIcon(QIcon(resource_path("icons/maximize.png")))
        self.maximizeButton.setIconSize(QSize(16, 16))
        
        self.closeButton = QPushButton()
        self.closeButton.setObjectName("closeButton")
        self.closeButton.setFixedSize(30, 30)
        self.closeButton.setIcon(QIcon(resource_path("icons/close.png")))
        self.closeButton.setIconSize(QSize(16, 16))
        
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

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setFixedSize(500, 400)  # 增加对话框大小
        self.setStyleSheet(STYLE_SHEET)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 启动设置
        startup_group = QGroupBox("启动设置")
        startup_layout = QFormLayout()
        startup_layout.setContentsMargins(15, 15, 15, 15)
        startup_layout.setSpacing(15)
        startup_layout.setLabelAlignment(Qt.AlignLeft)  # 左对齐标签
        
        self.startup_check = QCheckBox("开机自启动")
        self.startup_check.setChecked(self.is_startup_enabled())
        startup_layout.addRow(self.startup_check)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # 快捷键设置
        hotkey_group = QGroupBox("快捷键设置")
        hotkey_layout = QFormLayout()
        hotkey_layout.setContentsMargins(15, 15, 15, 15)
        hotkey_layout.setSpacing(15)
        hotkey_layout.setLabelAlignment(Qt.AlignLeft)  # 左对齐标签
        
        self.hotkey_edit = QKeySequenceEdit()
        self.hotkey_edit.setKeySequence(QKeySequence(self.get_hotkey()))
        self.hotkey_edit.setMinimumWidth(200)  # 设置最小宽度
        hotkey_layout.addRow("显示/隐藏快捷键:", self.hotkey_edit)
        
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)
        button_layout.setSpacing(15)
        
        save_btn = QPushButton("保存")
        save_btn.setFixedWidth(120)
        save_btn.setFixedHeight(35)
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedWidth(120)
        cancel_btn.setFixedHeight(35)
        cancel_btn.clicked.connect(self.reject)
        
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
    
    def save_settings(self):
        try:
            hotkey = self.hotkey_edit.keySequence().toString()
            
            # 保存快捷键设置
            settings = QSettings("TBox", "TBox")
            settings.setValue("hotkey", hotkey)
            
            # 设置开机启动
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_WRITE)
            if self.startup_check.isChecked():
                exe_path = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, "TBox", 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, "TBox")
                except WindowsError:
                    pass
            winreg.CloseKey(key)
            
            self.accept()
        except WindowsError as e:
            QMessageBox.warning(self, "错误", f"设置保存失败: {str(e)}")
            return

class GlobalHotkey(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.hotkey_id = 1
        self.registered = False
        
    def register_hotkey(self, key_sequence):
        try:
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
            
            logger.info(f"注册快捷键 - 修饰键: {modifiers}, 按键: {key}")
            
            # 注销旧的快捷键
            if self.registered:
                try:
                    win32gui.UnregisterHotKey(None, self.hotkey_id)
                    logger.info("成功注销旧的快捷键")
                except Exception as e:
                    logger.warning(f"注销旧快捷键失败: {str(e)}")
            
            # 注册新的快捷键
            try:
                result = win32gui.RegisterHotKey(None, self.hotkey_id, modifiers, key)
                if result == 0:  # 如果返回0，表示注册失败
                    error_code = win32api.GetLastError()
                    error_msg = win32api.FormatMessage(error_code)
                    raise Exception(f"注册快捷键失败 (错误代码: {error_code}): {error_msg}")
                logger.info("成功注册新的快捷键")
            except Exception as e:
                logger.error(f"注册快捷键失败: {str(e)}")
                return False
            
            self.registered = True
            return True
            
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
            
            # 创建阴影效果
            self.shadow = QGraphicsDropShadowEffect(self)
            self.shadow.setBlurRadius(20)
            self.shadow.setColor(QColor(0, 0, 0, 60))
            self.shadow.setOffset(0, 0)
            
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
            self.main_layout.setContentsMargins(20, 20, 20, 20)
            self.main_layout.setSpacing(15)
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
            self.tray_icon.hide()
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
            dialog = SettingsDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                # 重新设置快捷键
                self.setup_hotkey()
                logger.info("设置已保存")
        except Exception as e:
            logger.error(f"显示设置对话框时发生错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"设置保存失败: {str(e)}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.isMaximized():
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            
    def fade_in_animation(self):
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

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
        
        category_header = QWidget()
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("工具分类"))
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
        self.add_tool_btn = self.create_icon_button("添加工具", "rgba(70, 130, 220, 200)", "tool.png")
        self.del_tool_btn = self.create_icon_button("删除工具", "rgba(220, 70, 70, 200)", "delete.png")
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
        self.add_sc_btn = self.create_icon_button("添加快捷方式", "rgba(70, 130, 220, 200)", "shortcut.png")
        self.del_sc_btn = self.create_icon_button("删除快捷方式", "rgba(220, 70, 70, 200)", "delete.png")
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
        self.add_env_btn = self.create_icon_button("添加环境", "rgba(70, 130, 220, 200)", "environment.png")
        self.del_env_btn = self.create_icon_button("删除环境", "rgba(220, 70, 70, 200)", "delete.png")
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
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ 
                background-color: {color};
                opacity: 0.8;
            }}
        """)
        icon_path = resource_path(f"icons/{icon_name}")
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(16, 16))
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
        self.env_list.clear()
        self.env_list.addItems([e["display_name"] for e in self.environments])
        self.shortcut_list.clear()
        self.shortcut_list.addItems([s["display_name"] for s in self.shortcut_dirs])
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)
            self.update_tool_list()

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
                self.categories_order.append(name)
                self.categories[name] = []
                self.category_list.addItem(name)
                self.save_config()

    def delete_category(self):
        if items := self.category_list.selectedItems():
            reply = QMessageBox.question(
                self, "确认删除", f"确定要删除 {len(items)} 个分类吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                for item in items:
                    name = item.text()
                    self.categories_order.remove(name)
                    del self.categories[name]
                    self.category_list.takeItem(self.category_list.row(item))
                self.save_config()
                self.update_tool_list()

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
                
            env_name, ok = QInputDialog.getItem(
                self, "选择环境", "请选择运行环境:", 
                env_names, 0, False
            )
            if not ok: return
                
            env_path = next(
                e["path"] for e in self.environments
                if e["display_name"] == env_name
            )

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
            
            # 创建全局快捷键处理器
            self.hotkey_handler = GlobalHotkey(self.show_and_activate)
            
            # 注册全局快捷键
            if not self.hotkey_handler.register_hotkey(hotkey):
                raise Exception("注册全局快捷键失败，请尝试使用其他快捷键组合")
            
            # 安装事件过滤器
            QApplication.instance().installNativeEventFilter(self.hotkey_handler)
            
            logger.info(f"成功设置快捷键: {hotkey}")
            
        except Exception as e:
            logger.error(f"设置快捷键时发生错误: {str(e)}")
            QMessageBox.warning(self, "警告", f"快捷键设置失败: {str(e)}\n请尝试使用其他快捷键组合")
    
    def show_and_activate(self):
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

if __name__ == "__main__":
    try:
        # 确保只有一个实例运行
        socket = QLocalSocket()
        socket.connectToServer("TBox")
        if socket.waitForConnected(500):
            # 如果已经有一个实例在运行，则退出
            sys.exit(0)
        socket.close()
        
        # 创建本地服务器
        server = QLocalServer()
        server.listen("TBox")
        
        # 创建应用程序实例
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # 设置应用程序属性
        app.setQuitOnLastWindowClosed(False)
        
        # 创建主窗口
        window = ToolManagerApp()
        
        # 运行应用程序
        sys.exit(app.exec_())
        
    except Exception as e:
        logging.error(f"程序启动失败: {str(e)}")
        QMessageBox.critical(None, "错误", f"程序启动失败: {str(e)}")
        sys.exit(1)

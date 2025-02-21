import sys
import os
import json
import subprocess
import win32com.client
from PyQt5.QtCore import (
    Qt, QSize, QPropertyAnimation, 
    QEasingCurve, QModelIndex
)
from PyQt5.QtGui import QFont, QIcon, QColor, QBrush
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QFileDialog, QInputDialog,
    QSplitter, QTabWidget, QLabel, QMessageBox,
    QMenu, QAction, QLineEdit, QListWidgetItem
)

CONFIG_FILE = "tool_manager_config.json"

STYLE_SHEET = """
/* 现代扁平化设计 */
QWidget {
    background-color: #F5F7FA;
    color: #2D3A4B;
    font-family: 'Microsoft YaHei';
    font-size: 14px;
    border: none;
    outline: none;
}

QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #E4E7ED;
    border-radius: 8px;
    padding: 5px;
}

QListWidget::item {
    height: 40px;
    padding: 8px 12px;
    border-bottom: 1px solid #EBEEF5;
}

QListWidget::item:hover {
    background-color: #F5F7FA;
    border-radius: 6px;
}

QListWidget::item:selected {
    background-color: #409EFF;
    color: white;
    border-radius: 6px;
}

QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #DCDFE6;
    border-radius: 6px;
    padding: 8px 16px;
    min-width: 80px;
    color: #606266;
}

QPushButton:hover {
    background-color: #409EFF;
    color: white;
    border-color: #409EFF;
}

QLineEdit {
    border: 1px solid #DCDFE6;
    border-radius: 6px;
    padding: 8px;
    font-size: 14px;
    margin: 10px 0;
}

QLineEdit:focus {
    border-color: #409EFF;
}

QTabWidget::pane {
    border: 1px solid #E4E7ED;
    border-radius: 8px;
}

QTabBar::tab {
    background: #F5F7FA;
    border: 1px solid #E4E7ED;
    color: #909399;
    padding: 8px 20px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background: white;
    color: #409EFF;
    border-bottom-color: white;
}
"""

def resource_path(relative_path):
    """ 获取资源的绝对路径 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class ToolManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tool Manager Pro")
        self.setGeometry(200, 200, 1200, 800)
        self.setStyleSheet(STYLE_SHEET)
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        
        self.environments = []
        self.categories = {}
        self.shortcut_dirs = []
        self.categories_order = []
        self.search_keyword = ""
        
        self.load_config()
        self.init_ui()
        self.setup_connections()
        self.fade_in_animation()

    def fade_in_animation(self):
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("全局搜索工具（支持模糊匹配）...")
        main_layout.addWidget(self.search_input)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
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
        self.add_tool_btn = self.create_icon_button("添加工具", "#409EFF", "tool.png")
        self.del_tool_btn = self.create_icon_button("删除工具", "#F56C6C", "delete.png")
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
        self.add_sc_btn = self.create_icon_button("添加快捷方式", "#409EFF", "shortcut.png")
        self.del_sc_btn = self.create_icon_button("删除快捷方式", "#F56C6C", "delete.png")
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
        self.add_env_btn = self.create_icon_button("添加环境", "#409EFF", "environment.png")
        self.del_env_btn = self.create_icon_button("删除环境", "#F56C6C", "delete.png")
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
                background-color: {QColor(color).darker(115).name()};
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
            category = self.category_list.currentItem().text()
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ToolManagerApp()
    window.show()
    sys.exit(app.exec())

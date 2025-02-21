import sys
import os
import json
import subprocess
import win32com.client
from PyQt5.QtCore import (
    Qt, 
    QSize,          
    QPropertyAnimation, 
    QEasingCurve
)
from PyQt5.QtGui import (
    QFont, 
    QIcon, 
    QColor
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QFileDialog,
    QInputDialog,
    QSplitter,
    QTabWidget,
    QLabel,
    QMessageBox,
    QMenu,
    QAction
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

/* 列表控件 */
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

/* 按钮样式 */
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

QPushButton:pressed {
    background-color: #337ecc;
}

/* 滚动条 */
QScrollBar:vertical {
    background: #F5F7FA;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #C0C4CC;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

/* 下拉框 */
QComboBox {
    border: 1px solid #DCDFE6;
    border-radius: 6px;
    padding: 6px 12px;
    min-width: 120px;
    selection-background-color: #409EFF;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 20px;
    border-left: 1px solid #DCDFE6;
}

QComboBox QAbstractItemView {
    border: 1px solid #E4E7ED;
    selection-background-color: #409EFF;
    selection-color: white;
}

/* 选项卡 */
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

/* 输入对话框 */
QInputDialog QLabel {
    font-size: 14px;
    color: #606266;
}

QInputDialog QLineEdit {
    border: 1px solid #DCDFE6;
    border-radius: 6px;
    padding: 8px;
}

/* 消息框 */
QMessageBox {
    background-color: white;
}

QMessageBox QLabel {
    color: #606266;
    font-size: 14px;
}
"""

class ToolManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tool Manager Pro")
        self.setGeometry(200, 200, 1200, 800)
        self.setStyleSheet(STYLE_SHEET)
        self.setWindowIcon(QIcon("icon.png"))
        
        # 初始化数据
        self.environments = []
        self.categories = {}
        self.shortcut_dirs = []
        
        self.load_config()
        self.init_ui()
        self.setup_connections()
        
        # 启动动画
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
        
        main_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧分类面板
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # 分类标题栏
        category_header = QWidget()
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("工具分类"))
        header_layout.addStretch()
        self.add_cat_btn = self.create_icon_button("添加", "#409EFF", "plus.png")
        self.del_cat_btn = self.create_icon_button("删除", "#F56C6C", "delete.png")
        header_layout.addWidget(self.add_cat_btn)
        header_layout.addWidget(self.del_cat_btn)
        category_header.setLayout(header_layout)
        
        left_layout.addWidget(category_header)
        self.category_list = self.create_list_widget()
        left_layout.addWidget(self.category_list)
        left_panel.setLayout(left_layout)
        
        # 右侧主面板
        right_panel = QTabWidget()
        right_panel.setTabPosition(QTabWidget.North)
        
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
        
        # 快捷方式
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
        
        right_panel.addTab(tool_tab, QIcon("tool.png"), "工具")
        right_panel.addTab(shortcut_tab, QIcon("shortcut.png"), "快捷方式")
        right_panel.addTab(env_tab, QIcon("environment.png"), "运行环境")
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setHandleWidth(1)
        splitter.setSizes([250, 750])
        
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        
        self.load_data()
        
    
    def create_icon_button(self, text, color, icon_path=None):
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
        if icon_path:
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(16, 16))
        return btn

    def create_list_widget(self):
        list_widget = QListWidget()
        list_widget.setFont(QFont("Microsoft YaHei", 12))
        list_widget.setAlternatingRowColors(True)
        list_widget.setFocusPolicy(Qt.NoFocus)
        return list_widget
    
    

    # ---------- 核心功能方法 ---------- #
    def load_config(self):
        # 修改后的完整加载逻辑
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                data = json.load(f)
                self.environments = data.get("environments", [])
                self.categories = data.get("categories", {})
                self.shortcut_dirs = [{
                    "path": s["path"],
                    "display_name": s["display_name"],
                    "type": s.get("type", "dir" if os.path.isdir(s["path"]) else "lnk")
                } for s in data.get("shortcuts", [])]

    def save_config(self):
        data = {
            "environments": self.environments,
            "categories": self.categories,
            "shortcuts": [{
                "path": s["path"],
                "display_name": s["display_name"],
                "type": s.get("type", "dir")  # 兼容旧版本
            } for s in self.shortcut_dirs]
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        # 加载分类
        self.category_list.clear()
        self.category_list.addItems(self.categories.keys())
        
        # 加载环境
        self.env_list.clear()
        self.env_list.addItems([e["display_name"] for e in self.environments])
        
        # 加载快捷方式
        self.shortcut_list.clear()
        self.shortcut_list.addItems([s["display_name"] for s in self.shortcut_dirs])
        
        # 默认选中第一个分类
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)
            self.update_tool_list()

    def update_tool_list(self):
        self.tool_list.clear()
        if current := self.category_list.currentItem():
            category = current.text()
            self.tool_list.addItems([t["display_name"] for t in self.categories.get(category, [])])

    # ---------- 分类操作 ---------- #
    def add_category(self):
        name, ok = QInputDialog.getText(self, "新建分类", "分类名称:")
        if ok and name:
            if name not in self.categories:
                self.categories[name] = []
                self.category_list.addItem(name)
                self.save_config()

    def delete_category(self):
        if items := self.category_list.selectedItems():
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除 {len(items)} 个分类吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                for item in items:
                    del self.categories[item.text()]
                    self.category_list.takeItem(self.category_list.row(item))
                self.save_config()
                self.update_tool_list()

    # ---------- 工具操作 ---------- #
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

    # ---------- 环境操作 ---------- #
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

    # ---------- 快捷方式操作 ---------- #
    def add_shortcut(self):
        """添加目录或文件快捷方式"""
        # 选择类型
        types = ["目录", "文件快捷方式"]
        type_choice, ok = QInputDialog.getItem(
            self, "选择类型", "请选择要添加的类型:", types, 0, False
        )
        if not ok:
            return

        # 获取路径
        path = ""
        if type_choice == "目录":
            path = QFileDialog.getExistingDirectory(self, "选择目录")
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "选择快捷方式", 
                "", 
                "Shortcuts (*.lnk);;All Files (*)"
            )
        
        if not path:
            return

        # 验证路径有效性
        if not os.path.exists(path):
            QMessageBox.warning(self, "错误", "选择的路径不存在！")
            return

        # 获取显示名称
        default_name = os.path.basename(path)
        if type_choice == "文件快捷方式":
            default_name = os.path.splitext(default_name)[0]
        
        name, ok = QInputDialog.getText(
            self, "快捷方式名称", 
            "显示名称：", 
            text=default_name
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

    # ---------- 运行功能 ---------- #
    def run_tool(self, item):
        """运行工具的核心方法"""
        # 获取工具信息
        category_item = self.category_list.currentItem()
        if not category_item:
            QMessageBox.warning(self, "错误", "请先选择分类！")
            return
        
        category = category_item.text()
        tool_name = item.text()
        
        # 查找工具路径
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

        # 根据文件类型处理环境选择
        env_path = None
        if ext in ('.py', '.jar'):
            # 获取环境列表
            env_names = [e["display_name"] for e in self.environments]
            if not env_names:
                QMessageBox.warning(self, "错误", "请先添加运行环境！")
                return
                
            # 弹出环境选择对话框
            env_name, ok = QInputDialog.getItem(
                self, "选择环境", "请选择运行环境:", 
                env_names, 0, False
            )
            if not ok:
                return  # 用户取消选择
                
            # 获取环境路径
            env_path = next(
                e["path"] for e in self.environments
                if e["display_name"] == env_name
            )

        # 构建并执行命令
        cmd = self.build_command(tool_path, ext, env_path)
        self.execute_command(cmd, work_dir)

    def build_command(self, tool_path, ext, env_path=None):
        """构建命令行指令"""
        # 处理路径中的空格
        safe_tool_path = f'"{tool_path}"' if " " in tool_path else tool_path
        
        if ext == '.py':
            python_exe = os.path.join(env_path, "python.exe")
            safe_python = f'"{python_exe}"' if " " in python_exe else python_exe
            return f"{safe_python} {safe_tool_path}"
        
        elif ext == '.jar':
            java_exe = os.path.join(env_path, "java.exe")
            safe_java = f'"{java_exe}"' if " " in java_exe else java_exe
            return f"{safe_java} -jar {safe_tool_path}"
        
        else:  # 直接运行其他类型文件
            return safe_tool_path

    def execute_command(self, command, work_dir):
        """在新CMD窗口中执行命令"""
        try:
            # 处理工作目录中的空格
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

    # ---------- 快捷方式功能 ---------- #
    def open_shortcut(self, item):
        """打开快捷方式"""
        shortcut = next(
            (s for s in self.shortcut_dirs 
             if s["display_name"] == item.text()),
            None
        )
        if not shortcut:
            return

        path = shortcut["path"]
        target_path = path  # 默认目标路径

        try:
            # 如果是快捷方式文件
            if shortcut["type"] == "lnk":
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut_obj = shell.CreateShortCut(path)
                target_path = shortcut_obj.TargetPath

            # 统一处理路径
            if os.path.isdir(target_path):
                self.open_directory(target_path)
            else:
                # 打开文件所在目录并选中文件
                dir_path = os.path.dirname(target_path)
                if os.path.exists(dir_path):
                    os.startfile(dir_path)
                    # Windows下选中文件（需要额外处理）
                    if sys.platform == "win32":
                        subprocess.Popen(
                            f'explorer /select,"{target_path}"',
                            shell=True
                        )
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开失败: {str(e)}")

    def open_directory(self, path):
        """安全打开目录"""
        try:
            if os.path.isdir(path):
                os.startfile(path)
            else:
                QMessageBox.warning(self, "警告", "该路径不是有效的目录")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开目录: {str(e)}")

    def open_path(self, path):
        """打开路径（文件或目录）"""
        if os.path.isdir(path):
            os.startfile(path)
        elif os.path.isfile(path):
            os.startfile(os.path.dirname(path))
        else:
            QMessageBox.warning(self, "错误", "路径不存在！")

    # ---------- 右键菜单 ---------- #
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
            self.open_path(path)

    # ---------- 工具方法 ---------- #
    def create_list_widget(self):
        list_widget = QListWidget()
        list_widget.setAlternatingRowColors(True)
        list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        return list_widget

    def create_button(self, text, callback):
        btn = QPushButton(text)
        btn.setFixedSize(80, 28)
        btn.clicked.connect(callback)
        return btn

    def setup_connections(self):
        # 分类操作
        self.add_cat_btn.clicked.connect(self.add_category)
        self.del_cat_btn.clicked.connect(self.delete_category)
        
        # 工具操作
        self.add_tool_btn.clicked.connect(self.add_tool)
        self.del_tool_btn.clicked.connect(self.delete_tool)
        
        # 环境操作
        self.add_env_btn.clicked.connect(self.add_environment)
        self.del_env_btn.clicked.connect(self.delete_environment)
        
        # 快捷方式操作
        self.add_sc_btn.clicked.connect(self.add_shortcut)
        self.del_sc_btn.clicked.connect(self.delete_shortcut)
        
        # 列表交互
        self.category_list.currentItemChanged.connect(self.update_tool_list)
        self.tool_list.itemDoubleClicked.connect(self.run_tool)
        self.shortcut_list.itemDoubleClicked.connect(self.open_shortcut)
        
        # 右键菜单
        self.tool_list.customContextMenuRequested.connect(self.show_context_menu)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ToolManagerApp()
    window.show()
    sys.exit(app.exec())

import sys
import os
import subprocess
import json
# 修改导入部分，添加缺失的组件
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont  # 移动这行到正确的位置
from PyQt5.QtWidgets import (
    QApplication,
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
    QFrame,
    QStyle
)
from PyQt5.QtCore import Qt, QSize
import shutil  # 导入shutil模块
from PyQt5.QtGui import QIcon  # QIcon也属于QtGui模块


# 默认配置文件路径
CONFIG_FILE = "tool_manager_config.json"

STYLE_SHEET = """
/* 现代扁平化风格 - 兼容PyQt5样式表 */
QWidget {
    background-color: #F8F9FA;
    color: #212529;
    font-family: 'Segoe UI', sans-serif;
}



/* 去除所有默认阴影效果 */
QWidget {
    border: 0;
    outline: 0;
}

QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-radius: 8px;
    padding: 5px;
    margin: 5px 0;
}

QListWidget::item {
    height: 36px;
    padding: 8px;
    border-bottom: 1px solid #F1F3F5;
}

QListWidget::item:hover {
    background-color: #E9ECEF;
}

QListWidget::item:selected {
    background-color: #4DABF7;
    color: #FFFFFF;
    border-radius: 4px;
}

QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-radius: 6px;
    padding: 8px 16px;
    min-width: 100px;
    color: #212529;
}

QPushButton:hover {
    background-color: #4DABF7;
    color: #FFFFFF;
    border-color: #339AF0;
}

QPushButton:pressed {
    background-color: #228BE6;
}

QLabel {
    color: #868E96;
    font-weight: 500;
    font-size: 12px;
    padding: 4px 0;
}

QSplitter::handle {
    background: #DEE2E6;
    width: 1px;
}

QScrollBar:vertical {
    border: none;
    background: #F8F9FA;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #CED4DA;
    min-height: 30px;
    border-radius: 4px;
}
"""

class ToolManagerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tool Manager")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(200, 200, 1000, 700)
        self.setStyleSheet(STYLE_SHEET)

        # 初始化工具和分类数据
        self.environments = []  # List of environment directories
        self.categories = {}  # Dictionary of categories and tools
        self.shortcut_dirs = []  # List of directory shortcuts

        # 尝试读取配置文件
        self.load_config()

        self.init_ui()
        self.setup_tooltips()
    
    def showEvent(self, event):
        # 调用父类方法保持默认行为
        super().showEvent(event)  
        
        # 创建动画
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.start()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # 使用分栏布局
        splitter = QSplitter(Qt.Horizontal)

        # 左侧面板（分类管理）
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        # 分类管理
        left_layout.addWidget(QLabel("分类"))
        self.category_list = self.create_styled_list()
        left_layout.addWidget(self.category_list)

        self.add_category_btn = QPushButton("Add")
        self.del_category_btn = QPushButton("Delete")
        category_btn_layout = self.create_button_layout(self.add_category_btn, self.del_category_btn)
        left_layout.addLayout(category_btn_layout)

        left_panel.setLayout(left_layout)
        splitter.addWidget(left_panel)

        # 右侧面板（使用 QTabWidget 做标签页）
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 使用选项卡布局
        tab_widget = QTabWidget()
        
        # 工具管理标签页
        tool_tab = QWidget()
        tool_layout = QVBoxLayout()
        tool_layout.addWidget(QLabel("工具列表"))
        self.tool_list = self.create_styled_list()
        tool_layout.addWidget(self.tool_list)

        self.add_tool_btn = QPushButton("Add")
        self.del_tool_btn = QPushButton("Delete")
        tool_btn_layout = self.create_button_layout(self.add_tool_btn, self.del_tool_btn)
        tool_layout.addLayout(tool_btn_layout)
        tool_tab.setLayout(tool_layout)
        tab_widget.addTab(tool_tab, "工具")

        # 目录快捷方式标签页
        shortcut_tab = QWidget()
        shortcut_layout = QVBoxLayout()
        shortcut_layout.addWidget(QLabel("目录列表"))
        self.shortcut_list = self.create_styled_list()
        shortcut_layout.addWidget(self.shortcut_list)

        self.add_shortcut_btn = QPushButton("Add")
        self.del_shortcut_btn = QPushButton("Delete")
        shortcut_btn_layout = self.create_button_layout(self.add_shortcut_btn,self.del_shortcut_btn)
        shortcut_layout.addLayout(shortcut_btn_layout)
        shortcut_tab.setLayout(shortcut_layout)
        tab_widget.addTab(shortcut_tab, "目录")

        # 环境管理标签页
        env_tab = QWidget()
        env_layout = QVBoxLayout()
        env_layout.addWidget(QLabel("环境列表"))
        self.env_list = self.create_styled_list()
        env_layout.addWidget(self.env_list)

        self.add_env_btn = QPushButton("Add")
        self.del_env_btn = QPushButton("Delete")
        env_btn_layout = self.create_button_layout(self.add_env_btn, self.del_env_btn)
        env_layout.addLayout(env_btn_layout)
        env_tab.setLayout(env_layout)
        tab_widget.addTab(env_tab, "环境")

        

        # 将选项卡添加到右侧布局
        right_layout.addWidget(tab_widget)
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)

        splitter.setSizes([300, 700])
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)

        # 加载工具和分类
        self.load_tools_and_categories()

        # 连接信号
        self.connect_signals()

    def create_styled_list(self):
        """创建样式化的列表控件"""
        list_widget = QListWidget()
        list_widget.setAlternatingRowColors(True)
        list_widget.setDragDropMode(QListWidget.InternalMove)
        list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        list_widget.setFont(QFont("Arial", 10))
        return list_widget

    def create_button_layout(self, *buttons):
        """创建水平按钮布局"""
        layout = QHBoxLayout()
        layout.setSpacing(5)
        for btn in buttons:
            btn.setFixedSize(120, 30)
            btn.setIconSize(QSize(16, 16))
            layout.addWidget(btn)
        layout.addStretch()
        return layout

    def setup_tooltips(self):
        """设置工具提示"""
        self.add_env_btn.setToolTip("Add new environment directory")
        self.del_env_btn.setToolTip("Remove selected environment")
        self.add_category_btn.setToolTip("Create new category")
        self.del_category_btn.setToolTip("Delete selected category")
        self.add_tool_btn.setToolTip("Add tool to selected category")
        self.del_tool_btn.setToolTip("Remove selected tool")
        self.add_shortcut_btn.setToolTip("Add directory shortcut")

    def connect_signals(self):
        """连接信号与槽"""
        self.add_env_btn.clicked.connect(self.add_environment)
        self.del_env_btn.clicked.connect(self.delete_environment)
        self.add_category_btn.clicked.connect(self.add_category)
        self.del_category_btn.clicked.connect(self.delete_category)
        self.add_tool_btn.clicked.connect(self.add_tool)
        self.del_tool_btn.clicked.connect(self.delete_tool)
        self.add_shortcut_btn.clicked.connect(self.add_shortcut)
        self.tool_list.itemDoubleClicked.connect(self.run_tool)
        self.category_list.itemClicked.connect(self.update_tool_list)
        self.del_shortcut_btn.clicked.connect(self.delete_shortcut)  
    def update_tool_list(self, item):
        """根据点击的分类更新工具列表"""
        category_name = item.text()
        if category_name in self.categories:
            tools = self.categories[category_name]
            self.tool_list.clear()  # 清空当前工具列表
            for tool in tools:
                self.tool_list.addItem(tool)

    def load_config(self):
        """从配置文件加载工具和分类数据"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
                self.environments = config_data.get("environments", [])
                self.categories = config_data.get("categories", {})
                self.shortcut_dirs = config_data.get("shortcuts", [])
                
        else:
            # 创建默认配置文件
            self.create_default_config()

    def create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            "environments": [],
            "categories": {},
            "shortcuts": []
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f)

    def save_config(self):
        """保存配置文件"""
        config_data = {
            "environments": self.environments,
            "categories": self.categories,
            "shortcuts": self.shortcut_dirs
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f)

    def load_tools_and_categories(self):
        """加载工具和分类到界面"""
        # 加载环境
        self.env_list.clear()
        for env in self.environments:
            self.env_list.addItem(env)

        # 加载分类
        self.category_list.clear()
        categories = list(self.categories.keys())  # 获取所有分类名
        if categories:
            for category in categories:
                self.category_list.addItem(category)
            
            # 如果没有选择分类，默认加载第一个分类的工具
            selected_category = self.category_list.item(0)  # 默认选择第一个分类
            if selected_category:
                self.update_tool_list(selected_category)  # 更新工具列表
        else:
            self.tool_list.clear()  # 如果没有分类，清空工具列表

        # 加载工具
        self.tool_list.clear()

        # 如果没有选择分类，默认加载所有工具
        for category, tools in self.categories.items():
            for tool in tools:
                self.tool_list.addItem(tool)


    def add_environment(self):
        """选择一个目录作为环境"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Environment Directory")
        if folder_path:
            self.environments.append(folder_path)
            self.env_list.addItem(folder_path)
            self.save_config()  # 保存配置

    def delete_environment(self):
        item = self.env_list.currentItem()
        if item:
            self.environments.remove(item.text())
            self.env_list.takeItem(self.env_list.row(item))
            self.save_config()  # 保存配置

    def add_category(self):
        category_name, ok = QInputDialog.getText(self, "目录名")
        if ok and category_name:
            category_dir = os.path.join(os.getcwd(), category_name)
            if not os.path.exists(category_dir):
                os.mkdir(category_dir)
            self.categories[category_name] = []
            self.category_list.addItem(category_name)
            self.save_config()  # 保存配置

    def delete_category(self):
        """删除选中的分类"""
        selected_items = self.category_list.selectedItems()  # 获取所有选中的分类
        if selected_items:
            for item in selected_items:
                category_name = item.text()
                if category_name in self.categories:
                    del self.categories[category_name]  # 从数据中删除
                    category_dir = os.path.join(os.getcwd(), category_name)
                    if os.path.exists(category_dir):
                        shutil.rmtree(category_dir)  # 删除目录（非空）
                    self.category_list.takeItem(self.category_list.row(item))  # 从 UI 中删除
            self.save_config()  # 保存配置

    def add_tool(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Tool File", "", "Executable Files (*.exe);;Python Files (*.py);;Java Files (*.jar)")
        if file_path:
            category_name, ok = QInputDialog.getItem(self, "Select Category", "Select Category:", list(self.categories.keys()), 0, False)
            if ok:
                self.categories[category_name].append(file_path)
                self.tool_list.addItem(file_path)
                self.save_config()  # 保存配置

    def delete_tool(self):
        """删除选中的工具"""
        selected_items = self.tool_list.selectedItems()  # 获取所有选中的工具
        if selected_items:
            for item in selected_items:
                tool_path = item.text()
                for category, tools in self.categories.items():
                    if tool_path in tools:
                        tools.remove(tool_path)  # 从类别数据中删除
                        self.tool_list.takeItem(self.tool_list.row(item))  # 从 UI 中删除
            self.save_config()  # 保存配置

    def add_shortcut(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.shortcut_dirs.append(directory)
            self.shortcut_list.addItem(directory)
            self.save_config()  # 保存配置
    
    def delete_shortcut(self):
        """删除选中的快捷方式"""
        selected_items = self.shortcut_list.selectedItems()  # 获取所有选中的项
        if selected_items:
            for item in selected_items:
                shortcut_path = item.text()
                if shortcut_path in self.shortcut_dirs:
                    self.shortcut_dirs.remove(shortcut_path)  # 从数据中删除
                    self.shortcut_list.takeItem(self.shortcut_list.row(item))  # 从 UI 中删除
            self.save_config()  # 保存配置

    def run_tool(self, item):
        """双击工具时，根据文件类型判断如何运行"""
        tool_path = item.text()

        # 选择环境并根据文件类型运行
        env_dir, ok = QInputDialog.getItem(self, "Select Environment", "Choose Environment:", self.environments, 0, False)
        if not ok:
            return  # 如果用户没有选择环境，退出

        if tool_path.endswith(".py"):
            # 如果是Python文件，构建运行命令
            self.run_python_tool(tool_path, env_dir)
        elif tool_path.endswith(".jar"):
            # 如果是JAR文件，构建运行命令
            self.run_java_tool(tool_path, env_dir)
        elif tool_path.endswith(".exe"):
            # 如果是EXE文件，直接运行
            self.run_exe_tool(tool_path, env_dir)

    def run_python_tool(self, tool_path, env_dir):
        """运行Python工具"""
        # 获取工具所在的目录
        directory = os.path.dirname(tool_path)
        # 构建命令，确保路径格式正确
        command = [os.path.join(env_dir, "python"), f'"{tool_path}"']
        self.run_in_new_terminal(directory, command)

    def run_java_tool(self, tool_path, env_dir):
        """运行JAR文件"""
        directory = os.path.dirname(tool_path)
        # 确保路径包含空格时使用双引号包裹
        command = [os.path.join(env_dir, "java"), "-jar", f'"{tool_path}"']
        self.run_in_new_terminal(directory, command)

    def run_exe_tool(self, tool_path, env_dir):
        """运行EXE文件"""
        directory = os.path.dirname(tool_path)
        command = [tool_path]  # EXE文件直接运行
        self.run_in_new_terminal(directory, command)

    def run_in_new_terminal(self, directory, command):
        """在新终端窗口中切换到工具目录并运行命令"""
        if sys.platform == "win32":
            try:
                # 处理路径中的斜杠和空格
                directory = directory.replace("/", "\\").rstrip("\\")
                directory = f'"{directory}"'

                # 处理命令参数（仅在需要时添加双引号）
                processed_command = []
                for arg in command:
                    arg = arg.replace("/", "\\")
                    processed_command.append(f'"{arg}"' if " " in arg else arg)

                for i in range(len(command)):
                # 如果路径包含 Program Files 或 jdk，确保路径加上双引号
                    if "Program Files" in command[i] or "jdk" in command[i]:
                        command[i] = f'"{command[i]}"'
                

                # 构建命令字符串（使用 start 创建新窗口）
                command_str = (
                    f'cd /d {directory} && '
                    f'{" ".join(processed_command)}'
                )
                print("Running command in new terminal:", command_str)  # 输出命令查看

                # 使用 start 命令启动新窗口（关键修复）
                subprocess.Popen(
                    f'start cmd /k "{command_str}"',
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

            except Exception as e:
                print(f"Error occurred: {e}")
        else:
            # Linux/MacOS 部分保持不变
            try:
                subprocess.run(
                    ["gnome-terminal", "--", "bash", "-c",
                     f"cd {directory} && {' '.join(command)}; exec bash"]
                )
            except Exception as e:
                print(f"Error occurred: {e}")






if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ToolManagerApp()
    window.show()
    sys.exit(app.exec_())

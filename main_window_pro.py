"""
主窗口界面模块 - 专业三段式布局
使用PySide6构建GUI
"""
import sys
import os
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox,
        QProgressBar, QFileDialog, QGroupBox, QMessageBox, QSplitter,
        QListWidget, QListWidgetItem, QCheckBox, QRadioButton, QButtonGroup,
        QScrollArea, QFrame, QSizePolicy, QDialog
    )
    from PySide6.QtCore import Qt, QThread, Signal, QUrl, QSize
    from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QDesktopServices, QFont, QColor
except ImportError:
    print("错误: PySide6 未安装")
    print("请运行: pip install PySide6")
    sys.exit(1)

from config import Config
from review_workflow import ReviewWorkflow

logger = logging.getLogger(__name__)


class ReviewWorker(QThread):
    """审查工作线程"""

    # 信号定义
    progress = Signal(str, int)  # (message, progress_percent)
    finished = Signal(dict)  # review_result
    error = Signal(str)  # error_message
    checklist_generated = Signal(dict)  # 审查清单生成

    def __init__(
        self,
        contract_file: str,
        client_role: str,
        contract_type: str,
        user_concerns: str,
        output_format: str = "word"
    ):
        super().__init__()
        self.contract_file = contract_file
        self.client_role = client_role
        self.contract_type = contract_type
        self.user_concerns = user_concerns
        self.output_format = output_format
        self.workflow = None

    def run(self):
        """运行审查流程"""
        try:
            # 创建工作流实例
            self.workflow = ReviewWorkflow(
                progress_callback=lambda msg, prog: self.progress.emit(msg, prog)
            )

            # 执行审查
            result = self.workflow.review_contract(
                contract_file=self.contract_file,
                client_role=self.client_role,
                contract_type=self.contract_type,
                user_concerns=self.user_concerns,
                output_format=self.output_format
            )

            if result["success"]:
                self.finished.emit(result)
            else:
                self.error.emit(result["message"])

        except Exception as e:
            logger.exception("审查工作线程异常")
            self.error.emit(f"审查失败: {str(e)}")


class FileListWidget(QListWidget):
    """文件列表组件"""

    fileSelected = Signal(str)  # file_path
    fileRemoved = Signal(str)   # file_path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.DropOnly)
        # 样式将在create_left_sidebar中设置

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for file_path in files:
            if file_path.endswith(('.docx', '.pdf', '.doc')):
                self.add_file(file_path)

    def add_file(self, file_path: str):
        """添加文件到列表"""
        file_name = Path(file_path).name
        item = QListWidgetItem(f"📄 {file_name}")
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        item.setData(Qt.ItemDataRole.UserRole + 1, "pending")  # status
        self.addItem(item)
        self.fileSelected.emit(file_path)

    def update_file_status(self, file_path: str, status: str):
        """更新文件状态"""
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == file_path:
                item.setData(Qt.ItemDataRole.UserRole + 1, status)
                # 更新图标
                icon_map = {
                    "pending": "⏳",
                    "processing": "🔄",
                    "completed": "✅",
                    "error": "❌"
                }
                text = item.text().split(" ", 1)[1] if " " in item.text() else item.text()
                item.setText(f"{icon_map.get(status, '📄')} {text}")
                break


class CheckPointWidget(QWidget):
    """审查要点勾选组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkpoints = {}
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title = QLabel("📋 审查要点清单")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333; background-color: white;")
        layout.addWidget(title)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 30px;
            }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background-color: white;")
        self.check_layout = QVBoxLayout(self.container)
        scroll.setWidget(self.container)

        layout.addWidget(scroll)

    def load_checkpoints(self, checklist: dict):
        """加载审查要点"""
        # 清空现有项
        while self.check_layout.count():
            child = self.check_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.checkpoints = {}

        # 添加审查点
        for check in checklist.get("specific_checks", []):
            checkbox = QCheckBox(check["point"])
            checkbox.setChecked(True)
            checkbox.setToolTip(check["logic"])
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #333;
                    background-color: white;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)
            self.check_layout.addWidget(checkbox)
            self.checkpoints[check["point"]] = checkbox

        self.check_layout.addStretch()

    def get_selected_checkpoints(self) -> List[str]:
        """获取选中的审查点"""
        return [
            point for point, checkbox in self.checkpoints.items()
            if checkbox.isChecked()
        ]


class SourceTextView(QTextEdit):
    """原文展示组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                padding: 15px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                line-height: 1.6;
                color: #333;
            }
        """)
        self.setPlaceholderText("合同原文将显示在这里...")

    def highlight_text(self, text: str, color: str = "#FFEB3B"):
        """高亮显示文本"""
        # 简化实现，可以使用更复杂的高亮逻辑
        cursor = self.textCursor()
        format = cursor.charFormat()
        format.setBackground(QColor(color))

        # 查找并高亮
        pos = self.find(text)
        while pos:
            cursor = self.textCursor()
            cursor.mergeCharFormat(format)
            pos = self.find(text)


class AIInsightView(QTextEdit):
    """AI审查意见展示组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

        # 设置滚动条策略
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                padding: 15px;
                font-size: 13px;
                line-height: 1.8;
                color: #333;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar:horizontal {
                border: none;
                background-color: #f0f0f0;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #c0c0c0;
                min-width: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #a0a0a0;
            }
        """)
        self.setPlaceholderText("AI律师审查意见将实时显示在这里...")
        # 设置最小高度，确保有足够空间显示
        self.setMinimumHeight(400)

    def append_markdown(self, text: str):
        """追加Markdown内容"""
        # 简化处理，实际可以使用更完善的Markdown渲染库
        self.append(text)


class ChatInputWidget(QWidget):
    """与AI对话输入组件"""

    messageSent = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.input = QLineEdit()
        self.input.setPlaceholderText("💬 与AI律师对话，如：请补充审查保密条款...")
        self.input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 13px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        self.input.returnPressed.connect(self.send_message)
        layout.addWidget(self.input)

        send_btn = QPushButton("发送")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        layout.addWidget(send_btn)

    def send_message(self):
        """发送消息"""
        text = self.input.text().strip()
        if text:
            self.messageSent.emit(text)
            self.input.clear()


class ChatWorker(QThread):
    """AI对话工作线程"""

    response = Signal(str)
    error = Signal(str)

    def __init__(self, message: str, contract_file: Optional[str]):
        super().__init__()
        self.message = message
        self.contract_file = contract_file
        self.ai_engine = None

    def run(self):
        """运行AI对话"""
        try:
            # 初始化AI引擎
            from ai_engine import LLMFactory
            self.ai_engine = LLMFactory.create_llm()

            # 构建对话上下文
            messages = [
                {"role": "system", "content": "你是一位专业的合同审查律师。请根据用户的提问提供专业、准确的法律建议。"}
            ]

            # 如果有合同文件，添加合同上下文
            if self.contract_file:
                messages.append({
                    "role": "system",
                    "content": f"当前正在审查合同文件: {self.contract_file}"
                })

            # 添加用户消息
            messages.append({"role": "user", "content": self.message})

            # 调用AI
            response = self.ai_engine.chat(messages)
            self.response.emit(response)

        except Exception as e:
            logger.error(f"AI对话失败: {e}")
            self.error.emit(f"AI律师暂时无法回复: {str(e)}")


class MainWindowPro(QMainWindow):
    """专业三段式主窗口"""

    def __init__(self):
        super().__init__()

        # 重新加载.env配置，确保使用最新配置
        from dotenv import load_dotenv
        load_dotenv()

        self.current_file = None
        self.contract_text = ""
        self.worker = None
        self.init_ui()
        logger.info(f"专业版主窗口初始化完成 - 当前模型: {Config.AI_MODEL_TYPE} ({Config.OLLAMA_MODEL if Config.AI_MODEL_TYPE == 'local' else 'DeepSeek'})")

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{Config.APP_NAME} - 专业版")
        self.setGeometry(50, 50, 1400, 900)

        # 设置应用图标
        icon_path = Config.BASE_DIR / "assets" / "app_icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            # 同时设置应用程序图标，用于对话框等
            QApplication.instance().setWindowIcon(QIcon(str(icon_path)))

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局 - 三段式布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ============ 左侧导航栏 ============
        left_sidebar = self.create_left_sidebar()
        main_layout.addWidget(left_sidebar, 1)

        # ============ 中间配置与原文区 ============
        center_area = self.create_center_area()
        main_layout.addWidget(center_area, 2)

        # ============ 右侧AI交互区 ============
        right_area = self.create_right_area()
        main_layout.addWidget(right_area, 2)

        # 状态栏
        self.statusBar().showMessage("就绪 - 请拖放合同文件到左侧列表")

    def create_left_sidebar(self) -> QFrame:
        """创建左侧导航栏"""
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-right: 1px solid #1a252f;
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
            QPushButton {
                color: white;
                background-color: #34495e;
                border: 1px solid #4a5f7a;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d566e;
            }
            QRadioButton {
                color: white;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 9px;
            }
        """)
        sidebar.setFixedWidth(280)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # 标题
        title = QLabel("📂 文件管理")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        layout.addWidget(title)

        # 批量上传按钮
        upload_btn = QPushButton("+ 合同上传")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        upload_btn.clicked.connect(self.batch_upload)
        layout.addWidget(upload_btn)

        # 文件列表
        self.file_list = FileListWidget()
        # 修改为白色背景+灰色文字
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                padding: 5px;
                color: #333;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 3px;
                color: #333;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
                color: #333;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
        self.file_list.fileSelected.connect(self.on_file_selected)
        layout.addWidget(self.file_list)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #ddd;")
        layout.addWidget(line)

        # 模型配置 - 配置入口
        model_title = QLabel("⚙️ 模型配置")
        model_title.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        layout.addWidget(model_title)

        # 本地模型配置按钮
        ollama_config_btn = QPushButton("🏠 配置本地模型")
        ollama_config_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: 1px solid #4a5f7a;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d566e;
            }
        """)
        ollama_config_btn.clicked.connect(self.open_ollama_config)
        layout.addWidget(ollama_config_btn)

        # DeepSeek API配置按钮
        deepseek_config_btn = QPushButton("☁️ 配置DeepSeek API")
        deepseek_config_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: 1px solid #F57C00;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        deepseek_config_btn.clicked.connect(self.open_deepseek_config)
        layout.addWidget(deepseek_config_btn)

        # 模型切换按钮
        switch_model_btn = QPushButton("🔄 切换模型")
        switch_model_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: 1px solid #7B1FA2;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        switch_model_btn.clicked.connect(self.switch_model)
        layout.addWidget(switch_model_btn)

        # 当前模型显示 - 动态读取配置
        from dotenv import load_dotenv
        load_dotenv()
        current_type = os.getenv("AI_MODEL_TYPE", "local")
        model_name = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")
        self.current_model_label = QLabel(f"当前: {'本地(Ollama)' if current_type == 'local' else '云端(DepthSeek)'} - {model_name if current_type == 'local' else 'deepseek-chat'}")
        self.current_model_label.setStyleSheet("color: #bbb; font-size: 11px; background-color: transparent; padding: 5px;")
        self.current_model_label.setWordWrap(True)
        layout.addWidget(self.current_model_label)

        layout.addStretch()

        # 历史记录按钮
        history_btn = QPushButton("📜 历史记录")
        history_btn.setStyleSheet("""
            QPushButton {
                color: #333;
                background-color: white;
                border: 1px solid #ddd;
                padding: 8px;
                border-radius: 5px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border-color: #2196F3;
            }
        """)
        history_btn.clicked.connect(self.show_history)
        layout.addWidget(history_btn)

        # 帮助按钮
        help_btn = QPushButton("❓ 使用帮助")
        help_btn.setStyleSheet("""
            QPushButton {
                color: #333;
                background-color: white;
                border: 1px solid #ddd;
                padding: 8px;
                border-radius: 5px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border-color: #4CAF50;
            }
        """)
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)

        return sidebar

    def create_center_area(self) -> QFrame:
        """创建中间配置与原文区"""
        area = QFrame()
        area.setFrameShape(QFrame.Shape.StyledPanel)
        area.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
            }
        """)

        layout = QVBoxLayout(area)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # ============ 审查配置区域 ============
        config_group = QGroupBox("🎯 审查配置")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: white;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #333;
            }
        """)
        config_layout = QVBoxLayout(config_group)

        # 身份选择
        role_layout = QHBoxLayout()
        role_label = QLabel("👤 我方身份:")
        role_label.setStyleSheet("color: #333; background-color: white;")
        role_layout.addWidget(role_label)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["甲方", "乙方"])
        self.role_combo.setCurrentIndex(1)
        self.role_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
                color: #333;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
            QComboBox::drop-down {
                border: 1px solid #ddd;
            }
        """)
        role_layout.addWidget(self.role_combo)
        role_layout.addStretch()
        config_layout.addLayout(role_layout)

        # 合同类型
        type_layout = QHBoxLayout()
        type_label = QLabel("📋 合同类型:")
        type_label.setStyleSheet("color: #333; background-color: white;")
        type_layout.addWidget(type_label)
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("例如: 软件开发合同、采购合同...")
        self.type_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        type_layout.addWidget(self.type_input)
        config_layout.addLayout(type_layout)

        # 核心关注点
        concern_layout = QHBoxLayout()
        concern_label = QLabel("💡 核心关注:")
        concern_label.setStyleSheet("color: #333; background-color: white;")
        concern_layout.addWidget(concern_label)
        self.concern_input = QLineEdit()
        self.concern_input.setPlaceholderText("例如: 回款周期、交付标准、违约责任...")
        self.concern_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        concern_layout.addWidget(self.concern_input)
        config_layout.addLayout(concern_layout)

        layout.addWidget(config_group)

        # ============ 审查要点清单 ============
        self.checkpoint_widget = CheckPointWidget()
        # 设置白色背景
        self.checkpoint_widget.setStyleSheet("""
            CheckPointWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel {
                color: #333;
                background-color: white;
            }
            QCheckBox {
                color: #333;
                background-color: white;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        layout.addWidget(self.checkpoint_widget)

        # 开始审查按钮
        self.start_btn = QPushButton("🚀 开始审查")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.start_btn.clicked.connect(self.start_review)
        layout.addWidget(self.start_btn)

        # ============ 原文视图 ============
        source_group = QGroupBox("📄 合同原文")
        source_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: white;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #333;
            }
        """)
        source_layout = QVBoxLayout(source_group)

        self.source_text = SourceTextView()
        source_layout.addWidget(self.source_text)

        layout.addWidget(source_group)

        return area

    def create_right_area(self) -> QFrame:
        """创建右侧AI交互区"""
        area = QFrame()
        area.setFrameShape(QFrame.Shape.StyledPanel)
        area.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
            }
        """)

        layout = QVBoxLayout(area)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # 标题和导出按钮
        header_layout = QHBoxLayout()
        title = QLabel("🤖 AI律师审查意见")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: #333; background-color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        export_btn = QPushButton("📥 导出报告")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        export_btn.clicked.connect(self.export_report)
        header_layout.addWidget(export_btn)

        layout.addLayout(header_layout)

        # AI审查意见展示
        self.ai_insight = AIInsightView()
        layout.addWidget(self.ai_insight)

        # 与AI对话
        chat_group = QGroupBox("🗨️ 与AI律师对话")
        chat_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: white;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #333;
            }
        """)
        chat_layout = QVBoxLayout(chat_group)

        self.chat_input = ChatInputWidget()
        self.chat_input.messageSent.connect(self.send_chat_message)
        chat_layout.addWidget(self.chat_input)

        layout.addWidget(chat_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                text-align: center;
                font-weight: bold;
                font-size: 13px;
                color: #333;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50,
                    stop:0.5 #66BB6A,
                    stop:1 #4CAF50);
                border-radius: 10px;
                margin: 1px;
            }
        """)
        layout.addWidget(self.progress_bar)

        return area

    def batch_upload(self):
        """批量上传文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择合同文件",
            "",
            "支持的格式 (*.docx *.pdf *.doc);;Word文档 (*.docx *.doc);;PDF文档 (*.pdf)"
        )
        for file_path in files:
            self.file_list.add_file(file_path)

    def on_file_selected(self, file_path: str):
        """文件选择处理"""
        self.current_file = file_path
        self.statusBar().showMessage(f"已加载: {Path(file_path).name}")

        # 自动解析并显示原文
        try:
            from document_parser import DocumentParserFactory
            result = DocumentParserFactory.parse_document(file_path)
            self.contract_text = result["text"]
            self.source_text.setText(self.contract_text[:3000] + "...\n\n[文件较长，仅显示部分内容]")
        except Exception as e:
            logger.error(f"解析文件失败: {e}")
            self.source_text.setText(f"❌ 文件解析失败: {str(e)}")

    def start_review(self):
        """开始审查"""
        if not self.current_file:
            QMessageBox.warning(self, "提示", "请先从左侧文件列表选择一个合同")
            return

        contract_type = self.type_input.text().strip()
        if not contract_type:
            QMessageBox.warning(self, "提示", "请输入合同类型")
            return

        user_concerns = self.concern_input.text().strip()
        if not user_concerns:
            QMessageBox.warning(self, "提示", "请输入核心关注点")
            return

        # 更新文件状态
        self.file_list.update_file_status(self.current_file, "processing")

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.ai_insight.clear()

        # 禁用输入
        self.type_input.setEnabled(False)
        self.concern_input.setEnabled(False)

        # 启动工作线程
        self.worker = ReviewWorker(
            contract_file=self.current_file,
            client_role=self.role_combo.currentText(),
            contract_type=contract_type,
            user_concerns=user_concerns,
            output_format="word"
        )

        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)

        self.worker.start()
        self.statusBar().showMessage("🔄 AI正在深度审查中...")

    def on_progress(self, message: str, progress: int):
        """进度更新"""
        self.progress_bar.setValue(progress)
        self.ai_insight.append(f"**[{progress}%]** {message}")
        logger.info(f"进度: {progress}% - {message}")

    def on_finished(self, result: dict):
        """审查完成"""
        self.progress_bar.setVisible(False)
        self.type_input.setEnabled(True)
        self.concern_input.setEnabled(True)

        # 更新文件状态
        self.file_list.update_file_status(self.current_file, "completed")

        # 显示审查报告
        report = result["data"]["review_report"]
        self.ai_insight.clear()

        # 使用setText而不是setMarkdown，确保完整显示
        # 如果是Markdown格式，保留格式但作为普通文本显示
        self.ai_insight.setPlainText(report)

        # 滚动到顶部
        cursor = self.ai_insight.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self.ai_insight.setTextCursor(cursor)

        # 加载审查要点
        checklist = result["data"]["metadata"]["checklist"]
        self.checkpoint_widget.load_checkpoints(checklist)

        # 保存报告路径
        self.current_report_path = result["data"]["report_path"]

        # 保存历史记录
        try:
            from history_manager import get_history_manager
            history_mgr = get_history_manager()

            # 获取审查报告的前200字作为摘要
            report_summary = report[:200] + "..." if len(report) > 200 else report

            # 确定模型名称
            model_type = Config.AI_MODEL_TYPE
            if model_type == "local":
                model_name = Config.OLLAMA_MODEL
            else:
                model_name = Config.OPENAI_MODEL

            history_mgr.add_record(
                file_name=Path(self.current_file).name,
                file_path=self.current_file,
                client_role=self.role_combo.currentText(),
                contract_type=self.type_input.text(),
                user_concerns=self.concern_input.text(),
                model_type=model_type,
                model_name=model_name,
                status="success",
                report_path=self.current_report_path,
                review_summary=report_summary
            )
            logger.info("历史记录已保存")
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")

        self.statusBar().showMessage("✅ 审查完成 - 报告已完整显示，可导出Word文档查看格式化版本")

    def on_error(self, error_message: str):
        """审查错误"""
        self.progress_bar.setVisible(False)
        self.type_input.setEnabled(True)
        self.concern_input.setEnabled(True)

        # 更新文件状态
        self.file_list.update_file_status(self.current_file, "error")

        self.ai_insight.append(f"\n❌ **错误**: {error_message}")
        QMessageBox.critical(self, "错误", error_message)
        self.statusBar().showMessage("❌ 审查失败")

        # 保存失败的历史记录
        try:
            from history_manager import get_history_manager
            history_mgr = get_history_manager()

            # 确定模型名称
            model_type = Config.AI_MODEL_TYPE
            if model_type == "local":
                model_name = Config.OLLAMA_MODEL
            else:
                model_name = Config.OPENAI_MODEL

            history_mgr.add_record(
                file_name=Path(self.current_file).name if self.current_file else "未知文件",
                file_path=self.current_file if self.current_file else "",
                client_role=self.role_combo.currentText(),
                contract_type=self.type_input.text(),
                user_concerns=self.concern_input.text(),
                model_type=model_type,
                model_name=model_name,
                status="error",
                error_message=error_message
            )
            logger.info("错误历史记录已保存")
        except Exception as e:
            logger.error(f"保存错误历史记录失败: {e}")

    def send_chat_message(self, message: str):
        """发送聊天消息"""
        self.ai_insight.append(f"\n**👤 您**: {message}")

        # 创建AI对话线程并保存为实例变量，防止被过早销毁
        self.chat_worker = ChatWorker(message, self.current_file if hasattr(self, 'current_file') else None)
        self.chat_worker.response.connect(self.on_ai_response)
        self.chat_worker.error.connect(self.on_chat_error)
        self.chat_worker.start()

    def on_ai_response(self, response: str):
        """AI响应回调"""
        self.ai_insight.append(f"\n**🤖 AI律师**: {response}")
        # 自动滚动到底部
        scrollbar = self.ai_insight.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_chat_error(self, error_message: str):
        """对话错误回调"""
        self.ai_insight.append(f"\n❌ **错误**: {error_message}")

    def export_report(self):
        """导出报告"""
        if hasattr(self, 'current_report_path') and self.current_report_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.current_report_path))
        else:
            QMessageBox.information(self, "提示", "请先完成审查后再导出报告")

    def show_help(self):
        """显示帮助"""
        help_text = """
        <h3>📄 合同审查小助手 - 使用指南</h3>

        <h4>快速开始：</h4>
        <ol>
            <li><b>上传文件</b>：点击"合同上传"或拖放文件到左侧列表</li>
            <li><b>选择文件</b>：在左侧列表点击要审查的合同</li>
            <li><b>配置参数</b>：在中间区域设置身份、类型、关注点</li>
            <li><b>开始审查</b>：点击"开始审查"按钮</li>
            <li><b>查看结果</b>：右侧实时显示AI审查意见</li>
            <li><b>导出报告</b>：点击"导出报告"保存完整报告</li>
        </ol>

        <h4>功能特点：</h4>
        <ul>
            <li>✅ 支持批量上传多个合同</li>
            <li>✅ 本地模型保护隐私</li>
            <li>✅ 实时显示审查进度</li>
            <li>✅ 可与AI律师对话交互</li>
            <li>✅ 导出专业Word报告</li>
        </ul>

        <h4>提示：</h4>
        <ul>
            <li>关注点越具体，审查越精准</li>
            <li>可以在审查后补充问题与AI对话</li>
            <li>支持.docx和.pdf格式</li>
        </ul>
        """

        QMessageBox.information(self, "使用帮助", help_text)

    def show_history(self):
        """显示历史记录对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("📜 审查历史记录")
        dialog.setModal(True)
        dialog.setMinimumSize(900, 600)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题和工具栏
        header_layout = QHBoxLayout()

        title = QLabel("📜 审查历史记录")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        refresh_btn.clicked.connect(lambda: self.refresh_history(dialog))
        header_layout.addWidget(refresh_btn)

        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        clear_btn.clicked.connect(lambda: self.clear_history(dialog))
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # 统计信息
        stats_label = QLabel()
        stats_label.setStyleSheet("color: #666; font-size: 13px; padding: 10px; background-color: #f5f5f5; border-radius: 5px;")
        layout.addWidget(stats_label)

        # 搜索框
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 搜索历史记录（文件名、合同类型、关注点）...")
        search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 13px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        search_layout.addWidget(search_input)

        search_btn = QPushButton("搜索")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        search_layout.addWidget(search_btn)

        layout.addLayout(search_layout)

        # 历史记录列表
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

        history_table = QTableWidget()
        history_table.setColumnCount(7)
        history_table.setHorizontalHeaderLabels([
            "时间", "文件名", "合同类型", "身份", "模型", "状态", "操作"
        ])

        # 设置列宽
        header = history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        history_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                gridline-color: #f0f0f0;
                font-size: 12px;
                color: #333;
            }
            QTableWidget::item {
                padding: 8px;
                background-color: white;
                color: #333;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #ddd;
                color: #333;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #333;
            }
        """)
        history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        history_table.verticalHeader().setVisible(False)

        layout.addWidget(history_table)

        # 加载历史记录
        def load_records():
            from history_manager import get_history_manager
            history_mgr = get_history_manager()
            records = history_mgr.get_records()

            # 更新统计信息
            stats = history_mgr.get_statistics()
            stats_text = f"总计: {stats['total']}条 | 成功: {stats['success']}条 | 失败: {stats['error']}条"
            stats_label.setText(stats_text)

            # 填充表格
            history_table.setRowCount(len(records))

            for row, record in enumerate(records):
                # 时间
                history_table.setItem(row, 0, QTableWidgetItem(record.timestamp))

                # 文件名
                history_table.setItem(row, 1, QTableWidgetItem(record.file_name))

                # 合同类型
                history_table.setItem(row, 2, QTableWidgetItem(record.contract_type))

                # 身份
                history_table.setItem(row, 3, QTableWidgetItem(record.client_role))

                # 模型
                model_text = f"{record.model_name}"
                history_table.setItem(row, 4, QTableWidgetItem(model_text))

                # 状态
                status_item = QTableWidgetItem("✅ 成功" if record.status == "success" else "❌ 失败")
                if record.status == "success":
                    status_item.setForeground(QColor("#4CAF50"))
                else:
                    status_item.setForeground(QColor("#f44336"))
                history_table.setItem(row, 5, status_item)

                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(5, 2, 5, 2)

                # 查看详情按钮
                detail_btn = QPushButton("详情")
                detail_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                detail_btn.clicked.connect(lambda checked, r=record: self.show_record_detail(r))
                btn_layout.addWidget(detail_btn)

                # 打开报告按钮
                if record.status == "success" and record.report_path:
                    report_btn = QPushButton("报告")
                    report_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            padding: 5px 10px;
                            border-radius: 3px;
                            font-size: 11px;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                    """)
                    report_btn.clicked.connect(lambda checked, path=record.report_path: self.open_report(path))
                    btn_layout.addWidget(report_btn)

                history_table.setCellWidget(row, 6, btn_widget)

        # 搜索功能
        def search_records():
            keyword = search_input.text().strip()
            from history_manager import get_history_manager
            history_mgr = get_history_manager()

            if keyword:
                records = history_mgr.search_records(keyword)
            else:
                records = history_mgr.get_records()

            # 更新统计
            stats = history_mgr.get_statistics()
            stats_text = f"总计: {stats['total']}条 | 成功: {stats['success']}条 | 失败: {stats['error']}条"
            if keyword:
                stats_text += f" | 搜索结果: {len(records)}条"
            stats_label.setText(stats_text)

            # 填充表格（复用上面的逻辑）
            history_table.setRowCount(len(records))
            for row, record in enumerate(records):
                history_table.setItem(row, 0, QTableWidgetItem(record.timestamp))
                history_table.setItem(row, 1, QTableWidgetItem(record.file_name))
                history_table.setItem(row, 2, QTableWidgetItem(record.contract_type))
                history_table.setItem(row, 3, QTableWidgetItem(record.client_role))
                history_table.setItem(row, 4, QTableWidgetItem(record.model_name))

                status_item = QTableWidgetItem("✅ 成功" if record.status == "success" else "❌ 失败")
                if record.status == "success":
                    status_item.setForeground(QColor("#4CAF50"))
                else:
                    status_item.setForeground(QColor("#f44336"))
                history_table.setItem(row, 5, status_item)

                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(5, 2, 5, 2)

                detail_btn = QPushButton("详情")
                detail_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                detail_btn.clicked.connect(lambda checked, r=record: self.show_record_detail(r))
                btn_layout.addWidget(detail_btn)

                if record.status == "success" and record.report_path:
                    report_btn = QPushButton("报告")
                    report_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            padding: 5px 10px;
                            border-radius: 3px;
                            font-size: 11px;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                    """)
                    report_btn.clicked.connect(lambda checked, path=record.report_path: self.open_report(path))
                    btn_layout.addWidget(report_btn)

                history_table.setCellWidget(row, 6, btn_widget)

        search_btn.clicked.connect(search_records)
        search_input.returnPressed.connect(search_records)

        # 初始加载
        load_records()

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    def refresh_history(self, dialog: QDialog):
        """刷新历史记录"""
        dialog.close()
        self.show_history()

    def clear_history(self, dialog: QDialog):
        """清空历史记录"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有历史记录吗？\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            from history_manager import get_history_manager
            history_mgr = get_history_manager()
            if history_mgr.clear_all():
                QMessageBox.information(self, "✅ 成功", "历史记录已清空")
                dialog.close()
            else:
                QMessageBox.critical(self, "❌ 错误", "清空失败")

    def show_record_detail(self, record):
        """显示记录详情"""
        detail_dialog = QDialog(self)
        detail_dialog.setWindowTitle(f"📋 审查详情 - {record.file_name}")
        detail_dialog.setModal(True)
        detail_dialog.setMinimumWidth(600)

        layout = QVBoxLayout(detail_dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title = QLabel(f"📋 {record.file_name}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # 信息列表
        info_text = f"""
        <table style="border-collapse: collapse; width: 100%;">
            <tr><td style="padding: 8px; font-weight: bold; color: #666;">审查时间：</td><td style="padding: 8px;">{record.timestamp}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #666;">文件路径：</td><td style="padding: 8px;">{record.file_path}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #666;">合同类型：</td><td style="padding: 8px;">{record.contract_type}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #666;">客户身份：</td><td style="padding: 8px;">{record.client_role}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #666;">核心关注：</td><td style="padding: 8px;">{record.user_concerns}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #666;">使用模型：</td><td style="padding: 8px;">{record.model_name} ({record.model_type})</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #666;">审查状态：</td><td style="padding: 8px;">{'✅ 成功' if record.status == 'success' else '❌ 失败'}</td></tr>
        </table>
        """

        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setStyleSheet("font-size: 13px; color: #333; background-color: white;")
        layout.addWidget(info_label)

        # 错误信息
        if record.error_message:
            error_group = QGroupBox("❌ 错误信息")
            error_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #f44336;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding: 10px;
                    color: #f44336;
                }
            """)
            error_layout = QVBoxLayout(error_group)
            error_label = QLabel(record.error_message)
            error_label.setWordWrap(True)
            error_label.setStyleSheet("color: #333; background-color: white;")
            error_layout.addWidget(error_label)
            layout.addWidget(error_group)

        # 审查摘要
        if record.review_summary:
            summary_group = QGroupBox("📝 审查摘要")
            summary_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding: 10px;
                    color: #333;
                }
            """)
            summary_layout = QVBoxLayout(summary_group)
            summary_text = QTextEdit()
            summary_text.setPlainText(record.review_summary)
            summary_text.setReadOnly(True)
            summary_text.setMaximumHeight(200)
            summary_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    padding: 10px;
                    background-color: white;
                    font-size: 12px;
                }
            """)
            summary_layout.addWidget(summary_text)
            layout.addWidget(summary_group)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        close_btn.clicked.connect(detail_dialog.close)
        layout.addWidget(close_btn)

        detail_dialog.exec()

    def open_report(self, report_path: str):
        """打开报告文件"""
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(report_path))
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"无法打开报告:\n{str(e)}")

    def open_ollama_config(self):
        """打开Ollama本地模型配置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🏠 配置本地Ollama模型")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title = QLabel("🏠 本地Ollama模型配置")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E7D32;")
        layout.addWidget(title)

        # Ollama服务地址
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("服务地址:"))
        ollama_url_input = QLineEdit()
        ollama_url_input.setText(Config.OLLAMA_BASE_URL)
        ollama_url_input.setPlaceholderText("例如: http://localhost:11434")
        ollama_url_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #333;
            }
        """)
        url_layout.addWidget(ollama_url_input)
        layout.addLayout(url_layout)

        # 模型名称
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型名称:"))
        ollama_model_input = QLineEdit()
        ollama_model_input.setText(Config.OLLAMA_MODEL)
        ollama_model_input.setPlaceholderText("例如: qwen2.5:7b")
        ollama_model_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #333;
            }
        """)
        model_layout.addWidget(ollama_model_input)
        layout.addLayout(model_layout)

        # 测试连接按钮
        test_btn = QPushButton("🧪 测试连接")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        test_btn.clicked.connect(lambda: self.test_ollama_connection(ollama_url_input.text(), ollama_model_input.text()))
        layout.addWidget(test_btn)

        # 说明文本
        info_text = QLabel("💡 提示：请确保Ollama服务已启动。如果未安装Ollama，请访问 ollama.ai 下载安装。")
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #666; font-size: 12px; background-color: white;")
        layout.addWidget(info_text)

        # 按钮
        buttons = QHBoxLayout()
        save_btn = QPushButton("💾 保存配置")
        cancel_btn = QPushButton("取消")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        # 连接按钮
        save_btn.clicked.connect(lambda: self.save_ollama_config(ollama_url_input.text(), ollama_model_input.text(), dialog))
        cancel_btn.clicked.connect(dialog.close)

        dialog.exec()

    def test_ollama_connection(self, url: str, model: str):
        """测试Ollama连接"""
        try:
            import requests
            response = requests.get(f"{url}/api/tags", timeout=5)
            if response.status_code == 200:
                QMessageBox.information(self, "✅ 成功", f"Ollama服务连接成功！\n\n当前服务地址: {url}")
            else:
                QMessageBox.warning(self, "⚠️ 警告", f"Ollama服务响应异常:\n状态码: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"无法连接到Ollama服务:\n{str(e)}\n\n请检查:\n1. Ollama是否已启动\n2. 服务地址是否正确")

    def save_ollama_config(self, url: str, model: str, dialog: QDialog):
        """保存Ollama配置"""
        try:
            # 更新.env文件
            env_file = Config.BASE_DIR / ".env"
            env_content = env_file.read_text(encoding='utf-8')

            # 更新或添加配置
            lines = env_content.split('\n')
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('OLLAMA_BASE_URL='):
                    lines[i] = f'OLLAMA_BASE_URL={url}'
                    updated = True
                elif line.startswith('OLLAMA_MODEL='):
                    lines[i] = f'OLLAMA_MODEL={model}'
                    updated = True

            if not updated:
                lines.append(f'OLLAMA_BASE_URL={url}')
                lines.append(f'OLLAMA_MODEL={model}')

            # 写回文件
            env_file.write_text('\n'.join(lines), encoding='utf-8')

            # 更新Config
            Config.OLLAMA_BASE_URL = url
            Config.OLLAMA_MODEL = model

            QMessageBox.information(self, "✅ 成功", "Ollama配置已保存！")
            dialog.close()

        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"保存配置失败:\n{str(e)}")

    def open_deepseek_config(self):
        """打开DeepSeek API配置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("☁️ 配置DeepSeek API")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title = QLabel("☁️ DeepSeek API 配置")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF9800;")
        layout.addWidget(title)

        # API地址
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API地址:"))
        deepseek_api_input = QLineEdit()
        deepseek_api_input.setText(Config.DEEPSEEK_API_BASE)
        deepseek_api_input.setPlaceholderText("例如: https://api.deepseek.com/v1")
        deepseek_api_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #333;
            }
        """)
        api_layout.addWidget(deepseek_api_input)
        layout.addLayout(api_layout)

        # API密钥
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API密钥:"))
        deepseek_key_input = QLineEdit()
        deepseek_key_input.setText(Config.DEEPSEEK_API_KEY)
        deepseek_key_input.setEchoMode(QLineEdit.Password)
        deepseek_key_input.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        deepseek_key_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #333;
            }
        """)
        key_layout.addWidget(deepseek_key_input)
        layout.addLayout(key_layout)

        # 测试连接按钮
        test_btn = QPushButton("🧪 测试连接")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        test_btn.clicked.connect(lambda: self.test_deepseek_connection(deepseek_api_input.text(), deepseek_key_input.text()))
        layout.addWidget(test_btn)

        # 说明文本
        info_text = QLabel("💡 提示：请访问 <a href='https://platform.deepseek.com/'>https://platform.deepseek.com/</a> 获取API密钥")
        info_text.setWordWrap(True)
        info_text.setOpenExternalLinks(True)
        info_text.setStyleSheet("color: #666; font-size: 12px; background-color: white;")
        layout.addWidget(info_text)

        # 按钮
        buttons = QHBoxLayout()
        save_btn = QPushButton("💾 保存配置")
        cancel_btn = QPushButton("取消")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        # 连接按钮
        save_btn.clicked.connect(lambda: self.save_deepseek_config(deepseek_api_input.text(), deepseek_key_input.text(), dialog))
        cancel_btn.clicked.connect(dialog.close)

        dialog.exec()

    def test_deepseek_connection(self, api_base: str, api_key: str):
        """测试DeepSeek API连接"""
        try:
            import requests
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(f"{api_base}/models", headers=headers, timeout=10)

            if response.status_code == 200:
                QMessageBox.information(self, "✅ 成功", "DeepSeek API连接成功！")
            elif response.status_code == 401:
                QMessageBox.warning(self, "⚠️ 警告", "API密钥无效，请检查配置")
            else:
                QMessageBox.warning(self, "⚠️ 警告", f"API响应异常:\n状态码: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"无法连接到DeepSeek API:\n{str(e)}\n\n请检查:\n1. API地址是否正确\n2. API密钥是否有效\n3. 网络连接是否正常")

    def save_deepseek_config(self, api_base: str, api_key: str, dialog: QDialog):
        """保存DeepSeek配置"""
        try:
            # 更新.env文件
            env_file = Config.BASE_DIR / ".env"
            env_content = env_file.read_text(encoding='utf-8')

            # 更新或添加配置
            lines = env_content.split('\n')
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('DEEPSEEK_API_BASE='):
                    lines[i] = f'DEEPSEEK_API_BASE={api_base}'
                    updated = True
                elif line.startswith('DEEPSEEK_API_KEY='):
                    lines[i] = f'DEEPSEEK_API_KEY={api_key}'
                    updated = True

            if not updated:
                lines.append(f'DEEPSEEK_API_BASE={api_base}')
                lines.append(f'DEEPSEEK_API_KEY={api_key}')

            # 写回文件
            env_file.write_text('\n'.join(lines), encoding='utf-8')

            # 更新Config
            Config.DEEPSEEK_API_BASE = api_base
            Config.DEEPSEEK_API_KEY = api_key

            QMessageBox.information(self, "✅ 成功", "DeepSeek配置已保存！")
            dialog.close()

        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"保存配置失败:\n{str(e)}")

    def switch_model(self):
        """切换AI模型"""
        current_model = Config.AI_MODEL_TYPE

        # 创建切换对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("🔄 切换AI模型")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title = QLabel("选择AI模型")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # 说明
        info = QLabel("当前使用: " + ("云端(DepthSeek API)" if current_model == "cloud" else "本地(Ollama)"))
        info.setStyleSheet("color: #666; font-size: 13px; background-color: white; padding: 10px;")
        layout.addWidget(info)

        # 选项按钮组
        btn_group = QButtonGroup()

        # 云端模型选项
        cloud_radio = QRadioButton("☁️ 云端模型 (DeepSeek API)")
        cloud_radio.setStyleSheet("""
            QRadioButton {
                color: #333;
                background-color: white;
                padding: 10px;
                font-size: 14px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 9px;
            }
        """)
        if current_model == "cloud":
            cloud_radio.setChecked(True)
        btn_group.addButton(cloud_radio, 1)
        layout.addWidget(cloud_radio)

        cloud_desc = QLabel("    速度快，稳定可靠，需要网络连接")
        cloud_desc.setStyleSheet("color: #999; font-size: 12px; background-color: white; padding-left: 28px;")
        layout.addWidget(cloud_desc)

        # 本地模型选项
        local_radio = QRadioButton("🏠 本地模型 (Ollama)")
        local_radio.setStyleSheet("""
            QRadioButton {
                color: #333;
                background-color: white;
                padding: 10px;
                font-size: 14px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 9px;
            }
        """)
        if current_model == "local":
            local_radio.setChecked(True)
        btn_group.addButton(local_radio, 2)
        layout.addWidget(local_radio)

        local_desc = QLabel(f"    隐私保护，无网络限制，模型: {Config.OLLAMA_MODEL}")
        local_desc.setStyleSheet("color: #999; font-size: 12px; background-color: white; padding-left: 28px;")
        layout.addWidget(local_desc)

        layout.addStretch()

        # 按钮
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("取消")
        switch_btn = QPushButton("切换")

        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

        switch_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)

        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(switch_btn)
        layout.addLayout(buttons)

        # 连接按钮
        cancel_btn.clicked.connect(dialog.close)
        switch_btn.clicked.connect(lambda: self.do_switch_model(cloud_radio.isChecked(), dialog))

        dialog.exec()

    def do_switch_model(self, use_cloud: bool, dialog: QDialog):
        """执行模型切换"""
        try:
            new_model_type = "cloud" if use_cloud else "local"

            # 更新.env文件
            env_file = Config.BASE_DIR / ".env"
            env_content = env_file.read_text(encoding='utf-8')

            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('AI_MODEL_TYPE='):
                    lines[i] = f'AI_MODEL_TYPE={new_model_type}'
                    break

            # 写回文件
            env_file.write_text('\n'.join(lines), encoding='utf-8')

            # 更新Config
            Config.AI_MODEL_TYPE = new_model_type

            # 更新显示
            self.current_model_label.setText(
                f"当前: {'云端(DepthSeek)' if new_model_type == 'cloud' else f'本地(Ollama)'}"
            )

            model_name = "DeepSeek API" if use_cloud else f"Ollama ({Config.OLLAMA_MODEL})"
            QMessageBox.information(
                self,
                "✅ 切换成功",
                f"已切换到 {model_name}\n\n下次审查时将使用新模型。"
            )

            dialog.close()

        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"切换模型失败:\n{str(e)}")


def main():
    """主函数"""
    # 初始化日志
    logging.basicConfig(
        level=Config.LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.CACHE_DIR / "app.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # 检查是否已存在 QApplication 实例
    app = QApplication.instance()
    if app is None:
        # 不存在则创建新实例
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        should_exec = True
    else:
        # 已存在则复用，不重复执行 exec()
        should_exec = False

    # 创建主窗口
    window = MainWindowPro()
    window.show()

    # 只有在新创建 QApplication 时才执行事件循环
    if should_exec:
        sys.exit(app.exec())


if __name__ == "__main__":
    main()

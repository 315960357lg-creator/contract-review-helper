"""
主窗口界面模块
使用PySide6构建GUI
"""
import sys
import logging
from pathlib import Path
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox,
        QProgressBar, QFileDialog, QGroupBox, QMessageBox, QSplitter
    )
    from PySide6.QtCore import Qt, QThread, Signal, QUrl
    from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QDesktopServices
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


class DropZoneWidget(QLabel):
    """文件拖放区域"""

    fileDropped = Signal(str)  # file_path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("拖放合同文件到此处\n支持 .docx 和 .pdf 格式")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f5f5f5;
                padding: 40px;
                font-size: 14px;
                color: #666;
            }
            QLabel:hover {
                border-color: #4CAF50;
                background-color: #e8f5e9;
            }
        """)
        self.setMinimumHeight(150)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #4CAF50;
                    border-radius: 10px;
                    background-color: #e8f5e9;
                    padding: 40px;
                    font-size: 14px;
                    color: #333;
                }
            """)

    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f5f5f5;
                padding: 40px;
                font-size: 14px;
                color: #666;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            file_path = files[0]
            if file_path.endswith(('.docx', '.pdf')):
                self.fileDropped.emit(file_path)
                self.setText(f"已选择文件:\n{Path(file_path).name}")
            else:
                QMessageBox.warning(self, "格式错误", "仅支持 .docx 和 .pdf 格式的文件")


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.contract_file = None
        self.worker = None
        self.init_ui()
        logger.info("主窗口初始化完成")

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(Config.APP_NAME)
        self.setGeometry(100, 100, 1000, 700)

        # 设置应用图标
        icon_path = Config.BASE_DIR / "assets" / "app_icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            # 同时设置应用程序图标，用于对话框等
            QApplication.instance().setWindowIcon(QIcon(str(icon_path)))

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title = QLabel("📄 合同审查小助手")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E7D32;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # 1. 文件选择区域
        file_group = QGroupBox("1. 选择合同文件")
        file_layout = QVBoxLayout()

        self.drop_zone = DropZoneWidget()
        self.drop_zone.fileDropped.connect(self.on_file_dropped)
        file_layout.addWidget(self.drop_zone)

        # 浏览按钮
        browse_layout = QHBoxLayout()
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("color: #666;")
        browse_layout.addWidget(self.file_label)

        browse_btn = QPushButton("浏览文件")
        browse_btn.clicked.connect(self.browse_file)
        browse_btn.setStyleSheet("padding: 8px 16px;")
        browse_layout.addWidget(browse_btn)

        file_layout.addLayout(browse_layout)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # 2. 审查参数设置
        params_group = QGroupBox("2. 设置审查参数")
        params_layout = QVBoxLayout()

        # 客户身份
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("客户身份:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["甲方", "乙方"])
        self.role_combo.setCurrentIndex(1)  # 默认乙方
        role_layout.addWidget(self.role_combo)
        role_layout.addStretch()
        params_layout.addLayout(role_layout)

        # 合同类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("合同类型:"))
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("例如: 软件开发合同、劳动合同...")
        type_layout.addWidget(self.type_input)
        params_layout.addLayout(type_layout)

        # 关注点
        concern_layout = QHBoxLayout()
        concern_layout.addWidget(QLabel("关注点:"))
        self.concern_input = QLineEdit()
        self.concern_input.setPlaceholderText("例如: 关注付款周期和知识产权保护")
        concern_layout.addWidget(self.concern_input)
        params_layout.addLayout(concern_layout)

        # 输出格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("输出格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Word (.docx)", "Markdown (.md)"])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        params_layout.addLayout(format_layout)

        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)

        # 3. 开始审查按钮
        self.start_btn = QPushButton("🚀 开始审查")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.start_btn.clicked.connect(self.start_review)
        main_layout.addWidget(self.start_btn)

        # 4. 进度条
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
        main_layout.addWidget(self.progress_bar)

        # 5. 结果显示区域
        result_group = QGroupBox("3. 审查结果")
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("审查结果将显示在这里...")
        self.result_text.setMinimumHeight(200)
        result_layout.addWidget(self.result_text)

        # 操作按钮
        action_layout = QHBoxLayout()

        self.open_report_btn = QPushButton("📂 打开报告")
        self.open_report_btn.clicked.connect(self.open_report)
        self.open_report_btn.setEnabled(False)
        action_layout.addWidget(self.open_report_btn)

        self.open_folder_btn = QPushButton("📁 打开文件夹")
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        action_layout.addWidget(self.open_folder_btn)

        action_layout.addStretch()

        self.clear_btn = QPushButton("🗑️ 清空结果")
        self.clear_btn.clicked.connect(self.clear_results)
        action_layout.addWidget(self.clear_btn)

        result_layout.addLayout(action_layout)
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)

        # 状态栏
        self.statusBar().showMessage("就绪")

    def browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择合同文件",
            "",
            "支持的格式 (*.docx *.pdf);;Word文档 (*.docx);;PDF文档 (*.pdf)"
        )
        if file_path:
            self.on_file_dropped(file_path)
            self.drop_zone.setText(f"已选择文件:\n{Path(file_path).name}")

    def on_file_dropped(self, file_path: str):
        """文件拖放处理"""
        self.contract_file = file_path
        self.file_label.setText(f"✅ {Path(file_path).name}")
        self.file_label.setStyleSheet("color: #4CAF50;")
        self.statusBar().showMessage(f"已加载: {file_path}")

    def start_review(self):
        """开始审查"""
        # 验证输入
        if not self.contract_file:
            QMessageBox.warning(self, "错误", "请先选择合同文件")
            return

        contract_type = self.type_input.text().strip()
        if not contract_type:
            QMessageBox.warning(self, "错误", "请输入合同类型")
            return

        user_concerns = self.concern_input.text().strip()
        if not user_concerns:
            QMessageBox.warning(self, "错误", "请输入关注点")
            return

        # 禁用按钮
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.result_text.clear()
        self.open_report_btn.setEnabled(False)

        # 获取输出格式
        output_format = "word" if self.format_combo.currentIndex() == 0 else "markdown"

        # 启动工作线程
        self.worker = ReviewWorker(
            contract_file=self.contract_file,
            client_role=self.role_combo.currentText(),
            contract_type=contract_type,
            user_concerns=user_concerns,
            output_format=output_format
        )

        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)

        self.worker.start()
        self.statusBar().showMessage("审查进行中...")

    def on_progress(self, message: str, progress: int):
        """进度更新"""
        self.progress_bar.setValue(progress)
        self.result_text.append(f"[{progress}%] {message}")
        logger.info(f"进度: {progress}% - {message}")

    def on_finished(self, result: dict):
        """审查完成"""
        self.start_btn.setEnabled(True)
        self.open_report_btn.setEnabled(True)

        # 显示完整报告
        report = result["data"]["review_report"]
        self.result_text.setMarkdown(report)

        # 保存报告路径
        self.current_report_path = result["data"]["report_path"]

        QMessageBox.information(
            self,
            "审查完成",
            f"合同审查成功完成！\n报告已保存到:\n{self.current_report_path}"
        )

        self.statusBar().showMessage("审查完成")

    def on_error(self, error_message: str):
        """审查错误"""
        self.start_btn.setEnabled(True)
        self.result_text.append(f"\n❌ 错误: {error_message}")
        QMessageBox.critical(self, "错误", error_message)
        self.statusBar().showMessage("审查失败")

    def open_report(self):
        """打开报告"""
        if hasattr(self, 'current_report_path') and self.current_report_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.current_report_path))

    def open_output_folder(self):
        """打开输出文件夹"""
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(Config.OUTPUT_DIR)))

    def clear_results(self):
        """清空结果"""
        self.result_text.clear()
        self.contract_file = None
        self.file_label.setText("未选择文件")
        self.file_label.setStyleSheet("color: #666;")
        self.drop_zone.setText("拖放合同文件到此处\n支持 .docx 和 .pdf 格式")
        self.open_report_btn.setEnabled(False)
        self.statusBar().showMessage("已清空")


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
    window = MainWindow()
    window.show()

    # 只有在新创建 QApplication 时才执行事件循环
    if should_exec:
        sys.exit(app.exec())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
合同审查小助手 - 启动器
提供版本选择
"""
import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import Config

# 配置日志
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.CACHE_DIR / "app.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def check_dependencies():
    """检查必要的依赖"""
    missing = []

    try:
        import PySide6
    except ImportError:
        missing.append("PySide6")

    if missing:
        print("❌ 缺少必要的依赖包:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n请运行: pip install -r requirements.txt")
        return False

    return True


def init_config():
    """初始化配置"""
    # 检查 .env 文件
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  未找到 .env 配置文件")
        print("正在从 .env.example 创建默认配置...")

        env_example = project_root / ".env.example"
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ 已创建 .env 文件")
        else:
            print("⚠️  未找到 .env.example 文件")

    # 初始化目录
    try:
        Config.init_directories()
        print(f"✅ 目录初始化成功")
    except Exception as e:
        print(f"❌ 目录初始化失败: {e}")
        return False

    return True


def show_version_selector():
    """显示版本选择器"""
    try:
        from PySide6.QtWidgets import (
            QApplication, QDialog, QVBoxLayout, QHBoxLayout,
            QPushButton, QLabel, QGroupBox, QMessageBox, QWidget
        )
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont

        # 定义可点击的Widget类
        class ClickableWidget(QWidget):
            def __init__(self, version_name, description, is_selected, parent_dialog):
                super().__init__()
                self.version_name = version_name
                self.parent_dialog = parent_dialog

            def mousePressEvent(self, event):
                if self.version_name == "简洁版":
                    self.parent_dialog.select_version("simple")
                else:
                    self.parent_dialog.select_version("pro")

        class VersionSelector(QDialog):
            def __init__(self):
                super().__init__()
                self.selected_version = None
                self.init_ui()

            def init_ui(self):
                self.setWindowTitle("选择版本")
                self.setFixedSize(500, 200)

                # 主容器 - 白色背景，圆角，阴影
                self.setStyleSheet("""
                    QDialog {
                        background-color: white;
                        border-radius: 16px;
                    }
                """)

                layout = QVBoxLayout(self)
                layout.setSpacing(32)
                layout.setContentsMargins(24, 24, 24, 24)

                # 版本选项容器
                versions_layout = QHBoxLayout()
                versions_layout.setSpacing(32)

                # 简洁版卡片
                simple_card = self.create_version_card(
                    "简洁版",
                    "快速审查单个合同",
                    False
                )
                versions_layout.addWidget(simple_card)

                # 专业版卡片
                pro_card = self.create_version_card(
                    "专业版",
                    "批量审查和专业分析",
                    True  # 默认选中
                )
                versions_layout.addWidget(pro_card)

                layout.addLayout(versions_layout)

            def create_version_card(self, title, description, is_selected):
                """创建版本卡片"""
                from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
                from PySide6.QtCore import Qt

                # 创建一个可点击的容器widget
                card = ClickableWidget(title, description, is_selected, self)
                card.setFixedSize(200, 120)

                # 根据选中状态设置样式 - 使用淡绿色
                if is_selected:
                    card.setStyleSheet("""
                        border: 2px solid #1890ff;
                        border-radius: 12px;
                        background-color: #e8f5e9;
                    """)
                else:
                    card.setStyleSheet("""
                        border: 1px solid #000;
                        border-radius: 12px;
                        background-color: #f1f8f4;
                    """)

                # 创建布局
                layout = QVBoxLayout(card)
                layout.setSpacing(8)
                layout.setContentsMargins(16, 24, 16, 24)

                # 标题
                title_label = QLabel(title)
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                title_label.setStyleSheet("""
                    font-size: 16px;
                    color: #333;
                    font-weight: bold;
                    background-color: transparent;
                    border: none;
                """)

                # 简介文字
                desc_label = QLabel(description)
                desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                desc_label.setStyleSheet("""
                    font-size: 12px;
                    color: #666;
                    background-color: transparent;
                    border: none;
                """)

                layout.addWidget(title_label)
                layout.addWidget(desc_label)
                layout.addStretch()

                return card

            def select_version(self, version):
                self.selected_version = version
                self.accept()

        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        dialog = VersionSelector()
        dialog.exec()

        return dialog.selected_version

    except Exception as e:
        logger.error(f"版本选择器启动失败: {e}")
        # 如果GUI启动失败，默认使用简洁版
        print("\n版本选择器启动失败，将使用简洁版界面...")
        return "simple"


def main():
    """主函数"""
    print("=" * 60)
    print("📄 合同审查小助手 - 启动中...")
    print("=" * 60)
    print()

    # 检查依赖
    print("[1/3] 检查依赖包...")
    if not check_dependencies():
        input("\n按回车键退出...")
        sys.exit(1)

    # 初始化配置
    print("[2/3] 初始化配置...")
    if not init_config():
        input("\n按回车键退出...")
        sys.exit(1)

    # 选择版本
    print("[3/3] 启动界面...")
    print()

    version = show_version_selector()

    if version == "pro":
        print("✅ 已选择：专业版（三段式布局）")
        import main_window_pro
        # 直接运行而不是调用main()，避免重复创建QApplication
        import sys
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        main_window_pro.window = main_window_pro.MainWindowPro()
        main_window_pro.window.show()
        sys.exit(app.exec())
    else:
        print("✅ 已选择：简洁版（经典布局）")
        import main_window
        import sys
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        main_window.window = main_window.MainWindow()
        main_window.window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()

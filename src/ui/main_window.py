from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QLabel,
    QCheckBox, QFrame
)
from PyQt5.QtGui import QFont, QMouseEvent

from src.models.task import Task
from src.ui.styles import MAIN_STYLE


class TaskItemWidget(QWidget):
    """单个任务项的控件：复选框 + 文字 + 删除按钮"""

    def __init__(self, task: Task, on_toggle, on_delete, parent=None):
        super().__init__(parent)
        self.task = task
        self._on_toggle = on_toggle
        self._on_delete = on_delete

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(6)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(task.completed)
        self.checkbox.stateChanged.connect(self._handle_toggle)
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 18px; height: 18px;
                border: 2px solid #45475a;
                border-radius: 5px;
                background: #313244;
            }
            QCheckBox::indicator:checked {
                background: #a6e3a1;
                border-color: #a6e3a1;
            }
            QCheckBox::indicator:hover {
                border-color: #89b4fa;
            }
        """)

        self.label = QLabel(task.text)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("background: transparent; border: none;")

        self.del_btn = QPushButton("\u00d7")  # × 符号
        self.del_btn.setFixedSize(24, 24)
        self.del_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #6c7086;
                font-size: 18px;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: #f38ba8;
                color: #1e1e2e;
            }
        """)
        self.del_btn.clicked.connect(lambda: self._on_delete(self.task.id))

        layout.addWidget(self.checkbox)
        layout.addWidget(self.label, stretch=1)
        layout.addWidget(self.del_btn)

        self._update_style()

    def _handle_toggle(self, state):
        self.task.completed = (state == Qt.Checked)
        self._update_style()
        if self._on_toggle:
            self._on_toggle(self.task.id, self.task.completed)

    def _update_style(self):
        if self.task.completed:
            self.label.setStyleSheet("""
                background: transparent;
                border: none;
                color: #585b70;
                text-decoration: line-through;
            """)
            font = self.label.font()
            font.setItalic(True)
            self.label.setFont(font)
        else:
            self.label.setStyleSheet("""
                background: transparent;
                border: none;
                color: #cdd6f4;
            """)
            font = self.label.font()
            font.setItalic(False)
            self.label.setFont(font)


class MainWindow(QWidget):
    """无边框主窗口"""

    WINDOW_TITLE = "To-Do List"
    WIN_WIDTH = 380
    WIN_HEIGHT = 500

    def __init__(self):
        super().__init__()
        self._tasks: dict[str, Task] = {}
        self._drag_pos: QPoint | None = None

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setFixedSize(self.WIN_WIDTH, self.WIN_HEIGHT)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- 标题栏 ---
        title_bar = QFrame()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(36)
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(0, 0, 0, 0)
        tb_layout.setSpacing(0)

        self.title_label = QLabel("  " + self.WINDOW_TITLE)
        self.title_label.setObjectName("titleLabel")
        tb_layout.addWidget(self.title_label, stretch=1)

        close_btn = QPushButton("\u00d7")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(self.close)
        tb_layout.addWidget(close_btn)

        root.addWidget(title_bar)

        # --- 输入区域 ---
        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        if_layout = QHBoxLayout(input_frame)
        if_layout.setContentsMargins(10, 8, 10, 8)
        if_layout.setSpacing(0)

        self.input = QLineEdit()
        self.input.setPlaceholderText("输入新任务...")
        self.input.returnPressed.connect(self._add_task)

        self.add_btn = QPushButton("添加")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.clicked.connect(self._add_task)

        if_layout.addWidget(self.input, stretch=1)
        if_layout.addWidget(self.add_btn)
        root.addWidget(input_frame)

        # --- 任务列表 ---
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(0)
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        root.addWidget(self.list_widget, stretch=1)

    def _apply_style(self):
        self.setStyleSheet(MAIN_STYLE)

    # ── 窗口拖拽 ──────────────────────────────
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # 只在标题栏区域可拖拽
            if event.pos().y() <= 36:
                self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    # ── 任务操作 ──────────────────────────────
    def _add_task(self):
        text = self.input.text().strip()
        if not text:
            return

        task = Task.create(text)
        self._tasks[task.id] = task
        self._insert_item(task)
        self.input.clear()
        self.input.setFocus()

    def _insert_item(self, task: Task):
        item = QListWidgetItem(self.list_widget)
        widget = TaskItemWidget(
            task,
            on_toggle=self._on_task_toggle,
            on_delete=self._delete_task,
        )
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

    def _on_task_toggle(self, task_id: str, completed: bool):
        if task_id in self._tasks:
            self._tasks[task_id].completed = completed

    def _delete_task(self, task_id: str):
        # 查找并移除对应的 QListWidgetItem
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget and widget.task.id == task_id:
                self.list_widget.takeItem(i)
                break
        self._tasks.pop(task_id, None)

import json
import os

from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QLabel,
    QFrame
)
from PyQt5.QtGui import QMouseEvent, QFontMetrics

from src.models.task import Task
from src.ui.styles import MAIN_STYLE


class TaskItemWidget(QWidget):
    """单个任务项的控件：勾选按钮 + 文字 + 删除按钮 + 可展开详情"""

    ITEM_BASE_HEIGHT = 40

    def __init__(self, task: Task, on_toggle, on_delete, on_item_resize, parent=None):
        super().__init__(parent)
        self.task = task
        self._on_toggle = on_toggle
        self._on_delete = on_delete
        self._on_item_resize = on_item_resize
        self._expanded = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── 主行 ──
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(8, 4, 8, 12)
        row_layout.setSpacing(8)

        self.check_btn = QPushButton()
        self.check_btn.setFixedSize(20, 20)
        self.check_btn.setCheckable(True)
        self.check_btn.setChecked(task.completed)
        self.check_btn.clicked.connect(self._handle_toggle)
        self.check_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 2px solid #585b70;
                border-radius: 10px;
                color: transparent;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:checked {
                background: #a6e3a1;
                border-color: #a6e3a1;
                color: #1e1e2e;
            }
            QPushButton:hover {
                border-color: #89b4fa;
            }
            QPushButton:checked:hover {
                background: #94d89a;
                border-color: #94d89a;
            }
        """)
        self._update_check_btn_text()

        self.label = QLabel(task.text)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("background: transparent; border: none;")
        self.label.setCursor(Qt.PointingHandCursor)
        self.label.mousePressEvent = self._on_label_click

        self.del_btn = QPushButton("\u00d7")
        self.del_btn.setFixedSize(20, 20)
        self.del_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #6c7086;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background: #f38ba8;
                color: #1e1e2e;
            }
        """)
        self.del_btn.clicked.connect(lambda: self._on_delete(self.task.id))

        row_layout.addWidget(self.check_btn, alignment=Qt.AlignVCenter)
        row_layout.addWidget(self.label, stretch=1, alignment=Qt.AlignVCenter)
        row_layout.addWidget(self.del_btn, alignment=Qt.AlignVCenter)
        outer.addWidget(row)

        # ── 详情面板（默认隐藏）──
        self.detail_frame = QFrame()
        self.detail_frame.setStyleSheet("""
            QFrame {
                background: #11111b;
                border-top: 1px solid #313244;
                border-radius: 0 0 8px 8px;
            }
            QLabel {
                background: transparent;
                border: none;
                color: #a6adc8;
                font-size: 12px;
            }
        """)
        self.detail_frame.setVisible(False)
        detail_layout = QVBoxLayout(self.detail_frame)
        detail_layout.setContentsMargins(14, 8, 14, 8)
        detail_layout.setSpacing(4)

        self.detail_text = QLabel(f"任务: {task.text}")
        self.detail_text.setWordWrap(True)
        desc = task.description or "（无）"
        self.detail_desc = QLabel(f"备注: {desc}")
        self.detail_desc.setWordWrap(True)
        self.detail_time = QLabel(f"创建: {task.created_at}")

        detail_layout.addWidget(self.detail_text)
        detail_layout.addWidget(self.detail_desc)
        detail_layout.addWidget(self.detail_time)
        outer.addWidget(self.detail_frame)

        self.setMinimumHeight(self.ITEM_BASE_HEIGHT)
        self._update_style()

    def _on_label_click(self, event):
        self._expanded = not self._expanded
        self.detail_frame.setVisible(self._expanded)
        self._on_item_resize()
        if event:
            QLabel.mousePressEvent(self.label, event)

    def sizeHint(self):
        if not self._expanded:
            return QSize(0, self.ITEM_BASE_HEIGHT)
        # 动态计算详情面板所需高度
        fm = QFontMetrics(self.detail_text.font())
        avail_w = self.width() - 28  # 左右 margin 14*2
        if avail_w <= 0:
            avail_w = 300
        text_h = fm.boundingRect(0, 0, avail_w, 0,
                                 Qt.TextWordWrap, self.detail_text.text()).height()
        desc_h = fm.boundingRect(0, 0, avail_w, 0,
                                 Qt.TextWordWrap, self.detail_desc.text()).height()
        time_h = fm.height()
        detail_h = text_h + desc_h + time_h + 24  # 24 = padding + spacing
        return QSize(0, self.ITEM_BASE_HEIGHT + detail_h)

    def minimumSizeHint(self):
        return self.sizeHint()

    def _update_check_btn_text(self):
        self.check_btn.setText("\u2713" if self.task.completed else "")

    def _handle_toggle(self):
        self.task.completed = self.check_btn.isChecked()
        self._update_check_btn_text()
        self._update_style()
        if self._on_toggle:
            self._on_toggle(self.task.id, self.task.completed)

    def _update_style(self):
        font = self.label.font()
        if self.task.completed:
            self.label.setStyleSheet("""
                background: transparent;
                border: none;
                color: #585b70;
            """)
            font.setItalic(True)
            font.setStrikeOut(True)
        else:
            self.label.setStyleSheet("""
                background: transparent;
                border: none;
                color: #cdd6f4;
            """)
            font.setItalic(False)
            font.setStrikeOut(False)
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
        self._load_tasks()

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
        if_layout = QVBoxLayout(input_frame)
        if_layout.setContentsMargins(10, 8, 10, 8)
        if_layout.setSpacing(6)

        # 第一行：任务名 + 添加按钮
        name_row = QHBoxLayout()
        name_row.setSpacing(6)

        self.input = QLineEdit()
        self.input.setPlaceholderText("任务名称...")
        self.input.returnPressed.connect(self._add_task)

        self.add_btn = QPushButton("添加")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.clicked.connect(self._add_task)

        name_row.addWidget(self.input, stretch=1)
        name_row.addWidget(self.add_btn)
        if_layout.addLayout(name_row)

        # 第二行：备注（可选）
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("备注（可选）...")
        self.desc_input.returnPressed.connect(self._add_task)
        if_layout.addWidget(self.desc_input)

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

        description = self.desc_input.text().strip()
        task = Task.create(text, description)
        self._tasks[task.id] = task
        self._insert_item(task)
        self.input.clear()
        self.desc_input.clear()
        self.input.setFocus()
        self._save_tasks()

    def _insert_item(self, task: Task):
        item = QListWidgetItem(self.list_widget)
        widget = TaskItemWidget(
            task,
            on_toggle=self._on_task_toggle,
            on_delete=self._delete_task,
            on_item_resize=lambda: self._resize_item(item, widget),
        )
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

    def _resize_item(self, item: QListWidgetItem, widget: TaskItemWidget):
        item.setSizeHint(widget.sizeHint())
        self.list_widget.doItemsLayout()

    def _on_task_toggle(self, task_id: str, completed: bool):
        if task_id in self._tasks:
            self._tasks[task_id].completed = completed
        self._save_tasks()

    def _delete_task(self, task_id: str):
        # 查找并移除对应的 QListWidgetItem
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget and widget.task.id == task_id:
                self.list_widget.takeItem(i)
                break
        self._tasks.pop(task_id, None)
        self._save_tasks()

    # ── 数据持久化 ────────────────────────────
    def _get_data_path(self) -> str:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "tasks.json")

    def _save_tasks(self):
        tasks_data = []
        for task in self._tasks.values():
            tasks_data.append({
                "id": task.id,
                "text": task.text,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at,
            })
        with open(self._get_data_path(), "w", encoding="utf-8") as f:
            json.dump(tasks_data, f, ensure_ascii=False, indent=2)

    def _load_tasks(self):
        path = self._get_data_path()
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)
        for item in tasks_data:
            task = Task(
                id=item["id"],
                text=item["text"],
                description=item.get("description", ""),
                completed=item["completed"],
                created_at=item.get("created_at", ""),
            )
            self._tasks[task.id] = task
            self._insert_item(task)

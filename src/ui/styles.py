MAIN_STYLE = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}

/* 顶部栏 */
#titleBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
}
#titleLabel {
    font-size: 14px;
    font-weight: bold;
    color: #cdd6f4;
    padding-left: 12px;
}
#closeBtn {
    background: transparent;
    border: none;
    color: #cdd6f4;
    font-size: 18px;
    font-weight: bold;
    padding: 4px 12px;
}
#closeBtn:hover {
    background-color: #f38ba8;
    color: #1e1e2e;
}

/* 输入区域 */
#inputFrame {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    padding: 10px;
}
QLineEdit {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 8px 14px;
    color: #cdd6f4;
    font-size: 13px;
    selection-background-color: #89b4fa;
}
QLineEdit:focus {
    border-color: #89b4fa;
}
#addBtn {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: bold;
    margin-left: 8px;
}
#addBtn:hover {
    background-color: #74c7ec;
}
#addBtn:pressed {
    background-color: #89dceb;
}

/* 任务列表 */
QListWidget {
    background-color: #1e1e2e;
    border: none;
    outline: none;
    padding: 4px;
}
QListWidget::item {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    margin: 3px 6px;
    padding: 0px;
}
QListWidget::item:hover {
    border-color: #45475a;
}

QScrollBar:vertical {
    background: #181825;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #585b70;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

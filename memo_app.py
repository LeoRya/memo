import sys
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QDateTimeEdit, QPushButton, QListWidget,
    QLabel, QDialog, QSpinBox, QRadioButton, QGroupBox, QCheckBox,
    QSystemTrayIcon, QMenu, QAction, QSplitter, QHeaderView, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QColorDialog, QSizeGrip, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QEvent, QObject, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QIcon, QPixmap

# 获取资源路径（兼容开发环境和PyInstaller打包环境）
def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境 - 使用脚本所在目录，而不是当前工作目录
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(script_dir, relative_path)

TASK_STATUS_IN_PROGRESS = 'in_progress'
TASK_STATUS_COMPLETED = 'completed'
TASK_STATUS_CANCELLED = 'cancelled'

SORT_ORDER_NONE = 0
SORT_ORDER_ASC = 1
SORT_ORDER_DESC = 2

class PriorityColorDialog(QDialog):
    def __init__(self, parent=None, priority_colors=None, max_priority=5):
        super().__init__(parent)
        self.setWindowTitle('优先级颜色设置')
        self.setFixedSize(400, 300)
        self.layout = QVBoxLayout(self)
        
        self.priority_colors = priority_colors or {}
        self.max_priority = max_priority
        self.current_priority = 1
        
        # 优先级选择
        priority_select_layout = QHBoxLayout()
        priority_select_layout.addWidget(QLabel('选择优先级:'))
        self.priority_combo = QComboBox()
        for i in range(1, self.max_priority + 1):
            self.priority_combo.addItem(f'优先级 {i}')
        self.priority_combo.currentIndexChanged.connect(self.on_priority_changed)
        priority_select_layout.addWidget(self.priority_combo)
        priority_select_layout.addStretch()
        self.layout.addLayout(priority_select_layout)
        
        # 预览区域
        self.preview_group = QGroupBox('颜色预览')
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel('便签预览文本')
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(60)
        preview_layout.addWidget(self.preview_label)
        self.preview_group.setLayout(preview_layout)
        self.layout.addWidget(self.preview_group)
        
        # 颜色选择区域
        color_select_layout = QHBoxLayout()
        
        # 背景颜色选择
        bg_layout = QVBoxLayout()
        bg_layout.addWidget(QLabel('便签背景颜色:'))
        self.bg_button = QPushButton()
        self.bg_button.setMinimumSize(80, 40)
        self.bg_button.clicked.connect(self.select_bg_color)
        bg_layout.addWidget(self.bg_button)
        color_select_layout.addLayout(bg_layout)
        
        # 文字颜色选择
        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel('便签文字颜色:'))
        self.text_button = QPushButton()
        self.text_button.setMinimumSize(80, 40)
        self.text_button.clicked.connect(self.select_text_color)
        text_layout.addWidget(self.text_button)
        color_select_layout.addLayout(text_layout)
        
        self.layout.addLayout(color_select_layout)
        
        # 说明文字
        info_label = QLabel('提示: 选择优先级后，点击颜色方块可以更改该优先级的便签颜色')
        info_label.setWordWrap(True)
        info_label.setStyleSheet('color: gray; font-size: 12px;')
        self.layout.addWidget(info_label)
        
        self.layout.addStretch()
        
        # 按钮布局
        button_layout = QHBoxLayout()
        save_button = QPushButton('保存')
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        self.layout.addLayout(button_layout)
        
        # 初始化显示第一个优先级的颜色
        self.update_color_display()
    
    def on_priority_changed(self, index):
        self.current_priority = index + 1
        self.update_color_display()
    
    def update_color_display(self):
        """更新颜色显示"""
        # 定义每个优先级的默认颜色（与程序中一致）
        default_colors = {
            1: {'bg': '#FFF9C4', 'text': '#000000'},  # 优先级1: 浅黄背景，黑色文字
            2: {'bg': '#55FFFF', 'text': '#000000'},  # 优先级2: 青色背景，黑色文字
            3: {'bg': '#00AA00', 'text': '#FFFFFF'},  # 优先级3: 绿色背景，白色文字
            4: {'bg': '#FF5500', 'text': '#FFFFFF'},  # 优先级4: 橙色背景，白色文字
            5: {'bg': '#FF0000', 'text': '#FFFFFF'},  # 优先级5: 红色背景，白色文字
        }
        # 获取当前优先级的默认颜色
        default_color = default_colors.get(self.current_priority, {'bg': '#FFF9C4', 'text': '#000000'})
        bg_color = self.priority_colors.get(str(self.current_priority), {}).get('bg', default_color['bg'])
        text_color = self.priority_colors.get(str(self.current_priority), {}).get('text', default_color['text'])
        
        # 更新按钮颜色
        self.bg_button.setStyleSheet(f'background-color: {bg_color}; border: 2px solid #ccc;')
        self.text_button.setStyleSheet(f'background-color: {text_color}; border: 2px solid #ccc;')
        
        # 更新预览
        self.preview_label.setStyleSheet(f'''
            background-color: {bg_color};
            color: {text_color};
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
        ''')
        self.preview_label.setText(f'优先级 {self.current_priority} 便签预览')
    
    def get_default_color_for_priority(self, priority):
        """获取指定优先级的默认颜色"""
        default_colors = {
            1: {'bg': '#FFF9C4', 'text': '#000000'},
            2: {'bg': '#55FFFF', 'text': '#000000'},
            3: {'bg': '#00AA00', 'text': '#FFFFFF'},
            4: {'bg': '#FF5500', 'text': '#FFFFFF'},
            5: {'bg': '#FF0000', 'text': '#FFFFFF'},
        }
        return default_colors.get(priority, {'bg': '#FFF9C4', 'text': '#000000'})
    
    def select_bg_color(self):
        default_color = self.get_default_color_for_priority(self.current_priority)
        current_color = self.priority_colors.get(str(self.current_priority), {}).get('bg', default_color['bg'])
        color = QColorDialog.getColor(QColor(current_color), self, '选择便签背景颜色')
        if color.isValid():
            color_hex = color.name()
            self.priority_colors[str(self.current_priority)] = self.priority_colors.get(str(self.current_priority), {})
            self.priority_colors[str(self.current_priority)]['bg'] = color_hex
            self.update_color_display()
    
    def select_text_color(self):
        default_color = self.get_default_color_for_priority(self.current_priority)
        current_color = self.priority_colors.get(str(self.current_priority), {}).get('text', default_color['text'])
        color = QColorDialog.getColor(QColor(current_color), self, '选择便签文字颜色')
        if color.isValid():
            color_hex = color.name()
            self.priority_colors[str(self.current_priority)] = self.priority_colors.get(str(self.current_priority), {})
            self.priority_colors[str(self.current_priority)]['text'] = color_hex
            self.update_color_display()
    
    def get_priority_colors(self):
        return self.priority_colors


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置')
        self.setFixedSize(400, 350)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # 应用当前主题样式
        self.apply_dialog_theme(parent.settings.get('theme', 'light'))
        
        # 主题设置
        self.theme_group = QGroupBox('界面主题')
        self.theme_layout = QVBoxLayout()
        self.theme_layout.setSpacing(8)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem('亮色风格')
        self.theme_combo.addItem('暗色风格')
        current_theme = parent.settings.get('theme', 'light')
        self.theme_combo.setCurrentIndex(0 if current_theme == 'light' else 1)
        self.theme_layout.addWidget(self.theme_combo)
        self.theme_group.setLayout(self.theme_layout)
        
        # 优先级设置
        self.priority_group = QGroupBox('优先级设置')
        self.priority_layout = QVBoxLayout()
        self.priority_layout.setSpacing(8)
        
        # 优先级数量设置和颜色按钮
        self.priority_count_layout = QHBoxLayout()
        self.priority_count_layout.setSpacing(10)
        self.priority_spinbox = QSpinBox()
        self.priority_spinbox.setRange(1, 10)
        self.priority_spinbox.setValue(parent.settings.get('priority_count', 5))
        self.priority_count_layout.addWidget(QLabel('数量:'))
        self.priority_count_layout.addWidget(self.priority_spinbox)
        
        # 优先级颜色设置按钮
        self.priority_colors = parent.settings.get('priority_colors', {})
        self.color_button = QPushButton('设置优先级颜色')
        self.color_button.clicked.connect(self.open_color_dialog)
        self.priority_count_layout.addWidget(self.color_button)
        
        self.priority_count_layout.addStretch()
        self.priority_layout.addLayout(self.priority_count_layout)
        self.priority_group.setLayout(self.priority_layout)
        
        # 启动设置
        self.startup_group = QGroupBox('启动设置')
        self.startup_layout = QVBoxLayout()
        self.startup_layout.setSpacing(8)
        
        self.startup_checkbox = QCheckBox('开机自动启动')
        self.startup_checkbox.setChecked(parent.settings.get('auto_start', True))
        self.startup_layout.addWidget(self.startup_checkbox)
        
        self.startup_group.setLayout(self.startup_layout)
        
        # 按钮布局
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)
        self.save_button = QPushButton('保存')
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QPushButton('取消')
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)
        
        self.layout.addWidget(self.theme_group)
        self.layout.addWidget(self.priority_group)
        self.layout.addWidget(self.startup_group)
        self.layout.addStretch()
        self.layout.addLayout(self.button_layout)
    
    def open_color_dialog(self):
        dialog = PriorityColorDialog(self, self.priority_colors, self.priority_spinbox.value())
        if dialog.exec_() == QDialog.Accepted:
            self.priority_colors = dialog.get_priority_colors()
    
    def apply_dialog_theme(self, theme):
        """应用对话框主题样式"""
        if theme == 'dark':
            self.setStyleSheet('''
                QDialog {
                    background-color: #2b2b2b;
                }
                QGroupBox {
                    color: #ffffff;
                    border: 1px solid #555;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
                QComboBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 6px;
                }
                QSpinBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 6px;
                }
            ''')
        else:
            self.setStyleSheet('''
                QDialog {
                    background-color: #f0f0f0;
                }
                QGroupBox {
                    border: 1px solid #ddd;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
            ''')
    
    def save_settings(self):
        self.parent().settings['priority_count'] = self.priority_spinbox.value()
        self.parent().settings['priority_colors'] = self.priority_colors
        self.parent().settings['theme'] = 'light' if self.theme_combo.currentIndex() == 0 else 'dark'
        self.parent().settings['auto_start'] = self.startup_checkbox.isChecked()
        self.parent().save_settings()
        self.parent().update_priority_options()
        self.parent().update_reminder_formats()
        self.parent().apply_theme()
        # 应用开机自启动设置
        self.parent().apply_auto_start()
        self.accept()

class ReminderWindow(QWidget):
    # 类变量：跟踪所有打开的提醒框
    all_reminders = set()
    # 类变量：跟踪当前选中的提醒框
    selected_reminders = set()
    
    def __init__(self, task_id, task_text, priority, deadline, parent=None):
        super().__init__(None)
        self.task_id = task_id
        self.task_text = task_text
        self.priority = priority
        self.deadline = deadline
        self.parent_window = parent
        self.drag_start_pos = None
        self.drag_start_global_pos = None
        self.is_selected = False
        self.is_dragging = False  # 标记是否正在拖动
        
        # 添加到全局提醒框集合
        ReminderWindow.all_reminders.add(self)
        
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(100, 50)
        
        # 应用优先级颜色设置
        self.apply_priority_styles()
        
        # 拉伸相关变量
        self.resize_mode = False
        self.resize_edge = None
        self.last_pos = None
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建内容布局
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        self.task_label = QLabel(task_text)
        self.task_label.setAlignment(Qt.AlignCenter)
        self.task_label.setStyleSheet('font-size: 14px;')
        self.task_label.setToolTip(task_text)
        self.task_label.setWordWrap(True)  # 启用换行
        self.task_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        countdown_container = QWidget()
        countdown_layout = QVBoxLayout(countdown_container)
        countdown_layout.setContentsMargins(0, 0, 0, 0)
        
        # 只使用文本格式倒计时
        self.countdown_label = QLabel()
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet('font-size: 14px; font-weight: bold;')
        # 设置最小宽度以适应倒计时文本
        self.countdown_label.setMinimumWidth(100)
        countdown_layout.addWidget(self.countdown_label)
        
        self.complete_button = QPushButton('✓')
        self.complete_button.setFixedSize(30, 30)
        self.complete_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')
        self.complete_button.clicked.connect(self.complete_task)
        
        content_layout.addWidget(self.task_label, 1)
        content_layout.addWidget(countdown_container)
        content_layout.addWidget(self.complete_button)
        
        # 添加内容布局到主布局
        main_layout.addLayout(content_layout)
        
        # 添加QSizeGrip控件到四个角，确保拉伸功能正常工作
        # 右下角
        self.size_grip_bottom_right = QSizeGrip(self)
        self.size_grip_bottom_right.setGeometry(self.width() - 10, self.height() - 10, 10, 10)
        self.size_grip_bottom_right.setStyleSheet('background-color: transparent; border: none;')
        
        # 右上角
        self.size_grip_top_right = QSizeGrip(self)
        self.size_grip_top_right.setGeometry(self.width() - 10, 0, 10, 10)
        self.size_grip_top_right.setStyleSheet('background-color: transparent; border: none;')
        
        # 左下角
        self.size_grip_bottom_left = QSizeGrip(self)
        self.size_grip_bottom_left.setGeometry(0, self.height() - 10, 10, 10)
        self.size_grip_bottom_left.setStyleSheet('background-color: transparent; border: none;')
        
        # 左上角
        self.size_grip_top_left = QSizeGrip(self)
        self.size_grip_top_left.setGeometry(0, 0, 10, 10)
        self.size_grip_top_left.setStyleSheet('background-color: transparent; border: none;')
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)
        self.update_countdown()
        self.update_task_label_text()
    
    def apply_priority_styles(self):
        # 获取优先级颜色设置
        priority_colors = self.parent_window.settings.get('priority_colors', {})
        priority_color = priority_colors.get(str(self.priority), {})
        # 定义每个优先级的默认颜色
        default_colors = {
            1: {'bg': '#FFF9C4', 'text': '#000000'},  # 优先级1: 浅黄背景，黑色文字
            2: {'bg': '#55FFFF', 'text': '#000000'},  # 优先级2: 青色背景，黑色文字
            3: {'bg': '#00AA00', 'text': '#FFFFFF'},  # 优先级3: 绿色背景，白色文字
            4: {'bg': '#FF5500', 'text': '#FFFFFF'},  # 优先级4: 橙色背景，白色文字
            5: {'bg': '#FF0000', 'text': '#FFFFFF'},  # 优先级5: 红色背景，白色文字
        }
        # 获取当前优先级的默认颜色
        default_color = default_colors.get(self.priority, {'bg': '#FFF9C4', 'text': '#000000'})
        # 确保有默认值
        self.priority_color = {
            'bg': priority_color.get('bg', default_color['bg']),
            'text': priority_color.get('text', default_color['text'])
        }
        
        self.setStyleSheet(f'''
            QLabel {{
                font-family: Microsoft YaHei;
                color: {self.priority_color['text']};
            }}
            QSizeGrip {{
                background-color: transparent;
                border: none;
            }}
        ''')
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆角背景
        rect = self.rect()
        
        # 如果被选中，绘制反色边框效果
        if self.is_selected:
            # 反色边框：使用与背景色对比明显的颜色
            bg_color = QColor(self.priority_color['bg'])
            # 计算反色
            inverted_color = QColor(255 - bg_color.red(), 255 - bg_color.green(), 255 - bg_color.blue())
            painter.setPen(QPen(inverted_color, 3))
            # 绘制填充背景
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, 12, 12)
            
            # 绘制内边框（反色效果）
            inner_rect = rect.adjusted(4, 4, -4, -4)
            painter.setPen(QPen(inverted_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(inner_rect, 8, 8)
        else:
            painter.setPen(QPen(QColor('#FFD54F'), 1))
            painter.setBrush(QColor(self.priority_color['bg']))
            painter.drawRoundedRect(rect, 12, 12)
        
        # 调用父类的paintEvent以绘制子控件
        super().paintEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 拖动窗口
            self.start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            # 拖动窗口
            self.move(event.globalPos() - self.start_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.start_pos = None
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 更新所有size grip的位置
        if hasattr(self, 'size_grip_bottom_right'):
            self.size_grip_bottom_right.setGeometry(self.width() - 10, self.height() - 10, 10, 10)
        if hasattr(self, 'size_grip_top_right'):
            self.size_grip_top_right.setGeometry(self.width() - 10, 0, 10, 10)
        if hasattr(self, 'size_grip_bottom_left'):
            self.size_grip_bottom_left.setGeometry(0, self.height() - 10, 10, 10)
        if hasattr(self, 'size_grip_top_left'):
            self.size_grip_top_left.setGeometry(0, 0, 10, 10)
        # 延迟更新文本，确保布局已经更新
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, self.update_task_label_text)
    
    def update_task_label_text(self):
        # 确保wordWrap启用
        self.task_label.setWordWrap(True)
        
        # 计算当前窗口大小下能够显示的文本
        from PyQt5.QtCore import QRect
        fm = self.task_label.fontMetrics()
        available_width = self.task_label.width() - 10
        available_height = self.task_label.height() - 10
        
        if available_width > 0 and available_height > 0:
            # 计算完整文本需要的矩形大小（启用换行）
            text_rect = fm.boundingRect(QRect(0, 0, available_width, 0), 
                                       Qt.TextWordWrap | Qt.AlignLeft, 
                                       self.task_text)
            
            # 如果文本高度在可用范围内，直接显示完整文本
            if text_rect.height() <= available_height:
                display_text = self.task_text
            else:
                # 文本过高，需要截断并添加省略号
                # 二分查找最大可显示文本长度
                left = 0
                right = len(self.task_text)
                best_length = 0
                
                while left <= right:
                    mid = (left + right) // 2
                    test_text = self.task_text[:mid] + "..."
                    test_rect = fm.boundingRect(QRect(0, 0, available_width, 0), 
                                               Qt.TextWordWrap | Qt.AlignLeft, 
                                               test_text)
                    
                    if test_rect.height() <= available_height:
                        best_length = mid
                        left = mid + 1
                    else:
                        right = mid - 1
                
                if best_length > 0:
                    display_text = self.task_text[:best_length] + "..."
                else:
                    display_text = "..."
            
            # 设置文本
            self.task_label.setText(display_text)
            # 再次确保wordWrap启用
            self.task_label.setWordWrap(True)
        else:
            # 如果没有足够的空间，显示省略号
            self.task_label.setText("...")
            self.task_label.setWordWrap(True)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 记录拖动起始位置
            self.drag_start_pos = event.pos()
            self.drag_start_global_pos = event.globalPos()
            self.is_dragging = False  # 重置拖动标记
            
            # 处理Ctrl+点击多选
            if event.modifiers() & Qt.ControlModifier:
                self.toggle_selection()
                # 更新显示
                self.update()
            # 非Ctrl点击时不立即处理选择，在mouseRelease中根据是否拖动来决定
        event.accept()
    
    def event(self, event):
        # 处理窗口激活事件，当点击便签框时检查是否需要清除其他选择
        if event.type() == QEvent.WindowActivate:
            # 当便签框被激活时，检查鼠标位置
            from PyQt5.QtGui import QCursor
            global_pos = QCursor.pos()
            # 如果鼠标不在任何便签框内（可能是点击桌面或其他应用），清除选择
            clicked_on_any_reminder = False
            for reminder in ReminderWindow.all_reminders:
                if reminder.geometry().contains(global_pos):
                    clicked_on_any_reminder = True
                    break
            if not clicked_on_any_reminder:
                ReminderWindow.clear_all_selections()
        return super().event(event)
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_start_pos:
            # 标记正在拖动
            self.is_dragging = True
            
            # 计算移动距离
            delta = event.globalPos() - self.drag_start_global_pos
            
            # 如果当前便签被选中，移动所有选中的便签
            if self.is_selected:
                for reminder in ReminderWindow.selected_reminders:
                    new_pos = reminder.pos() + delta
                    reminder.move(new_pos)
            else:
                # 当前便签未被选中，只移动当前便签
                new_pos = self.pos() + delta
                self.move(new_pos)
            
            # 更新起始位置
            self.drag_start_global_pos = event.globalPos()
        event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 如果没有拖动（即这是一次单击），处理选择逻辑
            if not self.is_dragging and self.drag_start_pos:
                # 非Ctrl点击时，单击只选择当前便签
                if not (event.modifiers() & Qt.ControlModifier):
                    self.clear_all_selections()
                    self.add_to_selection()
                    self.update()
            
            self.drag_start_pos = None
            self.drag_start_global_pos = None
            self.is_dragging = False
    
    def toggle_selection(self):
        """切换当前提醒框的选中状态（Ctrl+点击）"""
        if self.is_selected:
            self.is_selected = False
            ReminderWindow.selected_reminders.discard(self)
        else:
            self.is_selected = True
            ReminderWindow.selected_reminders.add(self)
    
    def add_to_selection(self):
        """将当前提醒框添加到选中集合"""
        self.is_selected = True
        ReminderWindow.selected_reminders.add(self)
    
    @classmethod
    def clear_all_selections(cls):
        """清除所有选中状态"""
        for reminder in cls.selected_reminders.copy():
            reminder.is_selected = False
            reminder.update()
        cls.selected_reminders.clear()
    
    @classmethod
    def handle_global_mouse_press(cls, global_pos, source_window):
        """处理全局鼠标按下事件，判断是否点击了便签框外部"""
        # 检查点击位置是否在任何便签框内
        clicked_on_reminder = False
        for reminder in cls.all_reminders:
            if reminder.geometry().contains(global_pos):
                clicked_on_reminder = True
                break
        
        # 如果没有点击在任何便签框上，且不是从便签框发起的点击，则清除所有选择
        if not clicked_on_reminder and source_window not in cls.all_reminders:
            cls.clear_all_selections()
    
    def closeEvent(self, event):
        # 从集合中移除
        if self in ReminderWindow.all_reminders:
            ReminderWindow.all_reminders.remove(self)
        if self in ReminderWindow.selected_reminders:
            ReminderWindow.selected_reminders.remove(self)
        super().closeEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        # 按住Ctrl+双击：选取所有便签框，不弹出主界面
        if event.modifiers() & Qt.ControlModifier:
            self.select_all_reminders()
            event.accept()
            return
        
        # 普通双击：弹出主界面
        if self.parent_window:
            # 如果窗口被最小化，先恢复正常状态
            if self.parent_window.isMinimized():
                self.parent_window.showNormal()
            # 如果窗口不可见，显示窗口
            if not self.parent_window.isVisible():
                self.parent_window.show()
            # 激活窗口并置于前台
            self.parent_window.raise_()
            self.parent_window.activateWindow()
        event.accept()
    
    @classmethod
    def select_all_reminders(cls):
        """选取所有便签框"""
        for reminder in cls.all_reminders:
            reminder.is_selected = True
            cls.selected_reminders.add(reminder)
            reminder.update()
    
    def update_countdown(self):
        now = datetime.now()
        remaining_time = 0
        
        if isinstance(self.deadline, datetime):
            delta = self.deadline - now
            if delta.total_seconds() <= 0:
                remaining_time = 0
            else:
                remaining_time = delta.total_seconds()
        else:
            self.deadline -= 1
            if self.deadline <= 0:
                remaining_time = 0
            else:
                remaining_time = self.deadline
        
        # 只使用文本格式倒计时
        if remaining_time <= 0:
            text = '已截止'
            self.countdown_label.setText(text)
            # 根据文本内容动态设置最小宽度
            fm = self.countdown_label.fontMetrics()
            self.countdown_label.setMinimumWidth(fm.width(text) + 20)
            self.timer.stop()
        else:
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            text = f'{int(hours)}:{int(minutes):02d}:{int(seconds):02d}'
            self.countdown_label.setText(text)
            # 根据文本内容动态设置最小宽度
            fm = self.countdown_label.fontMetrics()
            self.countdown_label.setMinimumWidth(fm.width(text) + 20)
    
    def complete_task(self):
        if self.parent_window:
            self.parent_window.complete_task(self.task_id)
        self.close()

class MemoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('备忘录')
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QIcon(get_resource_path('icon.png')))
        
        self.settings = self.load_settings()
        self.tasks = []
        self.reminders = {}
        self.current_category = TASK_STATUS_IN_PROGRESS
        self.sort_by = None
        self.sort_order = SORT_ORDER_NONE
        
        # 应用主题
        self.apply_theme()
        
        # 应用开机自启动设置
        self.apply_auto_start()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        self.category_list = QListWidget()
        self.category_list.setMaximumWidth(150)
        self.category_list.addItem('正在进行')
        self.category_list.addItem('已完成')
        self.category_list.addItem('已取消')
        self.category_list.setCurrentRow(0)
        self.category_list.currentRowChanged.connect(self.change_category)
        self.category_list.setFocusPolicy(Qt.NoFocus)
        
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        
        self.title_layout = QHBoxLayout()
        self.sort_text_button = QPushButton('按内容排序')
        self.sort_priority_button = QPushButton('按优先级排序')
        self.sort_deadline_button = QPushButton('按截止时间排序')
        self.sort_text_button.clicked.connect(lambda: self.sort_tasks('text'))
        self.sort_priority_button.clicked.connect(lambda: self.sort_tasks('priority'))
        self.sort_deadline_button.clicked.connect(lambda: self.sort_tasks('deadline'))
        self.title_layout.addWidget(self.sort_text_button)
        self.title_layout.addWidget(self.sort_priority_button)
        self.title_layout.addWidget(self.sort_deadline_button)
        self.title_layout.addStretch()
        self.settings_button = QPushButton('设置')
        self.settings_button.clicked.connect(self.open_settings)
        self.title_layout.addWidget(self.settings_button)
        
        self.sort_buttons = {
            'text': self.sort_text_button,
            'priority': self.sort_priority_button,
            'deadline': self.sort_deadline_button
        }
        
        self.input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText('输入任务...')
        
        self.priority_combo = QComboBox()
        self.update_priority_options()
        
        self.deadline_mode = QComboBox()
        self.deadline_mode.addItem('具体时间')
        self.deadline_mode.addItem('倒计时(秒)')
        self.deadline_mode.currentIndexChanged.connect(self.update_deadline_input)
        
        self.deadline_input = QDateTimeEdit()
        self.deadline_input.setDateTime(datetime.now().replace(second=0, microsecond=0) + timedelta(hours=1))
        
        # 创建定时器，每秒更新一次默认截止时间
        self.deadline_timer = QTimer(self)
        self.deadline_timer.timeout.connect(self.update_deadline_default_time)
        self.deadline_timer.start(1000)  # 每秒更新一次
        
        self.countdown_input = QSpinBox()
        self.countdown_input.setRange(1, 86400)
        self.countdown_input.setValue(3600)
        self.countdown_input.hide()
        
        self.add_button = QPushButton('添加')
        self.add_button.clicked.connect(self.add_task)
        
        self.input_layout.addWidget(self.task_input)
        self.input_layout.addWidget(QLabel('优先级:'))
        self.input_layout.addWidget(self.priority_combo)
        self.input_layout.addWidget(QLabel('截止时间模式:'))
        self.input_layout.addWidget(self.deadline_mode)
        self.input_layout.addWidget(self.deadline_input)
        self.input_layout.addWidget(self.countdown_input)
        self.input_layout.addWidget(self.add_button)
        
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(4)
        self.task_table.setHorizontalHeaderLabels(['任务内容', '优先级', '截止时间', '操作'])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.task_table.horizontalHeader().setStretchLastSection(True)
        self.task_table.horizontalHeader().setSectionsMovable(True)
        self.task_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.task_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.task_table.setWordWrap(False)
        # 设置默认列宽
        self.task_table.setColumnWidth(0, 360)  # 任务内容栏宽度
        self.task_table.setColumnWidth(1, 90)   # 优先级栏宽度
        self.task_table.setColumnWidth(2, 140)  # 截止时间栏宽度
        self.task_table.setColumnWidth(3, 200)  # 操作栏宽度
        self.task_table.setTextElideMode(Qt.ElideRight)
        # 设置行高
        self.task_table.verticalHeader().setDefaultSectionSize(50)
        
        self.right_layout.addLayout(self.title_layout)
        self.right_layout.addLayout(self.input_layout)
        self.right_layout.addWidget(self.task_table)
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.category_list)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([150, 850])
        
        self.main_layout.addWidget(self.splitter)
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(get_resource_path('icon.png')))
        self.tray_icon.setToolTip('备忘录')
        
        self.tray_menu = QMenu(self)
        self.show_action = QAction('显示', self)
        self.show_action.triggered.connect(self.show)
        self.exit_action = QAction('退出', self)
        self.exit_action.triggered.connect(self.quit_app)
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.exit_action)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
        self.installEventFilter(self)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        self.load_tasks()
        self.show_active_reminders()
    
    def get_data_path(self, filename):
        """获取数据文件的完整路径"""
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(script_dir, filename)
    
    def load_settings(self):
        try:
            settings_path = self.get_data_path('settings.json')
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # 确保auto_start有默认值
                if 'auto_start' not in settings:
                    settings['auto_start'] = True
                return settings
        except Exception as e:
            print(f"加载设置失败: {e}")
            return {'priority_count': 5, 'auto_start': True}
    
    def save_settings(self):
        try:
            settings_path = self.get_data_path('settings.json')
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def apply_auto_start(self):
        """应用开机自启动设置"""
        try:
            import winreg
            # 获取程序路径
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller打包后的路径
                exe_path = os.path.join(sys._MEIPASS, 'memo_app.exe')
                exe_path = f'"{exe_path}"'
            else:
                # 开发环境 - 使用当前脚本路径
                script_path = os.path.abspath(sys.argv[0])
                # 获取pythonw.exe的完整路径
                python_exe = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
                # 如果pythonw.exe不存在，使用python.exe
                if not os.path.exists(python_exe):
                    python_exe = sys.executable
                
                # 如果是.py文件，使用pythonw.exe运行
                if script_path.endswith('.py'):
                    exe_path = f'"{python_exe}" "{script_path}"'
                else:
                    exe_path = f'"{script_path}"'
            
            # 打开注册表项
            key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            
            auto_start = self.settings.get('auto_start', True)
            if auto_start:
                # 添加开机自启动项
                winreg.SetValueEx(key, 'MemoApp', 0, winreg.REG_SZ, exe_path)
                print(f"已设置开机自启动: {exe_path}")
            else:
                # 删除开机自启动项
                try:
                    winreg.DeleteValue(key, 'MemoApp')
                    print("已取消开机自启动")
                except FileNotFoundError:
                    pass  # 如果键不存在，忽略错误
            
            winreg.CloseKey(key)
        except Exception as e:
            print(f"设置开机自启动失败: {e}")
    
    def apply_theme(self):
        """应用主题样式"""
        theme = self.settings.get('theme', 'light')
        
        if theme == 'dark':
            # 暗色主题
            self.setStyleSheet('''
                QMainWindow {
                    background-color: #2b2b2b;
                }
                QWidget {
                    font-family: Microsoft YaHei;
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
                QLineEdit {
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 14px;
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
                QComboBox {
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 14px;
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
                QDateTimeEdit {
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 14px;
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
                QSpinBox {
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 14px;
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
                QTableWidget {
                    border: 1px solid #555;
                    border-radius: 4px;
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
                QTableWidget::item {
                    padding: 8px;
                }
                QHeaderView::section {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 6px;
                }
                QTableCornerButton::section {
                    background-color: #2b2b2b;
                    border: 1px solid #555;
                }
                QListWidget {
                    border: 1px solid #555;
                    border-radius: 4px;
                    background-color: #3c3c3c;
                    color: #ffffff;
                    outline: none;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #444;
                    color: #ffffff;
                }
                QListWidget::item:selected {
                    background-color: #0d47a1;
                    color: #ffffff;
                }
                QListWidget::item:focus {
                    outline: none;
                    border: none;
                }
                QLabel {
                    color: #ffffff;
                }
                QGroupBox {
                    color: #ffffff;
                    border: 1px solid #555;
                }
            ''')
        else:
            # 亮色主题
            self.setStyleSheet('''
                QMainWindow {
                    background-color: #f0f0f0;
                }
                QWidget {
                    font-family: Microsoft YaHei;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
                QLineEdit {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 14px;
                }
                QComboBox {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 14px;
                }
                QDateTimeEdit {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 14px;
                }
                QSpinBox {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 14px;
                }
                QTableWidget {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: white;
                }
                QTableWidget::item {
                    padding: 8px;
                }
                QHeaderView::section {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #ddd;
                    padding: 6px;
                }
                QTableCornerButton::section {
                    background-color: #f0f0f0;
                    border: 1px solid #ddd;
                }
                QListWidget {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: white;
                    outline: none;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #f0f0f0;
                    color: black;
                }
                QListWidget::item:selected {
                    background-color: #e3f2fd;
                    color: black;
                }
                QListWidget::item:focus {
                    outline: none;
                    border: none;
                }
            ''')
    
    def load_tasks(self):
        try:
            tasks_path = self.get_data_path('tasks.json')
            with open(tasks_path, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
                for task in tasks:
                    if 'deadline' in task:
                        if task.get('mode') == 'datetime' and isinstance(task['deadline'], str):
                            try:
                                task['deadline'] = datetime.fromisoformat(task['deadline'])
                            except Exception as e:
                                print(f"解析截止时间失败: {e}")
                                task['deadline'] = datetime.now() + timedelta(hours=1)
                    if 'created_at' in task and isinstance(task['created_at'], str):
                        try:
                            task['created_at'] = datetime.fromisoformat(task['created_at'])
                        except Exception as e:
                            print(f"解析创建时间失败: {e}")
                            task['created_at'] = datetime.now()
                    if 'status' not in task:
                        task['status'] = TASK_STATUS_IN_PROGRESS
                    self.tasks.append(task)
                self.update_task_table()
        except Exception as e:
            print(f"加载任务失败: {e}")
    
    def save_tasks(self):
        try:
            tasks_path = self.get_data_path('tasks.json')
            tasks_to_save = []
            for task in self.tasks:
                task_copy = task.copy()
                if isinstance(task_copy['created_at'], datetime):
                    task_copy['created_at'] = task_copy['created_at'].isoformat()
                if task_copy.get('mode') == 'datetime' and isinstance(task_copy['deadline'], datetime):
                    task_copy['deadline'] = task_copy['deadline'].isoformat()
                tasks_to_save.append(task_copy)
            with open(tasks_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务失败: {e}")
    
    def update_priority_options(self):
        self.priority_combo.clear()
        for i in range(1, self.settings['priority_count'] + 1):
            self.priority_combo.addItem(f'优先级 {i}')
    
    def update_deadline_input(self):
        if self.deadline_mode.currentIndex() == 0:
            self.deadline_input.show()
            self.countdown_input.hide()
        else:
            self.deadline_input.hide()
            self.countdown_input.show()
    
    def update_deadline_default_time(self, force=False):
        """更新截止时间的默认值为当前时间后1小时，秒数固定为00
        
        Args:
            force: 如果为True，强制更新，不检查用户是否手动修改过
        """
        # 只有在"具体时间"模式下才更新
        if self.deadline_mode.currentIndex() != 0:
            return
        
        now = datetime.now()
        # 计算1小时后的时间，并将秒数设为00
        default_time = now + timedelta(hours=1)
        default_time = default_time.replace(second=0, microsecond=0)
        
        if force:
            # 强制更新，不检查
            self.deadline_input.setDateTime(default_time)
        else:
            # 获取当前显示的时间
            current_display_time = self.deadline_input.dateTime().toPyDateTime()
            
            # 计算当前显示时间与期望默认时间的差值（分钟）
            time_diff = abs((current_display_time - default_time).total_seconds() / 60)
            
            # 如果差值在1分钟以内，认为是默认值，需要更新
            # 如果差值超过1分钟，说明用户手动修改过，不更新
            if time_diff <= 1:
                self.deadline_input.setDateTime(default_time)
    
    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def change_category(self, row):
        if row == 0:
            self.current_category = TASK_STATUS_IN_PROGRESS
        elif row == 1:
            self.current_category = TASK_STATUS_COMPLETED
        else:
            self.current_category = TASK_STATUS_CANCELLED
        self.update_task_table()
    
    def sort_tasks(self, sort_by):
        if self.sort_by == sort_by:
            if self.sort_order == SORT_ORDER_NONE:
                self.sort_order = SORT_ORDER_ASC
            elif self.sort_order == SORT_ORDER_ASC:
                self.sort_order = SORT_ORDER_DESC
            else:
                self.sort_order = SORT_ORDER_NONE
                self.sort_by = None
        else:
            self.sort_by = sort_by
            self.sort_order = SORT_ORDER_ASC
        
        for key, button in self.sort_buttons.items():
            if key == self.sort_by:
                if self.sort_order == SORT_ORDER_ASC:
                    suffix = ' ↑'
                elif self.sort_order == SORT_ORDER_DESC:
                    suffix = ' ↓'
                else:
                    suffix = ''
                base_text = '按内容排序' if key == 'text' else '按优先级排序' if key == 'priority' else '按截止时间排序'
                button.setText(base_text + suffix)
            else:
                base_text = '按内容排序' if key == 'text' else '按优先级排序' if key == 'priority' else '按截止时间排序'
                button.setText(base_text)
        
        self.update_task_table()
    
    def update_task_table(self):
        self.task_table.setRowCount(0)
        
        filtered_tasks = [task for task in self.tasks if task['status'] == self.current_category]
        
        if self.sort_by and self.sort_order != SORT_ORDER_NONE:
            reverse = self.sort_order == SORT_ORDER_DESC
            if self.sort_by == 'text':
                filtered_tasks.sort(key=lambda x: (x['text'], x['created_at']), reverse=reverse)
            elif self.sort_by == 'priority':
                filtered_tasks.sort(key=lambda x: (x['priority'], x['created_at']), reverse=reverse)
            elif self.sort_by == 'deadline':
                # 处理不同类型的截止时间比较
                filtered_tasks.sort(key=lambda x: (
                    (x['deadline'] if isinstance(x['deadline'], datetime) else datetime.now() + timedelta(seconds=x['deadline'])),
                    x['created_at']
                ), reverse=reverse)
        
        for task in filtered_tasks:
            row = self.task_table.rowCount()
            self.task_table.insertRow(row)
            
            task_item = QTableWidgetItem(task['text'])
            task_item.setToolTip(task['text'])
            task_item.setData(Qt.DisplayRole, task['text'])
            # 设置文字大小
            font = task_item.font()
            font.setPointSize(13)
            task_item.setFont(font)
            self.task_table.setItem(row, 0, task_item)
            
            priority_item = QTableWidgetItem(f'优先级 {task["priority"]}')
            priority_item.setToolTip(f'优先级 {task["priority"]}')
            # 设置文字大小
            font = priority_item.font()
            font.setPointSize(13)
            priority_item.setFont(font)
            self.task_table.setItem(row, 1, priority_item)
            
            if task.get('mode') == 'countdown':
                hours, remainder = divmod(task['deadline'], 3600)
                minutes, seconds = divmod(remainder, 60)
                deadline_text = f'倒计时 {int(hours)}:{int(minutes):02d}:{int(seconds):02d}'
            else:
                deadline_text = task['deadline'].strftime('%Y-%m-%d %H:%M')
            deadline_item = QTableWidgetItem(deadline_text)
            deadline_item.setToolTip(deadline_text)
            # 设置文字大小
            font = deadline_item.font()
            font.setPointSize(13)
            deadline_item.setFont(font)
            self.task_table.setItem(row, 2, deadline_item)
            
            button_widget = QWidget()
            button_widget.setStyleSheet('background-color: transparent;')
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(5)
            
            if self.current_category == TASK_STATUS_IN_PROGRESS:
                complete_button = QPushButton('完成')
                complete_button.setFixedSize(80, 32)
                complete_button.setStyleSheet('''
                    QPushButton {
                        background-color: #228B22;
                        color: black;
                        border: none;
                        border-radius: 6px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: #1B6B1B;
                    }
                    QPushButton:pressed {
                        background-color: #145214;
                    }
                ''')
                complete_button.clicked.connect(lambda _, t=task: self.complete_task(t['id']))

                cancel_button = QPushButton('取消')
                cancel_button.setFixedSize(80, 32)
                cancel_button.setStyleSheet('''
                    QPushButton {
                        background-color: #FF0000;
                        color: black;
                        border: none;
                        border-radius: 6px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: #CC0000;
                    }
                    QPushButton:pressed {
                        background-color: #990000;
                    }
                ''')
                cancel_button.clicked.connect(lambda _, t=task: self.cancel_task(t['id']))

                button_layout.addWidget(complete_button)
                button_layout.addWidget(cancel_button)
            else:
                # 已完成和已取消界面的按钮
                restore_button = QPushButton('恢复')
                restore_button.setFixedSize(80, 32)
                restore_button.setStyleSheet('''
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                    QPushButton:pressed {
                        background-color: #1565C0;
                    }
                ''')
                restore_button.clicked.connect(lambda _, t=task: self.restore_task(t['id']))

                delete_button = QPushButton('删除')
                delete_button.setFixedSize(80, 32)
                delete_button.setStyleSheet('''
                    QPushButton {
                        background-color: #757575;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: #616161;
                    }
                    QPushButton:pressed {
                        background-color: #424242;
                    }
                ''')
                delete_button.clicked.connect(lambda _, t=task: self.delete_task(t['id']))
                
                button_layout.addWidget(restore_button)
                button_layout.addWidget(delete_button)
            
            self.task_table.setCellWidget(row, 3, button_widget)
    
    def add_task(self):
        task_text = self.task_input.text().strip()
        if not task_text:
            return
        
        priority = self.priority_combo.currentIndex() + 1
        
        # 生成唯一ID
        import time
        import random
        task_id = int(time.time() * 1000) + random.randint(0, 999)
        
        if self.deadline_mode.currentIndex() == 0:
            deadline = self.deadline_input.dateTime().toPyDateTime()
            task = {
                'id': task_id,
                'text': task_text,
                'priority': priority,
                'deadline': deadline,
                'created_at': datetime.now(),
                'mode': 'datetime',
                'status': TASK_STATUS_IN_PROGRESS
            }
        else:
            countdown_seconds = self.countdown_input.value()
            deadline = countdown_seconds
            task = {
                'id': task_id,
                'text': task_text,
                'priority': priority,
                'deadline': deadline,
                'created_at': datetime.now(),
                'mode': 'countdown',
                'status': TASK_STATUS_IN_PROGRESS
            }
        
        self.tasks.append(task)
        self.update_task_table()
        self.save_tasks()
        
        self.task_input.clear()
        if self.deadline_mode.currentIndex() == 0:
            self.update_deadline_default_time(force=True)
        else:
            self.countdown_input.setValue(3600)
        
        self.create_reminder(task)
    
    def create_reminder(self, task):
        reminder = ReminderWindow(task['id'], task['text'], task['priority'], task['deadline'], self)
        reminder.show()
        self.reminders[task['id']] = reminder
    
    def show_active_reminders(self):
        for task in self.tasks:
            if task['status'] == TASK_STATUS_IN_PROGRESS:
                self.create_reminder(task)
    
    def complete_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = TASK_STATUS_COMPLETED
                break
        
        if task_id in self.reminders:
            self.reminders[task_id].close()
            del self.reminders[task_id]
        
        self.update_task_table()
        self.save_tasks()
    
    def cancel_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = TASK_STATUS_CANCELLED
                break
        
        if task_id in self.reminders:
            self.reminders[task_id].close()
            del self.reminders[task_id]
        
        self.update_task_table()
        self.save_tasks()
    
    def restore_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = TASK_STATUS_IN_PROGRESS
                break
        
        self.update_task_table()
        self.save_tasks()
        
        # 为恢复的任务创建新的提醒框
        for task in self.tasks:
            if task['id'] == task_id:
                self.create_reminder(task)
                break
    
    def delete_task(self, task_id):
        # 从任务列表中删除任务
        self.tasks = [task for task in self.tasks if task['id'] != task_id]
        
        # 关闭并删除对应的提醒框
        if task_id in self.reminders:
            self.reminders[task_id].close()
            del self.reminders[task_id]
        
        self.update_task_table()
        self.save_tasks()
    
    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.Close:
            event.ignore()
            self.hide()
            return True
        return super().eventFilter(obj, event)
    
    def mousePressEvent(self, event):
        # 当点击主窗口时，检查是否点击在便签框外部
        ReminderWindow.handle_global_mouse_press(event.globalPos(), self)
        super().mousePressEvent(event)
    
    def tray_icon_activated(self, reason):
        # 双击托盘图标时只弹出主界面
        if reason == QSystemTrayIcon.DoubleClick:
            # 如果窗口被最小化，先恢复正常状态
            if self.isMinimized():
                self.showNormal()
            # 如果窗口不可见，显示窗口
            if self.isHidden():
                self.show()
            # 激活窗口并置于前台
            self.raise_()
            self.activateWindow()
    
    def quit_app(self):
        QApplication.quit()
    
    def update_reminder_formats(self):
        for task_id, reminder in list(self.reminders.items()):
            # 保存旧提醒框的位置
            old_pos = reminder.pos()
            # 关闭旧提醒框
            reminder.close()
            # 找到对应的任务
            for task in self.tasks:
                if task['id'] == task_id and task['status'] == TASK_STATUS_IN_PROGRESS:
                    # 创建新的提醒框，使用新的倒计时格式和颜色设置
                    new_reminder = ReminderWindow(task['id'], task['text'], task['priority'], task['deadline'], self)
                    # 恢复旧提醒框的位置
                    new_reminder.move(old_pos)
                    new_reminder.show()
                    self.reminders[task_id] = new_reminder
                    break

class GlobalMouseMonitor(QObject):
    """全局鼠标监视器，使用Windows钩子检测点击便签框外部的情况"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hook_id = None
        self.hook_proc = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_mouse_click)
        self.timer.start(50)  # 每50ms检查一次鼠标状态
        self.last_mouse_state = False
        self.last_click_pos = None
    
    def check_mouse_click(self):
        """通过检查鼠标状态来检测点击"""
        import ctypes
        from ctypes import wintypes
        
        # 获取当前鼠标按键状态 (VK_LBUTTON = 0x01)
        user32 = ctypes.windll.user32
        current_state = user32.GetAsyncKeyState(0x01) & 0x8000 != 0
        
        # 检测鼠标左键按下事件（从释放到按下）
        if current_state and not self.last_mouse_state:
            # 获取鼠标位置
            point = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(point))
            global_pos = QPoint(point.x, point.y)
            
            # 检查点击位置是否在任何便签框内
            clicked_on_reminder = False
            for reminder in ReminderWindow.all_reminders:
                if reminder.isVisible() and reminder.geometry().contains(global_pos):
                    clicked_on_reminder = True
                    break
            
            # 如果没有点击在任何便签框上，清除所有选择
            if not clicked_on_reminder and ReminderWindow.selected_reminders:
                ReminderWindow.clear_all_selections()
        
        self.last_mouse_state = current_state


if __name__ == '__main__':
    import ctypes
    from PyQt5.QtCore import QSharedMemory, QSystemSemaphore
    
    # 设置应用程序用户模型ID，确保任务栏显示正确的图标
    myappid = 'MemoApp.Memo.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    # 单实例运行检查
    shared_memory = QSharedMemory('MemoApp_SingleInstance')
    
    # 尝试创建共享内存
    if shared_memory.attach():
        # 如果共享内存已经存在，说明已经有实例在运行
        print("备忘录程序已经在运行中！")
        sys.exit(0)
    
    # 创建共享内存
    if not shared_memory.create(1):
        print("无法创建共享内存，程序可能已经在运行！")
        sys.exit(0)
    
    app = QApplication(sys.argv)
    app.setApplicationName('备忘录')
    app.setApplicationDisplayName('备忘录')
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口时不退出程序
    
    # 创建全局鼠标监视器
    mouse_monitor = GlobalMouseMonitor(app)
    
    window = MemoApp()
    window.show()
    sys.exit(app.exec_())

import sys,os
import win32gui
import win32con
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QPainter, QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, 
                             QCheckBox, QVBoxLayout, 
                             QPushButton, QHBoxLayout, 
                             QSlider, QLabel, QColorDialog)

class ControlPanel(QWidget):
    def __init__(self, dot):
        super().__init__()
        self.dot = dot
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("FPS固定准星")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedWidth(300)
        self.setLayout(QVBoxLayout())
        
        # 创建控件
        self.lock_checkbox = QCheckBox("锁定准星")
        self.radius_label = QLabel("准星大小:")
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setMinimum(2)
        self.radius_slider.setMaximum(20)
        self.radius_slider.setValue(self.dot.dot_radius)
        self.color_button = QPushButton("选择准星颜色")
        exit_button = QPushButton("退出程序")
        
        # 布局设置
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.color_button)
        button_layout.addStretch()
        button_layout.addWidget(exit_button)
        
        self.layout().addWidget(self.lock_checkbox)
        self.layout().addWidget(self.radius_label)
        self.layout().addWidget(self.radius_slider)
        self.layout().addLayout(button_layout)
        
        # 信号连接
        self.lock_checkbox.stateChanged.connect(self.toggle_lock)
        self.radius_slider.valueChanged.connect(self.set_dot_radius)
        self.color_button.clicked.connect(self.change_dot_color)
        exit_button.clicked.connect(self.close_application)

    def toggle_lock(self, state):
        if state == Qt.Checked:
            self.dot.lock_dot()
        else:
            self.dot.unlock_dot()

    def set_dot_radius(self, value):
        self.dot.dot_radius = value
        self.dot.setFixedSize(2 * value, 2 * value)
        self.dot.update()

    def change_dot_color(self):
        color = QColorDialog.getColor(self.dot.dot_color, self, "选择颜色")
        if color.isValid():
            self.dot.dot_color = color
            self.dot.update()

    def close_application(self):
        QApplication.instance().quit()

    def closeEvent(self, event):  # 新增关闭事件处理
        QApplication.instance().quit()

class TransparentDot(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.is_locked = False

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.dot_radius = 7
        self.dot_color = QColor(255, 0, 0, 255)
        self._drag_pos = QPoint()
        self.setFixedSize(2*self.dot_radius, 2*self.dot_radius)

    def set_window_activate(self, activatable):
        hwnd = int(self.winId())
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_style = style | win32con.WS_EX_NOACTIVATE if not activatable else style & ~win32con.WS_EX_NOACTIVATE
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
        win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                              win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.dot_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 2*self.dot_radius, 2*self.dot_radius)

    def mousePressEvent(self, event):
        if not self.is_locked and event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.pos()
            self.setCursor(Qt.BlankCursor)  # 点击时也隐藏光标

    def mouseMoveEvent(self, event):
        if not self.is_locked and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)

    def lock_dot(self):
        self.is_locked = True
        self.dot_color.setAlpha(255)
        self.set_window_activate(False)
        self.update()

    def unlock_dot(self):
        self.is_locked = False
        self.dot_color.setAlpha(255)
        self.set_window_activate(True)
        self.update()

    def enterEvent(self, event):
        self.setCursor(Qt.BlankCursor)  # 鼠标进入时隐藏光标

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)  # 鼠标离开时恢复光标

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 设置应用程序图标
    icon_path = os.path.join(os.path.dirname(__file__), 'sight.ico')  # 确保图标文件路径正确
    app.setWindowIcon(QIcon(icon_path))
    
    dot = TransparentDot()
    control_panel = ControlPanel(dot)
    
    # 由于您有两个窗口，您可能需要分别为它们设置图标
    control_panel.setWindowIcon(QIcon(icon_path))  # 如果需要为控制面板也设置图标
    
    dot.show()
    control_panel.show()
    
    sys.exit(app.exec_())
    
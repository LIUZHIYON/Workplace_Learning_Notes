"""
Median + CLAHE 低光照图像增强工具 (PyQt5)
支持中文文件名，实时预览，保存处理结果
"""

import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QSlider,
                             QFileDialog, QMessageBox, QSplitter, QGroupBox,
                             QGridLayout, QSpinBox, QDoubleSpinBox, QStatusBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont

# ──────────────────────────────────────────────
# 确保中文文件名支持
# ──────────────────────────────────────────────
import locale
locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8' if sys.platform != 'win32' else 'chs')


def np2qpixmap(img_bgr):
    """OpenCV BGR → QPixmap"""
    h, w, ch = img_bgr.shape
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    bytes_per_line = ch * w
    qt_img = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qt_img)


def process_median_clahe(img_bgr, median_ksize=5, clahe_clip=2.0, clahe_grid=8):
    """核心算法：Median → CLAHE"""
    # 1. 中值滤波去噪
    denoised = cv2.medianBlur(img_bgr, median_ksize)
    # 2. CLAHE 增强
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(clahe_grid, clahe_grid))
    l_enh = clahe.apply(l)
    result = cv2.cvtColor(cv2.merge([l_enh, a, b]), cv2.COLOR_LAB2BGR)
    return result


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_img = None
        self.result_img = None
        self.file_path = None
        self.init_ui()
        self.setWindowTitle("低光照增强工具 — Median + CLAHE")

    def init_ui(self):
        self.setMinimumSize(1200, 700)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # ── 控制面板 ──
        ctrl_group = QGroupBox("参数控制")
        ctrl_layout = QGridLayout(ctrl_group)

        # 中值滤波核大小
        ctrl_layout.addWidget(QLabel("中值滤波核大小:"), 0, 0)
        self.spin_median = QSpinBox()
        self.spin_median.setRange(3, 15)
        self.spin_median.setSingleStep(2)
        self.spin_median.setValue(5)
        self.spin_median.valueChanged.connect(self.on_param_change)
        ctrl_layout.addWidget(self.spin_median, 0, 1)

        ctrl_layout.addWidget(QLabel("（奇数，越大越平滑）"), 0, 2)

        # CLAHE clip
        ctrl_layout.addWidget(QLabel("CLAHE 对比度限制:"), 1, 0)
        self.spin_clip = QDoubleSpinBox()
        self.spin_clip.setRange(0.5, 5.0)
        self.spin_clip.setSingleStep(0.5)
        self.spin_clip.setValue(2.0)
        self.spin_clip.valueChanged.connect(self.on_param_change)
        ctrl_layout.addWidget(self.spin_clip, 1, 1)

        ctrl_layout.addWidget(QLabel("（越大对比度越强）"), 1, 2)

        # CLAHE grid
        ctrl_layout.addWidget(QLabel("CLAHE 分块大小:"), 2, 0)
        self.spin_grid = QSpinBox()
        self.spin_grid.setRange(4, 32)
        self.spin_grid.setSingleStep(2)
        self.spin_grid.setValue(8)
        self.spin_grid.valueChanged.connect(self.on_param_change)
        ctrl_layout.addWidget(self.spin_grid, 2, 1)

        ctrl_layout.addWidget(QLabel("（越小局部细节越强）"), 2, 2)

        main_layout.addWidget(ctrl_group)

        # ── 按钮栏 ──
        btn_layout = QHBoxLayout()
        self.btn_open = QPushButton("📂 打开图片")
        self.btn_open.clicked.connect(self.on_open)
        btn_layout.addWidget(self.btn_open)

        self.btn_save = QPushButton("💾 保存结果")
        self.btn_save.clicked.connect(self.on_save)
        self.btn_save.setEnabled(False)
        btn_layout.addWidget(self.btn_save)

        self.btn_reset = QPushButton("🔄 重置参数")
        self.btn_reset.clicked.connect(self.on_reset)
        btn_layout.addWidget(self.btn_reset)

        main_layout.addLayout(btn_layout)

        # ── 图片显示区 ──
        splitter = QSplitter(Qt.Horizontal)

        # 原图
        orig_widget = QWidget()
        orig_vbox = QVBoxLayout(orig_widget)
        orig_vbox.setContentsMargins(0, 0, 0, 0)
        orig_vbox.addWidget(QLabel("◀ 原始图像"))
        self.lbl_original = QLabel("点击「打开图片」加载...")
        self.lbl_original.setAlignment(Qt.AlignCenter)
        self.lbl_original.setStyleSheet("border: 1px solid #ccc; background: #f5f5f5;")
        self.lbl_original.setMinimumSize(400, 300)
        orig_vbox.addWidget(self.lbl_original)
        splitter.addWidget(orig_widget)

        # 处理后
        result_widget = QWidget()
        result_vbox = QVBoxLayout(result_widget)
        result_vbox.setContentsMargins(0, 0, 0, 0)
        result_vbox.addWidget(QLabel("▶ 增强结果"))
        self.lbl_result = QLabel("等待处理...")
        self.lbl_result.setAlignment(Qt.AlignCenter)
        self.lbl_result.setStyleSheet("border: 1px solid #4CAF50; background: #f0fff0;")
        self.lbl_result.setMinimumSize(400, 300)
        result_vbox.addWidget(self.lbl_result)
        splitter.addWidget(result_widget)

        main_layout.addWidget(splitter, stretch=1)

        # ── 状态栏 ──
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("就绪")

        # 处理防抖定时器
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self._debounce_timer.timeout.connect(self._do_process)

    # ── 槽函数 ──

    def on_open(self):
        """打开图片（支持中文路径）"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择低光照图片", "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp);;所有文件 (*.*)"
        )
        if not path:
            return

        # 用二进制读取确保中文路径没问题
        try:
            img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("无法解码图片")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法读取图片:\n{path}\n\n{str(e)}")
            return

        self.file_path = path
        self.original_img = img
        self.result_img = None

        # 显示原图
        h, w = img.shape[:2]
        pix = np2qpixmap(img)
        scaled = pix.scaled(self.lbl_original.size(), Qt.KeepAspectRatio,
                            Qt.SmoothTransformation)
        self.lbl_original.setPixmap(scaled)
        self.lbl_original.setText("")

        fname = os.path.basename(path)
        self.status.showMessage(f"已加载: {fname}  ({w}×{h})")
        self.btn_save.setEnabled(False)

        # 自动处理
        self._debounce_timer.start()

    def on_save(self):
        """保存结果（支持中文路径）"""
        if self.result_img is None:
            return

        default_name = "enhanced_" + os.path.basename(self.file_path) if self.file_path else "enhanced.jpg"
        path, _ = QFileDialog.getSaveFileName(
            self, "保存增强结果", default_name,
            "JPEG (*.jpg *.jpeg);;PNG (*.png);;BMP (*.bmp);;所有文件 (*.*)"
        )
        if not path:
            return

        try:
            # cv2.imencode + np.tofile 支持中文路径
            ext = os.path.splitext(path)[1].lower()
            if ext in ('.jpg', '.jpeg'):
                ok, buf = cv2.imencode('.jpg', self.result_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            elif ext == '.png':
                ok, buf = cv2.imencode('.png', self.result_img)
            else:
                ok, buf = cv2.imencode(ext, self.result_img)

            if not ok:
                raise ValueError("编码失败")
            with open(path, 'wb') as f:
                f.write(buf.tobytes())

            self.status.showMessage(f"已保存: {os.path.basename(path)}")
            QMessageBox.information(self, "保存成功", f"结果已保存至:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存图片:\n{str(e)}")

    def on_reset(self):
        """重置参数为默认值"""
        self.spin_median.setValue(5)
        self.spin_clip.setValue(2.0)
        self.spin_grid.setValue(8)

    def on_param_change(self):
        """参数变化 → 重新处理"""
        if self.original_img is not None:
            self._debounce_timer.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 窗口大小变化时重新缩放显示
        if self.original_img is not None:
            self._update_displays()

    def _do_process(self):
        """实际执行处理"""
        if self.original_img is None:
            return

        median_k = self.spin_median.value()
        if median_k % 2 == 0:
            median_k += 1
            self.spin_median.setValue(median_k)

        self.status.showMessage("处理中...")
        QApplication.processEvents()

        self.result_img = process_median_clahe(
            self.original_img,
            median_ksize=median_k,
            clahe_clip=self.spin_clip.value(),
            clahe_grid=self.spin_grid.value()
        )

        self._update_displays()
        self.btn_save.setEnabled(True)
        self.status.showMessage("处理完成", 3000)

    def _update_displays(self):
        """刷新显示（适应窗口）"""
        if self.original_img is not None:
            pix = np2qpixmap(self.original_img)
            scaled = pix.scaled(self.lbl_original.size(), Qt.KeepAspectRatio,
                                Qt.SmoothTransformation)
            self.lbl_original.setPixmap(scaled)

        if self.result_img is not None:
            pix = np2qpixmap(self.result_img)
            scaled = pix.scaled(self.lbl_result.size(), Qt.KeepAspectRatio,
                                Qt.SmoothTransformation)
            self.lbl_result.setPixmap(scaled)
            self.lbl_result.setText("")


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 9))

    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

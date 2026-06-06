"""
低光照增强工具 - PyQt5 图形界面
=================================
用法: python low_light_gui.py
"""

import sys
import os
import time
import cv2
import numpy as np
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSlider, QSpinBox, QDoubleSpinBox,
    QFileDialog, QLineEdit, QMessageBox, QProgressBar, QCheckBox,
    QGroupBox, QGridLayout, QFrame, QSplitter, QTabWidget, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon

# ===================== 增强方法（同 low_light_tool.py） =====================

def enhance_clahe(img, clip_limit=3.0, tile_size=8):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    l_enh = clahe.apply(l)
    enhanced = cv2.merge([l_enh, a, b])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


def enhance_clahe_stretch(img, clip_limit=2.5, tile_size=8):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    l_enh = clahe.apply(l)
    low, high = np.percentile(l_enh, [2, 98])
    l_stretched = np.clip((l_enh - low) * (255.0 / (high - low + 1e-6)), 0, 255).astype(np.uint8)
    enhanced = cv2.merge([l_stretched, a, b])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


def enhance_gamma(img, gamma=0.5):
    inv = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv * 255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(img, table)


def enhance_gamma_clahe(img, gamma=0.6, clip_limit=3.0):
    img = enhance_gamma(img, gamma)
    return enhance_clahe(img, clip_limit)


def enhance_retinex_ssr(img, sigma=80):
    img_f = np.float32(img) + 1.0
    blur = cv2.GaussianBlur(img_f, (0, 0), sigma)
    retinex = np.log(img_f) - np.log(blur)
    retinex = cv2.normalize(retinex, None, 0, 255, cv2.NORM_MINMAX)
    return np.uint8(retinex)


def enhance_retinex_msr(img, sigmas=[15, 80, 250]):
    img_f = np.float32(img) + 1.0
    retinex = np.zeros_like(img_f)
    for sigma in sigmas:
        blur = cv2.GaussianBlur(img_f, (0, 0), sigma)
        retinex += np.log(img_f) - np.log(blur)
    retinex /= len(sigmas)
    retinex = cv2.normalize(retinex, None, 0, 255, cv2.NORM_MINMAX)
    return np.uint8(retinex)


def enhance_brightness(img, low_pct=2, high_pct=98):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    low, high = np.percentile(gray, [low_pct, high_pct])
    stretched = np.clip((gray - low) * (255.0 / (high - low + 1e-6)), 0, 255).astype(np.uint8)
    return cv2.cvtColor(stretched, cv2.COLOR_GRAY2BGR)


ENHANCE_METHODS = {
    "CLAHE（推荐）":      enhance_clahe,
    "CLAHE+亮度拉伸":     enhance_clahe_stretch,
    "Gamma 校正":         enhance_gamma,
    "Gamma+CLAHE":        enhance_gamma_clahe,
    "Retinex SSR":        enhance_retinex_ssr,
    "Retinex MSR":        enhance_retinex_msr,
    "自适应亮度拉伸":     enhance_brightness,
}

# ===================== 图像显示工具 =====================

def cv2_to_qpixmap(cv_img, max_size=(800, 600)):
    """OpenCV BGR → QPixmap"""
    if len(cv_img.shape) == 2:
        h, w = cv_img.shape
        bytes_per_line = w
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
    else:
        h, w, _ = cv_img.shape
        bytes_per_line = 3 * w
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

    # 缩放显示
    scale = min(max_size[0] / w, max_size[1] / h, 1.0)
    if scale < 1.0:
        new_w, new_h = int(w * scale), int(h * scale)
        rgb = cv2.resize(rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)

    qimg = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.shape[1] * 3, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)


# ===================== 处理线程 =====================

class ProcessThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(object, object)  # (result_img, processing_time_ms)
    error = pyqtSignal(str)

    def __init__(self, img, method_name, params):
        super().__init__()
        self.img = img.copy()
        self.method_name = method_name
        self.params = params

    def run(self):
        try:
            self.log.emit(f"开始处理... 方法: {self.method_name}")
            self.progress.emit(10)

            fn = ENHANCE_METHODS.get(self.method_name)
            if fn is None:
                raise ValueError(f"未知方法: {self.method_name}")

            t0 = time.time()

            # 根据方法传参
            if self.method_name == "CLAHE（推荐）":
                result = fn(self.img, clip_limit=self.params.get("clip", 3.0))
            elif self.method_name == "CLAHE+亮度拉伸":
                result = fn(self.img, clip_limit=self.params.get("clip", 2.5))
            elif self.method_name == "Gamma 校正":
                result = fn(self.img, gamma=self.params.get("gamma", 0.5))
            elif self.method_name == "Gamma+CLAHE":
                result = fn(self.img, gamma=self.params.get("gamma", 0.6))
            elif self.method_name == "Retinex SSR":
                result = fn(self.img, sigma=self.params.get("sigma", 80))
            else:
                result = fn(self.img)

            elapsed = (time.time() - t0) * 1000

            self.progress.emit(100)
            self.log.emit(f"✅ 处理完成! 耗时: {elapsed:.1f}ms")
            self.finished.emit(result, elapsed)

        except Exception as e:
            self.error.emit(str(e))
            self.log.emit(f"❌ 错误: {e}")


# ===================== 主窗口 =====================

class LowLightApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("低光照增强工具 v1.0")
        self.setMinimumSize(1200, 750)

        self.original_img = None
        self.result_img = None
        self.current_path = None
        self.video_cap = None
        self.video_timer = None
        self.is_video = False
        self.is_processing = False

        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # === 顶部：文件选择 ===
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("选择图片或视频文件...")
        self.file_path.setReadOnly(True)
        btn_open = QPushButton("📂 打开文件")
        btn_open.setFixedWidth(120)
        btn_open.clicked.connect(self.open_file)
        btn_save = QPushButton("💾 保存结果")
        btn_save.setFixedWidth(120)
        btn_save.clicked.connect(self.save_result)
        btn_save_as = QPushButton("📝 另存为...")
        btn_save_as.setFixedWidth(120)
        btn_save_as.clicked.connect(self.save_as)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(btn_open)
        file_layout.addWidget(btn_save)
        file_layout.addWidget(btn_save_as)
        main_layout.addLayout(file_layout)

        # === 中间：图片显示 ===
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：原图
        left_group = QGroupBox("原始图像")
        left_layout = QVBoxLayout(left_group)
        self.lbl_original = QLabel("请打开文件")
        self.lbl_original.setAlignment(Qt.AlignCenter)
        self.lbl_original.setMinimumSize(400, 300)
        self.lbl_original.setStyleSheet("background: #1a1a1a; color: #888; border-radius: 6px;")
        left_layout.addWidget(self.lbl_original)
        self.lbl_original_info = QLabel("")
        self.lbl_original_info.setAlignment(Qt.AlignCenter)
        self.lbl_original_info.setStyleSheet("color: #666; font-size: 11px;")
        left_layout.addWidget(self.lbl_original_info)
        splitter.addWidget(left_group)

        # 右侧：结果
        right_group = QGroupBox("增强结果")
        right_layout = QVBoxLayout(right_group)
        self.lbl_result = QLabel("处理后可显示")
        self.lbl_result.setAlignment(Qt.AlignCenter)
        self.lbl_result.setMinimumSize(400, 300)
        self.lbl_result.setStyleSheet("background: #1a1a1a; color: #888; border-radius: 6px;")
        right_layout.addWidget(self.lbl_result)
        self.lbl_result_info = QLabel("")
        self.lbl_result_info.setAlignment(Qt.AlignCenter)
        self.lbl_result_info.setStyleSheet("color: #666; font-size: 11px;")
        right_layout.addWidget(self.lbl_result_info)
        splitter.addWidget(right_group)

        main_layout.addWidget(splitter, stretch=1)

        # === 底部：参数 + 控制 ===
        control_frame = QFrame()
        control_frame.setFrameShape(QFrame.StyledPanel)
        control_layout = QHBoxLayout(control_frame)

        # 左列：方法选择
        method_group = QGroupBox("增强方法")
        method_layout = QVBoxLayout(method_group)
        self.cmb_method = QComboBox()
        self.cmb_method.addItems(list(ENHANCE_METHODS.keys()))
        self.cmb_method.currentTextChanged.connect(self.on_method_changed)
        method_layout.addWidget(QLabel("选择方法:"))
        method_layout.addWidget(self.cmb_method)

        self.lbl_params = QLabel("参数说明: CLAHE 增强")
        self.lbl_params.setStyleSheet("color: #666; font-size: 11px;")
        method_layout.addWidget(self.lbl_params)

        # Gamma 滑块
        gamma_row = QHBoxLayout()
        gamma_row.addWidget(QLabel("Gamma:"))
        self.spin_gamma = QDoubleSpinBox()
        self.spin_gamma.setRange(0.1, 3.0)
        self.spin_gamma.setValue(0.5)
        self.spin_gamma.setSingleStep(0.1)
        gamma_row.addWidget(self.spin_gamma)
        gamma_row.addStretch()
        method_layout.addLayout(gamma_row)
        self.gamma_row_widget = gamma_row  # 便于显示/隐藏

        # CLAHE clip
        clip_row = QHBoxLayout()
        clip_row.addWidget(QLabel("CLAHE Clip:"))
        self.spin_clip = QDoubleSpinBox()
        self.spin_clip.setRange(0.5, 10.0)
        self.spin_clip.setValue(3.0)
        self.spin_clip.setSingleStep(0.5)
        clip_row.addWidget(self.spin_clip)
        clip_row.addStretch()
        method_layout.addLayout(clip_row)
        self.clip_row_widget = clip_row

        control_layout.addWidget(method_group)

        # 中列：操作按钮
        btn_group = QGroupBox("操作")
        btn_layout = QVBoxLayout(btn_group)
        self.btn_process = QPushButton("▶  开始处理")
        self.btn_process.setMinimumHeight(40)
        self.btn_process.setStyleSheet("font-size: 14px; font-weight: bold; background: #4CAF50; color: white; border-radius: 6px;")
        self.btn_process.clicked.connect(self.process_image)
        btn_layout.addWidget(self.btn_process)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        btn_layout.addWidget(self.progress)
        control_layout.addWidget(btn_group)

        # 右列：日志
        log_group = QGroupBox("日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        self.log_text.setStyleSheet("background: #1e1e1e; color: #d4d4d4; font-family: Consolas; font-size: 11px;")
        log_layout.addWidget(self.log_text)
        control_layout.addWidget(log_group, stretch=1)

        main_layout.addWidget(control_frame)

        # 初始隐藏参数行
        self.on_method_changed(self.cmb_method.currentText())

        # 状态栏
        self.statusBar().showMessage("就绪")

    # ========== 事件 ==========

    def on_method_changed(self, method):
        """切换方法时显示/隐藏对应参数"""
        has_gamma = "Gamma" in method and "CLAHE" not in method
        has_gamma_clahe = method == "Gamma+CLAHE"

        # Gamma 滑块：只有 Gamma 校正和 Gamma+CLAHE 时显示
        show_gamma = has_gamma or has_gamma_clahe
        for i in range(self.gamma_row_widget.count()):
            w = self.gamma_row_widget.itemAt(i).widget()
            if w:
                w.setVisible(show_gamma)

        # CLAHE clip 滑块
        show_clip = "CLAHE" in method
        for i in range(self.clip_row_widget.count()):
            w = self.clip_row_widget.itemAt(i).widget()
            if w:
                w.setVisible(show_clip)

        # 参数说明
        desc = {
            "CLAHE（推荐）":      "CLAHE 增强亮度通道，参数: Clip Limit",
            "CLAHE+亮度拉伸":     "CLAHE + 自适应拉伸直方图，增强对比度",
            "Gamma 校正":         "Gamma 曲线调整亮度 (gamma<1 提亮)",
            "Gamma+CLAHE":        "Gamma 提亮 → CLAHE 增强细节",
            "Retinex SSR":        "单尺度 Retinex，去光照分量",
            "Retinex MSR":        "多尺度 Retinex，效果更好",
            "自适应亮度拉伸":     "自动拉伸直方图到 [0,255]",
        }
        self.lbl_params.setText(desc.get(method, ""))

    def log(self, msg):
        self.log_text.append(msg)

    # ========== 文件操作 ==========

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片或视频",
            "",
            "图片和视频 (*.jpg *.jpeg *.png *.bmp *.tiff *.mp4 *.avi *.mov *.mkv);;"
            "图片 (*.jpg *.jpeg *.png *.bmp *.tiff);;"
            "视频 (*.mp4 *.avi *.mov *.mkv);;"
            "所有文件 (*)"
        )
        if not path:
            return

        self.current_path = path
        self.file_path.setText(path)

        ext = Path(path).suffix.lower()
        if ext in (".mp4", ".avi", ".mov", ".mkv"):
            self.load_video(path)
        else:
            self.load_image(path)

    def load_image(self, path):
        img = cv2.imread(path)
        if img is None:
            QMessageBox.warning(self, "错误", f"无法读取图片:\n{path}")
            return

        self.original_img = img
        self.result_img = None
        self.is_video = False

        # 停止视频定时器
        if self.video_timer:
            self.video_timer.stop()
            self.video_timer = None

        pix = cv2_to_qpixmap(img)
        self.lbl_original.setPixmap(pix)
        self.lbl_original.setFixedSize(pix.size())
        self.lbl_result.setText("点击「开始处理」")
        self.lbl_result_info.setText("")
        self.lbl_original_info.setText(f"{img.shape[1]}×{img.shape[0]}  |  未处理")
        self.lbl_result_info.setText("")
        self.statusBar().showMessage(f"已加载: {Path(path).name}")
        self.log(f"📷 加载图片: {Path(path).name} ({img.shape[1]}×{img.shape[0]})")
        self.btn_process.setEnabled(True)

    def load_video(self, path):
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            QMessageBox.warning(self, "错误", f"无法读取视频:\n{path}")
            return

        # 读取第一帧显示
        ret, frame = cap.read()
        cap.release()
        if not ret:
            QMessageBox.warning(self, "错误", "无法读取视频第一帧")
            return

        self.original_img = frame
        self.result_img = None
        self.is_video = True

        pix = cv2_to_qpixmap(frame)
        self.lbl_original.setPixmap(pix)
        self.lbl_original.setFixedSize(pix.size())
        self.lbl_result.setText("视频处理: 点击「开始处理」处理当前帧")
        self.lbl_original_info.setText(f"视频第一帧 {frame.shape[1]}×{frame.shape[0]}")
        self.statusBar().showMessage(f"已加载视频: {Path(path).name}")
        self.log(f"🎬 加载视频: {Path(path).name}")
        self.btn_process.setEnabled(True)

    def save_result(self):
        if self.result_img is None:
            QMessageBox.information(self, "提示", "请先处理图像")
            return

        if self.current_path is None:
            self.save_as()
            return

        # 自动生成文件名
        p = Path(self.current_path)
        method_short = self.cmb_method.currentText().split("（")[0][:8]
        save_path = p.parent / f"{p.stem}_{method_short}_enhanced{p.suffix}"
        cv2.imwrite(str(save_path), self.result_img)
        self.log(f"💾 已保存: {save_path.name}")
        self.statusBar().showMessage(f"已保存: {save_path.name}")

    def save_as(self):
        if self.result_img is None:
            QMessageBox.information(self, "提示", "请先处理图像")
            return

        default_name = "enhanced_result.jpg"
        if self.current_path:
            p = Path(self.current_path)
            default_name = f"{p.stem}_enhanced.jpg"

        path, _ = QFileDialog.getSaveFileName(
            self, "保存增强结果", default_name,
            "JPEG (*.jpg);;PNG (*.png);;BMP (*.bmp);;所有文件 (*)"
        )
        if path:
            cv2.imwrite(path, self.result_img)
            self.log(f"💾 已保存: {Path(path).name}")
            self.statusBar().showMessage(f"已保存: {Path(path).name}")

    # ========== 处理 ==========

    def process_image(self):
        if self.original_img is None:
            QMessageBox.information(self, "提示", "请先打开文件")
            return

        if self.is_processing:
            return

        self.is_processing = True
        self.btn_process.setEnabled(False)
        self.btn_process.setText("⏳ 处理中...")
        self.progress.setValue(0)
        self.lbl_result.setText("处理中...")
        self.log_text.clear()

        method = self.cmb_method.currentText()
        params = {
            "gamma": self.spin_gamma.value(),
            "clip": self.spin_clip.value(),
            "sigma": 80,
        }

        self.thread = ProcessThread(self.original_img, method, params)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.log.connect(self.log)
        self.thread.finished.connect(self.on_process_done)
        self.thread.error.connect(self.on_process_error)
        self.thread.start()

    def on_process_done(self, result, elapsed_ms):
        self.result_img = result

        pix = cv2_to_qpixmap(result)
        self.lbl_result.setPixmap(pix)
        self.lbl_result.setFixedSize(pix.size())

        info = f"{result.shape[1]}×{result.shape[0]}  |  {elapsed_ms:.0f}ms"
        self.lbl_result_info.setText(info)

        self.is_processing = False
        self.btn_process.setEnabled(True)
        self.btn_process.setText("▶  开始处理")
        self.progress.setValue(100)
        self.statusBar().showMessage(f"完成! {elapsed_ms:.0f}ms")

    def on_process_error(self, msg):
        self.is_processing = False
        self.btn_process.setEnabled(True)
        self.btn_process.setText("▶  开始处理")
        self.progress.setValue(0)
        self.lbl_result.setText(f"❌ 处理失败")
        self.statusBar().showMessage("处理失败")
        QMessageBox.warning(self, "处理错误", msg)


# ===================== 启动 =====================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LowLightApp()
    window.show()
    sys.exit(app.exec_())

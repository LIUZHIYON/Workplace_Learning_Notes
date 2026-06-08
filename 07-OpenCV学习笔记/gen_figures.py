"""
OpenCV 学习笔记 — 配图生成脚本
生成各类操作的示例对比图
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)
OUT = r"C:\Users\29503\Desktop\AI学习笔记\07-OpenCV学习笔记"


# ─── 测试图 ───
def make_test_img(noise=False):
    img = np.ones((300, 400, 3), dtype=np.uint8) * 200
    cv2.rectangle(img, (50, 50), (180, 250), (60, 80, 100), -1)
    cv2.rectangle(img, (220, 50), (350, 150), (80, 120, 160), -1)
    cv2.circle(img, (270, 220), 50, (40, 60, 140), -1)
    cv2.circle(img, (100, 100), 30, (200, 180, 50), -1)
    cv2.line(img, (200, 50), (200, 250), (0, 0, 0), 2)
    if noise:
        g = np.random.normal(0, 20, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + g, 0, 255).astype(np.uint8)
    return img


def make_gray():
    return cv2.cvtColor(make_test_img(), cv2.COLOR_BGR2GRAY)


# ─── 1. 滤波效果对比 ───
def fig_filter():
    noisy = make_test_img(noise=True)
    methods = {
        "Original (Noisy)": lambda x: x,
        "Gaussian Blur\n(5x5)": lambda x: cv2.GaussianBlur(x, (5,5), 1.5),
        "Median Blur\n(5x5)": lambda x: cv2.medianBlur(x, 5),
        "Bilateral Filter\n(d=9)": lambda x: cv2.bilateralFilter(x, 9, 50, 50),
    }
    fig, axes = plt.subplots(1, 4, figsize=(14, 4))
    axes[0].imshow(cv2.cvtColor(noisy, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original (Noisy)", fontsize=10)
    axes[0].axis('off')
    for i, (name, fn) in enumerate(methods.items()):
        if i == 0: continue
        r = fn(noisy)
        axes[i].imshow(cv2.cvtColor(r, cv2.COLOR_BGR2RGB))
        axes[i].set_title(name, fontsize=10)
        axes[i].axis('off')
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_filter.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_filter.png")


# ─── 2. 边缘检测对比 ───
def fig_edge():
    gray = make_gray()
    methods = {
        "Original": gray,
        "Sobel X": cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)),
        "Sobel Y": cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)),
        "Canny": cv2.Canny(gray, 50, 150),
    }
    fig, axes = plt.subplots(1, 4, figsize=(14, 4))
    for i, (name, r) in enumerate(methods.items()):
        axes[i].imshow(r, cmap='gray')
        axes[i].set_title(name, fontsize=10)
        axes[i].axis('off')
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_edge.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_edge.png")


# ─── 3. 阈值方法对比 ───
def fig_threshold():
    gray = make_gray()
    # 暗一些
    gray = cv2.convertScaleAbs(gray, alpha=0.6, beta=0)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    adapt = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    fig, axes = plt.subplots(1, 4, figsize=(14, 4))
    axes[0].imshow(gray, cmap='gray')
    axes[0].set_title("Original Gray", fontsize=10)
    axes[0].axis('off')
    axes[1].imshow(binary, cmap='gray')
    axes[1].set_title("Binary (127)", fontsize=10)
    axes[1].axis('off')
    axes[2].imshow(otsu, cmap='gray')
    axes[2].set_title("Otsu", fontsize=10)
    axes[2].axis('off')
    axes[3].imshow(adapt, cmap='gray')
    axes[3].set_title("Adaptive Gaussian", fontsize=10)
    axes[3].axis('off')
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_threshold.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_threshold.png")


# ─── 4. 形态学操作对比 ───
def fig_morph():
    # 二值图
    img = np.zeros((200, 300), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (120, 180), 255, -1)
    cv2.circle(img, (200, 100), 40, 255, -1)
    # 加噪声
    noise = np.random.random((200, 300))
    img[noise < 0.01] = 255
    img[noise > 0.99] = 0

    kernel = np.ones((5,5), np.uint8)
    methods = {
        "Binary\n(noisy)": img,
        "Erosion": cv2.erode(img, kernel, iterations=1),
        "Dilation": cv2.dilate(img, kernel, iterations=1),
        "Opening": cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel),
        "Closing": cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel),
        "Gradient": cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel),
    }
    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for i, (name, r) in enumerate(methods.items()):
        axes[i//3, i%3].imshow(r, cmap='gray')
        axes[i//3, i%3].set_title(name, fontsize=10)
        axes[i//3, i%3].axis('off')
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_morph.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_morph.png")


# ─── 5. 直方图与CLAHE对比 ───
def fig_hist():
    img = make_test_img()
    dark = cv2.convertScaleAbs(img, alpha=0.3, beta=10)
    gray = cv2.cvtColor(dark, cv2.COLOR_BGR2GRAY)
    eq = cv2.equalizeHist(gray)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)

    fig, axes = plt.subplots(2, 3, figsize=(12, 6))
    images = [("Dark", gray), ("HistEq", eq), ("CLAHE", clahe)]
    for i, (name, r) in enumerate(images):
        axes[0, i].imshow(r, cmap='gray')
        axes[0, i].set_title(name, fontsize=10)
        axes[0, i].axis('off')
        axes[1, i].hist(r.ravel(), 256, [0, 256], color='blue', alpha=0.7)
        axes[1, i].set_title(f"{name} Histogram", fontsize=9)
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_hist.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_hist.png")


# ─── 6. 轮廓检测 ───
def fig_contour():
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    cv2.rectangle(img, (50, 40), (180, 260), (0, 0, 0), -1)
    cv2.circle(img, (270, 160), 80, (0, 0, 0), -1)
    cv2.rectangle(img, (30, 30), (200, 280), (0, 0, 255), 2)
    cv2.circle(img, (270, 160), 80, (0, 255, 0), 2)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    canvas = np.ones_like(img) * 255
    cv2.drawContours(canvas, contours, -1, (0, 200, 0), 2)
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        cv2.putText(canvas, f"Area={int(area)}", (x, y-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 0, 0), 1)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original", fontsize=10)
    axes[0].axis('off')
    axes[1].imshow(bin_img, cmap='gray')
    axes[1].set_title("Binary", fontsize=10)
    axes[1].axis('off')
    axes[2].imshow(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    axes[2].set_title("Contours + Features", fontsize=10)
    axes[2].axis('off')
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_contour.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_contour.png")


# ─── 7. 色彩空间可视化 ───
def fig_color():
    img = make_test_img()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    axes[0,0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    axes[0,0].set_title("BGR (Original)", fontsize=10)
    axes[0,0].axis('off')
    axes[0,1].imshow(gray, cmap='gray')
    axes[0,1].set_title("GRAY", fontsize=10)
    axes[0,1].axis('off')
    axes[0,2].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    axes[0,2].set_title("(Used for processing)", fontsize=10)
    axes[0,2].axis('off')

    axes[1,0].imshow(hsv[:,:,2], cmap='gray')
    axes[1,0].set_title("HSV - V channel", fontsize=10)
    axes[1,0].axis('off')
    axes[1,1].imshow(lab[:,:,0], cmap='gray')
    axes[1,1].set_title("LAB - L channel", fontsize=10)
    axes[1,1].axis('off')

    # 颜色条
    axes[1,2].axis('off')
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_colorspace.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_colorspace.png")


# ─── 8. 几何变换 ───
def fig_geo():
    img = make_test_img()
    h, w = img.shape[:2]
    # 缩放
    small = cv2.resize(img, (w//2, h//2))
    # 旋转
    M = cv2.getRotationMatrix2D((w//2, h//2), 30, 1.0)
    rot = cv2.warpAffine(img, M, (w, h))
    # 仿射
    pts1 = np.float32([[50,50],[200,50],[50,200]])
    pts2 = np.float32([[10,100],[200,50],[100,250]])
    M2 = cv2.getAffineTransform(pts1, pts2)
    aff = cv2.warpAffine(img, M2, (w, h))
    # 透视
    pts3 = np.float32([[0,0],[w-1,0],[0,h-1],[w-1,h-1]])
    pts4 = np.float32([[50,20],[w-30,10],[20,h-20],[w-10,h-10]])
    M3 = cv2.getPerspectiveTransform(pts3, pts4)
    per = cv2.warpPerspective(img, M3, (w, h))

    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    titles = ["Original", "Resize (0.5x)", "Rotate 30°",
              "Affine Transform", "Perspective", "Flip"]
    imgs = [img, small, rot, aff, per, cv2.flip(img, 1)]
    for i, (t, im) in enumerate(zip(titles, imgs)):
        axes[i//3, i%3].imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
        axes[i//3, i%3].set_title(t, fontsize=10)
        axes[i//3, i%3].axis('off')
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_geo.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_geo.png")


# ─── 9. 图像金字塔 ───
def fig_pyramid():
    img = make_test_img()
    g1 = cv2.pyrDown(img)
    g2 = cv2.pyrDown(g1)
    l1 = cv2.pyrUp(g1)
    fig, axes = plt.subplots(1, 4, figsize=(14, 4))
    axes[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original", fontsize=10)
    axes[0].axis('off')
    axes[1].imshow(cv2.cvtColor(g1, cv2.COLOR_BGR2RGB))
    axes[1].set_title("pyrDown (x1/2)", fontsize=10)
    axes[1].axis('off')
    axes[2].imshow(cv2.cvtColor(g2, cv2.COLOR_BGR2RGB))
    axes[2].set_title("pyrDown (x1/4)", fontsize=10)
    axes[2].axis('off')
    axes[3].imshow(cv2.cvtColor(l1, cv2.COLOR_BGR2RGB))
    axes[3].set_title("pyrUp (back)", fontsize=10)
    axes[3].axis('off')
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_pyramid.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_pyramid.png")


# ─── 10. 低光照增强总结图 ───
def fig_lowlight():
    img = make_test_img()
    dark = cv2.convertScaleAbs(img, alpha=0.3, beta=0)
    clahe_img = cv2.createCLAHE(clipLimit=2.0).apply(
        cv2.cvtColor(dark, cv2.COLOR_BGR2LAB)[:,:,0])
    gamma = np.array([(i/255)**(1/1.5)*255 for i in range(256)], dtype=np.uint8)
    gamma_img = cv2.LUT(dark, gamma)

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes[0,0].imshow(cv2.cvtColor(dark, cv2.COLOR_BGR2RGB))
    axes[0,0].set_title("Low Light Original", fontsize=10)
    axes[0,0].axis('off')
    lab = cv2.cvtColor(dark, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l2 = cv2.createCLAHE(clipLimit=2.0).apply(l)
    clahe_full = cv2.cvtColor(cv2.merge([l2, a, b]), cv2.COLOR_LAB2BGR)
    axes[0,1].imshow(cv2.cvtColor(clahe_full, cv2.COLOR_BGR2RGB))
    axes[0,1].set_title("CLAHE Enhanced", fontsize=10)
    axes[0,1].axis('off')
    axes[1,0].imshow(cv2.cvtColor(gamma_img, cv2.COLOR_BGR2RGB))
    axes[1,0].set_title("Gamma Correction", fontsize=10)
    axes[1,0].axis('off')
    denoised = cv2.bilateralFilter(dark, 9, 50, 50)
    lab2 = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l3, a3, b3 = cv2.split(lab2)
    l3 = cv2.createCLAHE(clipLimit=2.0).apply(l3)
    full = cv2.cvtColor(cv2.merge([l3, a3, b3]), cv2.COLOR_LAB2BGR)
    axes[1,1].imshow(cv2.cvtColor(full, cv2.COLOR_BGR2RGB))
    axes[1,1].set_title("Bilateral + CLAHE\n(Industry Best)", fontsize=10)
    axes[1,1].axis('off')
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_lowlight.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_lowlight.png")


# ─── 11. DNN 模块示意图 ───
def fig_dnn():
    # 画一个简单的 DNN 流程 + OpenCV logo
    fig, ax = plt.subplots(1, 1, figsize=(10, 3))
    ax.text(0.1, 0.5, "Image Input", fontsize=12, ha='center', va='center',
            bbox=dict(boxstyle="round", fc="lightblue"))
    ax.annotate('', xy=(0.25, 0.5), xytext=(0.18, 0.5),
                arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(0.35, 0.5, "cv2.dnn.blobFromImage()", fontsize=12, ha='center', va='center',
            bbox=dict(boxstyle="round", fc="lightyellow"))
    ax.annotate('', xy=(0.55, 0.5), xytext=(0.48, 0.5),
                arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(0.65, 0.5, "setInput()\nforward()", fontsize=12, ha='center', va='center',
            bbox=dict(boxstyle="round", fc="lightgreen"))
    ax.annotate('', xy=(0.82, 0.5), xytext=(0.78, 0.5),
                arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(0.92, 0.5, "Result", fontsize=12, ha='center', va='center',
            bbox=dict(boxstyle="round", fc="salmon"))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title("OpenCV DNN Module Inference Pipeline", fontsize=12)
    plt.savefig(f"{OUT}\\fig_dnn.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_dnn.png")


# ─── Main ───
print("Generating figures for OpenCV learning notes...\n")
fig_filter()
fig_edge()
fig_threshold()
fig_morph()
fig_hist()
fig_contour()
fig_color()
fig_geo()
fig_pyramid()
fig_lowlight()
fig_dnn()
print("\nDone! All figures saved to:", OUT)

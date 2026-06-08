"""
OpenCV 低光照图像增强方法对比
生成合成低光照图像并应用多种增强方法
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)

OUTPUT_DIR = r"C:\Users\29503\Desktop\AI学习笔记\08-OpenCV低光照处理方法"

# ============================================================
# 1. 构造低光照测试图像（合成 + 真实感）
# ============================================================
def create_low_light_scene():
    """合成一张暗光场景，包含物体、渐变、纹理"""
    h, w = 480, 640
    img = np.ones((h, w, 3), dtype=np.uint8) * 255

    # 背景渐变（暗室/黄昏）
    for y in range(h):
        v = int(80 - 50 * (y / h))  # 顶部稍微亮一点点，整体很暗
        img[y, :] = (v, v, max(0, v - 10))

    # 窗户区域（来自外界的光）—— 矩形亮斑
    cv2.rectangle(img, (200, 80), (440, 280), (140, 160, 180), -1)
    cv2.rectangle(img, (210, 90), (240, 150), (200, 220, 240), -1)
    cv2.rectangle(img, (260, 90), (290, 150), (200, 220, 240), -1)
    cv2.rectangle(img, (310, 90), (340, 150), (200, 220, 240), -1)
    cv2.rectangle(img, (360, 90), (390, 150), (200, 220, 240), -1)
    cv2.rectangle(img, (400, 90), (430, 150), (200, 220, 240), -1)

    # 桌子（暗色长方形）
    cv2.rectangle(img, (50, 320), (590, 400), (35, 30, 25), -1)

    # 桌上的物体——杯子、书
    cv2.ellipse(img, (200, 340), (30, 25), 0, 0, 360, (70, 65, 60), -1)
    cv2.ellipse(img, (200, 320), (28, 8), 0, 0, 360, (120, 110, 100), -1)
    cv2.rectangle(img, (350, 330), (430, 390), (55, 50, 45), -1)
    cv2.rectangle(img, (355, 335), (425, 385), (80, 75, 65), -1)

    # 墙上的画框
    cv2.rectangle(img, (70, 150), (170, 250), (45, 40, 35), -1)
    cv2.rectangle(img, (80, 160), (160, 240), (90, 70, 50), -1)

    # 灯（微弱光源）
    cx, cy = 500, 120
    cv2.circle(img, (cx, cy), 15, (180, 170, 100), -1)
    # 光晕
    for r in range(20, 60, 5):
        alpha = max(0, 1 - r / 60)
        overlay = img.copy()
        cv2.circle(overlay, (cx, cy), r, (180, 160, 80), -1)
        img = cv2.addWeighted(overlay, alpha * 0.15, img, 1 - alpha * 0.15, 0)

    # 添加高斯噪声模拟暗光传感器噪声
    noise = np.random.normal(0, 8, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # 整体压暗，模拟低光照
    img = cv2.convertScaleAbs(img, alpha=0.5, beta=-10)
    img = np.clip(img.astype(np.int16), 0, 255).astype(np.uint8)

    return img


def create_low_light_portrait():
    """合成一张暗光人像风格（简化版：人脸+背景）"""
    h, w = 480, 640
    img = np.ones((h, w, 3), dtype=np.uint8) * 20

    # 肤色椭圆（人脸）
    face_center = (320, 220)
    face_axes = (90, 110)
    face = np.zeros((h, w, 3), dtype=np.uint8)
    cv2.ellipse(face, face_center, face_axes, 0, 0, 360, (80, 60, 50), -1)
    # 暗光下肤色偏暗黄
    img = cv2.addWeighted(img, 0.3, face, 0.7, 0)

    # 眼睛
    cv2.circle(img, (290, 200), 8, (15, 10, 10), -1)
    cv2.circle(img, (350, 200), 8, (15, 10, 10), -1)
    cv2.circle(img, (290, 200), 3, (40, 35, 30), -1)
    cv2.circle(img, (350, 200), 3, (40, 35, 30), -1)

    # 头发深色区域
    cv2.ellipse(img, (320, 130), (100, 50), 0, 0, 360, (10, 8, 8), -1)

    # 加噪声
    noise = np.random.normal(0, 6, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return img


# ============================================================
# 2. 低光照增强方法
# ============================================================

def method_hist_equal(img):
    """直方图均衡化（仅对亮度通道有效）"""
    if len(img.shape) == 3:
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        y_eq = cv2.equalizeHist(y)
        eq = cv2.merge([y_eq, cr, cb])
        return cv2.cvtColor(eq, cv2.COLOR_YCrCb2BGR)
    else:
        return cv2.equalizeHist(img)


def method_clahe(img, clip=2.0, grid=(8, 8)):
    """限制对比度自适应直方图均衡化 (CLAHE)"""
    if len(img.shape) == 3:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=grid)
        l_clahe = clahe.apply(l)
        lab_clahe = cv2.merge([l_clahe, a, b])
        return cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)
    else:
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=grid)
        return clahe.apply(img)


def method_gamma(img, gamma=1.5):
    """伽马校正（gamma > 1 变亮）"""
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(img, table)


def method_log_transform(img):
    """对数变换（拉伸暗部细节）"""
    normalized = img.astype(np.float32) / 255.0
    c = 1.0
    log_img = c * np.log(1 + normalized)
    log_img = np.clip(log_img * 255, 0, 255).astype(np.uint8)
    return log_img


def method_contrast_stretch(img, low=5, high=95):
    """对比度拉伸（线性拉伸）"""
    if len(img.shape) == 3:
        channels = cv2.split(img)
        stretched = []
        for ch in channels:
            p_low = np.percentile(ch, low)
            p_high = np.percentile(ch, high)
            stretched_ch = np.clip((ch.astype(np.float32) - p_low) * (255.0 / (p_high - p_low + 1e-6)), 0, 255).astype(np.uint8)
            stretched.append(stretched_ch)
        return cv2.merge(stretched)
    else:
        p_low = np.percentile(img, low)
        p_high = np.percentile(img, high)
        return np.clip((img.astype(np.float32) - p_low) * (255.0 / (p_high - p_low + 1e-6)), 0, 255).astype(np.uint8)


def method_retinex_single(img, sigma=80):
    """单尺度 Retinex (SSR) -- 模拟光照补偿"""
    img_float = img.astype(np.float32) + 1.0
    if len(img.shape) == 3:
        result = np.zeros_like(img_float)
        for i in range(3):
            blurred = cv2.GaussianBlur(img_float[:, :, i], (0, 0), sigma)
            log_img = np.log(img_float[:, :, i])
            log_blurred = np.log(blurred)
            result[:, :, i] = log_img - log_blurred
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX)
        return result.astype(np.uint8)
    else:
        blurred = cv2.GaussianBlur(img_float, (0, 0), sigma)
        log_img = np.log(img_float)
        log_blurred = np.log(blurred)
        result = log_img - log_blurred
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX)
        return result.astype(np.uint8)


def method_multi_scale_retinex(img, sigmas=(15, 80, 250)):
    """多尺度 Retinex (MSR)"""
    img_float = img.astype(np.float32) + 1.0
    if len(img.shape) == 3:
        result = np.zeros_like(img_float, dtype=np.float32)
        for sigma in sigmas:
            for i in range(3):
                blurred = cv2.GaussianBlur(img_float[:, :, i], (0, 0), sigma)
                log_img = np.log(img_float[:, :, i])
                log_blurred = np.log(blurred)
                result[:, :, i] += (log_img - log_blurred) / len(sigmas)
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX)
        return result.astype(np.uint8)
    else:
        result = np.zeros_like(img_float, dtype=np.float32)
        for sigma in sigmas:
            blurred = cv2.GaussianBlur(img_float, (0, 0), sigma)
            result += (np.log(img_float) - np.log(blurred)) / len(sigmas)
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX)
        return result.astype(np.uint8)


def method_bilateral_filter(img, d=9, sigma_color=75, sigma_space=75):
    """双边滤波保边去噪 + 亮度增强"""
    if len(img.shape) == 3:
        filtered = cv2.bilateralFilter(img, d, sigma_color, sigma_space)
        brightened = cv2.convertScaleAbs(filtered, alpha=1.3, beta=20)
        return brightened
    else:
        filtered = cv2.bilateralFilter(img, d, sigma_color, sigma_space)
        return cv2.convertScaleAbs(filtered, alpha=1.3, beta=20)


# ============================================================
# 3. 组合方法
# ============================================================

def method_gamma_clahe(img, gamma=1.8, clip=2.5):
    """伽马校正 + CLAHE"""
    g = method_gamma(img, gamma)
    return method_clahe(g, clip=clip)


def method_stretch_clahe(img):
    """对比度拉伸 + CLAHE"""
    s = method_contrast_stretch(img)
    return method_clahe(s, clip=2.0)


def method_retinex_clahe(img):
    """MSR + CLAHE"""
    msr = method_multi_scale_retinex(img)
    return method_clahe(msr, clip=2.0)


def method_full_pipeline(img):
    """完整流程：MSR -> 对比度拉伸 -> CLAHE -> 伽马校正"""
    r = method_multi_scale_retinex(img)
    s = method_contrast_stretch(r)
    c = method_clahe(s, clip=2.5)
    g = method_gamma(c, gamma=1.2)
    return g


# ============================================================
# 4. 生成对比图
# ============================================================

def make_comparison_grid(original, methods_dict, title, filename):
    """生成单方法对比网格图"""
    n = len(methods_dict)
    cols = (n + 1) // 2 + 1
    fig, axes = plt.subplots(2, cols,
                             figsize=(5 * cols, 11),
                             gridspec_kw={'hspace': 0.35, 'wspace': 0.1})
    axes = axes.flatten()

    axes[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original (Low Light)", fontsize=11, fontweight='bold')
    axes[0].axis('off')

    for i, (name, func) in enumerate(methods_dict.items()):
        result = func(original)
        axes[i + 1].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        axes[i + 1].set_title(name, fontsize=11, fontweight='bold')
        axes[i + 1].axis('off')

    for j in range(len(methods_dict) + 1, len(axes)):
        axes[j].axis('off')

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.subplots_adjust(top=0.92)
    path = f"{OUTPUT_DIR}\\{filename}"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Saved: {filename}")


def make_combined_comparison(original, combined_dict, title, filename):
    """生成组合方法对比图"""
    n = len(combined_dict)
    cols = (n + 1) // 2 + 1
    fig, axes = plt.subplots(2, cols,
                             figsize=(5 * cols, 11),
                             gridspec_kw={'hspace': 0.40, 'wspace': 0.1})
    axes = axes.flatten()

    axes[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original (Low Light)", fontsize=11, fontweight='bold')
    axes[0].axis('off')

    for i, (name, func) in enumerate(combined_dict.items()):
        result = func(original)
        axes[i + 1].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        axes[i + 1].set_title(name, fontsize=11, fontweight='bold')
        axes[i + 1].axis('off')

    for j in range(len(combined_dict) + 1, len(axes)):
        axes[j].axis('off')

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.subplots_adjust(top=0.92)
    path = f"{OUTPUT_DIR}\\{filename}"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Saved: {filename}")


def make_histogram_comparison(original, methods_dict, title, filename):
    """生成直方图对比"""
    n = len(methods_dict) + 1
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))

    gray_orig = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    axes[0].hist(gray_orig.ravel(), 256, [0, 256], color='gray', alpha=0.7)
    axes[0].set_title("Original Histogram", fontsize=10)
    axes[0].set_xlim([0, 256])

    for i, (name, func) in enumerate(methods_dict.items()):
        result = func(original)
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        axes[i + 1].hist(gray.ravel(), 256, [0, 256], color='blue', alpha=0.7)
        axes[i + 1].set_title(f"{name}\nHistogram", fontsize=10)
        axes[i + 1].set_xlim([0, 256])

    plt.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = f"{OUTPUT_DIR}\\{filename}"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Saved: {filename}")


# ============================================================
# 5. 主流程
# ============================================================

print("=" * 60)
print("OpenCV low-light image enhancement - comparison generator")
print("=" * 60)

# 生成测试图像
print("\n[1/4] Generating test images...")
scene = create_low_light_scene()
portrait = create_low_light_portrait()
# Use plt.imsave for paths with Chinese characters (cv2.imwrite fails on some Windows builds)
plt.imsave(f"{OUTPUT_DIR}\\test_scene_lowlight.png", cv2.cvtColor(scene, cv2.COLOR_BGR2RGB))
plt.imsave(f"{OUTPUT_DIR}\\test_portrait_lowlight.png", cv2.cvtColor(portrait, cv2.COLOR_BGR2RGB))
print("  [OK] test_scene_lowlight.png")
print("  [OK] test_portrait_lowlight.png")

# ---- Single method comparison ----
print("\n[2/4] Single method comparison (scene)...")
single_methods = {
    "HistEq": method_hist_equal,
    "CLAHE": lambda x: method_clahe(x, clip=2.0),
    "Gamma=1.8": lambda x: method_gamma(x, 1.8),
    "Log Transform": method_log_transform,
    "Contrast Stretch": method_contrast_stretch,
    "SSR": lambda x: method_retinex_single(x, 80),
    "MSR": method_multi_scale_retinex,
    "Bilateral + Brighten": method_bilateral_filter,
}
make_comparison_grid(scene, single_methods,
    "OpenCV Low-Light Enhancement Methods - Scene",
    "comparison_single_scene.png")

print("\n[3/4] Single method comparison (portrait)...")
make_comparison_grid(portrait, single_methods,
    "OpenCV Low-Light Enhancement Methods - Portrait",
    "comparison_single_portrait.png")

# ---- Histogram comparison ----
print("\n  -> Generating histogram comparison...")
hist_methods = {
    "HistEq": method_hist_equal,
    "CLAHE": lambda x: method_clahe(x, clip=2.0),
    "Gamma=1.8": lambda x: method_gamma(x, 1.8),
    "Stretch": method_contrast_stretch,
    "MSR": method_multi_scale_retinex,
}
make_histogram_comparison(scene, hist_methods,
    "Histogram Comparison - Before & After Enhancement",
    "histogram_comparison.png")

# ---- Combined methods ----
print("\n[4/4] Combined method comparison...")
combined_methods = {
    "Gamma + CLAHE": method_gamma_clahe,
    "Stretch + CLAHE": method_stretch_clahe,
    "MSR + CLAHE": method_retinex_clahe,
    "Full Pipeline\n(MSR+Stretch\n+CLAHE+Gamma)": method_full_pipeline,
}
make_combined_comparison(scene, combined_methods,
    "OpenCV Combined Enhancement Methods - Scene",
    "comparison_combined_scene.png")

make_combined_comparison(portrait, combined_methods,
    "OpenCV Combined Enhancement Methods - Portrait",
    "comparison_combined_portrait.png")

print("\n" + "=" * 60)
print("DONE! All comparison images saved to: " + OUTPUT_DIR)
print("=" * 60)

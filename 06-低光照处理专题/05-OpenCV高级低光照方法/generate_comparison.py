"""
OpenCV 高级低光照图像增强方法对比
涵盖 xphoto、ximgproc、photo 等扩展模块中的高级方法
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

np.random.seed(42)

OUTPUT_DIR = r"C:\Users\29503\Desktop\AI学习笔记\06-低光照处理专题\05-OpenCV高级低光照方法"


# ============================================================
# 1. 构造测试图像
# ============================================================

def add_noise(img, sigma=8):
    noise = np.random.normal(0, sigma, img.shape).astype(np.int16)
    return np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)


def create_low_light_scene():
    """合成暗光场景图——含窗户、桌子、物体、墙画、灯"""
    h, w = 480, 640
    img = np.ones((h, w, 3), dtype=np.uint8) * 255
    for y in range(h):
        v = int(80 - 50 * (y / h))
        img[y, :] = (v, v, max(0, v - 10))
    # 窗户
    cv2.rectangle(img, (200, 80), (440, 280), (140, 160, 180), -1)
    for x in range(210, 420, 40):
        cv2.rectangle(img, (x, 90), (x + 20, 150), (200, 220, 240), -1)
    # 桌子
    cv2.rectangle(img, (50, 320), (590, 400), (35, 30, 25), -1)
    # 桌上物体
    cv2.ellipse(img, (200, 340), (30, 25), 0, 0, 360, (70, 65, 60), -1)
    cv2.ellipse(img, (200, 320), (28, 8), 0, 0, 360, (120, 110, 100), -1)
    cv2.rectangle(img, (350, 330), (430, 390), (55, 50, 45), -1)
    cv2.rectangle(img, (355, 335), (425, 385), (80, 75, 65), -1)
    # 墙上画框
    cv2.rectangle(img, (70, 150), (170, 250), (45, 40, 35), -1)
    cv2.rectangle(img, (80, 160), (160, 240), (90, 70, 50), -1)
    # 灯
    cv2.circle(img, (500, 120), 15, (180, 170, 100), -1)
    for r in range(20, 60, 5):
        overlay = img.copy()
        cv2.circle(overlay, (500, 120), r, (180, 160, 80), -1)
        alpha = max(0, 1 - r / 60) * 0.15
        img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
    # 噪声 + 压暗
    img = add_noise(img, sigma=10)
    img = cv2.convertScaleAbs(img, alpha=0.45, beta=-12)
    img = np.clip(img, 0, 255).astype(np.uint8)
    return img


def create_low_light_portrait():
    """合成暗光人像风格图"""
    h, w = 480, 640
    img = np.ones((h, w, 3), dtype=np.uint8) * 20
    cv2.ellipse(img, (320, 220), (90, 110), 0, 0, 360, (75, 55, 45), -1)
    cv2.circle(img, (290, 200), 8, (15, 10, 10), -1)
    cv2.circle(img, (350, 200), 8, (15, 10, 10), -1)
    cv2.circle(img, (290, 200), 3, (40, 35, 30), -1)
    cv2.circle(img, (350, 200), 3, (40, 35, 30), -1)
    cv2.ellipse(img, (320, 130), (100, 50), 0, 0, 360, (10, 8, 8), -1)
    img = add_noise(img, sigma=8)
    return img


def create_extreme_low_light():
    """合成极端暗光场景"""
    h, w = 480, 640
    img = np.ones((h, w, 3), dtype=np.uint8) * 5
    cv2.rectangle(img, (100, 200), (300, 400), (12, 10, 8), -1)
    cv2.circle(img, (450, 300), 80, (10, 8, 12), -1)
    cv2.ellipse(img, (150, 150), (60, 40), 0, 0, 360, (8, 10, 9), -1)
    cv2.circle(img, (500, 100), 20, (25, 22, 18), -1)
    for r in range(25, 80, 10):
        overlay = img.copy()
        cv2.circle(overlay, (500, 100), r, (20, 18, 14), -1)
        img = cv2.addWeighted(overlay, 0.08, img, 0.92, 0)
    img = add_noise(img, sigma=12)
    img = np.clip(img, 0, 255).astype(np.uint8)
    return img


# ============================================================
# 2. 方法实现
# ============================================================

# --- 基准方法 ---

def method_clahe(img, clip=2.0):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8)).apply(l)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)


def method_gamma(img, gamma=1.8):
    table = np.array([(i / 255.0) ** (1.0 / gamma) * 255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(img, table)


def method_msr(img):
    img_f = img.astype(np.float32) + 1.0
    result = np.zeros_like(img_f, dtype=np.float32)
    for sigma in [15, 80, 250]:
        for i in range(3):
            blurred = cv2.GaussianBlur(img_f[:, :, i], (0, 0), sigma)
            result[:, :, i] += (np.log(img_f[:, :, i]) - np.log(blurred)) / 3
    return cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


# --- xphoto 模块方法 ---

def method_dct_denoising(img, sigma=15):
    """DCT 去噪 — 基于离散余弦变换的频域降噪"""
    b, g, r = cv2.split(img)
    b_dst = np.zeros_like(b); g_dst = np.zeros_like(g); r_dst = np.zeros_like(r)
    cv2.xphoto.dctDenoising(b, b_dst, sigma)
    cv2.xphoto.dctDenoising(g, g_dst, sigma)
    cv2.xphoto.dctDenoising(r, r_dst, sigma)
    return cv2.merge([b_dst, g_dst, r_dst])


def method_simple_wb(img):
    """简单白平衡 — 自动颜色校正"""
    wb = cv2.xphoto.createSimpleWB()
    return wb.balanceWhite(img)


def method_learning_wb(img):
    """学习型白平衡 — 基于ML的色彩校正"""
    wb = cv2.xphoto.createLearningBasedWB()
    return wb.balanceWhite(img)


# --- photo 模块方法 ---

def method_edge_preserving(img):
    """边缘保持滤波 — 去噪同时保留边缘"""
    return cv2.edgePreservingFilter(img, flags=1, sigma_s=60, sigma_r=0.4)


def method_detail_enhance(img):
    """细节增强 — 增强纹理和局部对比度"""
    return cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)


def method_illumination_change(img):
    """光照变化校正 — 模拟调整场景光照"""
    mask = np.ones(img.shape[:2], dtype=np.uint8)
    return cv2.illuminationChange(img, mask, alpha=1.8, beta=0.2)


# --- ximgproc 模块方法 ---

def method_guided_filter(img, radius=8, eps=0.01):
    """导向滤波 — 保边平滑降噪"""
    eps_val = float(eps ** 2 * 255 ** 2)
    gf = cv2.ximgproc.createGuidedFilter(img, radius, eps_val)
    return gf.filter(img)


def method_static_guided_filter(img, radius=8, eps=0.1):
    """导向滤波（静态） — 一步调用"""
    return cv2.ximgproc.guidedFilter(img, img, radius, eps)


def method_l0_smooth(img, lambda_=0.02):
    """L0 梯度最小化平滑 — 保边缘极致平滑"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l_f = l.astype(np.float32) / 255.0
    l_s = cv2.ximgproc.l0Smooth(l_f, lambda_=lambda_, kappa=2.0)
    l_s = np.clip(l_s * 255, 0, 255).astype(np.uint8)
    return cv2.cvtColor(cv2.merge([l_s, a, b]), cv2.COLOR_LAB2BGR)


def method_rolling_guidance(img):
    """滚动引导滤波 — 多尺度结构化平滑"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l_f = l.astype(np.float32) / 255.0
    l_rg = cv2.ximgproc.rollingGuidanceFilter(l_f, d=10, sigmaColor=25, sigmaSpace=3, numOfIter=4)
    l_rg = np.clip(l_rg * 255, 0, 255).astype(np.uint8)
    return cv2.cvtColor(cv2.merge([l_rg, a, b]), cv2.COLOR_LAB2BGR)


def method_fast_global_smoother(img):
    """快速全局平滑 — 全局正则化快速平滑"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l_dst = np.zeros_like(l, dtype=np.uint8)
    cv2.ximgproc.fastGlobalSmootherFilter(l, l, 100, 10, l_dst, 0.25, 3)
    return cv2.cvtColor(cv2.merge([l_dst, a, b]), cv2.COLOR_LAB2BGR)


def method_adaptive_manifold(img):
    """自适应流形滤波 — 高维空间的保边滤波"""
    am = cv2.ximgproc.AdaptiveManifoldFilter_create()
    return am.filter(img)


def method_bilateral_texture(img):
    """双边纹理滤波 — 去除纹理保留结构"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l_f = l.astype(np.float32) / 255.0
    l_bt = cv2.ximgproc.bilateralTextureFilter(l_f, None, 6, 3, 0.2, 0.8)
    l_bt = np.clip(l_bt * 255, 0, 255).astype(np.uint8)
    return cv2.cvtColor(cv2.merge([l_bt, a, b]), cv2.COLOR_LAB2BGR)


def method_joint_bilateral(img):
    """联合双边滤波 — 用引导图的结构信息做保边平滑"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    b, g, r = cv2.split(img)
    b_jb = cv2.ximgproc.jointBilateralFilter(gray, b, 9, 30, 30)
    g_jb = cv2.ximgproc.jointBilateralFilter(gray, g, 9, 30, 30)
    r_jb = cv2.ximgproc.jointBilateralFilter(gray, r, 9, 30, 30)
    return cv2.merge([b_jb, g_jb, r_jb])


def method_domain_transform(img):
    """域变换滤波 — 保边平滑"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    b, g, r = cv2.split(img)
    b_dt = cv2.ximgproc.dtFilter(gray, b, 10, 10)
    g_dt = cv2.ximgproc.dtFilter(gray, g, 10, 10)
    r_dt = cv2.ximgproc.dtFilter(gray, r, 10, 10)
    return cv2.merge([b_dt, g_dt, r_dt])


# --- 高级组合管线 ---

def pipeline_dct_gamma_clahe(img):
    """管线A: DCT去噪 → Gamma 提亮 → CLAHE 增强"""
    d = method_dct_denoising(img, sigma=12)
    g = method_gamma(d, gamma=1.8)
    return method_clahe(g, clip=2.0)


def pipeline_guided_gamma_clahe(img):
    """管线B: GuidedFilter去噪 → Gamma → CLAHE"""
    gf = method_guided_filter(img, radius=8, eps=0.02)
    g = method_gamma(gf, gamma=1.8)
    return method_clahe(g, clip=2.0)


def pipeline_l0_enhance(img):
    """管线C: L0 平滑 → Gamma → CLAHE (细节保留最强)"""
    s = method_l0_smooth(img, lambda_=0.02)
    g = method_gamma(s, gamma=1.8)
    return method_clahe(g, clip=2.0)


def pipeline_msr_clahe(img):
    """管线D: MSR 光照补偿 → CLAHE"""
    msr = method_msr(img)
    return method_clahe(msr, clip=2.0)


def pipeline_edge_clahe(img):
    """管线E: EdgePreserving → CLAHE"""
    ep = method_edge_preserving(img)
    return method_clahe(ep, clip=2.0)


def pipeline_detail_enhance(img):
    """管线F: DetailEnhance → Gamma → CLAHE"""
    de = method_detail_enhance(img)
    g = method_gamma(de, gamma=1.8)
    return method_clahe(g, clip=2.0)


def pipeline_rolling_enhance(img):
    """管线G: RollingGuidance → Gamma → CLAHE"""
    rg = method_rolling_guidance(img)
    g = method_gamma(rg, gamma=1.8)
    return method_clahe(g, clip=2.0)


def pipeline_extreme_enhance(img):
    """管线H (极端低光): DCT+L0 → MSR → CLAHE"""
    d = method_dct_denoising(img, sigma=15)
    s = method_l0_smooth(d, lambda_=0.02)
    msr = method_msr(s)
    return method_clahe(msr, clip=2.5)


# ============================================================
# 3. 可视化函数
# ============================================================

def bgr2rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def safe_apply(func, img):
    """安全调用方法，返回结果或 None"""
    try:
        return func(img.copy())
    except Exception as e:
        print(f"    [WARN] {func.__name__ if hasattr(func, '__name__') else 'lambda'} failed: {str(e)[:80]}")
        return None


def make_grid(original, methods_dict, title, filename, cols=5, figsize_per=3.5):
    """通用对比网格生成"""
    n = len(methods_dict)
    rows = (n + 1 + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(figsize_per * cols, figsize_per * rows + 1.0))
    if rows == 1:
        axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
    else:
        axes = axes.flatten()

    # 原始图
    axes[0].imshow(bgr2rgb(original))
    axes[0].set_title("Original (Low Light)", fontsize=11, fontweight='bold', color='darkred')
    axes[0].axis('off')

    for i, (name, func) in enumerate(methods_dict.items()):
        result = safe_apply(func, original)
        if result is not None:
            axes[i + 1].imshow(bgr2rgb(result))
        else:
            axes[i + 1].text(0.5, 0.5, "Error", ha='center', va='center', fontsize=8)
        axes[i + 1].set_title(name, fontsize=10, fontweight='bold')
        axes[i + 1].axis('off')

    for j in range(len(methods_dict) + 1, len(axes)):
        axes[j].axis('off')

    plt.suptitle(title, fontsize=15, fontweight='bold', y=1.01)
    plt.subplots_adjust(top=0.93, hspace=0.35, wspace=0.12)
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] Saved: {filename}")


def make_before_after(img, func, method_name, filename):
    """生成单张前后对比 + 直方图"""
    result = safe_apply(func, img)
    if result is None:
        print(f"  [SKIP] {filename} — method failed")
        return

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))

    axes[0].imshow(bgr2rgb(img))
    axes[0].set_title("Original (Low Light)", fontsize=12, fontweight='bold', color='darkred')
    axes[0].axis('off')

    axes[1].imshow(bgr2rgb(result))
    axes[1].set_title(f"{method_name}", fontsize=12, fontweight='bold', color='darkgreen')
    axes[1].axis('off')

    gray_orig = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_res = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    axes[2].hist(gray_orig.ravel(), 256, [0, 256], color='red', alpha=0.5, label='Original')
    axes[2].hist(gray_res.ravel(), 256, [0, 256], color='blue', alpha=0.5, label='Enhanced')
    axes[2].set_title("Histogram Comparison", fontsize=12, fontweight='bold')
    axes[2].set_xlim([0, 256])
    axes[2].legend()
    axes[2].set_xlabel("Pixel Value"); axes[2].set_ylabel("Count")

    plt.suptitle(f"{method_name} — Before vs After", fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] Saved: {filename}")


def make_histogram_group(original, methods_dict, title, filename):
    """多方法直方图对比"""
    n = len(methods_dict) + 1
    cols = min(n, 6)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4.5 * rows))
    if rows == 1 and cols == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    gray_orig = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    axes[0].hist(gray_orig.ravel(), 256, [0, 256], color='gray', alpha=0.7)
    axes[0].set_title("Original Histogram", fontsize=10)
    axes[0].set_xlim([0, 256])

    for i, (name, func) in enumerate(methods_dict.items()):
        result = safe_apply(func, original)
        if result is not None:
            gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
            axes[i + 1].hist(gray.ravel(), 256, [0, 256], color='blue', alpha=0.7)
        axes[i + 1].set_title(f"{name}\nHistogram", fontsize=10)
        axes[i + 1].set_xlim([0, 256])

    for j in range(n, len(axes)):
        axes[j].axis('off')

    plt.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] Saved: {filename}")


def make_pipeline_flow(img, steps_dict, title, filename):
    """生成管线逐步分解图"""
    n = len(steps_dict)
    fig, axes = plt.subplots(1, n, figsize=(n * 3.5, 3.8))
    if n == 1:
        axes = [axes]

    for i, (name, step_img) in enumerate(steps_dict.items()):
        axes[i].imshow(bgr2rgb(step_img))
        axes[i].set_title(name, fontsize=11, fontweight='bold')
        axes[i].axis('off')

    plt.suptitle(f"Pipeline Step-by-Step: {title}", fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] Saved: {filename}")


def make_zoom_comparison(original, pipeline_results, roi_label, filename):
    """ROI 区域放大对比"""
    h, w = original.shape[:2]
    # 定义 ROI 区域 (上左, 上右, 下左, 下右)
    roi_h, roi_w = 80, 80
    rois = {
        "Top-Left": original[20:20+roi_h, 20:20+roi_w],
        "Top-Right": original[20:20+roi_h, w-100:w-100+roi_w],
        "Bot-Left": original[h-100:h-100+roi_h, 20:20+roi_w],
        "Bot-Right": original[h-100:h-100+roi_h, w-100:w-100+roi_w],
    }

    n_methods = len(pipeline_results) + 1
    n_rois = 4
    fig, axes = plt.subplots(n_rois, n_methods, figsize=(4 * n_methods, 4 * n_rois))

    roi_names = list(rois.keys())
    method_names = ["Original"] + list(pipeline_results.keys())

    for col, m_name in enumerate(method_names):
        if m_name == "Original":
            src = original
        else:
            src = safe_apply(pipeline_results[m_name], original)
            if src is None:
                for row in range(n_rois):
                    axes[row, col].text(0.5, 0.5, "N/A", ha='center', va='center')
                    axes[row, col].axis('off')
                continue

        for row in range(n_rois):
            roi_name = roi_names[row]
            y, x = {
                "Top-Left": (20, 20),
                "Top-Right": (20, w-100),
                "Bot-Left": (h-100, 20),
                "Bot-Right": (h-100, w-100),
            }[roi_name]
            patch = src[y:y+roi_h, x:x+roi_w]
            axes[row, col].imshow(bgr2rgb(patch))
            if col == 0:
                axes[row, col].set_ylabel(roi_name, fontsize=10, fontweight='bold')
            axes[row, col].axis('off')

    for col, m_name in enumerate(method_names):
        axes[0, col].set_title(m_name, fontsize=11, fontweight='bold')

    plt.suptitle(f"ROI Zoom Comparison ({roi_label}) — 4 Regions × {n_methods} Methods",
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] Saved: {filename}")


# ============================================================
# 4. 主流程
# ============================================================

print("=" * 65)
print("OpenCV Advanced Low-Light Enhancement — Comparison Generator")
print(f"OpenCV: {cv2.__version__}")
print("=" * 65)

# --- 生成测试图像 ---
print("\n[1/8] Generating test images...")
scene = create_low_light_scene()
portrait = create_low_light_portrait()
extreme = create_extreme_low_light()
plt.imsave(os.path.join(OUTPUT_DIR, "test_scene_lowlight.png"), bgr2rgb(scene))
plt.imsave(os.path.join(OUTPUT_DIR, "test_portrait_lowlight.png"), bgr2rgb(portrait))
plt.imsave(os.path.join(OUTPUT_DIR, "test_extreme_lowlight.png"), bgr2rgb(extreme))
print("  [OK] 3 test images saved.")

# --- Group 1: xphoto 模块 — DCT去噪 + 白平衡 ---
print("\n[2/8] xphoto module — DCT Denoising & White Balance...")
xphoto_methods = {
    "DCT Denoising\n(σ=15)": method_dct_denoising,
    "Simple WB": method_simple_wb,
    "Learning WB": method_learning_wb,
}
make_grid(scene, xphoto_methods,
    "xphoto Module — DCT Denoising & White Balance",
    "01_comparison_xphoto_scene.png", cols=4, figsize_per=4.0)

# --- Group 2: photo 模块 — 边缘保持、细节增强、光照校正 ---
print("\n[3/8] photo module — Edge-Preserving, Detail, Illumination...")
photo_methods = {
    "Edge-Preserving\nFilter": method_edge_preserving,
    "Detail Enhance": method_detail_enhance,
    "Illumination\nChange\n(brighten ×1.8)": method_illumination_change,
}
make_grid(scene, photo_methods,
    "photo Module — Edge-Preserving, Detail Enhancement & Illumination Change",
    "02_comparison_photo_scene.png", cols=4, figsize_per=4.0)

# --- Group 3: ximgproc — 导向滤波系列 ---
print("\n[4/8] ximgproc module — Guided & Edge-Preserving Filters...")
ximgproc_methods = {
    "Guided Filter\n(radius=8)": method_guided_filter,
    "Static Guided\nFilter": method_static_guided_filter,
    "L0 Gradient\nMinimization": method_l0_smooth,
    "Rolling Guidance\n(4 iterations)": method_rolling_guidance,
    "Fast Global\nSmoother": method_fast_global_smoother,
    "Adaptive\nManifold Filter": method_adaptive_manifold,
    "Bilateral Texture\nFilter": method_bilateral_texture,
    "Joint Bilateral\nFilter": method_joint_bilateral,
    "Domain Transform\nFilter": method_domain_transform,
}
make_grid(scene, ximgproc_methods,
    "ximgproc Module — Edge-Preserving Smoothing & Advanced Filters",
    "03_comparison_ximgproc_scene.png", cols=5, figsize_per=3.8)

# --- Group 4: 直方图对比 ---
print("\n[5/8] Histogram comparison...")
hist_methods = {
    "DCT Denoising": method_dct_denoising,
    "Guided Filter": method_guided_filter,
    "L0 Smooth": method_l0_smooth,
    "EdgePreserving": method_edge_preserving,
    "DetailEnhance": method_detail_enhance,
}
make_histogram_group(scene, hist_methods,
    "Histogram Comparison — Advanced Denoising & Enhancement Methods",
    "04_histogram_comparison.png")

# --- Group 5: 高级组合管线 ---
print("\n[6/8] Advanced combined pipelines...")
pipeline_methods = {
    "Pipeline A\n(DCT→Gamma→CLAHE)": pipeline_dct_gamma_clahe,
    "Pipeline B\n(GF→Gamma→CLAHE)": pipeline_guided_gamma_clahe,
    "Pipeline C\n(L0→Gamma→CLAHE)": pipeline_l0_enhance,
    "Pipeline D\n(MSR→CLAHE)": pipeline_msr_clahe,
    "Pipeline E\n(EdgePres→CLAHE)": pipeline_edge_clahe,
    "Pipeline F\n(Detail→Gamma→CLAHE)": pipeline_detail_enhance,
    "Pipeline G\n(Rolling→Gamma→CLAHE)": pipeline_rolling_enhance,
    "Pipeline H\n(Extreme Low-Light)": pipeline_extreme_enhance,
}
make_grid(scene, pipeline_methods,
    "Advanced Combined Pipelines — Multi-Stage Enhancement (Scene)",
    "05_comparison_pipelines_scene.png", cols=4, figsize_per=3.8)

# 极限低光测试
make_grid(extreme, pipeline_methods,
    "Extreme Low-Light — Advanced Pipeline Comparison",
    "06_comparison_pipelines_extreme.png", cols=4, figsize_per=3.8)

# --- Group 6: 单张前后对比 ---
print("\n[7/8] Before/After detailed comparisons...")
make_before_after(scene, method_guided_filter, "Guided Filter (Edge-Preserving Denoising)", "07_before_after_guided.png")
make_before_after(scene, method_l0_smooth, "L0 Gradient Minimization Smoothing", "08_before_after_l0smooth.png")
make_before_after(scene, method_edge_preserving, "Edge-Preserving Filter (photo)", "09_before_after_edge_preserving.png")
make_before_after(scene, method_detail_enhance, "Detail Enhancement (photo)", "10_before_after_detail_enhance.png")
make_before_after(scene, pipeline_guided_gamma_clahe, "Pipeline B: GuidedFilter → Gamma → CLAHE", "11_before_after_pipeline_b.png")
make_before_after(scene, pipeline_l0_enhance, "Pipeline C: L0 → Gamma → CLAHE", "12_before_after_pipeline_c.png")
make_before_after(extreme, pipeline_extreme_enhance, "Pipeline H: Extreme Low-Light Enhancement", "13_before_after_pipeline_h.png")

# --- Group 7: 管线流程分解 ---
print("\n[8/8] Pipeline step-by-step flow...")
# Pipeline B 分解
gf = method_guided_filter(scene, radius=8, eps=0.02)
gamma_b = method_gamma(gf, gamma=1.8)
clahe_b = method_clahe(gamma_b, clip=2.0)
make_pipeline_flow(scene, {
    "① Original\n(Low Light)": scene,
    "② Guided Filter\n(denoise)": gf,
    "③ Gamma=1.8\n(brighten)": gamma_b,
    "④ CLAHE clip=2.0\n(local contrast)": clahe_b,
}, "Pipeline B: GuidedFilter → Gamma → CLAHE", "14_pipeline_flow_b.png")

# Pipeline H 分解
dct_h = method_dct_denoising(extreme, sigma=15)
l0_h = method_l0_smooth(dct_h, lambda_=0.02)
msr_h = method_msr(l0_h)
clahe_h = method_clahe(msr_h, clip=2.5)
make_pipeline_flow(extreme, {
    "① Original\n(Extreme Dark)": extreme,
    "② DCT Denoising\n(σ=15)": dct_h,
    "③ L0 Smooth\n(λ=0.02)": l0_h,
    "④ MSR\n(light compensate)": msr_h,
    "⑤ CLAHE clip=2.5\n(local enhance)": clahe_h,
}, "Pipeline H: DCT → L0 → MSR → CLAHE (Extreme Low-Light)", "15_pipeline_flow_h.png")

# --- Group 额外: ROI 放大对比 ---
print("\n  -> Generating ROI zoom comparison...")
pipeline_roi = {
    "Guided+Gamma+CLAHE": pipeline_guided_gamma_clahe,
    "L0+Gamma+CLAHE": pipeline_l0_enhance,
    "Extreme Pipeline": pipeline_extreme_enhance,
}
try:
    make_zoom_comparison(scene, pipeline_roi, "Scene", "16_roi_zoom_comparison.png")
except Exception as e:
    print(f"  [WARN] ROI zoom failed: {e}")

print("\n" + "=" * 65)
print(f"DONE! All images saved to:\n   {OUTPUT_DIR}")
print("=" * 65)

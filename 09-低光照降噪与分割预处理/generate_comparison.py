"""
OpenCV 低光照降噪与分割预处理 — 对比图生成
适用于 RK3576 平台，附 CPU 占用估算
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

np.random.seed(42)
OUTPUT_DIR = r"C:\Users\29503\Desktop\AI学习笔记\09-低光照降噪与分割预处理"

# ============================================================
# 1. 合成低光照 + 高噪声 测试图
# ============================================================
def create_noisy_low_light_scene():
    """合成暗光+噪声场景，模拟真实低光照摄像头输入"""
    h, w = 480, 640
    img = np.ones((h, w, 3), dtype=np.uint8) * 255

    # 暗背景渐变
    for y in range(h):
        v = int(60 - 35 * (y / h))
        img[y, :] = (v, v, max(0, v - 8))

    # 窗口亮区
    cv2.rectangle(img, (200, 80), (440, 280), (120, 140, 160), -1)
    for x in range(210, 440, 50):
        cv2.rectangle(img, (x, 90), (x+25, 150), (180, 200, 220), -1)

    # 暗色桌子
    cv2.rectangle(img, (50, 320), (590, 400), (30, 25, 20), -1)

    # 桌上的物体（不同灰度 — 分割目标）
    cv2.ellipse(img, (180, 340), (30, 25), 0, 0, 360, (90, 85, 80), -1)     # 杯子 A
    cv2.ellipse(img, (280, 340), (35, 20), 0, 0, 360, (45, 40, 35), -1)      # 杯子 B
    cv2.rectangle(img, (380, 330), (460, 390), (60, 55, 50), -1)             # 书本
    cv2.rectangle(img, (385, 335), (455, 385), (85, 78, 68), -1)

    # 墙上的画（分割目标）
    cv2.rectangle(img, (60, 140), (180, 260), (40, 35, 30), -1)
    cv2.rectangle(img, (70, 150), (170, 250), (95, 70, 45), -1)
    cv2.circle(img, (120, 200), 20, (110, 85, 55), -1)

    # 微弱灯光
    cv2.circle(img, (520, 100), 12, (160, 150, 80), -1)
    for r in range(15, 50, 5):
        alpha = max(0, 1 - r / 50)
        overlay = img.copy()
        cv2.circle(overlay, (520, 100), r, (160, 140, 70), -1)
        img = cv2.addWeighted(overlay, alpha * 0.12, img, 1 - alpha * 0.12, 0)

    # 整体压暗
    img = cv2.convertScaleAbs(img, alpha=0.45, beta=-5)
    img = np.clip(img.astype(np.int16), 0, 255).astype(np.uint8)

    # ---- 重点：模拟真实摄像机暗光噪声 ----
    # 高斯噪声（传感器热噪声）
    gauss = np.random.normal(0, 15, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + gauss, 0, 255).astype(np.uint8)
    # 椒盐噪声（坏点）
    salt_pepper = np.random.random(img.shape[:2])
    img[salt_pepper < 0.01] = 255
    img[salt_pepper > 0.99] = 0
    # 泊松噪声模拟（光子散粒噪声，亮区更明显）
    poisson = np.random.poisson(img.astype(np.float32) * 0.1).astype(np.int16)
    img = np.clip(img.astype(np.int16) + poisson, 0, 255).astype(np.uint8)

    return img


# ============================================================
# 2. 降噪方法（OpenCV 实现）
# ============================================================

def denoise_nlm(img, h=10, h_color=10, template=7, search=21):
    """Non-local Means 去噪 — 最强但最慢"""
    return cv2.fastNlMeansDenoisingColored(img, None, h, h_color, template, search)

def denoise_bilateral(img, d=9, sigma_color=50, sigma_space=50):
    """双边滤波 — 保边去噪"""
    return cv2.bilateralFilter(img, d, sigma_color, sigma_space)

def denoise_edge_preserving(img, sigma_s=60, sigma_r=0.3):
    """边缘保持滤波 — 快速且保边"""
    return cv2.edgePreservingFilter(img, flags=1, sigma_s=sigma_s, sigma_r=sigma_r)

def denoise_median(img, ksize=5):
    """中值滤波 — 去椒盐噪声好"""
    return cv2.medianBlur(img, ksize)

def denoise_gaussian(img, ksize=(5,5), sigma=1.0):
    """高斯模糊 — 基础平滑"""
    return cv2.GaussianBlur(img, ksize, sigma)

def denoise_guided(img, r=8, eps=400):
    """导向滤波 — 保边平滑 + 细节增强（基于OpenCV box filter）"""
    img_f = img.astype(np.float32) / 255.0
    result = np.zeros_like(img_f)
    ksize = r * 2 + 1
    eps_scaled = eps / 255.0
    for c in range(3):
        I = img_f[:,:,c]
        p = I
        mean_I = cv2.blur(I, (ksize, ksize))
        mean_p = cv2.blur(p, (ksize, ksize))
        mean_II = cv2.blur(I * I, (ksize, ksize))
        var_I = mean_II - mean_I * mean_I
        a = var_I / (var_I + eps_scaled + 1e-8)
        b = mean_p - a * mean_I
        mean_a = cv2.blur(a, (ksize, ksize))
        mean_b = cv2.blur(b, (ksize, ksize))
        result[:,:,c] = mean_a * I + mean_b
    return (np.clip(result * 255, 0, 255)).astype(np.uint8)


# ============================================================
# 3. 低光照增强（OpenCV）
# ============================================================

def enhance_clahe(img, clip=2.0):
    """CLAHE 增强"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8))
    return cv2.cvtColor(cv2.merge([clahe.apply(l), a, b]), cv2.COLOR_LAB2BGR)

def enhance_gamma(img, gamma=1.8):
    """伽马校正"""
    inv = 1.0 / gamma
    lut = np.array([(i/255.0)**inv*255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(img, lut)


# ============================================================
# 4. 降噪 + 增强 组合管线（针对分割预处理）
# ============================================================

def pipeline_nlm_clahe(img):
    """NLM去噪 → CLAHE"""
    d = denoise_nlm(img)
    return enhance_clahe(d)

def pipeline_bilateral_clahe(img):
    """双边滤波去噪 → CLAHE"""
    d = denoise_bilateral(img)
    return enhance_clahe(d)

def pipeline_edge_clahe(img):
    """边缘保持滤波 → CLAHE"""
    d = denoise_edge_preserving(img)
    return enhance_clahe(d)

def pipeline_guided_clahe(img):
    """导向滤波(保边+增强) → CLAHE"""
    d = denoise_guided(img)
    return enhance_clahe(d)

def pipeline_nlm_gamma(img):
    """NLM去噪 → 伽马校正"""
    d = denoise_nlm(img)
    return enhance_gamma(d, 1.8)

def pipeline_full_clean(img):
    """完整去噪管线：双边滤波 → NLM → CLAHE"""
    d1 = denoise_bilateral(img, d=7, sigma_color=30, sigma_space=30)
    d2 = denoise_edge_preserving(d1, sigma_s=40, sigma_r=0.2)
    return enhance_clahe(d2)

def pipeline_median_clahe(img):
    """中值滤波去噪 → CLAHE"""
    d = denoise_median(img)
    return enhance_clahe(d)


# ============================================================
# 5. 性能基准测试（模拟）
# ============================================================

def benchmark_methods(img, methods, warmup=3, runs=5):
    """估算各方法在 CPU 上的耗时（相对值）"""
    results = {}
    for name, func in methods.items():
        # warmup
        for _ in range(warmup):
            _ = func(img)
        # timed runs
        times = []
        for _ in range(runs):
            start = time.perf_counter()
            _ = func(img)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        avg = np.mean(times)
        # RK3576 4xA76 @2.2GHz vs test CPU: rough scale factor
        # 假设测试CPU约为RK3576单核性能的1.5x ~ 2x
        # 这里我们直接给出相对排行更准确
        results[name] = {
            'avg_sec': avg,
            'fps': 1.0 / avg if avg > 0 else 0,
        }
    return results


# ============================================================
# 6. 生成对比图
# ============================================================

def make_denoise_grid(original, methods_dict, title, filename):
    """生成降噪方法对比图"""
    n = len(methods_dict)
    cols = (n + 1) // 2 + 1
    fig, axes = plt.subplots(2, cols,
                             figsize=(5 * cols, 11),
                             gridspec_kw={'hspace': 0.35, 'wspace': 0.1})
    axes = axes.flatten()

    axes[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original\n(Low Light + Noise)", fontsize=10, fontweight='bold')
    axes[0].axis('off')

    for i, (name, func) in enumerate(methods_dict.items()):
        result = func(original)
        axes[i + 1].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        axes[i + 1].set_title(name, fontsize=10, fontweight='bold')
        axes[i + 1].axis('off')

    for j in range(len(methods_dict) + 1, len(axes)):
        axes[j].axis('off')

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.subplots_adjust(top=0.92)
    path = f"{OUTPUT_DIR}\\{filename}"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Saved: {filename}")


def make_edge_detail_comparison(original, title, filename):
    """边缘保留效果放大对比"""
    fig, axes = plt.subplots(2, 4, figsize=(20, 10),
                             gridspec_kw={'hspace': 0.35, 'wspace': 0.15})
    axes = axes.flatten()

    methods = [
        ("Original", lambda x: x),
        ("Gaussian Blur", lambda x: denoise_gaussian(x, (5,5), 1.5)),
        ("Median Blur", denoise_median),
        ("Bilateral", denoise_bilateral),
        ("Edge Preserving", denoise_edge_preserving),
        ("Guided Filter", denoise_guided),
        ("NLM Denoise", denoise_nlm),
        ("Bilateral+Edge\n+CLAHE", pipeline_full_clean),
    ]

    for i, (name, func) in enumerate(methods):
        result = func(original)
        # 取中间一块放大
        crop = result[140:340, 160:480]
        axes[i].imshow(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        axes[i].set_title(name, fontsize=10, fontweight='bold')
        axes[i].axis('off')

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.subplots_adjust(top=0.90)
    path = f"{OUTPUT_DIR}\\{filename}"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Saved: {filename}")


def make_pipeline_grid(original, pipelines_dict, title, filename):
    """降噪+增强管线对比"""
    n = len(pipelines_dict)
    cols = (n + 1) // 2 + 1
    fig, axes = plt.subplots(2, cols,
                             figsize=(5 * cols, 11),
                             gridspec_kw={'hspace': 0.38, 'wspace': 0.1})
    axes = axes.flatten()

    axes[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original\n(Noisy + Dark)", fontsize=10, fontweight='bold')
    axes[0].axis('off')

    for i, (name, func) in enumerate(pipelines_dict.items()):
        result = func(original)
        axes[i + 1].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        axes[i + 1].set_title(name, fontsize=10, fontweight='bold')
        axes[i + 1].axis('off')

    for j in range(len(pipelines_dict) + 1, len(axes)):
        axes[j].axis('off')

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.subplots_adjust(top=0.92)
    path = f"{OUTPUT_DIR}\\{filename}"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Saved: {filename}")


def make_segmentation_preview(original, pipelines_dict, title, filename):
    """模拟分割效果对比（Canny边缘检测作为分割代理指标）"""
    n = len(pipelines_dict) + 1
    fig, axes = plt.subplots(2, n, figsize=(5 * n, 10),
                             gridspec_kw={'hspace': 0.30, 'wspace': 0.1})
    # 第一行：增强结果，第二行：对应Canny边缘

    # 原图
    gray_orig = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    edges_orig = cv2.Canny(gray_orig, 20, 60)
    axes[0, 0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    axes[0, 0].set_title("Original", fontsize=10, fontweight='bold')
    axes[0, 0].axis('off')
    axes[1, 0].imshow(edges_orig, cmap='gray')
    axes[1, 0].set_title("Edges (noisy)", fontsize=10)
    axes[1, 0].axis('off')

    for i, (name, func) in enumerate(pipelines_dict.items()):
        result = func(original)
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 20, 60)
        axes[0, i+1].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        axes[0, i+1].set_title(name, fontsize=9, fontweight='bold')
        axes[0, i+1].axis('off')
        axes[1, i+1].imshow(edges, cmap='gray')
        axes[1, i+1].set_title(f"Edges after {name.split(chr(10))[0]}", fontsize=9)
        axes[1, i+1].axis('off')

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.subplots_adjust(top=0.88)
    path = f"{OUTPUT_DIR}\\{filename}"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Saved: {filename}")


# ============================================================
# 7. 主流程
# ============================================================

print("=" * 60)
print("OpenCV Low-Light Denoise + Enhancement for Segmentation")
print("=" * 60)

# 生成测试图
print("\n[1/5] Generating test images...")
scene = create_noisy_low_light_scene()
plt.imsave(f"{OUTPUT_DIR}\\test_noisy_lowlight.png",
           cv2.cvtColor(scene, cv2.COLOR_BGR2RGB))
print("  [OK] test_noisy_lowlight.png")

# ---- 降噪方法对比 ----
print("\n[2/5] Denoise method comparison...")
denoise_methods = {
    "Gaussian\nBlur (5x5)": lambda x: denoise_gaussian(x, (5,5), 1.5),
    "Median\nBlur (5x5)": denoise_median,
    "Bilateral\nFilter": denoise_bilateral,
    "Edge Preserving\nFilter": denoise_edge_preserving,
    "Guided\nFilter": denoise_guided,
    "NLM\nDenoise": denoise_nlm,
}
make_denoise_grid(scene, denoise_methods,
    "Denoise Methods Comparison - Low Light + Noise",
    "comparison_denoise_only.png")

# ---- 边缘保留放大对比 ----
print("\n  -> Edge/detail preservation comparison...")
make_edge_detail_comparison(scene,
    "Edge & Detail Preservation (zoomed crop)",
    "comparison_edge_preservation.png")

# ---- 降噪+增强管线对比 ----
print("\n[3/5] Pipeline (denoise + enhance) comparison...")
pipelines = {
    "Bilateral\n+ CLAHE": pipeline_bilateral_clahe,
    "EdgePreserve\n+ CLAHE": pipeline_edge_clahe,
    "NLM\n+ CLAHE": pipeline_nlm_clahe,
    "Median\n+ CLAHE": pipeline_median_clahe,
    "NLM\n+ Gamma": pipeline_nlm_gamma,
    "Full Clean\nPipeline": pipeline_full_clean,
}
make_pipeline_grid(scene, pipelines,
    "Denoise + Enhancement Pipelines for Segmentation Pre-processing",
    "comparison_pipeline.png")

# ---- Canny 边缘模拟分割效果 ----
print("\n[4/5] Segmentation simulation (Canny edges)...")
make_segmentation_preview(scene, pipelines,
    "Segmentation Preview - Image vs Edge Detection After Processing",
    "comparison_segmentation_preview.png")

# ---- 性能基准 ----
print("\n[5/5] Performance benchmark (simulated)...")
bench_methods = {
    "Gaussian 5x5": lambda x: denoise_gaussian(x, (5,5), 1.5),
    "Median 5x5": denoise_median,
    "Bilateral 9x9": denoise_bilateral,
    "Edge Preserving": denoise_edge_preserving,
    "NLM Denoise": denoise_nlm,
    "CLAHE only": lambda x: enhance_clahe(x),
    "Bilateral+CLAHE": pipeline_bilateral_clahe,
    "Full Pipeline": pipeline_full_clean,
}
bench = benchmark_methods(scene, bench_methods, warmup=2, runs=3)

print(f"\n{'Method':<25} {'Avg Time (ms)':<15} {'Est. FPS on RK3576':<20} {'CPU Load Est.':<15}")
print("-" * 75)
# 以 NLM 为基准估算 RK3576 缩放系数
# 桌面CPU ≈ RK3576 A76@2.2GHz 的 2~3x 单核性能
# 但 OpenCV NEON 优化在 ARM 上效率更高
# 我们保守估计 desktop_time * 2.5 ≈ RK3576 time (单核)
# RK3576 有 8 核，但典型 pipeline 用 2-4 核

for name, data in bench.items():
    ms = data['avg_sec'] * 1000
    fps_desktop = data['fps']

    # 估算 RK3576 耗时 (desktop * 2.5 保守估算单核差距)
    est_rk_time_ms = ms * 2.5
    # RK3576 多核并行优化 (A76 x4)
    # 简单线性操作受益于多核，复杂非线性受益较少
    if "Gaussian" in name or "Median" in name:
        est_rk_time_ms = est_rk_time_ms / 3.5  # 高度并行化
        cpu_load = "10-15% (1-2 cores)"
    elif "Bilateral" in name:
        est_rk_time_ms = est_rk_time_ms / 2.5
        cpu_load = "20-30% (2-3 cores)"
    elif "Edge" in name:
        est_rk_time_ms = est_rk_time_ms / 3.0
        cpu_load = "15-25% (2-3 cores)"
    elif "NLM" in name:
        est_rk_time_ms = est_rk_time_ms / 2.0  # NLM 难以完美并行
        cpu_load = "40-60% (3-4 cores)"
    elif "CLAHE" in name and "+" not in name:
        est_rk_time_ms = est_rk_time_ms / 3.0
        cpu_load = "15-20% (2 cores)"
    elif "Pipeline" in name:
        est_rk_time_ms = est_rk_time_ms / 2.5
        cpu_load = "30-50% (3-4 cores)"
    else:
        est_rk_time_ms = est_rk_time_ms / 2.5
        cpu_load = "20-35%"

    est_fps = 1000.0 / max(est_rk_time_ms, 0.1)
    print(f"{name:<25} {ms:<15.1f} {est_fps:<20.1f} {cpu_load}")

print("\n" + "=" * 60)
print("DONE! All images saved to: " + OUTPUT_DIR)
print("=" * 60)

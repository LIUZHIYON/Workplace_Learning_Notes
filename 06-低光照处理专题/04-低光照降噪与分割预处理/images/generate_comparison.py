"""
generate_comparison.py
Generate comparison charts for low-light image segmentation preprocessing
methods. All labels in English for font compatibility.

Usage:
    python generate_comparison.py [--input your_image.jpg]

Requires: opencv-contrib-python numpy matplotlib
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from pathlib import Path
import argparse
import warnings
warnings.filterwarnings('ignore')

OUTPUT_DIR = Path(__file__).parent
DPI = 150


def simulate_low_light_image(size=(640, 480)):
    """Generate a simulated low-light test image with shapes, text, and noise."""
    w, h = size
    img = np.ones((h, w, 3), dtype=np.uint8) * 20

    gradient = np.linspace(10, 60, w, dtype=np.uint8)
    img[:, :, :] += gradient.reshape(1, w, 1)

    cv2.rectangle(img, (50, 50), (200, 150), (80, 100, 120), -1)
    cv2.rectangle(img, (250, 100), (400, 200), (60, 90, 110), -1)
    cv2.rectangle(img, (450, 50), (600, 180), (100, 80, 60), -1)
    cv2.circle(img, (150, 300), 60, (90, 85, 70), -1)
    cv2.circle(img, (350, 280), 45, (70, 95, 80), -1)
    cv2.circle(img, (500, 350), 55, (85, 75, 90), -1)
    cv2.putText(img, "LOW LIGHT", (150, 420), cv2.FONT_HERSHEY_SIMPLEX,
                1.5, (100, 100, 100), 3)
    cv2.putText(img, "SEGMENTATION", (120, 460), cv2.FONT_HERSHEY_SIMPLEX,
                1.5, (100, 100, 100), 3)

    for i in range(0, w, 40):
        cv2.line(img, (i, 250), (i, 270),
                 (int(50 + i % 60), int(40 + i % 50), int(60 + i % 40)), 1)

    # Gaussian noise
    noise = np.random.normal(0, 8, img.shape).astype(np.int16)
    # Poisson noise
    poisson = np.random.poisson(3, img.shape).astype(np.int16)
    # Salt & pepper
    sp = np.zeros(img.shape, dtype=np.int16)
    mask = np.random.random(img.shape[:2]) < 0.005
    sp[mask] = np.random.choice([-30, 40], size=mask.sum()).reshape(-1, 1)

    img_noisy = img.astype(np.int16) + noise + poisson + sp
    return np.clip(img_noisy, 0, 255).astype(np.uint8)


def apply_clahe(img, clip_limit=2.0):
    """CLAHE in LAB L-channel"""
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    if len(img.shape) == 2:
        return clahe.apply(img)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = clahe.apply(l)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)


def apply_gamma(img, gamma=0.65):
    """Gamma correction via LUT"""
    lut = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(img, lut)


def apply_guided(img, radius=8, eps=0.02):
    """Guided filter denoising"""
    eps_scaled = eps * eps * 255 * 255
    return cv2.ximgproc.guidedFilter(img, img, radius, eps_scaled)


# ============================================================
# Figure 1: Denoising Methods Comparison (8 panels)
# ============================================================
def create_denoising_comparison(img):
    methods = [
        ("Original\n(Low Light)", lambda i: i),
        ("Gaussian\n(k=5, s=1.5)", lambda i: cv2.GaussianBlur(i, (5, 5), 1.5)),
        ("Median\n(k=3)", lambda i: cv2.medianBlur(i, 3)),
        ("Bilateral\n(d=5, sc=75)", lambda i: cv2.bilateralFilter(i, 5, 75, 75)),
        ("Guided Filter\n(r=8, eps=0.02)", lambda i: apply_guided(i, 8, 0.02)),
        ("NLM\n(sw=11, h=10)", lambda i: cv2.fastNlMeansDenoisingColored(i, None, 10, 10, 7, 11)),
        ("CLAHE only\n(clip=1.5)", lambda i: apply_clahe(i, 1.5)),
        ("Guided+CLAHE\n(* recommended)", lambda i: apply_clahe(apply_guided(i, 8, 0.02), 1.5)),
    ]

    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    axes = axes.flatten()

    for ax, (name, func) in zip(axes, methods):
        result = func(img)
        display = result if len(result.shape) == 2 else cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        ax.imshow(display)
        ax.set_title(name, fontsize=9, fontweight='bold')
        ax.axis('off')

    # Highlight recommended
    for idx in [-1]:
        rect = plt.Rectangle((-0.02, -0.02), 1.04, 1.04,
                             transform=axes[idx].transAxes,
                             linewidth=3, edgecolor='limegreen', facecolor='none')
        axes[idx].add_patch(rect)

    plt.suptitle('Low Light Image Denoising Methods Comparison',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    path = OUTPUT_DIR / 'denoising_comparison.png'
    plt.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path.name}")


# ============================================================
# Figure 2: Pipeline Comparison (8 panels)
# ============================================================
def create_pipeline_comparison(img):
    def gaussian_clahe(i):
        return apply_clahe(cv2.GaussianBlur(i, (5, 5), 1.5), 1.5)

    def median_clahe(i):
        return apply_clahe(cv2.medianBlur(i, 3), 1.5)

    def bilateral_clahe(i):
        return apply_clahe(cv2.bilateralFilter(i, 5, 75, 75), 1.5)

    def guided_clahe(i):
        return apply_clahe(apply_guided(i, 8, 0.02), 1.5)

    def nlm_clahe(i):
        return apply_clahe(cv2.fastNlMeansDenoisingColored(i, None, 10, 10, 7, 11), 1.5)

    def guided_gamma_clahe(i):
        i2 = apply_guided(i, 8, 0.02)
        i2 = apply_gamma(i2, 0.65)
        return apply_clahe(i2, 1.0)

    methods = [
        ("Original", lambda i: i),
        ("CLAHE only\n(noise boosted!)", lambda i: apply_clahe(i, 1.5)),
        ("Gaussian + CLAHE\n(edges blurred)", lambda i: gaussian_clahe(i)),
        ("Median + CLAHE\n(fast, decent)", lambda i: median_clahe(i)),
        ("Bilateral + CLAHE\n(good edge keep)", lambda i: bilateral_clahe(i)),
        ("Guided + CLAHE\n(* best balance)", lambda i: guided_clahe(i)),
        ("NLM + CLAHE\n(best quality, slow)", lambda i: nlm_clahe(i)),
        ("Guided+G+CLAHE\n(* recommended)", lambda i: guided_gamma_clahe(i)),
    ]

    fig, axes = plt.subplots(2, 4, figsize=(22, 11))
    axes = axes.flatten()

    for ax, (name, func) in zip(axes, methods):
        result = func(img)
        display = result if len(result.shape) == 2 else cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        ax.imshow(display)
        ax.set_title(name, fontsize=9, fontweight='bold')
        ax.axis('off')

    # Green highlight on recommended
    for idx in [5, 7]:
        rect = plt.Rectangle((-0.02, -0.02), 1.04, 1.04,
                             transform=axes[idx].transAxes,
                             linewidth=3, edgecolor='limegreen', facecolor='none')
        axes[idx].add_patch(rect)

    plt.suptitle('Low Light Preprocessing Pipeline Comparison',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    path = OUTPUT_DIR / 'pipeline_comparison.png'
    plt.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path.name}")


# ============================================================
# Figure 3: Detail Zoom Comparison
# ============================================================
def create_zoom_comparison(img):
    h, w = img.shape[:2]
    roi_x, roi_y = 120, 270
    roi_w, roi_h = 100, 100

    methods_detail = [
        ("Original", lambda i: i),
        ("Gaussian 5x5", lambda i: cv2.GaussianBlur(i, (5, 5), 1.5)),
        ("Median k=3", lambda i: cv2.medianBlur(i, 3)),
        ("Bilateral d=5", lambda i: cv2.bilateralFilter(i, 5, 75, 75)),
        ("Guided r=8", lambda i: apply_guided(i, 8, 0.02)),
        ("NLM sw=11", lambda i: cv2.fastNlMeansDenoisingColored(i, None, 10, 10, 7, 11)),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for ax, (name, func) in zip(axes, methods_detail):
        result = func(img)
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        cv2.rectangle(result_rgb, (roi_x, roi_y),
                      (roi_x + roi_w, roi_y + roi_h), (255, 0, 0), 2)

        zoom = result[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
        zoom_rgb = cv2.cvtColor(zoom, cv2.COLOR_BGR2RGB)

        # Stack full view (240h) and zoom (240h) side by side
        combined = np.hstack([
            cv2.resize(result_rgb, (320, 240)),
            cv2.resize(zoom_rgb, (240, 240)),
        ])

        ax.imshow(combined)
        ax.set_title(name, fontsize=10, fontweight='bold')
        ax.axis('off')
        ax.text(0.5, 1.02, 'Full View  -------  ROI Zoom (blue box)',
                transform=ax.transAxes, fontsize=7, color='gray', ha='center')

    plt.suptitle('Detail Preservation Comparison - ROI Zoom',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    path = OUTPUT_DIR / 'detail_zoom_comparison.png'
    plt.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path.name}")


# ============================================================
# Figure 4: CPU Usage Bar Chart
# ============================================================
def create_cpu_usage_chart():
    methods_cpu = [
        ("GaussianBlur (5x5)", 1.5),
        ("MedianBlur (k=3)", 2.5),
        ("MedianBlur (k=5)", 6.5),
        ("Bilateral (d=5)", 10.0),
        ("Bilateral (d=9)", 20.0),
        ("Guided Filter (r=4~16)", 8.0),
        ("NLM (sw=7)", 25.0),
        ("NLM (sw=11)", 50.0),
        ("NLM (sw=21)", 120.0),
        ("CLAHE (8x8)", 3.0),
        ("Gamma (LUT)", 0.5),
        ("Guided + CLAHE (*rec)", 11.0),
        ("Guided + G + CLAHE (*best)", 12.0),
        ("Median + CLAHE (fast)", 5.5),
    ]

    names = [m[0] for m in methods_cpu]
    times = [m[1] for m in methods_cpu]
    colors = (['#2196F3'] * 5 + ['#4CAF50'] * 2 + ['#FF9800'] * 3 +
              ['#2196F3'] * 2 + ['#4CAF50'] * 2)

    fig, ax = plt.subplots(figsize=(14, 7))
    bars = ax.barh(names, times, color=colors, edgecolor='white', height=0.7)

    for bar, t in zip(bars, times):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f'{t:.1f} ms', va='center', fontsize=9, fontweight='bold')

    ax.axvline(x=33, color='red', linestyle='--', linewidth=2, alpha=0.7,
               label='30 FPS budget (33ms/frame)')
    ax.axvline(x=100, color='orange', linestyle='--', linewidth=2, alpha=0.7,
               label='10 FPS budget (100ms/frame)')

    ax.set_xlabel('Estimated CPU Time (ms) - RK3576 A72 @ 2.2GHz, 720P', fontsize=11)
    ax.set_title('CPU Usage Comparison by Method (RK3576)', fontsize=13, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.set_xlim(0, 160)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    path = OUTPUT_DIR / 'cpu_usage_chart.png'
    plt.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path.name}")


# ============================================================
# Figure 5: Pipeline Diagram
# ============================================================
def create_pipeline_diagram():
    fig, ax = plt.subplots(figsize=(16, 4.5))

    steps = [
        ("Camera\nSensor", "#607D8B", "RAW"),
        ("ISP\n3DNR/HDR", "#455A64", "Noise\nReduction"),
        ("Resize\n640x480", "#2196F3", "Scaling"),
        ("Guided\nFilter", "#4CAF50", "Denoise\nO(N)"),
        ("Gamma\nLUT", "#FF9800", "Brighten\n0.65"),
        ("LAB\nCLAHE", "#9C27B0", "Enhance\n1.5"),
        ("NPU\nSeg Model", "#F44336", "Inference\n~100ms"),
    ]

    step_w, step_h = 1.8, 2.2
    x_start = 0.3
    y_center = 1.2

    for i, (name, color, note) in enumerate(steps):
        x = x_start + i * (step_w + 0.35)
        rect = plt.Rectangle((x, y_center), step_w, step_h,
                             facecolor=color, edgecolor='white',
                             linewidth=3, alpha=0.92)
        ax.add_patch(rect)
        ax.text(x + step_w / 2, y_center + 1.0, name,
                ha='center', va='center', fontsize=9,
                fontweight='bold', color='white')
        ax.text(x + step_w / 2, y_center - 0.3, note,
                ha='center', va='center', fontsize=7, color='#E0E0E0')

        if i < len(steps) - 1:
            arrow_x = x + step_w + 0.05
            ax.annotate('', xy=(arrow_x + 0.25, y_center + step_h / 2),
                        xytext=(arrow_x, y_center + step_h / 2),
                        arrowprops=dict(arrowstyle='->', lw=2.5, color='#333'))

        # CPU time labels
        if "Guided" in name:
            ax.text(x + step_w / 2, y_center - 0.9, '~8ms', ha='center',
                    fontsize=7, color='#FFD54F')
        elif "Gamma" in name:
            ax.text(x + step_w / 2, y_center - 0.9, '~0.5ms', ha='center',
                    fontsize=7, color='#FFD54F')
        elif "CLAHE" in name:
            ax.text(x + step_w / 2, y_center - 0.9, '~3ms', ha='center',
                    fontsize=7, color='#FFD54F')
        elif "ISP" in name:
            ax.text(x + step_w / 2, y_center - 0.9, '0ms (HW)', ha='center',
                    fontsize=7, color='#FFD54F')
        elif "Seg" in name:
            ax.text(x + step_w / 2, y_center - 0.9, '~100ms', ha='center',
                    fontsize=7, color='#FFD54F')
        elif "Resize" in name:
            ax.text(x + step_w / 2, y_center - 0.9, '~1ms', ha='center',
                    fontsize=7, color='#FFD54F')

    ax.text(8.5, 0.25,
            'Total: ~115ms/frame (CPU preprocessing ~12ms + NPU inference ~100ms)  =>  ~8.5 FPS',
            ha='center', fontsize=12, fontweight='bold', color='#1565C0',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#E3F2FD', edgecolor='#1565C0'))

    ax.set_xlim(0, 16)
    ax.set_ylim(0, 5)
    ax.axis('off')
    plt.suptitle('Recommended Preprocessing Pipeline for RK3576', fontsize=14,
                 fontweight='bold', y=1.02)
    plt.tight_layout()
    path = OUTPUT_DIR / 'pipeline_diagram.png'
    plt.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path.name}")


# ============================================================
# Figure 6: Noise Amplification Principle
# ============================================================
def create_noise_amplification_diagram():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    np.random.seed(42)

    low_light = np.clip(np.random.normal(25, 12, 10000), 0, 60).astype(int)
    stretched = low_light * 4.25
    denoised = np.clip(low_light + np.random.normal(0, 4, 10000), 0, 60)
    denoised_stretched = denoised * 4.25

    axes[0].hist(low_light, bins=60, color='darkblue', alpha=0.85, edgecolor='white')
    axes[0].set_title('Low Light Histogram\nSNR = 25/sqrt(25) ~ 5', fontsize=11, fontweight='bold')
    axes[0].set_xlim(0, 255)
    axes[0].axvspan(0, 60, alpha=0.2, color='red')
    axes[0].set_xlabel('Pixel Value')
    axes[0].set_ylabel('Count')

    axes[1].hist(stretched, bins=60, color='red', alpha=0.85, edgecolor='white')
    axes[1].set_title('After CLAHE Stretch\nNoise x5 amplified!', fontsize=11, fontweight='bold')
    axes[1].set_xlim(0, 255)
    axes[1].axvspan(0, 255, alpha=0.15, color='orange')
    axes[1].set_xlabel('Pixel Value')

    axes[2].hist(denoised_stretched, bins=60, color='green', alpha=0.85, edgecolor='white')
    axes[2].set_title('Denoise -> CLAHE\nCleaner, less noise!', fontsize=11, fontweight='bold')
    axes[2].set_xlim(0, 255)
    axes[2].set_xlabel('Pixel Value')

    for ax in axes:
        ax.grid(axis='y', alpha=0.3)

    plt.suptitle('Why "Denoise Before Enhance" Matters - Principle',
                 fontsize=14, fontweight='bold', y=1.05)
    plt.tight_layout()
    path = OUTPUT_DIR / 'noise_amplification_principle.png'
    plt.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path.name}")


# ============================================================
# Figure 7: RK3576 Architecture
# ============================================================
def create_rk3576_arch_diagram():
    fig, ax = plt.subplots(figsize=(14, 8))

    chip = plt.Rectangle((0.5, 0.3), 13, 7, facecolor='#ECEFF1',
                         edgecolor='#37474F', linewidth=3)
    ax.add_patch(chip)
    ax.text(7, 7.1, 'RK3576 SoC', ha='center', fontsize=16,
            fontweight='bold', color='#37474F')

    # CPU Big
    cpu_big = plt.Rectangle((1, 2.5), 3, 2, facecolor='#FF7043',
                            edgecolor='white', linewidth=2)
    ax.add_patch(cpu_big)
    ax.text(2.5, 4.1, 'A72 x4 (Big)\n2.2GHz', ha='center', fontsize=10,
            fontweight='bold', color='white')
    ax.text(2.5, 3.2, 'OpenCV Pipeline\nPreprocessing\n~10-15ms', ha='center',
            fontsize=8, color='#FFF3E0')

    # CPU LITTLE
    cpu_little = plt.Rectangle((1, 0.6), 3, 1.6, facecolor='#FFAB91',
                               edgecolor='white', linewidth=2)
    ax.add_patch(cpu_little)
    ax.text(2.5, 1.4, 'A53 x4 (LITTLE)\n2.0GHz', ha='center', fontsize=10,
            fontweight='bold', color='white')

    # NPU
    npu = plt.Rectangle((4.5, 2.5), 2.5, 2.5, facecolor='#7B1FA2',
                        edgecolor='white', linewidth=2)
    ax.add_patch(npu)
    ax.text(5.75, 4.5, 'NPU', ha='center', fontsize=11,
            fontweight='bold', color='white')
    ax.text(5.75, 3.8, '6 TOPS (INT8)', ha='center', fontsize=9, color='white')
    ax.text(5.75, 3.2, 'UNet / Seg\nModel\n~100ms', ha='center',
            fontsize=8, color='#E1BEE7')

    # GPU
    gpu = plt.Rectangle((4.5, 0.6), 2.5, 1.6, facecolor='#5C6BC0',
                        edgecolor='white', linewidth=2)
    ax.add_patch(gpu)
    ax.text(5.75, 1.4, 'Mali-G52 MC3\n145 GFLOPS', ha='center', fontsize=9,
            fontweight='bold', color='white')

    # ISP
    isp = plt.Rectangle((7.5, 2.5), 2.5, 2.5, facecolor='#00897B',
                        edgecolor='white', linewidth=2)
    ax.add_patch(isp)
    ax.text(8.75, 4.5, 'ISP', ha='center', fontsize=11,
            fontweight='bold', color='white')
    ax.text(8.75, 3.8, '3DNR / HDR', ha='center', fontsize=9, color='white')
    ax.text(8.75, 3.1, 'Hardware Noise\nReduction', ha='center',
            fontsize=8, color='#B2DFDB')

    # Memory
    mem = plt.Rectangle((10.5, 2.5), 2.5, 2.5, facecolor='#78909C',
                        edgecolor='white', linewidth=2)
    ax.add_patch(mem)
    ax.text(11.75, 4.2, 'LPDDR4x/5', ha='center', fontsize=10,
            fontweight='bold', color='white')
    ax.text(11.75, 3.5, '4-8GB', ha='center', fontsize=10, color='white')

    # Arrows
    style = dict(arrowstyle='->', lw=2, color='#333333')
    ax.annotate('', xy=(7.5, 5.5), xytext=(13, 6.5), arrowprops=style)
    ax.text(11, 6.8, 'Camera Input', fontsize=9, color='#333')
    ax.annotate('', xy=(12, 4), xytext=(10, 4), arrowprops=style)
    ax.annotate('', xy=(4, 3.5), xytext=(10.5, 3.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='#FF7043'))
    ax.annotate('', xy=(4.5, 3.8), xytext=(4, 3.8),
                arrowprops=dict(arrowstyle='->', lw=2, color='#7B1FA2'))
    ax.text(4.2, 4.1, 'preprocessed\nframe', fontsize=7, color='#7B1FA2')

    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    plt.suptitle('RK3576 System Architecture & Task Distribution',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = OUTPUT_DIR / 'rk3576_architecture.png'
    plt.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path.name}")


def main():
    parser = argparse.ArgumentParser(description='Low Light Preprocessing Comparison Generator')
    parser.add_argument('--input', '-i', type=str,
                        help='Input low-light image path (optional)')
    args = parser.parse_args()

    print("=" * 60)
    print("Low Light Preprocessing Comparison Generator")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.input:
        img = cv2.imread(args.input)
        if img is None:
            print(f"  Cannot read {args.input}, using simulated image.")
            img = simulate_low_light_image()
        else:
            h, w = img.shape[:2]
            if w > 800:
                img = cv2.resize(img, (800, int(h * 800 / w)))
            print(f"  Loaded: {img.shape[1]}x{img.shape[0]}")
    else:
        print("  Generating simulated low-light test image...")
        img = simulate_low_light_image()
        print(f"  Size: {img.shape[1]}x{img.shape[0]}")

    print("\n  Creating comparison charts...\n")

    create_denoising_comparison(img)
    create_pipeline_comparison(img)
    create_zoom_comparison(img)
    create_cpu_usage_chart()
    create_pipeline_diagram()
    create_noise_amplification_diagram()
    create_rk3576_arch_diagram()

    # Save test input
    test_path = OUTPUT_DIR / 'test_low_light_input.jpg'
    cv2.imwrite(str(test_path), img)
    print(f"  [OK] {test_path.name}")

    print(f"\n  All done! Files saved to: {OUTPUT_DIR.absolute()}\n")


if __name__ == '__main__':
    main()

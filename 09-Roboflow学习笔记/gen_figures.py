"""Roboflow 学习笔记 — 配图生成脚本"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.font_manager as fm
_font = r'C:\Windows\Fonts\simhei.ttf'
fm.fontManager.addfont(_font)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

OUT = r"C:\Users\29503\Desktop\AI学习笔记\09-Roboflow学习笔记"


def fig_pipeline():
    """Roboflow 完整工作流"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 3.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3)
    ax.axis('off')
    ax.set_title("Roboflow Complete Workflow", fontsize=13, fontweight='bold')

    steps = [
        (0.5, "Upload\nImages", '#E3F2FD', '#1565C0'),
        (2.0, "Annotate\n(Label)", '#FFF3E0', '#E65100'),
        (3.5, "Preprocess\n+ Augment", '#E8F5E9', '#2E7D32'),
        (5.0, "Generate\nVersion", '#F3E5F5', '#6A1B9A'),
        (6.5, "Train\nModel", '#FFEBEE', '#C62828'),
        (8.0, "Deploy\n(Inference)", '#E0F7FA', '#00695C'),
    ]

    for x, label, bg, ec in steps:
        rect = mpatches.FancyBboxPatch((x, 0.8), 1.2, 1.8, boxstyle="round,pad=0.15",
                                        facecolor=bg, edgecolor=ec, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 0.6, 1.7, label, ha='center', va='center', fontsize=9, fontweight='bold')

    for i in range(len(steps)-1):
        x1 = steps[i][0] + 1.2
        x2 = steps[i+1][0]
        ax.annotate('', xy=(x2, 1.7), xytext=(x1, 1.7),
                    arrowprops=dict(arrowstyle='->', lw=2, color='gray'))

    ax.text(0.5, 0.2, "(1) Create Project → (2) Upload → (3) Label → (4) Version → (5) Train → (6) Deploy",
            ha='center', fontsize=9, color='gray', style='italic')
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_pipeline.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_pipeline.png")


def fig_merge():
    """数据集合并示意图"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4)
    ax.axis('off')
    ax.set_title("Merge Datasets", fontsize=13, fontweight='bold')

    # Dataset A
    ax.add_patch(mpatches.FancyBboxPatch((0.5, 1.5), 2.5, 2, boxstyle="round,pad=0.1",
                                          facecolor='#BBDEFB', edgecolor='#1565C0', linewidth=2))
    ax.text(1.75, 3.2, "Dataset A", ha='center', fontsize=11, fontweight='bold', color='#1565C0')
    ax.text(1.75, 2.5, "• 100 images\n• VOC format\n• Classes: car, person", ha='center', fontsize=9)

    # Dataset B
    ax.add_patch(mpatches.FancyBboxPatch((4.0, 1.5), 2.5, 2, boxstyle="round,pad=0.1",
                                          facecolor='#C8E6C9', edgecolor='#2E7D32', linewidth=2))
    ax.text(5.25, 3.2, "Dataset B", ha='center', fontsize=11, fontweight='bold', color='#2E7D32')
    ax.text(5.25, 2.5, "• 80 images\n• COCO format\n• Classes: car, dog", ha='center', fontsize=9)

    # Arrow
    ax.annotate('', xy=(6.8, 2.5), xytext=(3.3, 2.5),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#FF6F00'))

    # Merged
    ax.add_patch(mpatches.FancyBboxPatch((7.2, 1), 2.5, 2.5, boxstyle="round,pad=0.1",
                                          facecolor='#FFE0B2', edgecolor='#E65100', linewidth=2.5))
    ax.text(8.45, 3.2, "Merged Dataset", ha='center', fontsize=11, fontweight='bold', color='#E65100')
    ax.text(8.45, 2.5, "• 180 images\n• Mixed formats\n• Classes: car, person, dog\n⚠️ Class mismatch!", ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_merge.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_merge.png")


def fig_formats():
    """标注格式对比"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    ax.axis('off')
    ax.set_title("Annotation Formats Supported by Roboflow", fontsize=13, fontweight='bold')

    formats = [
        ("YOLO (TXT)", "class x_center y_center width height\n0 0.5 0.5 0.3 0.4", '#FFF3E0'),
        ("COCO (JSON)", '{"images": [...], "annotations": [...]}', '#E3F2FD'),
        ("Pascal VOC (XML)", '<annotation><object><name>car</name>...', '#E8F5E9'),
        ("TFRecord", "TFRecord format (binary)", '#F3E5F5'),
        ("LabelMe (JSON)", '{"shapes": [{"label": "car", ...}]}', '#FFEBEE'),
        ("CreateML (JSON)", '"annotations": [{"label": "car", ...}]', '#E0F7FA'),
    ]

    for i, (name, desc, color) in enumerate(formats):
        y = 3.5 - i * 0.55
        ax.add_patch(mpatches.FancyBboxPatch((0.5, y-0.2), 2.5, 0.4, boxstyle="round,pad=0.05",
                                              facecolor=color, edgecolor='gray', linewidth=1))
        ax.text(1.75, y, name, ha='center', va='center', fontsize=9, fontweight='bold')
        ax.text(5.5, y, desc, ha='left', va='center', fontsize=8, color='gray')

    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_formats.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_formats.png")


def fig_deploy():
    """部署选项对比"""
    categories = ['Serverless API', 'Dedicated\nGPU', 'Self-Hosted\n(Docker)', 'Edge Device\n(Jetson/RK)', 'Batch\nProcessing']
    speed = [95, 90, 80, 60, 40]  # speed score
    cost = [30, 10, 60, 80, 70]   # cost efficiency (higher = cheaper)
    control = [40, 60, 85, 90, 50]

    x = np.arange(len(categories))
    fig, ax = plt.subplots(1, 1, figsize=(10, 4.5))
    w = 0.25
    ax.bar(x - w, speed, w, label='Speed', color='#43A047')
    ax.bar(x, cost, w, label='Cost Efficiency', color='#FB8C00')
    ax.bar(x + w, control, w, label='Control', color='#1E88E5')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=8)
    ax.set_ylabel("Score (0-100)", fontsize=10)
    ax.set_title("Roboflow Deployment Options Comparison", fontsize=13, fontweight='bold')
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_deploy.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_deploy.png")


# ─── Main ───
print("Generating Roboflow figures...\n")
fig_pipeline()
fig_merge()
fig_formats()
fig_deploy()
print("\nDone!")

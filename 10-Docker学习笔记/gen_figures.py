"""Docker 学习笔记 — 配图生成脚本"""
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

OUT = r"C:\Users\29503\Desktop\AI学习笔记\10-Docker学习笔记"


def fig_vm_vs_docker():
    """VM vs Docker 对比"""
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    
    # VM
    ax = axes[0]
    ax.set_xlim(0, 4); ax.set_ylim(0, 5)
    ax.set_title("Virtual Machine", fontsize=13, fontweight='bold')
    layers = [
        (0.3, 4, 3.4, 0.5, "App A", '#FFCDD2', '#C62828'),
        (0.3, 3.3, 3.4, 0.5, "App B", '#FFCDD2', '#C62828'),
        (0.3, 2.6, 3.4, 0.5, "Bins/Libs", '#FFF9C4', '#F57F17'),
        (0.3, 1.9, 3.4, 0.5, "Guest OS", '#BBDEFB', '#1565C0'),
        (0.3, 0.2, 3.4, 1.5, "Hypervisor\nHost OS\nHardware", '#C8E6C9', '#2E7D32'),
    ]
    for x, y, w, h, txt, bg, ec in layers:
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                              facecolor=bg, edgecolor=ec, linewidth=2))
        ax.text(x + w/2, y + h/2, txt, ha='center', va='center', fontsize=8, fontweight='bold')
    ax.axis('off')
    ax.text(2, 0.05, "Each VM: Guest OS ~GB, Boot ~minutes", ha='center', fontsize=8, color='gray')

    # Docker
    ax = axes[1]
    ax.set_xlim(0, 4); ax.set_ylim(0, 5)
    ax.set_title("Docker Containers", fontsize=13, fontweight='bold')
    layers = [
        (0.3, 4.2, 1.5, 0.5, "App A", '#FFCDD2', '#C62828'),
        (2.1, 4.2, 1.5, 0.5, "App B", '#FFCDD2', '#C62828'),
        (0.3, 3.4, 1.5, 0.6, "Bins/Libs", '#FFF9C4', '#F57F17'),
        (2.1, 3.4, 1.5, 0.6, "Bins/Libs", '#FFF9C4', '#F57F17'),
        (0.3, 2.4, 3.4, 0.7, "Docker Engine", '#BBDEFB', '#1565C0'),
        (0.3, 0.2, 3.4, 2.0, "Host OS\nHardware\n(Kernel)", '#C8E6C9', '#2E7D32'),
    ]
    for x, y, w, h, txt, bg, ec in layers:
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                              facecolor=bg, edgecolor=ec, linewidth=2))
        ax.text(x + w/2, y + h/2, txt, ha='center', va='center', fontsize=8, fontweight='bold')
    ax.axis('off')
    ax.text(2, 0.05, "Each container: ~MB, Boot ~seconds", ha='center', fontsize=8, color='gray')

    plt.suptitle("VM vs Docker Architecture", fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_vm_vs_docker.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_vm_vs_docker.png")


def fig_docker_architecture():
    """Docker 核心架构"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5)
    ax.axis('off')
    ax.set_title("Docker Core Architecture", fontsize=13, fontweight='bold')

    # Client
    ax.add_patch(mpatches.FancyBboxPatch((0.3, 3), 2, 1.5, boxstyle="round,pad=0.15",
                                          facecolor='#E3F2FD', edgecolor='#1565C0', linewidth=2))
    ax.text(1.3, 3.75, "Docker Client\n(docker CLI / API)", ha='center', va='center', fontsize=9, fontweight='bold')

    # Docker Host
    ax.add_patch(mpatches.FancyBboxPatch((3.5, 0.6), 5.5, 4, boxstyle="round,pad=0.15",
                                          facecolor='#F5F5F5', edgecolor='#424242', linewidth=2, linestyle='--'))
    ax.text(6.25, 4.3, "Docker Host (Daemon)", ha='center', fontsize=10, fontweight='bold', color='#424242')

    # Containers
    for i, (x, name) in enumerate([(4, "Container\nA"), (5.5, "Container\nB"), (7, "Container\nC")]):
        ax.add_patch(mpatches.FancyBboxPatch((x, 3), 1.3, 1, boxstyle="round,pad=0.08",
                                              facecolor='#FFCDD2', edgecolor='#C62828', linewidth=2))
        ax.text(x + 0.65, 3.5, name, ha='center', va='center', fontsize=8, fontweight='bold')

    # Images
    for i, (x, name) in enumerate([(4, "Image A"), (5.5, "Image B"), (7, "Image C")]):
        ax.add_patch(mpatches.FancyBboxPatch((x, 1.8), 1.3, 0.8, boxstyle="round,pad=0.08",
                                              facecolor='#FFF9C4', edgecolor='#F57F17', linewidth=2))
        ax.text(x + 0.65, 2.2, name, ha='center', va='center', fontsize=8, fontweight='bold')
        ax.plot([x + 0.65, x + 0.65], [2.8, 3], color='gray', lw=1, linestyle=':')
        ax.annotate('', xy=(x + 0.65, 3), xytext=(x + 0.65, 2.8),
                    arrowprops=dict(arrowstyle='->', lw=1, color='gray'))

    # Registry
    ax.add_patch(mpatches.FancyBboxPatch((3.5, 0.8), 6, 0.6, boxstyle="round,pad=0.08",
                                          facecolor='#C8E6C9', edgecolor='#2E7D32', linewidth=2))
    ax.text(6.5, 1.1, "Docker Registry (Docker Hub / Private)", ha='center', va='center', fontsize=9, fontweight='bold')

    # Registry to Images arrow
    ax.annotate('', xy=(6.5, 1.8), xytext=(6.5, 1.4),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='#2E7D32'))

    # Client to Docker Host
    ax.annotate('', xy=(3.5, 3.75), xytext=(2.3, 3.75),
                arrowprops=dict(arrowstyle='->', lw=2, color='#1565C0'))

    # Volumes
    ax.text(8.5, 3.5, "Volumes\n(Persistent\nData)", fontsize=8, color='#6A1B9A', fontweight='bold',
            bbox=dict(boxstyle="round", facecolor='#F3E5F5', edgecolor='#6A1B9A'))

    # Network
    ax.text(8.5, 2, "Network\n(bridge/host/\noverlay)", fontsize=8, color='#E65100', fontweight='bold',
            bbox=dict(boxstyle="round", facecolor='#FFF3E0', edgecolor='#E65100'))

    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_architecture.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_architecture.png")


def fig_dockerfile():
    """Dockerfile 分层示意"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5)
    ax.axis('off')
    ax.set_title("Docker Image Layers (Dockerfile)", fontsize=13, fontweight='bold')

    layers = [
        (0.5, 4, "FROM python:3.11-slim", "Base Image (Debian + Python)", '#E3F2FD', '#1565C0'),
        (1, 3.2, "WORKDIR /app", "Set working directory", '#BBDEFB', '#1565C0'),
        (1.5, 2.4, "COPY requirements.txt .", "Copy dependency list", '#FFF9C4', '#F57F17'),
        (2, 1.6, "RUN pip install -r req...", "Install Python packages", '#FFE0B2', '#E65100'),
        (2.5, 0.8, "COPY . .", "Copy app source", '#C8E6C9', '#2E7D32'),
        (3, 0, "CMD ['python', 'app.py']", "Start command", '#F3E5F5', '#6A1B9A'),
    ]

    for i, (offset, y, cmd, desc, bg, ec) in enumerate(layers):
        # Layer box
        ax.add_patch(mpatches.FancyBboxPatch((offset, y), 6, 0.65, boxstyle="round,pad=0.08",
                                              facecolor=bg, edgecolor=ec, linewidth=2))
        ax.text(offset + 0.3, y + 0.33, cmd, ha='left', va='center', fontsize=9, fontweight='bold')

        # Cached indicator
        if i < 4:
            ax.text(9.5, y + 0.33, "✅ CACHED", ha='center', va='center', fontsize=7,
                    color='#2E7D32', fontweight='bold',
                    bbox=dict(boxstyle="round", facecolor='#C8E6C9', edgecolor='#2E7D32'))
        else:
            ax.text(9.5, y + 0.33, "🔄 CHANGED", ha='center', va='center', fontsize=7,
                    color='#C62828', fontweight='bold',
                    bbox=dict(boxstyle="round", facecolor='#FFCDD2', edgecolor='#C62828'))
            ax.plot([0.5, 9], [y + 0.33, y + 0.33], color='red', lw=1, linestyle=':')

        # Description on right
        ax.text(7.2, y + 0.33, desc, ha='left', va='center', fontsize=8, color='gray')

    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_dockerfile.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_dockerfile.png")


def fig_network():
    """Docker 网络模式对比"""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    configs = [
        ("Bridge (Default)", ['Container\nA:80', 'Container\nB:3000', 'Container\nC:5432'],
         'Bridge', 'Host', '#BBDEFB', '#1565C0'),
        ("Host", ['Container\n:80 (host:80)', 'Container\n:3000 (host:3000)'],
         'Host Network', '', '#FFE0B2', '#E65100'),
        ("Overlay (Swarm)", ['Container\n(on node 1)', 'Container\n(on node 2)'],
         'Overlay Network', 'Node1 --- Node2', '#C8E6C9', '#2E7D32'),
    ]

    for ax, (title, containers, net, extra, bg, ec) in zip(axes, configs):
        ax.set_xlim(0, 4); ax.set_ylim(0, 4)
        ax.set_title(title, fontsize=10, fontweight='bold')
        for i, c in enumerate(containers):
            y = 2.5 - i * 1.2
            ax.add_patch(mpatches.FancyBboxPatch((0.3, y), 1.5, 0.7, boxstyle="round,pad=0.08",
                                                  facecolor=bg, edgecolor=ec, linewidth=2))
            ax.text(1.05, y + 0.35, c, ha='center', va='center', fontsize=7, fontweight='bold')
        ax.add_patch(mpatches.FancyBboxPatch((2.3, 0.5), 1.5, 3, boxstyle="round,pad=0.08",
                                              facecolor='#F5F5F5', edgecolor='#424242', linewidth=2))
        ax.text(3.05, 2, net, ha='center', va='center', fontsize=8, fontweight='bold', color='#424242')
        if extra:
            ax.text(3.05, 0.7, extra, ha='center', va='center', fontsize=7, color='gray')
        ax.axis('off')

    plt.suptitle("Docker Network Modes", fontsize=14, fontweight='bold', y=1.05)
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_network.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_network.png")


print("Generating Docker figures...\n")
fig_vm_vs_docker()
fig_docker_architecture()
fig_dockerfile()
fig_network()
print("\nDone!")

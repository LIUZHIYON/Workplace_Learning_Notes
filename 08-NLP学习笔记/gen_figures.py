"""
NLP 学习笔记 — 配图生成脚本
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# 设置中文字体 — 使用绝对路径确保生效
import matplotlib.font_manager as fm
_font_path = r'C:\Windows\Fonts\simhei.ttf'
fm.fontManager.addfont(_font_path)
_cn_font = {'fontfamily': 'SimHei'}
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DengXian', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 辅助函数：获取 FontProperties 对象
from matplotlib.font_manager import FontProperties
def get_cn_font(size=12, bold=False):
    return FontProperties(fname=_font_path, size=size, weight='bold' if bold else 'normal')

OUT = r"C:\Users\29503\Desktop\AI学习笔记\08-NLP学习笔记"

# ─── 1. NLP 技术演进时间线 ───
def fig_timeline():
    fig, ax = plt.subplots(1, 1, figsize=(14, 4))
    ax.set_xlim(1990, 2026)
    ax.set_ylim(0, 1)
    ax.axhline(0.5, color='gray', linewidth=2, linestyle='-', alpha=0.5)
    ax.axis('off')
    ax.set_title('NLP Technology Evolution Timeline', fontproperties=get_cn_font(14, bold=True))

    milestones = [
        (1993, 'Statistical\nNLP', '#B0B0B0'),
        (2003, 'NNLM\n(Bengio)', '#87CEEB'),
        (2013, 'Word2Vec\n(Mikolov)', '#4CAF50'),
        (2014, 'Seq2Seq\n+Attention', '#FF9800'),
        (2017, 'Transformer\n(Vaswani)', '#F44336'),
        (2018, 'BERT/GPT\n(Pre-train)', '#9C27B0'),
        (2020, 'GPT-3\n(175B)', '#E91E63'),
        (2022, 'ChatGPT\nInstructGPT', '#FF5722'),
        (2023, 'LLaMA/GPT-4\nOpen-source LLMs', '#2196F3'),
        (2024, 'RAG/Agents\nMultimodal', '#00BCD4'),
        (2025, 'Reasoning\nDeepSeek-R1', '#009688'),
    ]

    for i, (year, label, color) in enumerate(milestones):
        x = year
        y = 0.5
        ax.plot(x, y, 'o', markersize=18, color=color, zorder=5)
        ax.plot(x, y, 'o', markersize=14, color='white', zorder=6)
        ax.plot(x, y, 'o', markersize=10, color=color, zorder=7)
        va = 'bottom' if i % 2 == 0 else 'top'
        offset = 0.08 if va == 'bottom' else -0.08
        ax.text(x, y + offset, label, ha='center', va=va, fontsize=8,
                fontweight='bold', color=color,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, alpha=0.8))

    # English legend
    ax.text(0.5, -0.1,
            'NLP has evolved from statistical methods to deep learning and now large language models',
            ha='center', transform=ax.transAxes, fontsize=9, color='gray', style='italic')

    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_timeline.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_timeline.png")


# ─── 2. Transformer 架构图 ───
def fig_transformer():
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title("Transformer Architecture (Simplified)", fontsize=13, fontweight='bold')

    def draw_box(x, y, w, h, text, color='lightblue', ec='navy'):
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                        facecolor=color, edgecolor=ec, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=9, fontweight='bold')

    # Encoder
    draw_box(1, 7, 3, 2, "Multi-Head\nSelf-Attention", '#B3E5FC', '#0277BD')
    draw_box(1, 4.5, 3, 2, "Feed Forward\n(MLP)", '#B3E5FC', '#0277BD')
    draw_box(1, 3, 3, 1, "Add & LayerNorm", '#E1F5FE', '#0277BD')
    draw_box(0.5, 8.5, 4, 0.6, "Input Embedding", '#FFF9C4', '#F57F17')
    ax.annotate('', xy=(2.5, 7), xytext=(2.5, 8.5), arrowprops=dict(arrowstyle='->', lw=1.5))

    ax.text(0.5, 6, "×N", fontsize=12, fontweight='bold', color='#0277BD')

    # Decoder
    draw_box(6, 7, 3, 2, "Masked Multi-Head\nSelf-Attention", '#FFE0B2', '#E65100')
    draw_box(6, 4.5, 3, 2, "Cross-Attention", '#FFE0B2', '#E65100')
    draw_box(6, 2, 3, 2, "Feed Forward\n(MLP)", '#FFE0B2', '#E65100')
    draw_box(6, 0.5, 3, 1, "Linear + Softmax", '#FFE0B2', '#E65100')
    draw_box(5.5, 8.5, 4, 0.6, "Output Embedding", '#FFF9C4', '#F57F17')

    ax.text(7.5, 3.5, "×N", fontsize=12, fontweight='bold', color='#E65100')

    # Skip connections
    ax.annotate('', xy=(4, 6), xytext=(4, 8), arrowprops=dict(
        arrowstyle='->', lw=2, color='#0277BD', connectionstyle='arc3,rad=0.3'))

    # Decoder label
    ax.text(9.5, 5, "Decoder", fontsize=12, fontweight='bold', color='#E65100')
    ax.text(4.5, 8, "Encoder", fontsize=12, fontweight='bold', color='#0277BD')

    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_transformer.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_transformer.png")


# ─── 3. 模型参数规模对比图 ───
def fig_model_size():
    models = [
        'BERT-Base\n(2018)', 'BERT-Large\n(2018)', 'GPT-2\n(2019)',
        'RoBERTa\n(2019)', 'GPT-3\n(2020)', 'PaLM\n(2022)',
        'LLaMA-65B\n(2023)', 'GPT-4\n(2023)', 'LLaMA3-70B\n(2024)',
        'DeepSeek-V3\n(2024)', 'GroK-3\n(2025)'
    ]
    params = [0.11, 0.34, 1.5, 0.355, 175, 540, 65, 1800, 70, 671, 2000]

    colors = ['#64B5F6']*4 + ['#FFB74D']*2 + ['#4DB6AC']*3 + ['#E57373']*2

    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    bars = ax.bar(range(len(models)), params, color=colors, width=0.6)
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, fontsize=8)
    ax.set_ylabel("Parameters (Billions)", fontsize=12)
    ax.set_title("NLP Model Size Evolution (Parameters)", fontsize=14, fontweight='bold')
    ax.set_yscale('log')

    for bar, val in zip(bars, params):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.1,
                f'{val}B' if val < 1000 else f'{val/1000:.1f}T' if val >= 1000 else f'{val}B',
                ha='center', va='bottom', fontsize=7, rotation=45)

    legend = [
        mpatches.Patch(color='#64B5F6', label='BERT Era (Encoder)'),
        mpatches.Patch(color='#FFB74D', label='GPT Era (Decoder)'),
        mpatches.Patch(color='#4DB6AC', label='Open-source LLMs'),
        mpatches.Patch(color='#E57373', label='Frontier Models'),
    ]
    ax.legend(handles=legend, loc='upper left', fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_model_size.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_model_size.png")


# ─── 4. NLP 框架与工具流行度 ───
def fig_frameworks():
    categories = ['HuggingFace\nTransformers', 'PyTorch', 'spaCy', 'NLTK',
                  'Jieba\n(Chinese)', 'Stanza', 'LangChain', 'vLLM',
                  'LlamaIndex', 'DeepSpeed']
    values = [95, 90, 70, 55, 75, 40, 80, 50, 45, 35]
    colors = ['#FF6F00', '#E53935', '#43A047', '#1E88E5',
              '#FDD835', '#8E24AA', '#00ACC1', '#FB8C00',
              '#3949AB', '#6D4C41']

    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    bars = ax.barh(range(len(categories)), values, color=colors, height=0.6)
    ax.set_yticks(range(len(categories)))
    ax.set_yticklabels(categories, fontsize=10)
    ax.set_xlabel("Popularity Score", fontsize=12)
    ax.set_title("NLP Frameworks & Tools Popularity (2025)", fontsize=14, fontweight='bold')
    ax.set_xlim(0, 100)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{val}', ha='left', va='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_frameworks.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_frameworks.png")


# ─── 5. RAG 架构图 ───
def fig_rag():
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    ax.set_title("Retrieval-Augmented Generation (RAG) Pipeline", fontsize=14, fontweight='bold')

    def box(x, y, w, h, text, color='lightblue', ec='navy'):
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                        facecolor=color, edgecolor=ec, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=9, fontweight='bold')

    # User Query
    box(0, 3.5, 2, 1, "User\nQuery", '#FFF9C4', '#F57F17')

    # Retriever
    box(3, 3.5, 2, 1, "Retriever\n(Embedding +\nVector DB)", '#B3E5FC', '#0277BD')

    # Documents
    box(3, 1, 2, 1.8, "Document\nStore\n(PDF, Web,\nWiki)", '#FFE0B2', '#E65100')

    # Context
    box(6, 3.5, 2, 1, "Augmented\nContext", '#C8E6C9', '#2E7D32')

    # LLM
    box(8.5, 2.5, 1.5, 2, "LLM\n(GPT/LLaMA\n/DeepSeek)", '#F8BBD0', '#C2185B')

    # Answer
    box(8.5, 0.5, 1.5, 1, "Answer", '#E1BEE7', '#4527A0')

    # Arrows
    ax.annotate('', xy=(2, 4), xytext=(3, 4), arrowprops=dict(arrowstyle='->', lw=2, color='#F57F17'))
    ax.annotate('', xy=(5, 4), xytext=(6, 4), arrowprops=dict(arrowstyle='->', lw=2, color='#0277BD'))
    ax.annotate('', xy=(8, 4), xytext=(8.5, 4), arrowprops=dict(arrowstyle='->', lw=2, color='#2E7D32'))
    ax.annotate('', xy=(9.25, 2.5), xytext=(9.25, 1.5), arrowprops=dict(arrowstyle='->', lw=2, color='#C2185B'))

    # Document retrieval arrow
    ax.annotate('', xy=(4, 2.8), xytext=(4, 3.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='#E65100'))

    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_rag.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_rag.png")


# ─── 6. NLP 任务云图/柱状图 ───
def fig_tasks():
    tasks = ['Text\nClassification', 'NER', 'QA', 'Summarization',
             'Translation', 'Sentiment', 'Text\nGeneration',
             'Semantic\nSimilarity', 'Relation\nExtraction',
             'Dialogue', 'Code\nGeneration', 'RAG']
    values = [90, 85, 80, 75, 70, 88, 95, 60, 50, 65, 78, 82]
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(tasks)))

    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    bars = ax.bar(range(len(tasks)), values, color=colors, width=0.6)
    ax.set_xticks(range(len(tasks)))
    ax.set_xticklabels(tasks, fontsize=8)
    ax.set_ylabel("Usage Frequency", fontsize=12)
    ax.set_title("NLP Tasks Popularity (2025)", fontsize=14, fontweight='bold')

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                str(val), ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_tasks.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_tasks.png")


# ─── 7. Pre-training / Fine-tuning / Prompting 对比 ───
def fig_paradigms():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    data = [
        ("Traditional\nFine-tuning", ['Pre-train\n(All data)', 'Fine-tune\n(Task data)'], [0.8, 0.2],
         '#4CAF50', '#FF9800', "Train all params\nper task"),
        ("PEFT\n(LoRA/Adapter)", ['Pre-train\n(All data)', 'LoRA\n(<1% params)'], [0.8, 0.02],
         '#4CAF50', '#2196F3', "Train small\nadapters"),
        ("Prompting\n(In-Context)", ['Pre-train\n(All data)', 'Prompt\n(No training)'], [0.8, 0.001],
         '#4CAF50', '#E91E63', "No training,\njust prompt"),
    ]

    for ax, (title, labels, vals, c1, c2, desc) in zip(axes, data):
        ax.barh([0, 1], vals, color=[c1, c2], height=0.5)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlim(0, 1)
        ax.text(0.5, -0.3, desc, ha='center', fontsize=9, style='italic', color='gray')
        for i, v in enumerate(vals):
            ax.text(v + 0.02, i, f'{v*100:.0f}%', ha='left', va='center', fontsize=9, fontweight='bold')

    plt.suptitle("Paradigm Shift in NLP: Computation Distribution", fontsize=14, fontweight='bold', y=1.05)
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_paradigms.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_paradigms.png")


# ─── 8. Word Embedding 可视化 ───
def fig_embedding():
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    words = ['king', 'queen', 'prince', 'princess', 'man', 'woman', 'boy', 'girl',
             'apple', 'banana', 'orange', 'grape']
    np.random.seed(42)
    coords = np.random.randn(len(words), 2)
    # Make king-queen close, man-woman close, fruits close
    coords[0] = [2, 3];  coords[1] = [1.8, 2.5]
    coords[2] = [1.5, 2.8]; coords[3] = [1.3, 2.3]
    coords[4] = [-2, 1]; coords[5] = [-2.2, 0.3]
    coords[6] = [-1.5, 0.8]; coords[7] = [-1.7, 0.1]
    coords[8] = [0, -2]; coords[9] = [0.5, -1.5]
    coords[10] = [-0.3, -2.2]; coords[11] = [0.2, -1.8]

    colors = ['red']*4 + ['blue']*4 + ['green']*4
    for i, word in enumerate(words):
        ax.scatter(coords[i, 0], coords[i, 1], color=colors[i], s=100, alpha=0.7)
        ax.annotate(word, (coords[i, 0], coords[i, 1]), fontsize=10,
                    ha='center', va='bottom')

    # king - man + woman = queen arrow
    ax.annotate('', xy=(1.8, 2.5), xytext=(2, 3),
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    ax.text(1.7, 2.9, "king - man + woman ≈ queen", fontsize=8, fontweight='bold',
            color='red', style='italic')
    ax.set_title("Word Embedding: Semantic Relationships (PCA)", fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color='gray', lw=0.5)
    ax.axvline(0, color='gray', lw=0.5)

    legend = [mpatches.Patch(color='red', label='Royalty'),
              mpatches.Patch(color='blue', label='Gender'),
              mpatches.Patch(color='green', label='Fruits')]
    ax.legend(handles=legend, loc='upper right', fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{OUT}\\fig_embedding.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] fig_embedding.png")


# ─── Main ───
print("Generating NLP figures...\n")
fig_timeline()
fig_transformer()
fig_model_size()
fig_frameworks()
fig_rag()
fig_tasks()
fig_paradigms()
fig_embedding()
print("\nDone! All figures saved to:", OUT)

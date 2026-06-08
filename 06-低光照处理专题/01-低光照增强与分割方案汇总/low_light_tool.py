"""
低光照增强与分割工具 —— 单核2.0GHz友好版
============================================
支持：图片处理 / 视频处理 / 实时摄像头
方法：CLAHE / Gamma / Retinex / 亮度拉伸 / Zero-DCE(可选)

用法：
    python low_light_tool.py image input.jpg -o output.jpg -m clahe
    python low_light_tool.py video input.mp4 -o output.mp4 -m clahe
    python low_light_tool.py camera -m clahe --segment
"""

import cv2
import numpy as np
import argparse
import os
import time
from pathlib import Path


# ===================== 增强方法 =====================

def enhance_clahe(img, clip_limit=3.0, tile_size=8):
    """CLAHE 增强（推荐首选）"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    l_enh = clahe.apply(l)
    enhanced = cv2.merge([l_enh, a, b])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


def enhance_clahe_stretch(img, clip_limit=2.5, tile_size=8):
    """CLAHE + 自适应亮度拉伸"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    l_enh = clahe.apply(l)
    low, high = np.percentile(l_enh, [2, 98])
    l_stretched = np.clip((l_enh - low) * (255.0 / (high - low + 1e-6)), 0, 255).astype(np.uint8)
    enhanced = cv2.merge([l_stretched, a, b])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


def enhance_gamma(img, gamma=0.5):
    """Gamma 校正 (gamma<1 提亮暗部)"""
    inv = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv * 255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(img, table)


def enhance_gamma_clahe(img, gamma=0.6, clip_limit=3.0):
    """Gamma → CLAHE 串联"""
    img = enhance_gamma(img, gamma)
    return enhance_clahe(img, clip_limit)


def enhance_retinex_ssr(img, sigma=80):
    """Single Scale Retinex"""
    img_f = np.float32(img) + 1.0
    blur = cv2.GaussianBlur(img_f, (0, 0), sigma)
    retinex = np.log(img_f) - np.log(blur)
    retinex = cv2.normalize(retinex, None, 0, 255, cv2.NORM_MINMAX)
    return np.uint8(retinex)


def enhance_retinex_msr(img, sigmas=[15, 80, 250]):
    """Multi-Scale Retinex"""
    img_f = np.float32(img) + 1.0
    retinex = np.zeros_like(img_f)
    for sigma in sigmas:
        blur = cv2.GaussianBlur(img_f, (0, 0), sigma)
        retinex += np.log(img_f) - np.log(blur)
    retinex /= len(sigmas)
    retinex = cv2.normalize(retinex, None, 0, 255, cv2.NORM_MINMAX)
    return np.uint8(retinex)


def enhance_adaptive_brightness(img, low_pct=2, high_pct=98):
    """自适应亮度拉伸"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    low, high = np.percentile(gray, [low_pct, high_pct])
    stretched = np.clip((gray - low) * (255.0 / (high - low + 1e-6)), 0, 255).astype(np.uint8)
    return cv2.cvtColor(stretched, cv2.COLOR_GRAY2BGR)


# ===================== 分割方法 =====================

def segment_otsu(luma, invert=False):
    """Otsu 二值化分割"""
    _, mask = cv2.threshold(luma, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if invert:
        mask = cv2.bitwise_not(mask)
    return mask


def segment_adaptive(luma, block_size=31, c=2, invert=False):
    """自适应阈值分割（适合不均匀光照）"""
    mask = cv2.adaptiveThreshold(luma, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, block_size, c)
    if invert:
        mask = cv2.bitwise_not(mask)
    return mask


def segment_kmeans(img, k=2):
    """K-Means 聚类分割（地板/墙壁分为2类）"""
    data = img.reshape(-1, 3).astype(np.float32)
    _, labels, centers = cv2.kmeans(data, k, None,
                                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0),
                                    10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    result = centers[labels.flatten()].reshape(img.shape)
    mask = labels.reshape(img.shape[:2]).astype(np.uint8) * 255 // (k - 1)
    return mask, result


# ===================== 通用处理 =====================

ENHANCE_METHODS = {
    "clahe":         enhance_clahe,
    "clahe_stretch": enhance_clahe_stretch,
    "gamma":         enhance_gamma,
    "gamma_clahe":   enhance_gamma_clahe,
    "retinex_ssr":   enhance_retinex_ssr,
    "retinex_msr":   enhance_retinex_msr,
    "brightness":    enhance_adaptive_brightness,
}

SEGMENT_METHODS = {
    "otsu":     segment_otsu,
    "adaptive": segment_adaptive,
    "kmeans":   segment_kmeans,
}


def process_frame(frame, method="clahe", segment=None, segment_invert=False, visualize=False, method_fn=None):
    """处理单帧图像"""
    # 增强：优先用传入的函数，否则按名称查找
    if method_fn is not None:
        enhancer = method_fn
    else:
        enhancer = ENHANCE_METHODS.get(method, enhance_clahe)
    enhanced = enhancer(frame)

    if segment:
        # 取亮度通道做分割
        luma = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
        segmenter = SEGMENT_METHODS.get(segment, segment_otsu)
        if segment == "kmeans":
            mask, _ = segment_kmeans(enhanced)
        else:
            mask = segmenter(luma, invert=segment_invert)

        # 形态学去噪
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        if visualize:
            # 覆盖半透明 mask 在增强图上
            overlay = enhanced.copy()
            overlay[mask > 0] = (0, 200, 0)  # 墙壁/目标区域标绿
            blended = cv2.addWeighted(enhanced, 0.7, overlay, 0.3, 0)
            return blended, mask, enhanced
        return enhanced, mask, None

    return enhanced, None, None


# ===================== 图片处理 =====================

def process_image(input_path, output_path, method="clahe",
                  segment=None, segment_invert=False, visualize=False,
                  method_fn=None):
    img = cv2.imread(str(input_path))
    if img is None:
        print(f"❌ 无法读取图片: {input_path}")
        return False

    print(f"📷 输入: {input_path} ({img.shape[1]}×{img.shape[0]})")
    print(f"⚙️  增强方法: {method}", end="")
    if segment:
        print(f" + 分割: {segment}", end="")
    print()

    t0 = time.time()
    result, mask, enhanced = process_frame(img, method, segment, segment_invert, visualize, method_fn)
    t = (time.time() - t0) * 1000

    print(f"⏱️  耗时: {t:.1f}ms")

    cv2.imwrite(str(output_path), result)
    print(f"💾 已保存: {output_path}")

    if mask is not None:
        mask_path = output_path.with_stem(output_path.stem + "_mask")
        cv2.imwrite(str(mask_path), mask)
        print(f"💾 已保存: {mask_path}")

    return True


# ===================== 视频处理 =====================

def process_video(input_path, output_path, method="clahe",
                  segment=None, segment_invert=False, visualize=False,
                  max_frames=None, show=False, method_fn=None):
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        print(f"❌ 无法读取视频: {input_path}")
        return False

    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))

    print(f"🎬 输入: {input_path} ({w}×{h}, {fps:.1f}FPS, {total}帧)")
    print(f"⚙️  增强: {method}", end="")
    if segment:
        print(f" + 分割: {segment}", end="")
    print()

    frame_count = 0
    times = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        t0 = time.time()
        result, mask, _ = process_frame(frame, method, segment, segment_invert, visualize, method_fn)
        times.append((time.time() - t0) * 1000)

        out.write(result)
        frame_count += 1

        if show:
            cv2.imshow("Low Light Enhancement", result)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        if frame_count % 30 == 0:
            avg = np.mean(times[-30:])
            print(f"  帧 {frame_count}/{total}  |  平均 {avg:.1f}ms  |  {1000/avg:.1f}FPS")

        if max_frames and frame_count >= max_frames:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    avg_time = np.mean(times)
    print(f"\n✅ 完成！处理了 {frame_count} 帧")
    print(f"⏱️  平均每帧: {avg_time:.1f}ms  |  等效 FPS: {1000/avg_time:.1f}")
    print(f"💾 已保存: {output_path}")
    return True


# ===================== 摄像头实时 =====================

def process_camera(method="clahe", segment=None, segment_invert=False,
                   visualize=False, camera_id=0, width=320, height=240,
                   method_fn=None):
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if not cap.isOpened():
        print(f"❌ 无法打开摄像头 #{camera_id}")
        return

    print(f"📷 摄像头 #{camera_id} 已开启 ({width}×{height})")
    print(f"⚙️  增强: {method}", end="")
    if segment:
        print(f" + 分割: {segment}", end="")
    print("\n按 Q 退出，按 S 保存当前帧\n")

    times = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        t0 = time.time()
        result, mask, _ = process_frame(frame, method, segment, segment_invert, visualize, method_fn)
        times.append((time.time() - t0) * 1000)

        # 显示信息
        avg = np.mean(times[-30:])
        info = f"{method.upper()} | {avg:.0f}ms | Q:退出 S:保存"
        cv2.putText(result, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2)

        # 并排显示原图
        display = np.hstack([frame, result])
        cv2.imshow("Low Light Tool (原图 | 增强)", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("s"):
            save_path = f"capture_{frame_idx:04d}.jpg"
            cv2.imwrite(save_path, result)
            print(f"💾 已保存: {save_path}")
            frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()

    if times:
        print(f"\n📊 平均: {np.mean(times):.1f}ms  |  峰值: {np.mean(times[-5:]):.1f}ms")


# ===================== 主入口 =====================

def main():
    parser = argparse.ArgumentParser(
        description="低光照增强与分割工具 - 单核2.0GHz友好版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 图片处理
  python low_light_tool.py image test.jpg -o out.jpg -m clahe
  python low_light_tool.py image test.jpg -o out.jpg -m clahe_stretch --segment otsu
  python low_light_tool.py image test.jpg -o out.jpg -m gamma --gamma 0.4

  # 视频处理
  python low_light_tool.py video input.mp4 -o output.mp4 -m clahe
  python low_light_tool.py video input.mp4 -o output.mp4 -m retinex_msr --segment adaptive

  # 摄像头实时
  python low_light_tool.py camera -m clahe_stretch --segment otsu --visualize
  python low_light_tool.py camera -m gamma_clahe --width 320 --height 240

可用增强方法: {enhance_list}
可用分割方法: {segment_list}
        """.format(
            enhance_list=", ".join(ENHANCE_METHODS.keys()),
            segment_list=", ".join(SEGMENT_METHODS.keys())
        )
    )

    sub = parser.add_subparsers(dest="mode", required=True, help="模式")

    # image
    p_img = sub.add_parser("image", help="处理单张图片")
    p_img.add_argument("input", help="输入图片路径")
    p_img.add_argument("-o", "--output", default=None, help="输出路径（默认自动生成）")
    p_img.add_argument("-m", "--method", default="clahe", choices=ENHANCE_METHODS.keys(), help="增强方法")
    p_img.add_argument("--gamma", type=float, default=0.5, help="Gamma 值 (仅 gamma/gamma_clahe)")
    p_img.add_argument("--segment", default=None, choices=SEGMENT_METHODS.keys(), help="分割方法")
    p_img.add_argument("--invert", action="store_true", help="反转分割 mask")
    p_img.add_argument("--visualize", action="store_true", help="可视化分割结果（半透明覆盖）")

    # video
    p_vid = sub.add_parser("video", help="处理视频文件")
    p_vid.add_argument("input", help="输入视频路径")
    p_vid.add_argument("-o", "--output", default=None, help="输出路径")
    p_vid.add_argument("-m", "--method", default="clahe", choices=ENHANCE_METHODS.keys(), help="增强方法")
    p_vid.add_argument("--gamma", type=float, default=0.5)
    p_vid.add_argument("--segment", default=None, choices=SEGMENT_METHODS.keys(), help="分割方法")
    p_vid.add_argument("--invert", action="store_true")
    p_vid.add_argument("--visualize", action="store_true")
    p_vid.add_argument("--max-frames", type=int, default=None, help="最大处理帧数")
    p_vid.add_argument("--show", action="store_true", help="实时预览")

    # camera
    p_cam = sub.add_parser("camera", help="实时摄像头处理")
    p_cam.add_argument("-m", "--method", default="clahe", choices=ENHANCE_METHODS.keys(), help="增强方法")
    p_cam.add_argument("--gamma", type=float, default=0.5)
    p_cam.add_argument("--segment", default=None, choices=SEGMENT_METHODS.keys(), help="分割方法")
    p_cam.add_argument("--invert", action="store_true")
    p_cam.add_argument("--visualize", action="store_true")
    p_cam.add_argument("--camera-id", type=int, default=0, help="摄像头编号")
    p_cam.add_argument("--width", type=int, default=320, help="摄像头宽度")
    p_cam.add_argument("--height", type=int, default=240, help="摄像头高度")

    args = parser.parse_args()

    # gamma 参数通过 lambda 闭包传入
    method_fn = ENHANCE_METHODS.get(args.method, enhance_clahe)
    gamma_val = getattr(args, "gamma", 0.5)
    if args.method == "gamma":
        method_fn = lambda img, g=gamma_val: enhance_gamma(img, g)
    elif args.method == "gamma_clahe":
        method_fn = lambda img, g=gamma_val: enhance_gamma_clahe(img, g)

    if args.mode == "image":
        inp = Path(args.input)
        if args.output is None:
            out = inp.parent / f"{inp.stem}_{args.method}{inp.suffix}"
        else:
            out = Path(args.output)
        process_image(inp, out, args.method, args.segment, args.invert, args.visualize, method_fn)

    elif args.mode == "video":
        inp = Path(args.input)
        if args.output is None:
            out = inp.parent / f"{inp.stem}_{args.method}.mp4"
        else:
            out = Path(args.output)
        process_video(inp, out, args.method, args.segment, args.invert,
                      args.visualize, args.max_frames, args.show, method_fn)

    elif args.mode == "camera":
        process_camera(args.method, args.segment, args.invert,
                       args.visualize, args.camera_id, args.width, args.height, method_fn)


if __name__ == "__main__":
    main()

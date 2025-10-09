#!/usr/bin/env python3
from pathlib import Path
import argparse, time, tarfile, sys, subprocess, shutil
import zstandard as zstd
from tqdm import tqdm

def parse_args():
    p = argparse.ArgumentParser(
        description="将若干文件夹中的 PNG 以流式方式打包为 tar，并用 zstd 压缩（.tar.zst）"
    )
    # 至少提供其一：--folders 或 --folders-file
    p.add_argument(
        "-f", "--folders",
        nargs="+",
        help="要压缩的文件夹路径（可多个）"
    )
    p.add_argument(
        "--folders-file",
        help="从文本文件读取文件夹列表（每行一个路径，支持相对/绝对路径）"
    )
    p.add_argument(
        "-o", "--output",
        required=True,
        help="输出 .tar.zst 文件路径，例如 /opt/notebooks/left_automorph_2029.tar.zst"
    )
    p.add_argument(
        "--suffixes",
        nargs="+",
        default=[".png", ".PNG"],
        help="仅包含这些后缀（默认：.png .PNG）"
    )
    p.add_argument(
        "--level",
        type=int,
        default=1,
        help="Zstd 压缩等级，1~3 速度最佳；更高更小但更慢（默认 1）"
    )
    p.add_argument(
        "--threads",
        type=int,
        default=0,
        help="Zstd 线程数，0 表示自动按 CPU 核心数（默认 0）"
    )
    p.add_argument(
        "--no-progress",
        action="store_true",
        help="关闭 tqdm 进度条"
    )
    return p.parse_args()

def normalize_suffixes(suffixes):
    norm = set()
    for s in suffixes:
        s = s.strip()
        if not s:
            continue
        if not s.startswith("."):
            s = "." + s
        norm.add(s)
    return norm

def add_pngs_to_tar_stream(folders, include_suffixes, compressor_fileobj, show_progress=True):
    """将多个文件夹中的匹配后缀文件流式写入 tar（tar 的目标是 zstd 包裹的 fileobj）"""
    with tarfile.open(fileobj=compressor_fileobj, mode="w|") as tar:  # 流式写入，几乎不占额外内存
        for root in folders:
            root = Path(root)
            if not root.is_dir():
                print(f"[WARN] 跳过不存在目录：{root}")
                continue

            files = [p for p in root.rglob("*") if p.is_file() and p.suffix in include_suffixes]
            iterator = tqdm(files, desc=f"Packing {root.name}", unit="file", disable=not show_progress)

            for p in iterator:
                # 归档内路径：以顶层目录名为前缀，避免跨目录重名
                arcname = Path(root.name) / p.relative_to(root)
                tar.add(p, arcname=str(arcname))

def main():
    args = parse_args()

    # 组装文件夹列表
    folders = []
    if args.folders_file:
        txt = Path(args.folders_file)
        if not txt.is_file():
            print(f"[ERROR] 列表文件不存在：{txt}", file=sys.stderr)
            sys.exit(2)
        with txt.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    folders.append(line)

    if args.folders:
        folders.extend(args.folders)

    if not folders:
        print("[ERROR] 必须提供 --folders 或 --folders-file 中的至少一个。", file=sys.stderr)
        sys.exit(2)

    include_suffixes = normalize_suffixes(args.suffixes)
    archive_path = Path(args.output)

    # 创建输出目录
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    # 压缩上下文
    cctx = zstd.ZstdCompressor(level=args.level, threads=args.threads)

    start = time.time()
    with open(archive_path, "wb") as fout:
        with cctx.stream_writer(fout) as zfh:
            add_pngs_to_tar_stream(
                folders=folders,
                include_suffixes=include_suffixes,
                compressor_fileobj=zfh,
                show_progress=not args.no_progress
            )

    elapsed = time.time() - start
    print(f"完成：{archive_path}  用时 {elapsed:.2f}s")

if __name__ == "__main__":
    main()

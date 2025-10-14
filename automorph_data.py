"""Utility helpers for preparing the AutoMorph working directories."""

import argparse
import os
import shutil


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _ensure_symlink(target: str, link_path: str) -> None:
    if os.path.islink(link_path):
        existing_target = os.readlink(link_path)
        if existing_target == target:
            return
        os.unlink(link_path)
    elif os.path.exists(link_path):
        if os.path.isdir(link_path):
            shutil.rmtree(link_path)
        else:
            os.remove(link_path)
    os.symlink(target, link_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Prepare AutoMorph runtime directories.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--image_folder', required=True, help='Directory containing the input images.')
    parser.add_argument('--result_folder', required=True, help='Directory that stores AutoMorph outputs.')
    parser.add_argument('--runtime_base', required=True, help='Temporary directory used to mimic legacy layout.')
    args = parser.parse_args()

    image_folder = os.path.abspath(args.image_folder)
    result_folder = os.path.abspath(args.result_folder)
    runtime_base = os.path.abspath(args.runtime_base)

    _ensure_dir(result_folder)
    for stage in ('M0', 'M1', 'M2', 'M3'):
        _ensure_dir(os.path.join(result_folder, stage))

    _ensure_dir(runtime_base)
    _ensure_symlink(image_folder, os.path.join(runtime_base, 'images'))
    _ensure_symlink(result_folder, os.path.join(runtime_base, 'Results'))


if __name__ == '__main__':
    main()


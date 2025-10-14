"""Utility for creating the resolution lookup CSV used by AutoMorph."""

import argparse
import os
import shutil
from typing import List

import pandas as pd


def _list_images(image_folder: str) -> List[str]:
    """Return a sorted list of image file names within ``image_folder``."""

    if os.path.exists(os.path.join(image_folder, ".ipynb_checkpoints")):
        shutil.rmtree(os.path.join(image_folder, ".ipynb_checkpoints"))

    return [
        name
        for name in sorted(os.listdir(image_folder))
        if not name.startswith(".") and os.path.isfile(os.path.join(image_folder, name))
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate resolution CSV for AutoMorph runs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--image_folder",
        required=True,
        help="Folder that contains the original fundus images.",
    )
    parser.add_argument(
        "--output_csv",
        required=True,
        help="Destination CSV file that will store the resolution table.",
    )
    parser.add_argument(
        "--pixel_resolution",
        type=float,
        default=0.008,
        help="Pixel resolution (in mm) to assign to each image when metadata is absent.",
    )

    args = parser.parse_args()
    image_folder = os.path.abspath(args.image_folder)
    output_csv = os.path.abspath(args.output_csv)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    image_list = _list_images(image_folder)
    res_list = [args.pixel_resolution for _ in image_list]

    df = pd.DataFrame({"fundus": image_list, "res": res_list})
    df.to_csv(output_csv, index=False, encoding="utf8")


if __name__ == "__main__":
    main()

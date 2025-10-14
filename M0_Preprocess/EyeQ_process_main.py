"""Pre-processing entry point for the AutoMorph M0 stage."""

import argparse
import os
import shutil
from typing import List

import pandas as pd
from PIL import ImageFile

import fundus_prep as prep

ImageFile.LOAD_TRUNCATED_IMAGES = True


def _list_images(image_folder: str) -> List[str]:
    return [
        name
        for name in sorted(os.listdir(image_folder))
        if not name.startswith('.')
    ]


def process(image_list: List[str], image_folder: str, result_folder: str, resolution_csv: str) -> None:
    radius_list = []
    centre_list_w = []
    centre_list_h = []
    name_list = []
    path_list = []
    list_resolution = []
    scale_resolution = []

    resolution_list = pd.read_csv(resolution_csv)

    output_image_dir = os.path.join(result_folder, 'M0', 'images')
    os.makedirs(output_image_dir, exist_ok=True)

    for image_path in image_list:
        dst_image = os.path.join(image_folder, image_path)
        output_image_path = os.path.join(
            output_image_dir, image_path.split('.')[0] + '.png'
        )
        if os.path.exists(output_image_path):
            print('continue...')
            continue
        try:
            resolution_ = resolution_list['res'][
                resolution_list['fundus'] == image_path
            ].values[0]
            list_resolution.append(resolution_)
            img = prep.imread(dst_image)
            r_img, borders, mask, r_img, radius_list, centre_list_w, centre_list_h = prep.process_without_gb(
                img,
                img,
                radius_list,
                centre_list_w,
                centre_list_h,
            )
            prep.imwrite(output_image_path, r_img)
            name_list.append(image_path.split('.')[0] + '.png')
            path_list.append(output_image_path)

        except Exception:  # noqa: BLE001
            pass

    scale_list = [a * 2 / 912 for a in radius_list]
    scale_resolution = [a * b * 1000 for a, b in zip(list_resolution, scale_list)]
    Data4stage2 = pd.DataFrame(
        {
            'Name': name_list,
            'Path': path_list,
            'centre_w': centre_list_w,
            'centre_h': centre_list_h,
            'radius': radius_list,
            'Scale': scale_list,
            'Scale_resolution': scale_resolution,
        }
    )
    crop_info_path = os.path.join(result_folder, 'M0', 'crop_info.csv')
    Data4stage2.to_csv(crop_info_path, index=None, encoding='utf8')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Preprocess retinal images for AutoMorph',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--image_folder', required=True, help='Directory containing original images.')
    parser.add_argument('--result_folder', required=True, help='Directory where M0 results are stored.')
    parser.add_argument(
        '--resolution_csv',
        required=True,
        help='CSV file containing the resolution mapping produced by generate_resolution.py.',
    )
    args = parser.parse_args()

    image_folder = os.path.abspath(args.image_folder)
    result_folder = os.path.abspath(args.result_folder)
    resolution_csv = os.path.abspath(args.resolution_csv)

    checkpoints = os.path.join(image_folder, '.ipynb_checkpoints')
    if os.path.exists(checkpoints):
        shutil.rmtree(checkpoints)
    image_list = _list_images(image_folder)

    process(image_list, image_folder, result_folder, resolution_csv)

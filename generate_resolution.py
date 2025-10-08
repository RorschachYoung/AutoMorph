import argparse
import os
from pathlib import Path
import pandas as pd

DEFAULT_PIXEL_RESOLUTION = 0.008


def build_dataframe(image_folder: Path, pixel_resolution: float) -> pd.DataFrame:
    images = [entry.name for entry in sorted(image_folder.iterdir()) if entry.is_file()]
    return pd.DataFrame({'fundus': images, 'res': [pixel_resolution] * len(images)})


def main() -> str:
    parser = argparse.ArgumentParser(description='Generate resolution_information.csv for AutoMorph runs.')
    parser.add_argument('--image_folder', required=True, help='Folder containing input images.')
    parser.add_argument('--result_folder', help='Folder where pipeline results are stored.')
    parser.add_argument('--output', help='Explicit path where resolution_information.csv should be written.')
    parser.add_argument('--pixel_resolution', type=float, default=None, help='Pixel resolution value to use for all images.')
    args = parser.parse_args()

    image_path = Path(args.image_folder).expanduser().resolve()
    if not image_path.exists():
        raise FileNotFoundError(f'Image folder {image_path} does not exist')

    result_path = Path(args.result_folder).expanduser().resolve() if args.result_folder else None

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
    elif result_path is not None:
        output_path = result_path / 'resolution_information.csv'
    else:
        output_path = image_path.parent / 'resolution_information.csv'

    pixel_resolution = args.pixel_resolution
    if pixel_resolution is None:
        pixel_resolution = os.getenv('AUTOMORPH_PIXEL_RESOLUTION')
        pixel_resolution = float(pixel_resolution) if pixel_resolution else DEFAULT_PIXEL_RESOLUTION

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = build_dataframe(image_path, pixel_resolution)
    df.to_csv(output_path, index=False, encoding='utf8')

    print(str(output_path))
    return str(output_path)


if __name__ == '__main__':
    main()

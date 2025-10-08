import shutil
import os
import pandas as pd
from argparse import ArgumentParser
from pathlib import Path
import tempfile
import atexit

DEFAULT_AUTOMORPH_DATA = os.getenv('AUTOMORPH_DATA','.')


def prepare_automorph_data(image_folder, result_folder):

    image_path = Path(image_folder).expanduser().resolve()
    result_path = Path(result_folder).expanduser().resolve()

    image_path.mkdir(parents=True, exist_ok=True)
    result_path.mkdir(parents=True, exist_ok=True)

    if (
        image_path.name.lower() == 'images'
        and result_path.name.lower() == 'results'
        and image_path.parent == result_path.parent
    ):
        return str(image_path.parent)

    temp_dir = Path(tempfile.mkdtemp(prefix='automorph_data_'))
    atexit.register(shutil.rmtree, temp_dir, ignore_errors=True)

    images_link = temp_dir / 'images'
    results_link = temp_dir / 'Results'
    if not images_link.exists():
        images_link.symlink_to(image_path, target_is_directory=True)
    if not results_link.exists():
        results_link.symlink_to(result_path, target_is_directory=True)

    resolution_link = temp_dir / 'resolution_information.csv'
    for candidate in (
        image_path.parent / 'resolution_information.csv',
        result_path.parent / 'resolution_information.csv',
    ):
        if candidate.exists() and not resolution_link.exists():
            resolution_link.symlink_to(candidate)
            break

    return str(temp_dir)


def main():
    parser = ArgumentParser(description='Merge AutoMorph CSV outputs')
    parser.add_argument(
        '--image_folder',
        default=str(Path(DEFAULT_AUTOMORPH_DATA) / 'images'),
        help='Path to the folder containing input images'
    )
    parser.add_argument(
        '--result_folder',
        default=str(Path(DEFAULT_AUTOMORPH_DATA) / 'Results'),
        help='Path to the AutoMorph results folder'
    )
    args = parser.parse_args()

    automorph_base = prepare_automorph_data(args.image_folder, args.result_folder)
    os.environ['AUTOMORPH_DATA'] = automorph_base

    # merge all csvs
    Disc_whole_image = pd.read_csv(f'{automorph_base}/Results/M3/Disc_centred/Disc_Measurement.csv')
    Disc_zone_b = pd.read_csv(f'{automorph_base}/Results/M3/Disc_centred/Disc_Zone_B_Measurement.csv')
    Disc_zone_c = pd.read_csv(f'{automorph_base}/Results/M3/Disc_centred/Disc_Zone_C_Measurement.csv')

    Macular_whole_image = pd.read_csv(f'{automorph_base}/Results/M3/Macular_centred/Macular_Measurement.csv')
    Macular_zone_b = pd.read_csv(f'{automorph_base}/Results/M3/Macular_centred/Macular_Zone_B_Measurement.csv')
    Macular_zone_c = pd.read_csv(f'{automorph_base}/Results/M3/Macular_centred/Macular_Zone_C_Measurement.csv')

    Disc_zone = Disc_zone_b.merge(Disc_zone_c, how='outer', on=['Name', 'Disc_height', 'Disc_width', 'Cup_height', 'Cup_width',
                                                                'CDR_vertical', 'CDR_horizontal'], suffixes=('_zone_b', '_zone_c'))

    Disc_all = Disc_whole_image.merge(Disc_zone, how='outer', on=['Name', 'Disc_height', 'Disc_width', 'Cup_height', 'Cup_width',
                                                                  'CDR_vertical', 'CDR_horizontal'])


    Macular_zone = Macular_zone_b.merge(Macular_zone_c, how='outer', on=['Name', 'Disc_height', 'Disc_width', 'Cup_height', 'Cup_width',
                                                                         'CDR_vertical', 'CDR_horizontal'], suffixes=('_zone_b', '_zone_c'))

    Macular_all = Macular_whole_image.merge(Macular_zone, how='outer', on=['Name', 'Disc_height', 'Disc_width', 'Cup_height', 'Cup_width',
                                                                           'CDR_vertical', 'CDR_horizontal'])


    # replace all -1 with empty string
    Disc_all.replace(-1, "", inplace=True)
    Macular_all.replace(-1, "", inplace=True)

    Disc_all.to_csv(f'{automorph_base}/Results/M3/Disc_Features.csv', index=False)
    Macular_all.to_csv(f'{automorph_base}/Results/M3/Macular_Features.csv', index=False)

    # remove the sub csvs
    shutil.rmtree(f'{automorph_base}/Results/M3/Disc_centred/')
    shutil.rmtree(f'{automorph_base}/Results/M3/Macular_centred/')


if __name__ == '__main__':
    main()


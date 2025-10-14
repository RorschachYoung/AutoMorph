"""Merge stage M3 feature CSV files into summary outputs."""

import argparse
import os
import shutil

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Merge AutoMorph feature CSV files.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--image_folder', type=str, default=None,
                        help='Original image directory (unused here).')
    parser.add_argument('--result_folder', type=str, required=True,
                        help='Root directory for AutoMorph results.')
    args = parser.parse_args()

    result_folder = os.path.abspath(args.result_folder)

    disc_centred_dir = os.path.join(result_folder, 'M3', 'Disc_centred')
    macular_centred_dir = os.path.join(result_folder, 'M3', 'Macular_centred')

    disc_whole_image = pd.read_csv(os.path.join(disc_centred_dir, 'Disc_Measurement.csv'))
    disc_zone_b = pd.read_csv(os.path.join(disc_centred_dir, 'Disc_Zone_B_Measurement.csv'))
    disc_zone_c = pd.read_csv(os.path.join(disc_centred_dir, 'Disc_Zone_C_Measurement.csv'))

    macular_whole_image = pd.read_csv(os.path.join(macular_centred_dir, 'Macular_Measurement.csv'))
    macular_zone_b = pd.read_csv(os.path.join(macular_centred_dir, 'Macular_Zone_B_Measurement.csv'))
    macular_zone_c = pd.read_csv(os.path.join(macular_centred_dir, 'Macular_Zone_C_Measurement.csv'))

    disc_zone = disc_zone_b.merge(
        disc_zone_c,
        how='outer',
        on=['Name', 'Disc_height', 'Disc_width', 'Cup_height', 'Cup_width', 'CDR_vertical', 'CDR_horizontal'],
        suffixes=('_zone_b', '_zone_c'),
    )

    disc_all = disc_whole_image.merge(
        disc_zone,
        how='outer',
        on=['Name', 'Disc_height', 'Disc_width', 'Cup_height', 'Cup_width', 'CDR_vertical', 'CDR_horizontal'],
    )

    macular_zone = macular_zone_b.merge(
        macular_zone_c,
        how='outer',
        on=['Name', 'Disc_height', 'Disc_width', 'Cup_height', 'Cup_width', 'CDR_vertical', 'CDR_horizontal'],
        suffixes=('_zone_b', '_zone_c'),
    )

    macular_all = macular_whole_image.merge(
        macular_zone,
        how='outer',
        on=['Name', 'Disc_height', 'Disc_width', 'Cup_height', 'Cup_width', 'CDR_vertical', 'CDR_horizontal'],
    )

    disc_all.replace(-1, '', inplace=True)
    macular_all.replace(-1, '', inplace=True)

    disc_all.to_csv(os.path.join(result_folder, 'M3', 'Disc_Features.csv'), index=False)
    macular_all.to_csv(os.path.join(result_folder, 'M3', 'Macular_Features.csv'), index=False)

    shutil.rmtree(disc_centred_dir)
    shutil.rmtree(macular_centred_dir)


if __name__ == '__main__':
    main()

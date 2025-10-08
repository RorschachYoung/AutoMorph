import numpy as np
import pandas as pd
import shutil
import os
from argparse import ArgumentParser
from pathlib import Path
import tempfile
import atexit

DEFAULT_AUTOMORPH_DATA = os.getenv('AUTOMORPH_DATA', '..')


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
    parser = ArgumentParser(description='Merge AutoMorph quality assessment results')
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

    result_Eyepacs = Path(automorph_base) / 'Results' / 'M1' / 'results_ensemble.csv'

    good_quality_dir = Path(automorph_base) / 'Results' / 'M1' / 'Good_quality'
    bad_quality_dir = Path(automorph_base) / 'Results' / 'M1' / 'Bad_quality'
    good_quality_dir.mkdir(parents=True, exist_ok=True)
    bad_quality_dir.mkdir(parents=True, exist_ok=True)

    result_Eyepacs_ = pd.read_csv(result_Eyepacs)

    Eyepacs_pre = result_Eyepacs_['Prediction']
    Eyepacs_bad_mean = result_Eyepacs_['softmax_bad']
    Eyepacs_usable_sd = result_Eyepacs_['usable_sd']
    name_list = result_Eyepacs_['Name']

    Eye_good = 0
    Eye_bad = 0

    for i in range(len(name_list)):

        if Eyepacs_pre[i]==0:
            Eye_good+=1
            shutil.copy(name_list[i], good_quality_dir)
        elif (Eyepacs_pre[i]==1) and (Eyepacs_bad_mean[i]<0.25):
        #elif (Eyepacs_pre[i]==1) and (Eyepacs_bad_mean[i]<0.25) and (Eyepacs_usable_sd[i]<0.1):
            Eye_good+=1
            shutil.copy(name_list[i], good_quality_dir)
        else:
            Eye_bad+=1
            shutil.copy(name_list[i], bad_quality_dir)
            #shutil.copy(name_list[i], '../Results/M1/Good_quality/')


    print('Gradable cases by EyePACS_QA is {} '.format(Eye_good))
    print('Ungradable cases by EyePACS_QA is {} '.format(Eye_bad))


if __name__ == '__main__':
    main()

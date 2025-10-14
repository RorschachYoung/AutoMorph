import argparse
import os
import shutil

import numpy as np
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Split quality assessment results into good/bad folders.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--image_folder', type=str, default=None,
                        help='Original image directory (unused for this step).')
    parser.add_argument('--result_folder', type=str, required=True,
                        help='Root directory for AutoMorph results.')
    args = parser.parse_args()

    result_folder = os.path.abspath(args.result_folder)

    result_Eyepacs = os.path.join(result_folder, 'M1', 'results_ensemble.csv')

    good_dir = os.path.join(result_folder, 'M1', 'Good_quality')
    bad_dir = os.path.join(result_folder, 'M1', 'Bad_quality')
    os.makedirs(good_dir, exist_ok=True)
    os.makedirs(bad_dir, exist_ok=True)

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
        shutil.copy(name_list[i], good_dir)
    elif (Eyepacs_pre[i]==1) and (Eyepacs_bad_mean[i]<0.25):
    #elif (Eyepacs_pre[i]==1) and (Eyepacs_bad_mean[i]<0.25) and (Eyepacs_usable_sd[i]<0.1):
        Eye_good+=1
        shutil.copy(name_list[i], good_dir)
    else:
        Eye_bad+=1
        shutil.copy(name_list[i], bad_dir)
        #shutil.copy(name_list[i], '../Results/M1/Good_quality/')


    print('Gradable cases by EyePACS_QA is {} '.format(Eye_good))
    print('Ungradable cases by EyePACS_QA is {} '.format(Eye_bad))


if __name__ == '__main__':
    main()

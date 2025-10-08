import fundus_prep as prep
import os
import pandas as pd
from PIL import ImageFile
import shutil
from argparse import ArgumentParser
from pathlib import Path
import tempfile
import atexit

ImageFile.LOAD_TRUNCATED_IMAGES = True

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


AUTOMORPH_DATA = DEFAULT_AUTOMORPH_DATA

def process(image_list, save_path):
    
    radius_list = []
    centre_list_w = []
    centre_list_h = []
    name_list = []
    list_resolution = []
    scale_resolution = []
    
    resolution_list = pd.read_csv(f'{AUTOMORPH_DATA}/resolution_information.csv')
    
    for image_path in image_list:
        
        dst_image = f'{AUTOMORPH_DATA}/images/' + image_path
        if os.path.exists(f'{AUTOMORPH_DATA}/Results/M0/images/' + image_path):
            print('continue...')
            continue
        try:
            resolution_ = resolution_list['res'][resolution_list['fundus']==image_path].values[0]
            list_resolution.append(resolution_)
            img = prep.imread(dst_image)
            r_img, borders, mask, r_img, radius_list,centre_list_w, centre_list_h = prep.process_without_gb(img,img,radius_list,centre_list_w, centre_list_h)
            prep.imwrite(save_path + image_path.split('.')[0] + '.png', r_img)
            name_list.append(image_path.split('.')[0] + '.png')
        
        except:
            pass

    scale_list = [a*2/912 for a in radius_list]
    scale_resolution = [a*b*1000 for a,b in zip(list_resolution,scale_list)]
    Data4stage2 = pd.DataFrame({'Name':name_list, 'centre_w':centre_list_w, 'centre_h':centre_list_h, 'radius':radius_list, 'Scale':scale_list, 'Scale_resolution':scale_resolution})
    Data4stage2.to_csv(f'{AUTOMORPH_DATA}/Results/M0/crop_info.csv', index = None, encoding='utf8')


if __name__ == "__main__":
    parser = ArgumentParser(description="Preprocess fundus images for AutoMorph")
    parser.add_argument(
        "--image_folder",
        default=str(Path(DEFAULT_AUTOMORPH_DATA) / "images"),
        help="Path to the folder containing source images",
    )
    parser.add_argument(
        "--result_folder",
        default=str(Path(DEFAULT_AUTOMORPH_DATA) / "Results"),
        help="Path to the AutoMorph results folder",
    )
    args = parser.parse_args()

    AUTOMORPH_DATA = prepare_automorph_data(args.image_folder, args.result_folder)
    os.environ['AUTOMORPH_DATA'] = AUTOMORPH_DATA

    if os.path.exists(f'{AUTOMORPH_DATA}/images/.ipynb_checkpoints'):
        shutil.rmtree(f'{AUTOMORPH_DATA}/images/.ipynb_checkpoints')
    image_list = sorted(os.listdir(f'{AUTOMORPH_DATA}/images'))
    save_path = f'{AUTOMORPH_DATA}/Results/M0/images/'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    process(image_list, save_path)

        





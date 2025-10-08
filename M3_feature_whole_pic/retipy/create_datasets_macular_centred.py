#!/usr/bin/env python3

# Retipy - Retinal Image Processing on Python
# Copyright (C) 2017  Alejandro Valdes
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
script to estimate the linear tortuosity of a set of retinal images, it will output the values
to a file in the output folder defined in the configuration. The output will only have the
estimated value and it is sorted by image file name.
"""

import argparse
import glob
# import numpy as np
import os
import h5py
import shutil
import pandas as pd
# import scipy.stats as stats
from pathlib import Path
import tempfile
import atexit

from retipy import configuration, retina, tortuosity_measures

DEFAULT_AUTOMORPH_DATA = os.getenv('AUTOMORPH_DATA','../..')


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

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c",
    "--configuration",
    help="the configuration file location",
    default="resources/retipy.config")
parser.add_argument(
    "--image_folder",
    default=str(Path(DEFAULT_AUTOMORPH_DATA) / 'images'),
    help="Path to the folder containing input images"
)
parser.add_argument(
    "--result_folder",
    default=str(Path(DEFAULT_AUTOMORPH_DATA) / 'Results'),
    help="Path to the AutoMorph results folder"
)
args = parser.parse_args()

AUTOMORPH_DATA = prepare_automorph_data(args.image_folder, args.result_folder)
os.environ['AUTOMORPH_DATA'] = AUTOMORPH_DATA

if os.path.exists(f'{AUTOMORPH_DATA}/Results/M2/artery_vein/artery_binary_skeleton/.ipynb_checkpoints'):
    shutil.rmtree(f'{AUTOMORPH_DATA}/Results/M2/artery_vein/artery_binary_skeleton/.ipynb_checkpoints')
if os.path.exists(f'{AUTOMORPH_DATA}/Results/M2/binary_vessel/binary_skeleton/.ipynb_checkpoints'):
    shutil.rmtree(f'{AUTOMORPH_DATA}/Results/M2/binary_vessel/binary_skeleton/.ipynb_checkpoints')
if os.path.exists(f'{AUTOMORPH_DATA}/Results/M2/artery_vein/vein_binary_skeleton/.ipynb_checkpoints'):
    shutil.rmtree(f'{AUTOMORPH_DATA}/Results/M2/artery_vein/vein_binary_skeleton/.ipynb_checkpoints')
if not os.path.exists(f'{AUTOMORPH_DATA}/Results/M3/Macular_centred/Width/'):
    os.makedirs(f'{AUTOMORPH_DATA}/Results/M3/Macular_centred/Width/')

#if os.path.exists('./DDR/av_seg/raw/.ipynb_checkpoints'):
#    shutil.rmtree('./DDR/av_seg/raw/.ipynb_checkpoints')


CONFIG = configuration.Configuration(args.configuration)
binary_FD_binary,binary_VD_binary,binary_Average_width,binary_t2_list,binary_t4_list,binary_t5_list = [],[],[],[],[],[]
artery_FD_binary,artery_VD_binary,artery_Average_width,artery_t2_list,artery_t4_list,artery_t5_list = [],[],[],[],[],[]
vein_FD_binary,vein_VD_binary,vein_Average_width,vein_t2_list,vein_t4_list,vein_t5_list = [],[],[],[],[],[]
name_binary_list = []
name_artery_list = []
name_vein_list = []

Artery_PATH = f'{AUTOMORPH_DATA}/Results/M2/artery_vein/macular_centred_artery_skeleton'
Vein_PATH = f'{AUTOMORPH_DATA}/Results/M2/artery_vein/macular_centred_vein_skeleton'
Binary_PATH = f'{AUTOMORPH_DATA}/Results/M2/binary_vessel/macular_centred_binary_skeleton'

for filename in sorted(glob.glob(os.path.join(Binary_PATH, '*.png'))):
    
    try:
        segmentedImage = retina.Retina(None, filename, store_path=f'{AUTOMORPH_DATA}/Results/M2/binary_vessel/macular_centred_binary_process')
        #segmentedImage.threshold_image()
        #segmentedImage.reshape_square()
        #window_sizes = segmentedImage.get_window_sizes()
        window_sizes = [912]
        window = retina.Window(
            segmentedImage, window_sizes[-1], min_pixels=CONFIG.pixels_per_window)
        FD_binary,VD_binary,Average_width, t2, t4, td = tortuosity_measures.evaluate_window(window, CONFIG.pixels_per_window, CONFIG.sampling_size, CONFIG.r_2_threshold,store_path=f'{AUTOMORPH_DATA}/Results/M2/binary_vessel/macular_centred_binary_process/')
        #print(window.tags)
        binary_t2_list.append(t2)
        binary_t4_list.append(t4)
        binary_t5_list.append(td)
        binary_FD_binary.append(FD_binary)
        binary_VD_binary.append(VD_binary)
        binary_Average_width.append(Average_width)
        name_binary_list.append(filename.split('/')[-1])
        
    except:
        binary_t2_list.append(-1)
        binary_t4_list.append(-1)
        binary_t5_list.append(-1)
        binary_FD_binary.append(-1)
        binary_VD_binary.append(-1)
        binary_Average_width.append(-1)
        name_binary_list.append(filename.split('/')[-1])


for filename in sorted(glob.glob(os.path.join(Artery_PATH, '*.png'))):

    try:
        
        segmentedImage = retina.Retina(None, filename,store_path=f'{AUTOMORPH_DATA}/Results/M2/artery_vein/macular_centred_artery_process')
        window_sizes = [912]
        window = retina.Window(
            segmentedImage, window_sizes[-1], min_pixels=CONFIG.pixels_per_window)
        FD_binary,VD_binary,Average_width, t2, t4, td = tortuosity_measures.evaluate_window(window, CONFIG.pixels_per_window, CONFIG.sampling_size, CONFIG.r_2_threshold,store_path=f'{AUTOMORPH_DATA}/Results/M2/artery_vein/macular_centred_artery_process/')
        #print(window.tags)
        artery_t2_list.append(t2)
        artery_t4_list.append(t4)
        artery_t5_list.append(td)
        artery_FD_binary.append(FD_binary)
        artery_VD_binary.append(VD_binary)
        artery_Average_width.append(Average_width)
        name_artery_list.append(filename.split('/')[-1]) 
    
    
    except:
        artery_t2_list.append(-1)
        artery_t4_list.append(-1)
        artery_t5_list.append(-1)
        artery_FD_binary.append(-1)
        artery_VD_binary.append(-1)
        artery_Average_width.append(-1)   
        name_artery_list.append(filename.split('/')[-1])  


for filename in sorted(glob.glob(os.path.join(Vein_PATH, '*.png'))):

    try:
        segmentedImage = retina.Retina(None, filename,store_path=f'{AUTOMORPH_DATA}/Results/M2/artery_vein/macular_centred_vein_process')
        window_sizes = [912]
        window = retina.Window(
            segmentedImage, window_sizes[-1], min_pixels=CONFIG.pixels_per_window)
        FD_binary,VD_binary,Average_width, t2, t4, td = tortuosity_measures.evaluate_window(window, CONFIG.pixels_per_window, CONFIG.sampling_size, CONFIG.r_2_threshold,store_path=f'{AUTOMORPH_DATA}/Results/M2/artery_vein/macular_centred_vein_process/')
        #print(window.tags)
        vein_t2_list.append(t2)
        vein_t4_list.append(t4)
        vein_t5_list.append(td)
        vein_FD_binary.append(FD_binary)
        vein_VD_binary.append(VD_binary)
        vein_Average_width.append(Average_width)
        name_vein_list.append(filename.split('/')[-1])
    
    except:
        
        vein_t2_list.append(-1)
        vein_t4_list.append(-1)
        vein_t5_list.append(-1)
        vein_FD_binary.append(-1)
        vein_VD_binary.append(-1)
        vein_Average_width.append(-1)
        name_vein_list.append(filename.split('/')[-1])
        
        
Disc_file = pd.read_csv(f"{AUTOMORPH_DATA}/Results/M3/Macular_centred/Disc_cup_results.csv").astype({"Name": "object"})

Data4stage2_binary = pd.DataFrame(
    {
        "Name": name_binary_list,
        "Fractal_dimension": binary_FD_binary,
        "Vessel_density": binary_VD_binary,
        "Average_width": binary_Average_width,
        "Distance_tortuosity": binary_t2_list,
        "Squared_curvature_tortuosity": binary_t4_list,
        "Tortuosity_density": binary_t5_list,
    }
).astype({"Name": "object"})

Data4stage2_artery = pd.DataFrame(
    {
        "Name": name_artery_list,
        "Artery_Fractal_dimension": artery_FD_binary,
        "Artery_Vessel_density": artery_VD_binary,
        "Artery_Average_width": artery_Average_width,
        "Artery_Distance_tortuosity": artery_t2_list,
        "Artery_Squared_curvature_tortuosity": artery_t4_list,
        "Artery_Tortuosity_density": artery_t5_list,
    }
).astype({"Name": "object"})

Data4stage2_vein = pd.DataFrame(
    {
        "Name": name_vein_list,
        "Vein_Fractal_dimension": vein_FD_binary,
        "Vein_Vessel_density": vein_VD_binary,
        "Vein_Average_width": vein_Average_width,
        "Vein_Distance_tortuosity": vein_t2_list,
        "Vein_Squared_curvature_tortuosity": vein_t4_list,
        "Vein_Tortuosity_density": vein_t5_list,
    }
).astype({"Name": "object"})


Disc_file_binary = pd.merge(Disc_file, Data4stage2_binary, how="outer", on=["Name"])
artery_vein = pd.merge(Data4stage2_artery, Data4stage2_vein, how="outer", on=["Name"])
Data4stage2 = pd.merge(Disc_file_binary, artery_vein, how="outer", on=["Name"])

Data4stage2.to_csv(f'{AUTOMORPH_DATA}/Results/M3/Macular_centred/Macular_Measurement.csv', index = None, encoding='utf8')

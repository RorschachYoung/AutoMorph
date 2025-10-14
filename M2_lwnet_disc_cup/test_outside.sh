date

IMAGE_FOLDER=${IMAGE_FOLDER:-".."}
RESULT_FOLDER=${RESULT_FOLDER:-"../Results"}

python generate_av_results.py --config_file experiments/wnet_All_three_1024_disc_cup/30/config.cfg --im_size 512 --device cuda:0 \
    --result_folder="${RESULT_FOLDER}" --image_folder="${IMAGE_FOLDER}"
                           

date
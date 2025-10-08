date

IMAGE_FOLDER=${1:-${AUTOMORPH_IMAGE_FOLDER}}
RESULT_FOLDER=${2:-${AUTOMORPH_RESULT_FOLDER}}

if [ -z "${AUTOMORPH_DATA}" ]; then
  AUTOMORPH_DATA=".."
fi

if [ -z "${IMAGE_FOLDER}" ]; then
  IMAGE_FOLDER="${AUTOMORPH_DATA}/images"
fi

if [ -z "${RESULT_FOLDER}" ]; then
  RESULT_FOLDER="${AUTOMORPH_DATA}/Results"
fi

python generate_av_results.py --config_file experiments/wnet_All_three_1024_disc_cup/30/config.cfg --im_size 512 --device cuda:0 \
  --image_folder="${IMAGE_FOLDER}" --result_folder="${RESULT_FOLDER}"
                           

date
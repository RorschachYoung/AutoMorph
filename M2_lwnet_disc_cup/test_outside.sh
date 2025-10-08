date

IMAGE_FOLDER=${1:-${AUTOMORPH_IMAGE_FOLDER}}
RESULT_FOLDER=${2:-${AUTOMORPH_RESULT_FOLDER}}
BATCH_SIZE_RAW=${3:-}
NUM_WORKERS_RAW=${4:-}

if [ -z "${AUTOMORPH_DATA}" ]; then
  AUTOMORPH_DATA=".."
fi

if [ -z "${IMAGE_FOLDER}" ]; then
  IMAGE_FOLDER="${AUTOMORPH_DATA}/images"
fi

if [ -z "${RESULT_FOLDER}" ]; then
  RESULT_FOLDER="${AUTOMORPH_DATA}/Results"
fi

if [ -z "${BATCH_SIZE_RAW}" ]; then
  if [ -n "${AUTOMORPH_BATCH_SIZE}" ]; then
    BATCH_SIZE=${AUTOMORPH_BATCH_SIZE}
  else
    BATCH_SIZE=16
  fi
else
  BATCH_SIZE=${BATCH_SIZE_RAW}
fi

if [ -z "${NUM_WORKERS_RAW}" ]; then
  if [ -n "${AUTOMORPH_NUM_WORKERS}" ]; then
    NUM_WORKERS=${AUTOMORPH_NUM_WORKERS}
  else
    NUM_WORKERS=8
  fi
else
  NUM_WORKERS=${NUM_WORKERS_RAW}
fi

python generate_av_results.py --config_file experiments/wnet_All_three_1024_disc_cup/30/config.cfg --im_size 512 --device cuda:0 \
  --batch_size=${BATCH_SIZE} --num_workers=${NUM_WORKERS} \
  --image_folder="${IMAGE_FOLDER}" --result_folder="${RESULT_FOLDER}"
                           

date
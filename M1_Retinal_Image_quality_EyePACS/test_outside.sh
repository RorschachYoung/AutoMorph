
CUDA_NUMBER=0

export PYTHONPATH=.:$PYTHONPATH

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
    BATCH_SIZE=64
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

for model in 'efficientnet'
do
    for n_round in 0
    do
    seed_number=$((42-2*n_round))
    CUDA_VISIBLE_DEVICES=${CUDA_NUMBER} python test_outside.py --epochs=1 --batch-size=${BATCH_SIZE} --task_name='Retinal_quality' --model=${model} --round=${n_round} --train_on_dataset='EyePACS_quality' \
    --test_on_dataset='customised_data' --test_csv_dir="${RESULT_FOLDER}/M0/images/" --n_class=3 --seed_num=${seed_number} \
    --num_workers=${NUM_WORKERS} --image_folder="${IMAGE_FOLDER}" --result_folder="${RESULT_FOLDER}"

    
    done

done



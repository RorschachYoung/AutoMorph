
CUDA_NUMBER=0

export PYTHONPATH=.:$PYTHONPATH

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

for model in 'efficientnet'
do
    for n_round in 0
    do
    seed_number=$((42-2*n_round))
    CUDA_VISIBLE_DEVICES=${CUDA_NUMBER} python test_outside.py --e=1 --b=64 --task_name='Retinal_quality' --model=${model} --round=${n_round} --train_on_dataset='EyePACS_quality' \
    --test_on_dataset='customised_data' --test_csv_dir="${RESULT_FOLDER}/M0/images/" --n_class=3 --seed_num=${seed_number} \
    --image_folder="${IMAGE_FOLDER}" --result_folder="${RESULT_FOLDER}"

    
    done

done




CUDA_NUMBER=0

export PYTHONPATH=.:$PYTHONPATH

IMAGE_FOLDER=${IMAGE_FOLDER:-".."}
RESULT_FOLDER=${RESULT_FOLDER:-"../Results"}

M0_IMAGES="${RESULT_FOLDER}/M0/images"

for model in 'efficientnet'
do
    for n_round in 0
    do
    seed_number=$((42-2*n_round))
    CUDA_VISIBLE_DEVICES=${CUDA_NUMBER} python test_outside.py --e=1 --b=64 --task_name='Retinal_quality' --model=${model} --round=${n_round} --train_on_dataset='EyePACS_quality' \
    --test_on_dataset='customised_data' --test_csv_dir="${M0_IMAGES}" --n_class=3 --seed_num=${seed_number} \
    --result_folder="${RESULT_FOLDER}" --image_folder="${IMAGE_FOLDER}"


    done

done



#This is sh file for SEGAN

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

# define your job name

gpu_id=0

date
                                                
dataset_name='ALL-SIX'

seed_number=$((42-2*seed))

job_name=20210630_uniform_thres40_${dataset_name}

CUDA_VISIBLE_DEVICES=${gpu_id} python test_outside_integrated.py --epochs=1 \
                                                --batchsize=8 \
                                                --learning_rate=2e-4 \
                                                --validation_ratio=10.0 \
                                                --alpha=0.08 \
                                                --beta=1.1 \
                                                --gamma=0.5\
                                                --dataset=${dataset_name} \
                                                --dataset_test=${dataset_name} \
                                                --uniform='True' \
                                                --jn=${job_name} \
                                                --worker_num=2 \
                                                --save_model='best' \
                                                --train_test_mode='test' \
                                                --pre_threshold=40.0 \
                                                --seed_num=${seed_number} \
                                                --out_test="${RESULT_FOLDER}/M2/binary_vessel/" \
                                                --image_folder="${IMAGE_FOLDER}" \
                                                --result_folder="${RESULT_FOLDER}"
                                                
                                        

date
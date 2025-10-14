#This is sh file for SEGAN

IMAGE_FOLDER=${IMAGE_FOLDER:-".."}
RESULT_FOLDER=${RESULT_FOLDER:-"../Results"}

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
                                                --result_folder="${RESULT_FOLDER}" \
                                                --image_folder="${IMAGE_FOLDER}"
                                                
                                        

date
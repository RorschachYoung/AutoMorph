#This is SH file for LearningAIM

export PYTHONPATH=.:$PYTHONPATH

IMAGE_FOLDER=${1:-${AUTOMORPH_IMAGE_FOLDER}}
RESULT_FOLDER=${2:-${AUTOMORPH_RESULT_FOLDER}}

seed_number=42
dataset_name='ALL-AV'
test_checkpoint=1401

if [ -z "${AUTOMORPH_DATA}" ]; then
  AUTOMORPH_DATA=".."
fi

if [ -z "${IMAGE_FOLDER}" ]; then
  IMAGE_FOLDER="${AUTOMORPH_DATA}/images"
fi

if [ -z "${RESULT_FOLDER}" ]; then
  RESULT_FOLDER="${AUTOMORPH_DATA}/Results"
fi

date
CUDA_VISIBLE_DEVICES=0 python test_outside.py --batch-size=8 \
                                                --dataset=${dataset_name} \
                                                --job_name=20210724_${dataset_name}_randomseed \
                                                --checkstart=${test_checkpoint} \
                                                --uniform=True \
                                                --image_folder="${IMAGE_FOLDER}" \
                                                --result_folder="${RESULT_FOLDER}"


date


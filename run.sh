#!/bin/bash  
# RUN FILE FOR AUTOMORPH
# YUKUN ZHOU 2023-08-24
# Updated: 2025-06-21

date

# ----------------------------- #
# Parse optional arguments
# ----------------------------- #
NO_PROCESS=0
NO_QUALITY=0
NO_SEGMENTATION=0
NO_FEATURE=0
IMAGE_FOLDER=""
RESULT_FOLDER=""
BATCH_SIZE=""
NUM_WORKERS=""

usage() {
  cat <<'EOF'
Usage: sh run.sh [options]

Options:
  --image_folder=PATH   Absolute or relative path to the folder containing input images.
  --result_folder=PATH  Absolute or relative path where pipeline outputs should be written.
  --batch_size=INT      Override the batch size used by deep learning modules.
  --num_workers=INT     Override the DataLoader worker count used by deep learning modules.
  --no_process          Skip the preprocessing stage.
  --no_quality          Skip the image quality assessment stage.
  --no_segmentation     Skip the vessel/artery-vein/optic-disc segmentation stage.
  --no_feature          Skip feature extraction and CSV merging.
  -h, --help            Show this help message and exit.

If paths are omitted, the script falls back to ./images and ./Results, or
${AUTOMORPH_DATA}/images and ${AUTOMORPH_DATA}/Results when the environment
variable AUTOMORPH_DATA is set.
EOF
}

for arg in "$@"; do
  case $arg in
    -h|--help)
      usage
      exit 0
      ;;
    --no_process)
      NO_PROCESS=1
      shift
      ;;
    --no_quality)
      NO_QUALITY=1
      shift
      ;;
    --no_segmentation)
      NO_SEGMENTATION=1
      shift
      ;;
    --no_feature)
      NO_FEATURE=1
      shift
      ;;
    --image_folder=*)
      IMAGE_FOLDER="${arg#*=}"
      shift
      ;;
    --result_folder=*)
      RESULT_FOLDER="${arg#*=}"
      shift
      ;;
    --batch_size=*)
      BATCH_SIZE="${arg#*=}"
      shift
      ;;
    --num_workers=*)
      NUM_WORKERS="${arg#*=}"
      shift
      ;;
  esac
done

# Default paths if not provided
if [ -z "$IMAGE_FOLDER" ]; then
  if [ -n "${AUTOMORPH_DATA}" ]; then
    IMAGE_FOLDER="${AUTOMORPH_DATA}/images"
  else
    IMAGE_FOLDER="./images"
  fi
fi

if [ -z "$RESULT_FOLDER" ]; then
  if [ -n "${AUTOMORPH_DATA}" ]; then
    RESULT_FOLDER="${AUTOMORPH_DATA}/Results"
  else
    RESULT_FOLDER="./Results"
  fi
fi

echo "Using image folder: ${IMAGE_FOLDER}"
echo "Using result folder: ${RESULT_FOLDER}"
if [ -n "${BATCH_SIZE}" ]; then
  echo "Using batch size override: ${BATCH_SIZE}"
fi
if [ -n "${NUM_WORKERS}" ]; then
  echo "Using dataloader workers override: ${NUM_WORKERS}"
fi

export PYTHONPATH="$(pwd):${PYTHONPATH}"

if [ -n "${BATCH_SIZE}" ]; then
  export AUTOMORPH_BATCH_SIZE="${BATCH_SIZE}"
fi
if [ -n "${NUM_WORKERS}" ]; then
  export AUTOMORPH_NUM_WORKERS="${NUM_WORKERS}"
fi

QUALITY_BATCH_ARG="${BATCH_SIZE}"
QUALITY_WORKER_ARG="${NUM_WORKERS}"
SEG_BATCH_ARG="${BATCH_SIZE}"
SEG_WORKER_ARG="${NUM_WORKERS}"
CUP_BATCH_ARG="${BATCH_SIZE}"
CUP_WORKER_ARG="${NUM_WORKERS}"
AV_BATCH_ARG="${BATCH_SIZE}"
AV_WORKER_ARG="${NUM_WORKERS}"

# ----------------------------- #
# Step 0 - Prepare AUTOMORPH_DATA directory and clean up results
# ----------------------------- #

python automorph_data.py

mkdir -p "${RESULT_FOLDER}"

mkdir -p "${IMAGE_FOLDER}"

clean_stage_paths() {
  if [ $# -eq 0 ]; then
    return 0
  fi

  for relative_path in "$@"; do
    local target="${RESULT_FOLDER}/${relative_path}"
    if [ -e "${target}" ]; then
      echo "Cleaning ${target}"
      rm -rf "${target}"
    fi
  done
}

RESOLUTION_FILE=$(python generate_resolution.py --image_folder "${IMAGE_FOLDER}" --result_folder "${RESULT_FOLDER}")
export AUTOMORPH_RESOLUTION_FILE="${RESOLUTION_FILE}"

# ----------------------------- #
# Step 1 - Image Preprocessing
# ----------------------------- #
if [ $NO_PROCESS -eq 0 ]; then
  clean_stage_paths "M0"
  echo "### Preprocess Start ###"
  cd M0_Preprocess
  python EyeQ_process_main.py --image_folder "${IMAGE_FOLDER}" --result_folder "${RESULT_FOLDER}"
  cd ..
else
  echo "### Skipping Preprocessing ###"
fi

# ----------------------------- #
# Step 2 - Image Quality Assessment
# ----------------------------- #
if [ $NO_QUALITY -eq 0 ]; then
  clean_stage_paths "M1"
  echo "### Image Quality Assessment ###"
  cd M1_Retinal_Image_quality_EyePACS
  sh test_outside.sh "${IMAGE_FOLDER}" "${RESULT_FOLDER}" "${QUALITY_BATCH_ARG}" "${QUALITY_WORKER_ARG}"
  python merge_quality_assessment.py --image_folder "${IMAGE_FOLDER}" --result_folder "${RESULT_FOLDER}"
  cd ..
else
  echo "### Skipping Image Quality Assessment ###"
fi

# ----------------------------- #
# Step 3 - Segmentation Modules
# ----------------------------- #
if [ $NO_SEGMENTATION -eq 0 ]; then
  clean_stage_paths "M2"
  echo "### Segmentation Modules ###"

  cd M2_Vessel_seg
  sh test_outside.sh "${IMAGE_FOLDER}" "${RESULT_FOLDER}" "${SEG_BATCH_ARG}" "${SEG_WORKER_ARG}"
  cd ..

  cd M2_Artery_vein
  sh test_outside.sh "${IMAGE_FOLDER}" "${RESULT_FOLDER}" "${AV_BATCH_ARG}" "${AV_WORKER_ARG}"
  cd ..

  cd M2_lwnet_disc_cup
  sh test_outside.sh "${IMAGE_FOLDER}" "${RESULT_FOLDER}" "${CUP_BATCH_ARG}" "${CUP_WORKER_ARG}"
  cd ..
else
  echo "### Skipping Segmentation Modules ###"
fi

# ----------------------------- #
# Step 4 - Feature Measurement
# ----------------------------- #
if [ $NO_FEATURE -eq 0 ]; then
  clean_stage_paths "M3"
  echo "### Feature Measuring ###"

  cd M3_feature_zone/retipy/
  python create_datasets_disc_centred_B.py --image_folder "${IMAGE_FOLDER}" --result_folder "${RESULT_FOLDER}"
  python create_datasets_disc_centred_C.py --image_folder "${IMAGE_FOLDER}" --result_folder "${RESULT_FOLDER}"
  python create_datasets_macular_centred_B.py --image_folder "${IMAGE_FOLDER}" --result_folder "${RESULT_FOLDER}"
  python create_datasets_macular_centred_C.py --image_folder "${IMAGE_FOLDER}" --result_folder "${RESULT_FOLDER}"
  cd ../..

  cd M3_feature_whole_pic/retipy/
  python create_datasets_macular_centred.py --image_folder "${IMAGE_FOLDER}" --result_folder "${RESULT_FOLDER}"
  python create_datasets_disc_centred.py --image_folder "${IMAGE_FOLDER}" --result_folder "${RESULT_FOLDER}"
  cd ../..

  python csv_merge.py --image_folder "${IMAGE_FOLDER}" --result_folder "${RESULT_FOLDER}"
else
  echo "### Skipping Feature Measurement ###"
fi

echo "### Done ###"
date

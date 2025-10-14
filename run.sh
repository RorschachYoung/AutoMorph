#!/bin/bash
# RUN FILE FOR AUTOMORPH
# YUKUN ZHOU 2023-08-24
# Updated: 2025-06-21

set -euo pipefail

date

# ----------------------------- #
# Parse optional arguments
# ----------------------------- #
NO_PROCESS=0
NO_QUALITY=0
NO_SEGMENTATION=0
NO_FEATURE=0
IMAGE_FOLDER="images"
RESULT_FOLDER="Results"

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case $1 in
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
    --image_folder)
      IMAGE_FOLDER=$2
      shift 2
      ;;
    --image_folder=*)
      IMAGE_FOLDER=${1#*=}
      shift
      ;;
    --result_folder)
      RESULT_FOLDER=$2
      shift 2
      ;;
    --result_folder=*)
      RESULT_FOLDER=${1#*=}
      shift
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done
set -- "${POSITIONAL[@]}"

abspath() {
  python - "$1" <<'PY'
import os, sys
print(os.path.abspath(sys.argv[1]))
PY
}

IMAGE_FOLDER=$(abspath "$IMAGE_FOLDER")
RESULT_FOLDER=$(abspath "$RESULT_FOLDER")
RUNTIME_BASE="${RESULT_FOLDER}/.automorph_runtime"
RESOLUTION_CSV="${RESULT_FOLDER}/resolution_information.csv"

export IMAGE_FOLDER
export RESULT_FOLDER

# ----------------------------- #
# Step 0 - Prepare runtime directories
# ----------------------------- #
python automorph_data.py --image_folder "$IMAGE_FOLDER" --result_folder "$RESULT_FOLDER" --runtime_base "$RUNTIME_BASE"
export AUTOMORPH_DATA="$RUNTIME_BASE"

python generate_resolution.py --image_folder "$IMAGE_FOLDER" --output_csv "$RESOLUTION_CSV"
ln -sfn "$RESOLUTION_CSV" "${RUNTIME_BASE}/resolution_information.csv"

delete_stage_artifacts() {
  local stage_dir="$1"
  if [ -d "$stage_dir" ]; then
    find "$stage_dir" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
  fi
}

# ----------------------------- #
# Step 1 - Image Preprocessing
# ----------------------------- #
if [ $NO_PROCESS -eq 0 ]; then
  echo "### Preprocess Start ###"
  delete_stage_artifacts "${RESULT_FOLDER}/M0"
  (cd M0_Preprocess && python EyeQ_process_main.py \
    --image_folder "$IMAGE_FOLDER" \
    --result_folder "$RESULT_FOLDER" \
    --resolution_csv "$RESOLUTION_CSV")
else
  echo "### Skipping Preprocessing ###"
fi

# ----------------------------- #
# Step 2 - Image Quality Assessment
# ----------------------------- #
if [ $NO_QUALITY -eq 0 ]; then
  echo "### Image Quality Assessment ###"
  delete_stage_artifacts "${RESULT_FOLDER}/M1"
  (cd M1_Retinal_Image_quality_EyePACS && \
    IMAGE_FOLDER="$IMAGE_FOLDER" RESULT_FOLDER="$RESULT_FOLDER" sh test_outside.sh)
  (cd M1_Retinal_Image_quality_EyePACS && \
    python merge_quality_assessment.py --result_folder "$RESULT_FOLDER" --image_folder "$IMAGE_FOLDER")
else
  echo "### Skipping Image Quality Assessment ###"
fi

# ----------------------------- #
# Step 3 - Segmentation Modules
# ----------------------------- #
if [ $NO_SEGMENTATION -eq 0 ]; then
  echo "### Segmentation Modules ###"
  delete_stage_artifacts "${RESULT_FOLDER}/M2"

  (cd M2_Vessel_seg && IMAGE_FOLDER="$IMAGE_FOLDER" RESULT_FOLDER="$RESULT_FOLDER" sh test_outside.sh)
  (cd M2_Artery_vein && IMAGE_FOLDER="$IMAGE_FOLDER" RESULT_FOLDER="$RESULT_FOLDER" sh test_outside.sh)
  (cd M2_lwnet_disc_cup && IMAGE_FOLDER="$IMAGE_FOLDER" RESULT_FOLDER="$RESULT_FOLDER" sh test_outside.sh)
else
  echo "### Skipping Segmentation Modules ###"
fi

# ----------------------------- #
# Step 4 - Feature Measurement
# ----------------------------- #
if [ $NO_FEATURE -eq 0 ]; then
  echo "### Feature Measuring ###"
  delete_stage_artifacts "${RESULT_FOLDER}/M3"

  (cd M3_feature_zone/retipy/ && \
    python create_datasets_disc_centred_B.py --result_folder "$RESULT_FOLDER" --image_folder "$IMAGE_FOLDER" && \
    python create_datasets_disc_centred_C.py --result_folder "$RESULT_FOLDER" --image_folder "$IMAGE_FOLDER" && \
    python create_datasets_macular_centred_B.py --result_folder "$RESULT_FOLDER" --image_folder "$IMAGE_FOLDER" && \
    python create_datasets_macular_centred_C.py --result_folder "$RESULT_FOLDER" --image_folder "$IMAGE_FOLDER")

  (cd M3_feature_whole_pic/retipy/ && \
    python create_datasets_macular_centred.py --result_folder "$RESULT_FOLDER" --image_folder "$IMAGE_FOLDER" && \
    python create_datasets_disc_centred.py --result_folder "$RESULT_FOLDER" --image_folder "$IMAGE_FOLDER")

  python csv_merge.py --result_folder "$RESULT_FOLDER" --image_folder "$IMAGE_FOLDER"
else
  echo "### Skipping Feature Measurement ###"
fi

echo "### Done ###"
date

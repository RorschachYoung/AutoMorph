import argparse
import os
import shutil
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Split quality assessment results into good/bad folders.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--image_folder',
        type=str,
        default=None,
        help='Original image directory (used to resolve relative paths).'
    )
    parser.add_argument(
        '--result_folder',
        type=str,
        required=True,
        help='Root directory for AutoMorph results.'
    )
    args = parser.parse_args()

    result_folder = os.path.abspath(args.result_folder)

    # results_ensemble.csv: must include columns: Name, Prediction, softmax_bad[, usable_sd]
    csv_path = os.path.join(result_folder, 'M1', 'results_ensemble.csv')
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'CSV not found: {csv_path}')

    df = pd.read_csv(csv_path)

    # 列名校验（避免静默 KeyError）
    required_cols = {'Name', 'Prediction', 'softmax_bad'}
    missing = required_cols - set(df.columns)
    if missing:
        raise KeyError(f'Missing columns in CSV: {missing}. Columns found: {list(df.columns)}')

    # 目标目录
    good_dir = os.path.join(result_folder, 'M1', 'Good_quality')
    bad_dir = os.path.join(result_folder, 'M1', 'Bad_quality')
    os.makedirs(good_dir, exist_ok=True)
    os.makedirs(bad_dir, exist_ok=True)

    eye_good = 0
    eye_bad = 0

    def resolve_path(name: str) -> str:
        """把 CSV 中的 Name 解析成可读文件路径。"""
        if os.path.isabs(name) and os.path.exists(name):
            return name
        if os.path.exists(name):
            return os.path.abspath(name)
        if args.image_folder:
            candidate = os.path.join(args.image_folder, name)
            if os.path.exists(candidate):
                return candidate
        # 找不到就原样返回，后面 copy 会报错并提示
        return name

    for row in df.itertuples(index=False):
        name = getattr(row, 'Name')
        pred = getattr(row, 'Prediction')
        bad_prob = getattr(row, 'softmax_bad')

        src = resolve_path(str(name))
        try:
            if pred == 0:
                shutil.copy(src, good_dir)
                eye_good += 1
            elif (pred == 1) and (bad_prob < 0.25):
                shutil.copy(src, good_dir)
                eye_good += 1
            else:
                shutil.copy(src, bad_dir)
                eye_bad += 1
        except FileNotFoundError:
            # 文件不存在时给出清晰提示，但不中断整批处理
            print(f'[WARN] Image not found, skip: {src}')

    print(f'Gradable cases by EyePACS_QA: {eye_good}')
    print(f'Ungradable cases by EyePACS_QA: {eye_bad}')


if __name__ == '__main__':
    main()

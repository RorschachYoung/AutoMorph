"""Utilities for preparing AutoMorph input/output directories."""
from __future__ import annotations

import atexit
import csv
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple

DEFAULT_PIXEL_RESOLUTION = 0.008


def _coerce_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _write_resolution_file(destination: Path, image_path: Path, pixel_resolution: float) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    images = [entry.name for entry in sorted(image_path.iterdir()) if entry.is_file()]
    with destination.open('w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['fundus', 'res'])
        for name in images:
            writer.writerow([name, pixel_resolution])
    return destination


def _resolve_resolution_source(
    provided_resolution: Optional[str], image_path: Path, result_path: Path
) -> Optional[Path]:
    candidates = []
    if provided_resolution:
        candidates.append(Path(provided_resolution).expanduser())
    candidates.extend(
        [
            image_path / 'resolution_information.csv',
            result_path / 'resolution_information.csv',
            image_path.parent / 'resolution_information.csv',
            result_path.parent / 'resolution_information.csv',
        ]
    )

    for candidate in candidates:
        try:
            candidate_resolved = candidate.resolve(strict=True)
        except FileNotFoundError:
            continue
        if candidate_resolved.is_file():
            return candidate_resolved
    return None


def _ensure_resolution_file(
    destination: Path, image_path: Path, result_path: Path, provided_resolution: Optional[str]
) -> Path:
    destination = destination.expanduser()
    if destination.exists() and destination.is_file():
        return destination

    source = _resolve_resolution_source(provided_resolution, image_path, result_path)
    if source:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.resolve() == source:
            return destination
        shutil.copyfile(source, destination)
        return destination

    pixel_resolution = _coerce_float(os.getenv('AUTOMORPH_PIXEL_RESOLUTION'))
    if pixel_resolution is None:
        pixel_resolution = DEFAULT_PIXEL_RESOLUTION
    return _write_resolution_file(destination, image_path, pixel_resolution)


def prepare_automorph_data(
    image_folder: str, result_folder: str, resolution_file: Optional[str] = None
) -> Tuple[str, str]:
    """Prepare AutoMorph runtime directories.

    Returns a tuple with the AutoMorph base directory and the path to
    ``resolution_information.csv`` within that directory.
    """

    image_path = Path(image_folder).expanduser().resolve()
    result_path = Path(result_folder).expanduser().resolve()

    image_path.mkdir(parents=True, exist_ok=True)
    result_path.mkdir(parents=True, exist_ok=True)

    provided_resolution = resolution_file or os.getenv('AUTOMORPH_RESOLUTION_FILE')

    if (
        image_path.name.lower() == 'images'
        and result_path.name.lower() == 'results'
        and image_path.parent == result_path.parent
    ):
        base_path = image_path.parent
        resolution_path = _ensure_resolution_file(
            base_path / 'resolution_information.csv', image_path, result_path, provided_resolution
        )
    else:
        temp_dir = Path(tempfile.mkdtemp(prefix='automorph_data_'))
        atexit.register(shutil.rmtree, temp_dir, ignore_errors=True)

        images_link = temp_dir / 'images'
        results_link = temp_dir / 'Results'
        if not images_link.exists():
            images_link.symlink_to(image_path, target_is_directory=True)
        if not results_link.exists():
            results_link.symlink_to(result_path, target_is_directory=True)

        resolution_path = _ensure_resolution_file(
            temp_dir / 'resolution_information.csv', image_path, result_path, provided_resolution
        )
        base_path = temp_dir

    os.environ['AUTOMORPH_DATA'] = str(base_path)
    os.environ['AUTOMORPH_RESOLUTION_FILE'] = str(resolution_path)
    return str(base_path), str(resolution_path)

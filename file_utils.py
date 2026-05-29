from pathlib import Path
import shutil


def file_already_exists(destination_folder, file_name):
    destination_path = Path(destination_folder) / file_name
    return destination_path.exists()


def get_safe_destination_path(destination_folder, file_name):
    destination_folder = Path(destination_folder)
    destination_path = destination_folder / file_name

    if not destination_path.exists():
        return destination_path

    stem = destination_path.stem
    suffix = destination_path.suffix
    counter = 1

    while True:
        new_name = f"{stem} ({counter}){suffix}"
        new_path = destination_folder / new_name

        if not new_path.exists():
            return new_path

        counter += 1


def copy_or_move_file(
    source_path,
    destination_folder,
    move_files,
    destination_file_name=None
):
    source_path = Path(source_path)
    destination_folder = Path(destination_folder)

    destination_folder.mkdir(parents=True, exist_ok=True)

    if destination_file_name is None:
        destination_file_name = source_path.name

    destination_path = get_safe_destination_path(
        destination_folder,
        destination_file_name
    )

    if move_files:
        shutil.move(str(source_path), str(destination_path))
        action = "moved"
    else:
        shutil.copy2(str(source_path), str(destination_path))
        action = "copied"

    return destination_path, action
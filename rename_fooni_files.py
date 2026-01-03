import os
import re
from pathlib import Path
import logging

# Configure this if using another destination than the media folder of this project
MEDIA = Path(r"media/")

# # Regex to match the pattern: - Not used anymore
# # Fooni_{FistLastName}_{Perspective}_{SessionNr}_{YYYY-MM-DD}_{HH-MM-SS}.mp4
# PATTERN1 = re.compile(
#     r"""^
#     .*?                      # anything at start, lazily
#     _(?P<pos>Bottom|Centerline|Top|Sideline)  # perspective
#     _(?P<num>\d+)            # integer after perspective
#     _(?P<date>\d{4}-\d{2}-\d{2}) # date like 2025-12-28
#     _(?P<time>\d{2}-\d{2}-\d{2}) # time like 09-11-52 (ignored, just matched)
#     \.(?P<ext>[^.]+)         # extension
#     $""",
#     re.IGNORECASE | re.VERBOSE,
# )
# to use in make_new_filename
# Convert 2025-12-28 -> 20251228
# y, mth, d = date_str.split("-")
# new_date = f"{y}{mth}{d}"
# new_name = f"{new_date}-{hh_mm}-{num}_{pos}.{ext.lower()}"


def log_rename(path, new_path):
    """When doing bulk rename of files, save original and new filename to file renamed_files.txt"""
    with open(f"{MEDIA}/renamed_files.txt", "a") as file:
        file.write(f"{path} -> {new_path}\n")


def make_new_filename(filename: str, session_time: str) -> str:
    """
    Create new filename eg. #1_20251226_200452_Bottom.mp4 -> 20251226_20_00_1_bottom.mp4
    Will use the session_time instead of the time that is part of the provided filename

    Arguments
    ---------
    filename:
        the attribute 'data-filename' of the class_ 'input':
            #main > div > div:nth-child(2) > div > div:nth-child(1) > div.media_container_responsive >
            div.media-select-box > label > input
    session_time:
        hh_mm format
    """

    # Regex to match the filename from media-select and not the the url headers
    # "#1_20251226_200452_Bottom.mp4"
    pattern = re.compile(
        r"""^
        .*?(?P<num>\d+)
        _(?P<date>\d{8})
        _(?P<time>\d{6})
        _(?P<pos>Bottom|Centerline|Top|Sideline)(?P<ext>\.mp4)""",
        re.IGNORECASE | re.VERBOSE,
    )

    m = pattern.match(filename)

    if not m:
        return None  # skip files that don't match

    num = m.group("num")
    pos = m.group("pos").lower()

    date_str = m.group("date")
    ext = m.group("ext")
    new_name = f"{date_str}-{session_time}-{num}_{pos}.mp4"

    return new_name


def rename_files(root: Path = MEDIA, rename: bool = True, filename: str = None):
    """Rename either all files in root or just the provided filename, using the pattern in
    make_new_filename()
    Arguments
    ---------
    root
        Path of the parent folder. Can contain subdirectories
    rename
        If true, renames the files in root, else returns the new filename
    filename
        File that should be renamed. If none, then all contents of the root folder
        where the pattern matches will be renamed
    """

    if filename is not None:
        root = Path(filename)

    for path in root.rglob("*"):
        logging.basicConfig(level=logging.INFO)

        if not path.is_file():
            continue
        else:
            # m = pattern.match(path.name)
            new_name = make_new_filename(
                filename=path.name, session_time=path.parent.name, pattern=PATTERN2
            )
            new_path = path.with_name(new_name)

        # Do not overwrite existing files
        if new_path.exists():
            logging.info(f"Skipping (target exists): {new_path}")
            continue

        logging.info(f"Renaming: {path} -> {new_name}")
        if rename:
            path.rename(new_path)
            log_rename(path, new_name)
        else:
            return new_path


if __name__ == "__main__":
    rename_files(MEDIA, rename=True)
    # print(make_new_filename("#1_20251226_200452_Bottom.mp4", "12_30"))

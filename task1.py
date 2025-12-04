import asyncio
import argparse
import logging
import os
import shutil
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

NO_EXTENSION_DIR = "NO_EXTENSION"


async def copy_file(source_path: Path, output_dir: Path):
    if source_path.suffix:
        extension = source_path.suffix[1:].upper()
    else:
        extension = NO_EXTENSION_DIR

    target_dir = output_dir / extension
    target_path = target_dir / source_path.name

    try:
        await asyncio.to_thread(target_dir.mkdir, parents=True, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create target directory {target_dir}: {e}")
        return

    try:
        logging.info(f"Copying {source_path.name} to {extension}/...")
        await asyncio.to_thread(shutil.copy2, source_path, target_path)
    except Exception as e:
        logging.error(f"Error copying file {source_path}: {e}")


async def read_folder(source_dir: Path, output_dir: Path):
    logging.info(f"Starting scan of source directory: {source_dir}")

    tasks = []

    try:
        for root, dirs, files in await asyncio.to_thread(os.walk, source_dir):
            root_path = Path(root)
            for file_name in files:
                source_path = root_path / file_name
                tasks.append(copy_file(source_path, output_dir))
    except Exception as e:
        logging.error(f"Error while scanning directory {source_dir}: {e}")
        return

    if not tasks:
        logging.warning("No files found in the source directory.")
        return

    logging.info(f"Found {len(tasks)} files. Starting asynchronous copying...")

    await asyncio.gather(*tasks)

    logging.info("All files processed. Sorting complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Asynchronous file sorter by extension.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "source_dir", type=str, help="Path to the source folder for reading files."
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Path to the output folder for creating subdirectories.",
    )

    args = parser.parse_args()

    source_path = Path(args.source_dir)
    output_path = Path(args.output_dir)

    if not source_path.is_dir():
        logging.error(
            f"Source directory not found or is not a directory: {source_path}"
        )
        return

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create output directory {output_path}: {e}")
        return

    try:
        asyncio.run(read_folder(source_path, output_path))
    except KeyboardInterrupt:
        logging.warning("Operation interrupted by the user.")
    except Exception as e:
        logging.critical(f"Unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

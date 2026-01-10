from typing import List
import cyclopts
from pathlib import Path
import shutil
import requests
import os

from db import Database

app = cyclopts.App()


def get_directories(directory: Path) -> List[os.DirEntry]:
    """
    Give a list of directories found in the given directory.
    """
    folders = []
    with os.scandir(directory) as directories:
        for d in directories:
            if d.is_dir():
                folders.append(d)
    return folders


@app.command
def organize(directory: str):
    """
    Move zip files into a better named directory
    """
    dir = Path(directory)
    zip_files = list[Path](dir.glob("*.zip"))

    if not zip_files:
        print("Found no zip files to organize. Bailing.")
        return 0

    for file in zip_files:
        normalized_name = (
            file.name.replace("\\((.+)\\)", "")
            .replace("_", ":")
            .split(".zip")[0]
            .strip()
        )

        new_dir = directory / normalized_name
        orig_file_path = "/".join(file.parts)

        try:
            os.mkdir(new_dir)
            print(f"Created directory {normalized_name}.")
        except FileExistsError:
            print(f"Directory {normalized_name} already exists.")

        try:
            shutil.move(orig_file_path, Path(new_dir, f"{normalized_name}.zip"))
        except FileNotFoundError:
            print(f"Could not find {orig_file_path}.")
            continue
        except shutil.Error as e:
            print(f"Error when moving file {orig_file_path}. {e}")
            continue


@app.command
def download_cover_photos(directory: str):
    """
    Give the directory of folders, and attempt to pull down cover photos for each one.

    @NOTE: requires .env with a SEACH_API_KEY and SEACH_API_KEY setup. This is setup through Google Developer Console.
    """
    dir_name = directory.split("/")[-1]  # n64, ps1, etc
    for directory in get_directories(Path(directory)):
        try:
            if len(list[Path](Path(directory).glob("cover.*"))) > 0:
                print(f"Cover photo already exists in {directory.name}. Moving on..")
                continue

            response = requests.get(
                "https://customsearch.googleapis.com/customsearch/v1",
                {
                    "searchType": "image",
                    "imageType": "photo",
                    "imageSize": "large",
                    "cx": os.environ.get("SEARCH_ENGINE_ID"),
                    "key": os.environ.get("SEACH_API_KEY"),
                    "q": f"{directory.name} {dir_name} box art",
                },
            )
            response.raise_for_status()

            data = response.json()

            if items := data.get("items", None):
                image_url = items[0].get("link")
                extension = (
                    image_url.split(".")[-1].split("?")[0].split("/")[0].lower()
                )  # Possible to get query strings and junk. This approach isn't great, but its quick
                image_req = requests.get(
                    image_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
                    },
                )
                image_req.raise_for_status()

                cover_path = directory / f"cover.{extension}"
                with open(cover_path, "wb") as f:
                    f.write(image_req.content)
                print(f"Cover photo added in {cover_path}.")
        except Exception as e:
            print(f"Error while downloading cover art: {e}.")
            return 0


@app.command
def insert_cover_photos(directory: str):
    home = Path.home()
    openemu_path = home / "Library" / "Application Support" / "OpenEmu" / "Game Library"
    db_path = openemu_path / "Library.storedata"
    art_path = openemu_path / "Artwork"

    with Database(db_path) as db:
        games = db.get_games(no_cover_art_only=True)
        if not games:
            print("Could not find any games without boxart.")
            return

        for game in games:
            print(game)


if __name__ == "__main__":
    app()

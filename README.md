# OpenEmu Scripts

A personal toolkit for managing OpenEmu.

`uv run --env-file=.env main.py download_cover_photos ./n64` - Scrapes all directories under `./n64` using the directory name to seach google for cover art images, and downloading them to each directory

`uv run organize ./n64` - Takes all `.zip` files found in `./n64` and create distinct directories for each

`uv run insert_cover_photos ./n64` - [WIP] Takes each cover art image found in the subdirectories, and automatically creates OpenEmu db entries.
# Network Uploader

Network Uploader is a lightweight Python desktop utility for copying or moving files to configured network destinations.

The app is built with Python, Tkinter, and tkinterdnd2. It supports drag-and-drop uploads, destination categories, optional file renaming, duplicate-file handling, and first-run setup.

## Features

- Drag and drop supported files into the upload list
- Copy or move files to configured network folders
- Create and manage destination categories
- Rename files before upload
- Detect duplicate files and auto-rename when needed
- Track which user uploaded files
- First-run setup for network share and destination configuration
- Local logging for upload activity

## Requirements

- Python 3.10 or newer
- tkinterdnd2

## Install dependencies with:

pip install tkinterdnd2

## Running the App

From the project folder, run:

python main.py

On first launch, Network Uploader will ask you to choose a base network folder and create your first upload destination.

## Building an Executable

This project can be packaged with PyInstaller.

Install PyInstaller:

pip install pyinstaller

## Build the app:

pyinstaller --onefile --windowed --name "Network Uploader" --collect-all tkinterdnd2 main.py

The executable will be created in the dist folder. It will run standalone and install / create all dependencies. 

## Configuration

Network Uploader creates local configuration files on the user's machine. These files should not be committed to GitHub.

Ignored local files include:

config.json
settings.json
logs/
build/
dist/
*.spec
Project Status

""This project is a simple desktop utility created as a learning project while studying computer science. It is functional, but still evolving.""

## License

This project is licensed under the MIT License. See the LICENSE file for details.
# Network Uploader

Network Uploader is a lightweight Python desktop utility for copying or moving files to configured network destinations.

The app is built with Python, Tkinter, and tkinterdnd2. It supports drag-and-drop uploads, destination categories, optional file renaming, duplicate-file handling, first-run setup, local logging, custom app icons, and a simple GitHub-based version check.

## Features

- Drag and drop files into the upload list
- Copy or move files to configured network folders
- Create and manage destination categories
- Rename files before upload
- Detect duplicate files and auto-rename when needed
- Track which user uploaded files
- First-run setup for network share and destination configuration
- Local logging for upload activity
- Custom application icon for the executable, app window, and taskbar
- Startup version check using a public GitHub version.json file

## Requirements

- Python 3.10 or newer
- tkinterdnd2
- Pillow, only needed if regenerating the icon
- PyInstaller, only needed for building an executable

Install runtime dependencies with:

pip install tkinterdnd2

Optional development/build tools:

pip install pillow pyinstaller

## Running the App

From the project folder, run:

python main.py

On first launch, Network Uploader will ask you to choose a base network folder and create your first upload destination.

## Building an Executable

This project can be packaged with PyInstaller.

Build the app with:

pyinstaller --onefile --windowed --name "Network Uploader" --icon assets\network_uploader.ico --add-data "assets\network_uploader.ico;assets" --add-data "assets\network_uploader.png;assets" --collect-all tkinterdnd2 main.py

The executable will be created in the dist folder.

The finished .exe is standalone for normal use, but it does not install Python globally or modify the system. Local app configuration is created separately when the program runs.

## Version Checking

Network Uploader checks a public GitHub version.json file at startup.

Example version.json:

{
    "latest_version": "1.5.0",
    "download_url": "https://github.com/rickethyo/NetworkUploader/",
    "message": "A new version of Network Uploader is available."
}

If latest_version is higher than the local APP_VERSION, the app displays an update message.

## Configuration

Network Uploader creates local configuration files on the user's machine. These files should not be committed to GitHub because they may contain local paths or user-specific settings.

Ignored local files include:

config.json
settings.json
logs/
build/
dist/
*.spec

Safe example files may be committed instead:

config.example.json
settings.example.json

## Project Structure

NetworkUploader/
    assets/
        network_uploader.ico
        network_uploader.png
    file_utils.py
    first_run_window.py
    main.py
    settings_window.py
    version.json
    README.md
    LICENSE
    .gitignore

## Project Status

This project is a simple desktop utility created as a learning project while studying computer science. It is functional, but still evolving.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

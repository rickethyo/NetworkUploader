##5/28/2026##

from pathlib import Path
import json
import logging
import os
import sys
import tkinter as tk
import urllib.request
from tkinter import messagebox
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

from file_utils import file_already_exists, copy_or_move_file
from first_run_window import FirstRunWindow
from settings_window import SettingsWindow


APP_NAME = "Network Uploader"
APP_DISPLAY_NAME = "Network Uploader"
APP_VERSION = "1.5.2"
VERSION_CHECK_URL = "https://raw.githubusercontent.com/rickethyo/NetworkUploader/master/version.json"

ICON_ICO_FILE_NAME = "assets/network_uploader.ico"
ICON_PNG_FILE_NAME = "assets/network_uploader.png"

CONFIG_FILE_NAME = "config.json"
SETTINGS_FILE_NAME = "settings.json"

INVALID_FILE_NAME_CHARS = set('<>:"/\\|?*')

DEFAULT_CONFIG = {
    "network_share": "",
    "destinations": {},
    "move_files": False,
    "uploaders": ["User"]
}

BG_COLOR = "#202434"
PANEL_COLOR = "#2b3045"
TEXT_COLOR = "#f4f4f8"
MUTED_TEXT_COLOR = "#c9cedf"
ACCENT_COLOR = "#4f8cff"
BUTTON_COLOR = "#3f6fd6"
BUTTON_TEXT_COLOR = "#ffffff"
INPUT_COLOR = "#ffffff"


def get_resource_folder():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)

    return Path(__file__).parent

def get_resource_path(file_name):
    return get_resource_folder() / file_name

def get_user_data_folder():
    appdata = os.getenv("APPDATA")

    if appdata:
        data_folder = Path(appdata) / APP_NAME
    else:
        data_folder = Path.home() / APP_NAME

    data_folder.mkdir(parents=True, exist_ok=True)
    return data_folder


RESOURCE_FOLDER = get_resource_folder()
USER_DATA_FOLDER = get_user_data_folder()

BUNDLED_CONFIG_FILE = RESOURCE_FOLDER / CONFIG_FILE_NAME
CONFIG_FILE = USER_DATA_FOLDER / CONFIG_FILE_NAME
SETTINGS_FILE = USER_DATA_FOLDER / SETTINGS_FILE_NAME
LOG_FOLDER = USER_DATA_FOLDER / "logs"


def set_application_icon(root):
    icon_ico_path = get_resource_path(ICON_ICO_FILE_NAME)
    icon_png_path = get_resource_path(ICON_PNG_FILE_NAME)

    try:
        if icon_ico_path.exists():
            root.iconbitmap(icon_ico_path)
    except tk.TclError:
        pass

    try:
        if icon_png_path.exists():
            icon_image = tk.PhotoImage(file=icon_png_path)
            root.iconphoto(True, icon_image)

            # Keep a reference so Python does not garbage collect the image.
            root.icon_image = icon_image
    except tk.TclError:
        pass


def load_bundled_config_template():
    if not BUNDLED_CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(BUNDLED_CONFIG_FILE, "r", encoding="utf-8") as file:
            bundled_config = json.load(file)

        return normalize_config(bundled_config)

    except (OSError, json.JSONDecodeError):
        return DEFAULT_CONFIG.copy()


def get_startup_config(root):
    if CONFIG_FILE.exists():
        return load_config()

    default_config = load_bundled_config_template()

    setup_window = FirstRunWindow(
        parent=root,
        config_file=CONFIG_FILE,
        default_config=default_config
    )

    root.wait_window(setup_window.window)

    if not setup_window.config_created:
        return None

    return normalize_config(setup_window.created_config)


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            config = json.load(file)

        normalized_config = normalize_config(config)

        if normalized_config != config:
            save_config(normalized_config)

        return normalized_config

    except FileNotFoundError:
        raise

    except json.JSONDecodeError as error:
        messagebox.showerror(
            "Config Error",
            f"config.json is not valid JSON:\n\n{CONFIG_FILE}\n\n{error}"
        )
        raise


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)


def normalize_config(config):
    normalized_config = DEFAULT_CONFIG.copy()
    normalized_config.update(config)

    raw_destinations = normalized_config.get("destinations", {})
    normalized_destinations = {}

    legacy_labels = {
        "mtg": "MTG Videos",
        "drone": "Drone Captures",
        "other": "Other / Unsorted",
        "movies": "Movies",
        "tv": "TV Shows"
    }

    for key, value in raw_destinations.items():
        safe_key = make_safe_key(key)

        if isinstance(value, dict):
            label = value.get("label") or make_label_from_key(safe_key)
            path = value.get("path", "")
        else:
            label = legacy_labels.get(safe_key, make_label_from_key(safe_key))
            path = str(value)

        normalized_destinations[safe_key] = {
            "label": label,
            "path": path
        }

    normalized_config["destinations"] = normalized_destinations

    normalized_config.pop("video_extensions", None)
    normalized_config["move_files"] = bool(normalized_config.get("move_files", False))
    normalized_config["network_share"] = str(normalized_config.get("network_share", "")).strip()
    normalized_config["uploaders"] = normalize_uploaders(normalized_config.get("uploaders", []))

    return normalized_config


def normalize_uploaders(uploaders):
    if not uploaders:
        return ["User"]

    normalized_uploaders = []

    for uploader in uploaders:
        uploader = str(uploader).strip()

        if uploader and uploader not in normalized_uploaders:
            normalized_uploaders.append(uploader)

    if not normalized_uploaders:
        normalized_uploaders = ["User"]

    return normalized_uploaders


def make_safe_key(key):
    safe_key = str(key).strip().lower()
    safe_key = "".join(char if char.isalnum() else "_" for char in safe_key)
    safe_key = "_".join(part for part in safe_key.split("_") if part)

    if not safe_key:
        safe_key = "destination"

    return safe_key


def make_label_from_key(key):
    return str(key).replace("_", " ").title()


def setup_logging():
    LOG_FOLDER.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=LOG_FOLDER / "uploader.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def load_settings():
    if not SETTINGS_FILE.exists():
        return {"last_uploaded_by": "User"}

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        return {"last_uploaded_by": "User"}


def save_settings(uploaded_by):
    settings = {
        "last_uploaded_by": uploaded_by
    }

    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)

def parse_version(version_text):
    version_parts = []

    for part in version_text.split("."):
        try:
            version_parts.append(int(part))
        except ValueError:
            version_parts.append(0)

    return tuple(version_parts)


def check_for_updates(parent):
    try:
        with urllib.request.urlopen(VERSION_CHECK_URL, timeout=3) as response:
            data = response.read().decode("utf-8")

        version_info = json.loads(data)

        latest_version = version_info.get("latest_version", "").strip()
        download_url = version_info.get("download_url", "").strip()
        message = version_info.get(
            "message",
            "A new version of Network Uploader is available."
        )

        if not latest_version:
            return

        if parse_version(latest_version) > parse_version(APP_VERSION):
            messagebox.showinfo(
                "Update Available",
                f"{message}\n\n"
                f"Current version: {APP_VERSION}\n"
                f"Latest version: {latest_version}\n\n"
                f"Download:\n{download_url}",
                parent=parent
            )

    except Exception:
        logging.info("Version check failed.", exc_info=True)

class NetworkUploaderApp:
    def __init__(self, root, config):
        self.root = root
        self.root.title(f"{APP_DISPLAY_NAME} v{APP_VERSION}")
        self.root.geometry("760x800")
        self.root.minsize(760, 800)
        self.root.configure(bg=BG_COLOR)

        self.config = config
        self.selected_files = []
        self.upload_file_names = {}

        self.settings = load_settings()

        self.uploaded_by_var = tk.StringVar(value=self.get_default_uploader())
        self.uploader_option_menu = None

        default_category = self.get_default_category()
        self.category_var = tk.StringVar(value=default_category)

        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Ready")

        self.category_frame = None

        self.build_gui()
        self.root.after(1000, lambda: check_for_updates(self.root))

    def create_button(self, parent, text, command, width=18):
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            font=("Segoe UI", 10, "bold"),
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            activebackground=ACCENT_COLOR,
            activeforeground=BUTTON_TEXT_COLOR,
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=4
        )

    def create_label(self, parent, text, font=None, fg=None):
        if font is None:
            font = ("Segoe UI", 10)

        if fg is None:
            fg = TEXT_COLOR

        return tk.Label(
            parent,
            text=text,
            font=font,
            bg=BG_COLOR,
            fg=fg
        )

    def get_uploaders(self):
        return normalize_uploaders(self.config.get("uploaders", []))

    def get_default_uploader(self):
        uploaders = self.get_uploaders()
        last_uploaded_by = self.settings.get("last_uploaded_by", uploaders[0])

        if last_uploaded_by not in uploaders:
            return uploaders[0]

        return last_uploaded_by

    def get_default_category(self):
        destinations = self.config.get("destinations", {})

        if destinations:
            return next(iter(destinations.keys()))

        return ""

    def build_gui(self):
        self.build_menu()

        title_label = tk.Label(
            self.root,
            text=f"{APP_DISPLAY_NAME} v{APP_VERSION}",
            font=("Segoe UI", 24, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title_label.pack(pady=(18, 4))

        subtitle_label = tk.Label(
            self.root,
            text="Quickly copy or move files to configured network destinations.",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg=MUTED_TEXT_COLOR
        )
        subtitle_label.pack(pady=(0, 12))

        upload_frame = tk.Frame(self.root, bg=BG_COLOR)
        upload_frame.pack(fill="x", padx=24)

        tk.Label(
            upload_frame,
            text="Uploaded by:",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky="w")

        self.uploader_option_menu = tk.OptionMenu(
            upload_frame,
            self.uploaded_by_var,
            *self.get_uploaders()
        )
        self.uploader_option_menu.configure(
            font=("Segoe UI", 10),
            bg=INPUT_COLOR,
            fg="#000000",
            activebackground="#e6e6e6",
            relief="flat",
            width=18
        )
        self.uploader_option_menu.grid(
            row=0,
            column=1,
            sticky="w",
            padx=(8, 0),
            pady=3
        )

        self.category_frame = tk.LabelFrame(
            self.root,
            text="Destination Category",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )
        self.category_frame.pack(fill="x", padx=24, pady=12)

        self.build_destination_buttons()

        drop_label = tk.Label(
            self.root,
            text="Drag files into the box below",
            font=("Segoe UI", 12, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        drop_label.pack(pady=(8, 5))

        self.file_listbox = tk.Listbox(
            self.root,
            width=85,
            height=12,
            font=("Segoe UI", 9),
            bg="#f7f7fb",
            fg="#111111",
            selectbackground=ACCENT_COLOR,
            selectforeground="#ffffff",
            relief="flat"
        )
        self.file_listbox.pack(
            padx=24,
            pady=5,
            fill="both",
            expand=True
        )

        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind("<<Drop>>", self.handle_drop)
        self.file_listbox.bind("<<ListboxSelect>>", self.handle_file_selection)

        rename_frame = tk.LabelFrame(
            self.root,
            text="Rename Selected File",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )
        rename_frame.pack(fill="x", padx=24, pady=8)
        rename_frame.columnconfigure(1, weight=1)

        tk.Label(
            rename_frame,
            text="Upload as:",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky="w", padx=8, pady=8)

        self.rename_var = tk.StringVar()
        self.rename_entry = tk.Entry(
            rename_frame,
            textvariable=self.rename_var,
            font=("Segoe UI", 10),
            relief="flat"
        )
        self.rename_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=8)
        self.rename_entry.bind(
            "<Return>",
            lambda event: self.apply_selected_file_name()
        )

        self.create_button(
            rename_frame,
            "Apply Rename",
            self.apply_selected_file_name,
            width=14
        ).grid(row=0, column=2, padx=5, pady=8)

        self.create_button(
            rename_frame,
            "Use Original",
            self.reset_selected_file_name,
            width=14
        ).grid(row=0, column=3, padx=8, pady=8)

        button_frame = tk.Frame(self.root, bg=BG_COLOR)
        button_frame.pack(pady=10)

        self.create_button(
            button_frame,
            "Upload Files",
            self.upload_files
        ).grid(row=0, column=0, padx=5)

        self.create_button(
            button_frame,
            "Clear List",
            self.clear_files
        ).grid(row=0, column=1, padx=5)

        self.create_button(
            button_frame,
            "Settings",
            self.open_settings
        ).grid(row=0, column=2, padx=5)

        progress_frame = tk.Frame(self.root, bg=BG_COLOR)
        progress_frame.pack(fill="x", padx=24, pady=8)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill="x")

        self.status_label = tk.Label(
            progress_frame,
            textvariable=self.status_var,
            anchor="w",
            bg=BG_COLOR,
            fg=MUTED_TEXT_COLOR,
            font=("Segoe UI", 9)
        )
        self.status_label.pack(fill="x", pady=3)

    def refresh_uploader_menu(self):
        uploaders = self.get_uploaders()

        if self.uploaded_by_var.get() not in uploaders:
            self.uploaded_by_var.set(uploaders[0])

        menu = self.uploader_option_menu["menu"]
        menu.delete(0, "end")

        for uploader in uploaders:
            menu.add_command(
                label=uploader,
                command=lambda value=uploader: self.uploaded_by_var.set(value)
            )

    def build_destination_buttons(self):
        for widget in self.category_frame.winfo_children():
            widget.destroy()

        destinations = self.config.get("destinations", {})

        if not destinations:
            tk.Label(
                self.category_frame,
                text="No destinations configured. Open Settings to add one.",
                bg=PANEL_COLOR,
                fg=MUTED_TEXT_COLOR,
                font=("Segoe UI", 10)
            ).pack(anchor="w", padx=8, pady=8)
            self.category_var.set("")
            return

        current_category = self.category_var.get()

        if current_category not in destinations:
            self.category_var.set(self.get_default_category())

        for destination_key, destination_data in destinations.items():
            label = destination_data.get("label", make_label_from_key(destination_key))

            tk.Radiobutton(
                self.category_frame,
                text=label,
                variable=self.category_var,
                value=destination_key,
                bg=PANEL_COLOR,
                fg=TEXT_COLOR,
                selectcolor=BG_COLOR,
                activebackground=PANEL_COLOR,
                activeforeground=TEXT_COLOR,
                font=("Segoe UI", 10)
            ).pack(anchor="w")

    def build_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def show_about(self):
        messagebox.showinfo(
            "About",
            f"{APP_DISPLAY_NAME}\n"
            f"Version {APP_VERSION}\n\n"
            f"Config location:\n{CONFIG_FILE}\n\n"
            f"Logs location:\n{LOG_FOLDER}"
        )

    def open_settings(self):
        SettingsWindow(
            parent=self.root,
            config=self.config,
            config_file=CONFIG_FILE,
            on_save_callback=self.apply_updated_config
        )

    def apply_updated_config(self, updated_config):
        self.config = normalize_config(updated_config)
        save_config(self.config)
        self.refresh_uploader_menu()
        self.build_destination_buttons()
        self.status_var.set("Settings updated.")

    def handle_drop(self, event):
        dropped_files = self.root.tk.splitlist(event.data)

        for file_name in dropped_files:
            file_path = Path(file_name)

            if not file_path.is_file():
                messagebox.showwarning(
                    "Skipped Item",
                    f"Only files can be uploaded:\n{file_path.name}"
                )
                continue

            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.upload_file_names[file_path] = file_path.name
                self.file_listbox.insert(
                    tk.END,
                    self.get_file_display_name(file_path)
                )

        self.status_var.set(f"Files ready: {len(self.selected_files)}")

        if self.selected_files and not self.file_listbox.curselection():
            self.file_listbox.selection_set(0)
            self.load_selected_file_name(0)

    def clear_files(self):
        self.selected_files.clear()
        self.upload_file_names.clear()
        self.rename_var.set("")
        self.file_listbox.delete(0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("Ready")

    def get_file_display_name(self, source_path):
        upload_file_name = self.upload_file_names.get(
            source_path,
            source_path.name
        )

        if upload_file_name == source_path.name:
            return str(source_path)

        return f"{source_path}  ->  {upload_file_name}"

    def normalize_upload_file_name(self, source_path, upload_file_name):
        upload_file_name = upload_file_name.strip()

        if not upload_file_name:
            return source_path.name

        if any(char in upload_file_name for char in INVALID_FILE_NAME_CHARS):
            raise ValueError(
                'File names cannot contain these characters: < > : " / \\ | ? *'
            )

        upload_path = Path(upload_file_name)

        if upload_path.name != upload_file_name:
            raise ValueError("Enter a file name only, not a folder path.")

        if not upload_path.stem:
            raise ValueError("Enter a file name before the extension.")

        if not upload_path.suffix:
            upload_file_name = f"{upload_file_name}{source_path.suffix}"

        return upload_file_name

    def refresh_file_list_item(self, index):
        source_path = self.selected_files[index]
        self.file_listbox.delete(index)
        self.file_listbox.insert(index, self.get_file_display_name(source_path))
        self.file_listbox.selection_clear(0, tk.END)
        self.file_listbox.selection_set(index)

    def load_selected_file_name(self, index):
        source_path = self.selected_files[index]
        self.rename_var.set(
            self.upload_file_names.get(source_path, source_path.name)
        )

    def handle_file_selection(self, event):
        selection = self.file_listbox.curselection()

        if selection:
            self.load_selected_file_name(selection[0])

    def apply_selected_file_name(self):
        selection = self.file_listbox.curselection()

        if not selection:
            messagebox.showerror(
                "No File Selected",
                "Select a file from the list before renaming it."
            )
            return False

        index = selection[0]
        source_path = self.selected_files[index]

        try:
            upload_file_name = self.normalize_upload_file_name(
                source_path,
                self.rename_var.get()
            )
        except ValueError as error:
            messagebox.showerror("Invalid File Name", str(error))
            return False

        self.upload_file_names[source_path] = upload_file_name
        self.refresh_file_list_item(index)
        self.status_var.set(f"Renamed for upload: {upload_file_name}")
        return True

    def reset_selected_file_name(self):
        selection = self.file_listbox.curselection()

        if not selection:
            messagebox.showerror(
                "No File Selected",
                "Select a file from the list before resetting its name."
            )
            return

        index = selection[0]
        source_path = self.selected_files[index]
        self.upload_file_names[source_path] = source_path.name
        self.rename_var.set(source_path.name)
        self.refresh_file_list_item(index)
        self.status_var.set(f"Using original name: {source_path.name}")

    def upload_files(self):
        uploaded_by = self.uploaded_by_var.get().strip()
        category = self.category_var.get()

        if not uploaded_by:
            uploaded_by = "User"

        if not self.selected_files:
            messagebox.showerror(
                "No Files",
                "Drag at least one file into the box first."
            )
            return

        if category not in self.config["destinations"]:
            messagebox.showerror(
                "Config Error",
                "Please select a valid destination category."
            )
            return

        if self.file_listbox.curselection() and not self.apply_selected_file_name():
            return

        save_settings(uploaded_by)

        destination_data = self.config["destinations"][category]
        destination_folder = Path(destination_data["path"])
        move_files = self.config.get("move_files", False)

        successful_uploads = 0
        skipped_uploads = 0
        failed_uploads = 0
        total_files = len(self.selected_files)

        self.progress_var.set(0)
        self.status_var.set("Starting upload...")
        self.root.update_idletasks()

        for index, source_path in enumerate(self.selected_files, start=1):
            try:
                upload_file_name = self.upload_file_names.get(
                    source_path,
                    source_path.name
                )

                self.status_var.set(
                    f"Checking {index} of {total_files}: {upload_file_name}"
                )
                self.root.update_idletasks()

                if file_already_exists(destination_folder, upload_file_name):
                    should_upload = messagebox.askyesno(
                        "File Already Exists",
                        f"This file already exists in the destination:\n\n"
                        f"{upload_file_name}\n\n"
                        f"Do you want to upload it anyway?\n\n"
                        f"If yes, it will be renamed automatically."
                    )

                    if not should_upload:
                        logging.info(
                            "Skipped duplicate file by %s: %s",
                            uploaded_by,
                            source_path
                        )

                        skipped_uploads += 1

                        progress_percent = (index / total_files) * 100
                        self.progress_var.set(progress_percent)
                        self.status_var.set(
                            f"Skipped {index} of {total_files}: {upload_file_name}"
                        )
                        self.root.update_idletasks()
                        continue

                self.status_var.set(
                    f"Uploading {index} of {total_files}: {upload_file_name}"
                )
                self.root.update_idletasks()

                destination_path, action = copy_or_move_file(
                    source_path,
                    destination_folder,
                    move_files,
                    upload_file_name
                )

                logging.info(
                    "File %s by %s: %s -> %s",
                    action,
                    uploaded_by,
                    source_path,
                    destination_path
                )

                successful_uploads += 1

                progress_percent = (index / total_files) * 100
                self.progress_var.set(progress_percent)
                self.status_var.set(
                    f"Uploaded {index} of {total_files}: {upload_file_name}"
                )
                self.root.update_idletasks()

            except Exception as error:
                failed_uploads += 1

                logging.exception("Failed to upload file: %s", source_path)
                messagebox.showerror(
                    "Upload Failed",
                    f"Could not upload:\n{source_path.name}\n\n{error}"
                )

                progress_percent = (index / total_files) * 100
                self.progress_var.set(progress_percent)
                self.status_var.set(
                    f"Failed {index} of {total_files}: {source_path.name}"
                )
                self.root.update_idletasks()

        self.progress_var.set(100)
        self.status_var.set("Upload complete.")
        self.root.update_idletasks()

        messagebox.showinfo(
            "Upload Complete",
            f"Files uploaded successfully: {successful_uploads}\n"
            f"Files skipped: {skipped_uploads}\n"
            f"Files failed: {failed_uploads}"
        )

        self.clear_files()


def main():
    setup_logging()
    logging.info("Starting %s version %s", APP_NAME, APP_VERSION)

    root = TkinterDnD.Tk()
    set_application_icon(root)

    try:
        config = get_startup_config(root)

        if config is None:
            logging.info("First-run setup was cancelled. Exiting.")
            root.destroy()
            return

        NetworkUploaderApp(root, config)
        root.mainloop()

    except Exception as error:
        logging.exception("Application failed to start.")

        messagebox.showerror(
            "Startup Error",
            f"The application failed to start:\n\n{error}"
        )

        root.destroy()


if __name__ == "__main__":
    main()
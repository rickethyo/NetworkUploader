##5/28/2026##

import json
import re
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from tkinter import filedialog


BG_COLOR = "#202434"
PANEL_COLOR = "#2b3045"
TEXT_COLOR = "#f4f4f8"
MUTED_TEXT_COLOR = "#c9cedf"
ACCENT_COLOR = "#4f8cff"
BUTTON_COLOR = "#3f6fd6"
BUTTON_TEXT_COLOR = "#ffffff"
INPUT_COLOR = "#ffffff"


class SettingsWindow:
    def __init__(self, parent, config, config_file, on_save_callback):
        self.parent = parent
        self.config = config.copy()
        self.config_file = Path(config_file)
        self.on_save_callback = on_save_callback
        self.destination_rows = []

        self.window = tk.Toplevel(parent)
        self.window.title("Network Uploader Settings")
        self.window.geometry("820x700")
        self.window.minsize(820, 700)
        self.window.configure(bg=BG_COLOR)
        self.window.transient(parent)
        self.window.grab_set()

        self.network_share_var = tk.StringVar(
            value=self.config.get("network_share", "")
        )

        self.move_files_var = tk.BooleanVar(value=self.config.get("move_files", False))

        uploaders = self.config.get("uploaders", ["User"])
        self.uploaders_var = tk.StringVar(value=", ".join(uploaders))

        self.build_gui()
        self.load_destination_rows()

    def create_button(self, parent, text, command, width=14):
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

    def build_gui(self):
        title_label = tk.Label(
            self.window,
            text="Network Uploader Settings",
            font=("Segoe UI", 20, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title_label.pack(pady=(16, 4))

        subtitle_label = tk.Label(
            self.window,
            text="Manage users, upload behavior, and network destinations.",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg=MUTED_TEXT_COLOR
        )
        subtitle_label.pack(pady=(0, 12))

        base_frame = tk.LabelFrame(
            self.window,
            text="Base Network Share",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )
        base_frame.pack(fill="x", padx=20, pady=6)
        base_frame.columnconfigure(1, weight=1)

        tk.Label(
            base_frame,
            text="Base folder:",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky="w", padx=8, pady=8)

        tk.Entry(
            base_frame,
            textvariable=self.network_share_var,
            font=("Segoe UI", 10),
            relief="flat"
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=8)

        self.create_button(
            base_frame,
            "Browse",
            self.browse_network_share,
            width=10
        ).grid(row=0, column=2, padx=8, pady=8)

        destinations_frame = tk.LabelFrame(
            self.window,
            text="Destination Folders",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )
        destinations_frame.pack(fill="both", expand=True, padx=20, pady=6)

        header_frame = tk.Frame(destinations_frame, bg=PANEL_COLOR)
        header_frame.pack(fill="x", padx=8, pady=(8, 2))
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=3)

        tk.Label(
            header_frame,
            text="Display Name",
            bg=PANEL_COLOR,
            fg=MUTED_TEXT_COLOR,
            font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            header_frame,
            text="Folder Path",
            bg=PANEL_COLOR,
            fg=MUTED_TEXT_COLOR,
            font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=1, sticky="w")

        self.destinations_container = tk.Frame(destinations_frame, bg=PANEL_COLOR)
        self.destinations_container.pack(fill="both", expand=True, padx=8, pady=4)

        self.create_button(
            destinations_frame,
            "Add Destination",
            self.add_blank_destination_row,
            width=18
        ).pack(anchor="w", padx=8, pady=(2, 8))

        users_frame = tk.LabelFrame(
            self.window,
            text="Upload Users",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )
        users_frame.pack(fill="x", padx=20, pady=6)
        users_frame.columnconfigure(0, weight=1)

        tk.Label(
            users_frame,
            text="Separate users with commas. The first user becomes the default.",
            bg=PANEL_COLOR,
            fg=MUTED_TEXT_COLOR,
            font=("Segoe UI", 9)
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))

        tk.Entry(
            users_frame,
            textvariable=self.uploaders_var,
            font=("Segoe UI", 10),
            relief="flat"
        ).grid(row=1, column=0, sticky="ew", padx=8, pady=(2, 8))


        behavior_frame = tk.LabelFrame(
            self.window,
            text="Upload Behavior",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )
        behavior_frame.pack(fill="x", padx=20, pady=6)

        tk.Radiobutton(
            behavior_frame,
            text="Copy files to destination",
            variable=self.move_files_var,
            value=False,
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            selectcolor=BG_COLOR,
            activebackground=PANEL_COLOR,
            activeforeground=TEXT_COLOR,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=8, pady=2)

        tk.Radiobutton(
            behavior_frame,
            text="Move files to destination",
            variable=self.move_files_var,
            value=True,
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            selectcolor=BG_COLOR,
            activebackground=PANEL_COLOR,
            activeforeground=TEXT_COLOR,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=8, pady=2)

        button_frame = tk.Frame(self.window, bg=BG_COLOR)
        button_frame.pack(pady=12)

        self.create_button(
            button_frame,
            "Save",
            self.save_settings,
            width=14
        ).grid(row=0, column=0, padx=5)

        self.create_button(
            button_frame,
            "Cancel",
            self.window.destroy,
            width=14
        ).grid(row=0, column=1, padx=5)

    def browse_network_share(self):
        initial_directory = self.network_share_var.get().strip()

        if not initial_directory:
            initial_directory = str(Path.home())

        selected_folder = filedialog.askdirectory(
            parent=self.window,
            title="Select Base Network Folder",
            initialdir=initial_directory
        )

        if selected_folder:
            self.network_share_var.set(selected_folder)

    def load_destination_rows(self):
        destinations = self.config.get("destinations", {})

        for destination_key, destination_data in destinations.items():
            if isinstance(destination_data, dict):
                label = destination_data.get("label", destination_key)
                path = destination_data.get("path", "")
            else:
                label = self.make_label_from_key(destination_key)
                path = str(destination_data)

            self.add_destination_row(
                key=destination_key,
                label=label,
                path=path
            )

        if not self.destination_rows:
            self.add_destination_row(
                key=None,
                label="New Destination",
                path=""
            )

    def add_blank_destination_row(self):
        self.add_destination_row(
            key=None,
            label="New Destination",
            path=""
        )

    def add_destination_row(self, key, label, path):
        row_frame = tk.Frame(self.destinations_container, bg=PANEL_COLOR)
        row_frame.pack(fill="x", pady=3)
        row_frame.columnconfigure(0, weight=1)
        row_frame.columnconfigure(1, weight=3)

        label_var = tk.StringVar(value=label)
        path_var = tk.StringVar(value=path)

        tk.Entry(
            row_frame,
            textvariable=label_var,
            font=("Segoe UI", 10),
            relief="flat"
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        tk.Entry(
            row_frame,
            textvariable=path_var,
            font=("Segoe UI", 10),
            relief="flat"
        ).grid(row=0, column=1, sticky="ew", padx=5)

        self.create_button(
            row_frame,
            "Browse",
            lambda: self.browse_folder(path_var),
            width=10
        ).grid(row=0, column=2, padx=5)

        self.create_button(
            row_frame,
            "Remove",
            lambda: self.remove_destination_row(row_frame),
            width=10
        ).grid(row=0, column=3, padx=(5, 0))

        row_data = {
            "key": key,
            "frame": row_frame,
            "label_var": label_var,
            "path_var": path_var
        }

        self.destination_rows.append(row_data)

    def remove_destination_row(self, row_frame):
        if len(self.destination_rows) <= 1:
            messagebox.showerror(
                "Cannot Remove",
                "At least one destination is required.",
                parent=self.window
            )
            return

        for row in self.destination_rows:
            if row["frame"] == row_frame:
                self.destination_rows.remove(row)
                row_frame.destroy()
                return

    def browse_folder(self, variable):
        initial_directory = variable.get().strip()

        if not initial_directory:
            initial_directory = self.network_share_var.get().strip()

        if not initial_directory:
            initial_directory = str(Path.home())

        selected_folder = filedialog.askdirectory(
            parent=self.window,
            title="Select Destination Folder",
            initialdir=initial_directory
        )

        if selected_folder:
            variable.set(selected_folder)

    def parse_uploaders(self):
        raw_uploaders = self.uploaders_var.get().strip()

        if not raw_uploaders:
            return ["User"]

        uploaders = []

        for uploader in raw_uploaders.split(","):
            uploader = uploader.strip()

            if uploader and uploader not in uploaders:
                uploaders.append(uploader)

        if not uploaders:
            uploaders = ["User"]

        return uploaders

    def build_destinations_config(self):
        destinations = {}
        used_keys = set()

        for row in self.destination_rows:
            label = row["label_var"].get().strip()
            path = row["path_var"].get().strip()

            if not label:
                raise ValueError("Destination names cannot be blank.")

            if not path:
                raise ValueError(f"The path for '{label}' cannot be blank.")

            key = row["key"]

            if not key:
                key = self.make_key_from_label(label, used_keys)
            else:
                key = self.make_safe_existing_key(key)

                if key in used_keys:
                    key = self.make_key_from_label(label, used_keys)

            used_keys.add(key)

            destinations[key] = {
                "label": label,
                "path": path
            }

        if not destinations:
            raise ValueError("At least one destination is required.")

        return destinations

    def make_safe_existing_key(self, key):
        key = str(key).strip().lower()
        key = re.sub(r"[^a-z0-9]+", "_", key)
        key = key.strip("_")

        if not key:
            key = "destination"

        return key

    def make_key_from_label(self, label, used_keys):
        base_key = label.strip().lower()
        base_key = re.sub(r"[^a-z0-9]+", "_", base_key)
        base_key = base_key.strip("_")

        if not base_key:
            base_key = "destination"

        candidate_key = base_key
        counter = 2

        while candidate_key in used_keys:
            candidate_key = f"{base_key}_{counter}"
            counter += 1

        return candidate_key

    def make_label_from_key(self, key):
        return str(key).replace("_", " ").title()

    def save_settings(self):
        try:
            network_share = self.network_share_var.get().strip()

            if not network_share:
                raise ValueError("Base folder cannot be blank.")

            updated_config = self.config.copy()
            updated_config["network_share"] = network_share
            updated_config["destinations"] = self.build_destinations_config()
            updated_config["move_files"] = self.move_files_var.get()
            updated_config["uploaders"] = self.parse_uploaders()

            with open(self.config_file, "w", encoding="utf-8") as file:
                json.dump(updated_config, file, indent=4)

            self.on_save_callback(updated_config)

            messagebox.showinfo(
                "Settings Saved",
                "Settings were saved successfully.",
                parent=self.window
            )

            self.window.destroy()

        except ValueError as error:
            messagebox.showerror(
                "Invalid Settings",
                str(error),
                parent=self.window
            )

        except OSError as error:
            messagebox.showerror(
                "Save Failed",
                f"Could not save settings:\n\n{error}",
                parent=self.window
            )
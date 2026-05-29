import json
import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from tkinter import messagebox


BG_COLOR = "#202434"
PANEL_COLOR = "#2b3045"
TEXT_COLOR = "#f4f4f8"
MUTED_TEXT_COLOR = "#c9cedf"
ACCENT_COLOR = "#4f8cff"
BUTTON_COLOR = "#3f6fd6"
BUTTON_TEXT_COLOR = "#ffffff"
INPUT_COLOR = "#ffffff"


class FirstRunWindow:
    def __init__(self, parent, config_file, default_config):
        self.parent = parent
        self.config_file = Path(config_file)
        self.default_config = default_config.copy()
        self.config_created = False
        self.created_config = None

        self.window = tk.Toplevel(parent)
        self.window.title("First Run Setup")
        self.window.geometry("760x820")
        self.window.minsize(760, 820)
        self.window.configure(bg=BG_COLOR)
        self.window.transient(parent)
        self.window.grab_set()

        self.network_share_var = tk.StringVar(
            value=self.default_config.get("network_share", "")
        )

        self.destination_name_var = tk.StringVar(value="Main Uploads")
        self.destination_path_var = tk.StringVar(
            value=self.default_config.get("network_share", "")
        )

        extensions = self.default_config.get(
            "video_extensions",
            [".mp4", ".mkv", ".mov", ".avi", ".m4v", ".wmv"]
        )

        self.extensions_var = tk.StringVar(value=", ".join(extensions))
        self.move_files_var = tk.BooleanVar(
            value=self.default_config.get("move_files", False)
        )

        self.default_uploader_var = tk.StringVar(value="User")
        self.additional_uploaders_var = tk.StringVar(value="")

        self.build_gui()

        self.window.protocol("WM_DELETE_WINDOW", self.cancel_setup)

    def create_button(self, parent, text, command, width=16):
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
            text="Welcome to Network Uploader",
            font=("Segoe UI", 22, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title_label.pack(pady=(16, 5))

        intro_label = tk.Label(
            self.window,
            text=(
                "Before using the uploader, choose your base network folder, "
                "create your first upload destination, and optionally add users."
            ),
            wraplength=700,
            justify="center",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg=MUTED_TEXT_COLOR
        )
        intro_label.pack(pady=(0, 15))

        base_frame = tk.LabelFrame(
            self.window,
            text="Base Network Share",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )
        base_frame.pack(fill="x", padx=20, pady=8)
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

        tk.Label(
            base_frame,
            text=r"Example: \\SERVER\Share\Uploads",
            anchor="w",
            bg=PANEL_COLOR,
            fg=MUTED_TEXT_COLOR,
            font=("Segoe UI", 9)
        ).grid(row=1, column=1, sticky="w", padx=5, pady=(0, 8))

        destination_frame = tk.LabelFrame(
            self.window,
            text="First Destination",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )
        destination_frame.pack(fill="x", padx=20, pady=8)
        destination_frame.columnconfigure(1, weight=1)

        tk.Label(
            destination_frame,
            text="Display name:",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky="w", padx=8, pady=8)

        tk.Entry(
            destination_frame,
            textvariable=self.destination_name_var,
            font=("Segoe UI", 10),
            relief="flat"
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=8)

        tk.Label(
            destination_frame,
            text="Folder path:",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10)
        ).grid(row=1, column=0, sticky="w", padx=8, pady=8)

        tk.Entry(
            destination_frame,
            textvariable=self.destination_path_var,
            font=("Segoe UI", 10),
            relief="flat"
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=8)

        self.create_button(
            destination_frame,
            "Browse",
            self.browse_destination_folder,
            width=10
        ).grid(row=1, column=2, padx=8, pady=8)

        self.create_button(
            destination_frame,
            "Use Base Folder",
            self.use_base_as_destination,
            width=16
        ).grid(row=2, column=1, sticky="w", padx=5, pady=(0, 8))

        users_frame = tk.LabelFrame(
            self.window,
            text="Upload Users",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )
        users_frame.pack(fill="x", padx=20, pady=8)
        users_frame.columnconfigure(1, weight=1)

        tk.Label(
            users_frame,
            text="Default user:",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky="w", padx=8, pady=8)

        tk.Entry(
            users_frame,
            textvariable=self.default_uploader_var,
            font=("Segoe UI", 10),
            relief="flat"
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=8)

        tk.Label(
            users_frame,
            text="Additional users:",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10)
        ).grid(row=1, column=0, sticky="w", padx=8, pady=8)

        tk.Entry(
            users_frame,
            textvariable=self.additional_uploaders_var,
            font=("Segoe UI", 10),
            relief="flat"
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=8)

        tk.Label(
            users_frame,
            text="Separate additional users with commas. Example: User 2, User 3",
            anchor="w",
            bg=PANEL_COLOR,
            fg=MUTED_TEXT_COLOR,
            font=("Segoe UI", 9)
        ).grid(row=2, column=1, sticky="w", padx=5, pady=(0, 8))

        extensions_frame = tk.LabelFrame(
            self.window,
            text="Allowed File Extensions",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )
        extensions_frame.pack(fill="x", padx=20, pady=8)
        extensions_frame.columnconfigure(0, weight=1)

        tk.Label(
            extensions_frame,
            text="Separate extensions with commas.",
            bg=PANEL_COLOR,
            fg=MUTED_TEXT_COLOR,
            font=("Segoe UI", 9)
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))

        tk.Entry(
            extensions_frame,
            textvariable=self.extensions_var,
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
        behavior_frame.pack(fill="x", padx=20, pady=8)

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
        button_frame.pack(pady=14)

        self.create_button(
            button_frame,
            "Save and Start",
            self.save_setup,
            width=16
        ).grid(row=0, column=0, padx=5)

        self.create_button(
            button_frame,
            "Cancel",
            self.cancel_setup,
            width=16
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

            if not self.destination_path_var.get().strip():
                self.destination_path_var.set(selected_folder)

    def browse_destination_folder(self):
        initial_directory = self.destination_path_var.get().strip()

        if not initial_directory:
            initial_directory = self.network_share_var.get().strip()

        if not initial_directory:
            initial_directory = str(Path.home())

        selected_folder = filedialog.askdirectory(
            parent=self.window,
            title="Select First Destination Folder",
            initialdir=initial_directory
        )

        if selected_folder:
            self.destination_path_var.set(selected_folder)

    def use_base_as_destination(self):
        base_folder = self.network_share_var.get().strip()

        if not base_folder:
            messagebox.showerror(
                "Missing Base Folder",
                "Enter or browse to a base folder first.",
                parent=self.window
            )
            return

        self.destination_path_var.set(base_folder)

    def parse_extensions(self):
        raw_extensions = self.extensions_var.get().strip()

        if not raw_extensions:
            raise ValueError("At least one file extension is required.")

        extensions = []

        for extension in raw_extensions.split(","):
            extension = extension.strip().lower()

            if not extension:
                continue

            if not extension.startswith("."):
                extension = f".{extension}"

            if extension not in extensions:
                extensions.append(extension)

        if not extensions:
            raise ValueError("At least one file extension is required.")

        return extensions

    def parse_uploaders(self):
        uploaders = []

        default_uploader = self.default_uploader_var.get().strip()

        if not default_uploader:
            default_uploader = "User"

        uploaders.append(default_uploader)

        raw_additional_uploaders = self.additional_uploaders_var.get().strip()

        if raw_additional_uploaders:
            for uploader in raw_additional_uploaders.split(","):
                uploader = uploader.strip()

                if uploader and uploader not in uploaders:
                    uploaders.append(uploader)

        if not uploaders:
            uploaders = ["User"]

        return uploaders

    def make_key_from_label(self, label):
        key = label.strip().lower()
        key = re.sub(r"[^a-z0-9]+", "_", key)
        key = key.strip("_")

        if not key:
            key = "destination"

        return key

    def save_setup(self):
        try:
            network_share = self.network_share_var.get().strip()
            destination_name = self.destination_name_var.get().strip()
            destination_path = self.destination_path_var.get().strip()
            extensions = self.parse_extensions()
            uploaders = self.parse_uploaders()

            if not network_share:
                raise ValueError("Base folder cannot be blank.")

            if not destination_name:
                raise ValueError("First destination name cannot be blank.")

            if not destination_path:
                raise ValueError("First destination path cannot be blank.")

            destination_key = self.make_key_from_label(destination_name)

            config = self.default_config.copy()

            config["network_share"] = network_share
            config["destinations"] = {
                destination_key: {
                    "label": destination_name,
                    "path": destination_path
                }
            }
            config["video_extensions"] = extensions
            config["move_files"] = self.move_files_var.get()
            config["uploaders"] = uploaders

            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as file:
                json.dump(config, file, indent=4)

            self.config_created = True
            self.created_config = config

            messagebox.showinfo(
                "Setup Complete",
                "Setup is complete. Network Uploader will now open.",
                parent=self.window
            )

            self.window.destroy()

        except ValueError as error:
            messagebox.showerror(
                "Invalid Setup",
                str(error),
                parent=self.window
            )

        except OSError as error:
            messagebox.showerror(
                "Setup Failed",
                f"Could not save config file:\n\n{error}",
                parent=self.window
            )

    def cancel_setup(self):
        should_exit = messagebox.askyesno(
            "Exit Setup",
            "Network Uploader cannot start until setup is complete.\n\nExit the program?",
            parent=self.window
        )

        if should_exit:
            self.window.destroy()
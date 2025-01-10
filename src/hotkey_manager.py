from tkinter import simpledialog, messagebox
import json
import os
import tkinter as tk


class HotkeyManager:
    def __init__(self, data_dir):
        """
        Hotkey manager class to manage hotkeys for the keylogger.

        :param data_dir: The directory to save the hotkeys to.
        """

        self.data_dir = data_dir
        self.hotkeys = self.load_hotkeys(self.data_dir)

    def customize_hotkeys(self, root):
        """
        Open a GUI window to customize all hotkeys.
        """

        # Create a new window
        hotkey_window = tk.Toplevel(root)
        hotkey_window.title("Customize Hotkeys")

        # Display the current hotkeys in a form
        tk.Label(hotkey_window, text="Customize Hotkeys", font=("Arial", 14)).pack(pady=10)

        # Frame to hold hotkey entries
        frame = tk.Frame(hotkey_window)
        frame.pack(pady=10, padx=10, fill="both", expand=True)

        hotkey_entries = {}

        # Create a row for each hotkey
        for action, current_hotkey in self.hotkeys.items():
            row = tk.Frame(frame)
            row.pack(fill="x", pady=5)

            tk.Label(row, text=f"{action}:", width=15, anchor="w").pack(side="left")
            hotkey_entry = tk.Entry(row)
            hotkey_entry.insert(0, current_hotkey)
            hotkey_entry.pack(side="left", fill="x", expand=True)
            hotkey_entries[action] = hotkey_entry

        def save_hotkeys():
            """
            Save the updated hotkeys and close the window.
            """
            for action, entry in hotkey_entries.items():
                new_hotkey = entry.get().strip()
                if new_hotkey:
                    self.hotkeys[action] = new_hotkey

            # Save the updated hotkeys to file
            self.save_hotkeys(self.data_dir)
            messagebox.showinfo("Hotkeys Updated", "Hotkeys have been successfully updated.")
            hotkey_window.destroy()

        # Save and Cancel buttons
        button_frame = tk.Frame(hotkey_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Save", command=save_hotkeys).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel", command=hotkey_window.destroy).pack(side="left", padx=10)

    def get_hotkeys(self):
        """
        Retrieve the current hotkey configuration.

        :return: The current hotkey configuration.
        """

        return self.hotkeys

    def save_hotkeys(self, dir):
        """
        Save the current hotkey configuration to a file.

        :param dir: The directory to save the hotkeys to.
        :return: None
        """

        with open(dir + "/hotkeys.json", "w") as f:
            json.dump(self.hotkeys, f)

    def load_hotkeys(self, dir):
        """
        Load the hotkey configuration from a file or set defaults if the file does not exist.

        :param dir: The directory to load the hotkeys from.
        :return: The hotkey configuration.
        """

        if not os.path.exists(dir + "/hotkeys.json"):
            return {
                "Start": "<Control-s>",
                "Stop": "<Control-x>",
                "Save": "<Control-v>",
                "Load": "<Control-l>",
            }
        else:
            with open(dir + "/hotkeys.json", "r") as f:
                return json.load(f)

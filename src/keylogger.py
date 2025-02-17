from pynput import keyboard
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import sys
import threading
import tkinter as tk


class Keylogger:
    def __init__(self):
        """
        Keylogger class to log key presses and display them in a table.
        """

        # Load metadata
        if getattr(sys, "frozen", False):  # Check if running as an executable
            base_path = sys._MEIPASS  # PyInstaller's temporary directory
        else:
            base_path = os.path.dirname(__file__)  # Directory of the script

        # Construct the full path to metadata.json
        metadata_path = os.path.join(base_path, "metadata.json")

        # Load metadata
        with open(metadata_path, "r") as f:
            data = json.load(f)
        self.title = f"Keylogger - v{data['version']}"

        # Keylogger state
        self.key_counts = {}
        self.save_file = "keylogger_state.json"
        self.run = False

        self.table = None
        self.root = None
        self.listener = None

        # Create the data directory if it doesn't exist
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def save_state(self) -> None:
        """
        Save the current key counts to a JSON file.

        :return: None
        """

        if self.run:
            messagebox.showwarning("Save File", "Cannot save state while keylogger is running.")
            return

        file_name = simpledialog.askstring("Save File", "Enter a file name:")
        if not file_name:
            messagebox.showwarning("Save File", "Save operation canceled.")
            return

        file_path = os.path.join(self.data_dir, f"{file_name}.json")
        with open(file_path, "w") as f:
            sorted_counts = {k: v for k, v in sorted(self.key_counts.items(), key=lambda x: x[1], reverse=True)}
            json.dump(sorted_counts, f, indent=4)
        messagebox.showinfo("Save State", f"State saved to {file_path}.")

    def load_state(self) -> None:
        """
        Load key counts from a JSON file.

        :return: None
        """

        if self.run:
            messagebox.showwarning("Load File", "Cannot load state while keylogger is running.")
            return

        file_path = filedialog.askopenfilename(
            initialdir=self.data_dir,
            title="Select a file to load",
            filetypes=(("JSON Files", "*.json"), ("All Files", "*.*")),
        )
        if not file_path:
            messagebox.showwarning("Load File", "Load operation canceled.")
            return

        with open(file_path, "r") as f:
            self.key_counts = json.load(f)
        if not self.run:
            self.update_table()
        messagebox.showinfo("Load State", f"State loaded from {file_path}.")

    def update_table(self) -> None:
        """
        Update the table with the current key counts, sorted by the count in descending order.

        :return: None
        """

        # Clear the existing table rows
        for row in self.table.get_children():
            self.table.delete(row)

        # Sort key_counts by count in descending order
        sorted_counts = sorted(self.key_counts.items(), key=lambda x: x[1], reverse=True)

        # Insert the sorted data into the table
        for key, count in sorted_counts:
            self.table.insert("", "end", values=(key, count))

        if self.run:
            self.root.after(1000, self.update_table)

    def on_press(self, key: keyboard.Key) -> None:
        """
        Callback function to handle key press events.

        :param key: The key that was pressed.
        :return: None
        """

        try:
            key_name = key.char if key.char else str(key)
        except AttributeError:
            key_name = str(key)  # Handle special keys
        self.key_counts[key_name] = self.key_counts.get(key_name, 0) + 1

    def start_keylogger(self) -> None:
        """
        Start the keylogger in a separate thread.

        :return: None
        """

        if self.run:
            messagebox.showinfo(self.title, "Keylogger is already running.")
            return

        def run_listener():
            self.run = True
            # Store a reference to the listener
            self.listener = keyboard.Listener(on_press=self.on_press)
            with self.listener:
                self.listener.join()
            self.run = False

        # Start the listener in a separate thread
        threading.Thread(target=run_listener, daemon=True).start()
        self.update_table()
        self.status_label.config(text=f"Running", bg="green")
        messagebox.showinfo(self.title, "Keylogger started.")

    def stop_keylogger(self) -> None:
        """
        Stop the keylogger.

        :return: None
        """

        if self.run:
            self.run = False
            if self.listener:  # Stop the listener explicitly
                self.listener.stop()
            self.status_label.config(text=f"Stopped", bg="red")
            messagebox.showinfo(self.title, "Keylogger stopped.")
        else:
            messagebox.showinfo(self.title, "Keylogger is not running.")

    def reset_keylogger(self) -> None:
        """
        Reset the keylogger state.

        :return: None
        """

        confirm = messagebox.askyesno(
            "Confirm Reset", "Are you sure you want to reset the keylogger? This will clear all logged keys."
        )
        if confirm:
            self.key_counts.clear()
            self.update_table()
            messagebox.showinfo("Keylogger Reset", "The keylogger has been reset.")

    def about(self) -> None:
        """
        Display information about the keylogger.

        :return: None
        """

        messagebox.showinfo("About", self.title)

    def create_gui(self) -> None:
        """
        Create the GUI for the keylogger.

        :return: None
        """

        self.root = tk.Tk()
        self.root.title(self.title)

        # Create the menu bar
        menu_bar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Start Keylogger", command=self.start_keylogger)
        file_menu.add_command(label=f"Stop Keylogger", command=self.stop_keylogger)
        file_menu.add_command(label=f"Reset Keylogger", command=self.reset_keylogger)
        file_menu.add_separator()
        file_menu.add_command(label=f"Save State", command=self.save_state)
        file_menu.add_command(label=f"Load State", command=self.load_state)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=lambda: self.root.destroy())
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Attach the menu bar to the window
        self.root.config(menu=menu_bar)

        # Table for key counts
        table_frame = tk.Frame(self.root)
        table_frame.pack(pady=10)

        self.table = ttk.Treeview(table_frame, columns=("Key", "Count"), show="headings")
        self.table.heading("Key", text="Key")
        self.table.heading("Count", text="Count")
        self.table.pack()

        # Status Bubble
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10, fill="x", side="bottom")

        self.status_label = tk.Label(
            status_frame,
            text="Stopped",
            bg="red",
            fg="white",
            font=("Arial", 12),
            width=10,
            relief="ridge",
            anchor="center",
        )
        self.status_label.pack(side="right", padx=10, pady=10)

        # Run the main loop
        self.root.mainloop()

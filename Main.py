import threading
import tkinter as tk

import keyboard  # Import the keyboard library
import win32gui


def get_app_window(title):
    def enum_windows(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            if title.lower() in win32gui.GetWindowText(hwnd).lower():
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(enum_windows, hwnds)
    return hwnds[0] if hwnds else None


def update_overlay_position():
    while not exit_event.is_set():
        app_hwnd = get_app_window('SolidWorks')
        if app_hwnd:
            rect = win32gui.GetWindowRect(app_hwnd)
            overlay.geometry(f'{rect[2] - rect[0]}x{rect[3] - rect[1]}+{rect[0]}+{rect[1]}')
            update_rectangle()
        exit_event.wait(1)


def exit_app():
    exit_event.set()
    overlay.destroy()


def toggle_overlay_visibility():
    global overlay_visible
    overlay_visible = not overlay_visible
    overlay.attributes('-alpha', 1.0 if overlay_visible else 0.0)


def update_rectangle():
    width = overlay.winfo_width()
    height = overlay.winfo_height()
    border_size = 230  # Adjust the border size as needed
    canvas.coords(rectangle, border_size, border_size, width - border_size, height - border_size)


# Setup global hotkeys using the keyboard library
def setup_global_hotkeys():
    keyboard.add_hotkey('ctrl+shift+e', exit_app)
    keyboard.add_hotkey('ctrl+shift+h', toggle_overlay_visibility)


overlay = tk.Tk()
overlay.attributes('-transparentcolor', 'black')
overlay.attributes('-topmost', True)
overlay.overrideredirect(True)

canvas = tk.Canvas(overlay, bg='white', highlightthickness=0)
canvas.pack(fill='both', expand=True)

# Initial rectangle, will be resized in update_rectangle
rectangle = canvas.create_rectangle(50, 50, 100, 100, fill='black', outline='white')

overlay_visible = True  # Initial state of the overlay visibility

exit_event = threading.Event()
thread = threading.Thread(target=update_overlay_position, daemon=True)
thread.start()

# Call the function to setup global hotkeys
setup_global_hotkeys()

overlay.mainloop()

# Cleanup: remove hotkeys when the application is closed
keyboard.unhook_all_hotkeys()

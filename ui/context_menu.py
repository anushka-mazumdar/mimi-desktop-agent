import tkinter as tk
from tkinter import Menu
from typing import Optional, Callable

class MimiContextMenu:
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.menu = Menu(parent, tearoff=0)
        self._keyboard_callback: Optional[Callable] = None
        self._voice_callback: Optional[Callable] = None
        self._settings_callback: Optional[Callable] = None
        self._exit_callback: Optional[Callable] = None

        self._build_menu()

    def _build_menu(self) -> None:
        self.menu.add_command(
            label="Keyboard",
            command=self._on_keyboard
        )
        self.menu.add_command(
            label="Voice",
            command=self._on_voice
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="Settings",
            command=self._on_settings
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="Exit",
            command=self._on_exit
        )

    def _on_keyboard(self) -> None:
        if self._keyboard_callback:
            self._keyboard_callback()

    def _on_voice(self) -> None:
        if self._voice_callback:
            self._voice_callback()

    def _on_settings(self) -> None:
        if self._settings_callback:
            self._settings_callback()

    def _on_exit(self) -> None:
        if self._exit_callback:
            self._exit_callback()

    def show(self, x: int, y: int) -> None:
        try:
            self.menu.tk_popup(x, y)
        finally:
            self.menu.grab_release()

    def set_keyboard_callback(self, callback: Callable) -> None:
        self._keyboard_callback = callback

    def set_voice_callback(self, callback: Callable) -> None:
        self._voice_callback = callback

    def set_settings_callback(self, callback: Callable) -> None:
        self._settings_callback = callback

    def set_exit_callback(self, callback: Callable) -> None:
        self._exit_callback = callback


if __name__ == "__main__":
    def on_keyboard():
        print("Keyboard selected")

    def on_voice():
        print("Voice selected")

    def on_settings():
        print("Settings selected")

    def on_exit():
        print("Exit selected")
        root.quit()

    root = tk.Tk()
    root.title("Context Menu Test")
    root.geometry("400x300")

    def on_right_click(event):
        menu.show(event.x_root, event.y_root)

    menu = MimiContextMenu(root)
    menu.set_keyboard_callback(on_keyboard)
    menu.set_voice_callback(on_voice)
    menu.set_settings_callback(on_settings)
    menu.set_exit_callback(on_exit)

    root.bind("<Button-3>", on_right_click)

    label = tk.Label(
        root,
        text="Right-click anywhere to test the menu",
        font=("Arial", 14)
    )
    label.pack(expand=True)

    root.mainloop()
import sys
import traceback
from typing import Optional
import customtkinter as ctk
from ui.mimi_pet import MimiPet

def setup_root_window() -> ctk.CTk:
    root = ctk.CTk()
    root.title("Mimi Desktop Agent")
    root.geometry("1x1")
    root.withdraw()
    return root

def launch_mimi() -> Optional[MimiPet]:
    try:
        print("Mimi Desktop Agent Starting...")
        root = setup_root_window()
        pet = MimiPet(root)
        pet.run()

        def on_closing():
            print("Mimi Desktop Agent Closed")
            root.quit()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        return pet

    except KeyboardInterrupt:
        print("\nMimi Desktop Agent Closed")
        sys.exit(0)

    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        print("Mimi Desktop Agent Closed")
        sys.exit(1)

if __name__ == "__main__":
    launch_mimi()
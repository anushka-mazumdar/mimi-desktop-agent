import sys
import traceback
from typing import Optional
import customtkinter as ctk
from ui.mimi_pet import MimiPet
from agent.mimi import MimiAgent
from llm.schemas import AgentResponse
from ui.widget_state import WidgetState

def setup_root_window() -> ctk.CTk:
    root = ctk.CTk()
    root.title("Mimi Desktop Agent")
    root.geometry("1x1")
    root.withdraw()
    return root

def print_agent_result(command: str, response: AgentResponse, execution_success: bool) -> None:
    print("\n" + "=" * 60)
    print(f"Command Received: {command}")
    print(f"Intent: {response.intent}")
    print(f"Target: {response.target}")
    print(f"Action: {response.action}")
    if response.url:
        print(f"URL: {response.url}")
    print(f"Confidence: {response.confidence}")
    print(f"Execution Success: {execution_success}")
    print("=" * 60 + "\n")

def launch_mimi() -> Optional[MimiPet]:
    try:
        print("Mimi Desktop Agent Starting...")
        
        root = setup_root_window()
        
        pet = MimiPet(root)
        agent = MimiAgent()
        pet.run()

        def handle_task_submission(task: str) -> None:
            print(f"\nCommand Received: {task}")
            
            pet.state_manager.set_state(WidgetState.THINKING)
            
            try:
                result = agent.process_command(task)
                response = result["response"]
                execution_success = result["execution_success"]
                
                print_agent_result(task, response, execution_success)
                
                if execution_success:
                    pet.state_manager.set_state(WidgetState.SUCCESS)
                else:
                    pet.state_manager.set_state(WidgetState.ERROR)
                    
            except Exception as e:
                print(f"Error processing command: {e}")
                pet.state_manager.set_state(WidgetState.ERROR)
            
            root.after(1000, lambda: pet.state_manager.set_state(WidgetState.IDLE))

        pet.command_bar.on_submit(handle_task_submission)

        def on_closing():
            print("\nMimi Desktop Agent Closed")
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
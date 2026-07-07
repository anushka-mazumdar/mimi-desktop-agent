import sys
import traceback
from typing import Optional, Dict, Any
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
    print(f"Application: {response.application}")
    print(f"Intent: {response.intent}")
    print(f"Target: {response.target}")
    print(f"Action: {response.action}")
    if response.parameters:
        print(f"Parameters: {response.parameters}")
    if response.url:
        print(f"URL: {response.url}")
    print(f"Confidence: {response.confidence}")
    print(f"Execution Success: {execution_success}")
    print("=" * 60 + "\n")

def launch_mimi() -> Optional[MimiPet]:
    try:
        print("Mimi Desktop Agent Starting...")
        print("Session Started")
        
        root = setup_root_window()
        
        pet = MimiPet(root)
        agent = MimiAgent()
        pet.run()

        clarification_state: Dict[str, Any] = {
            "active": False,
            "original_command": "",
            "question": "",
            "options": []
        }

        def process_command(task: str) -> None:
            print(f"\nCommand Received: {task}")
            
            pet.state_manager.set_state(WidgetState.THINKING)
            
            try:
                result = agent.process_command(task)
                response = result["response"]
                execution_success = result["execution_success"]
                
                if response.parameters.get("clarification_required", False):
                    print("Clarification Requested")
                    clarification_state["active"] = True
                    clarification_state["original_command"] = task
                    clarification_state["question"] = response.parameters.get("question", "Which application should I use?")
                    clarification_state["options"] = response.parameters.get("options", [])
                    
                    pet.command_bar.input_field.delete(0, "end")
                    pet.command_bar.input_field.configure(
                        placeholder_text=clarification_state["question"]
                    )
                    pet.command_bar.focus_input()
                    pet.state_manager.set_state(WidgetState.INPUT_OPEN)
                    return
                
                print_agent_result(task, response, execution_success)
                
                if execution_success:
                    print("Execution Successful")
                    print("Context Updated")
                    pet.state_manager.set_state(WidgetState.SUCCESS)
                else:
                    print("Execution Failed")
                    pet.state_manager.set_state(WidgetState.ERROR)
                    
            except Exception as e:
                print(f"Error processing command: {e}")
                pet.state_manager.set_state(WidgetState.ERROR)
            
            root.after(1000, lambda: pet.state_manager.set_state(WidgetState.IDLE))

        def handle_task_submission(task: str) -> None:
            if clarification_state["active"]:
                print(f"Clarification Answer: {task}")
                
                original = clarification_state["original_command"]
                combined = f"{original} in {task}"
                print(f"Combined Command: {combined}")
                
                clarification_state["active"] = False
                clarification_state["original_command"] = ""
                clarification_state["question"] = ""
                clarification_state["options"] = []
                
                pet.command_bar.input_field.configure(
                    placeholder_text="Enter a task..."
                )
                
                pet.command_bar.hide_bar()
                process_command(combined)
                return
            
            process_command(task)

        def handle_clarification_cancel() -> None:
            if clarification_state["active"]:
                print("Clarification Cancelled")
                clarification_state["active"] = False
                clarification_state["original_command"] = ""
                clarification_state["question"] = ""
                clarification_state["options"] = []
                pet.command_bar.input_field.configure(
                    placeholder_text="Enter a task..."
                )
                pet.command_bar.hide_bar()
                pet.state_manager.set_state(WidgetState.IDLE)

        original_handle_escape = pet.command_bar._handle_escape
        
        def custom_handle_escape(event=None):
            if clarification_state["active"]:
                handle_clarification_cancel()
            else:
                original_handle_escape(event)
        
        pet.command_bar._handle_escape = custom_handle_escape
        pet.command_bar.bind("<Escape>", custom_handle_escape)

        pet.command_bar.on_submit(handle_task_submission)

        def on_closing():
            print("\nContext Cleared")
            agent.session_context.clear()
            print("Mimi Desktop Agent Closed")
            root.quit()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        return pet

    except KeyboardInterrupt:
        print("\nContext Cleared")
        print("Mimi Desktop Agent Closed")
        sys.exit(0)

    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        print("Mimi Desktop Agent Closed")
        sys.exit(1)

if __name__ == "__main__":
    launch_mimi()
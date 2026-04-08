import os
from dotenv import load_dotenv
import json
from openai import OpenAI
from app.config import DEFAULT_MODEL, MAX_STEPS
from app.tools import TOOLS_SCHEMA, TOOL_FUNCTIONS
from app.safety import execute_tool_safely

load_dotenv()

class WorkflowSafetyAgent:
    def __init__(self, model: str = DEFAULT_MODEL, use_safety: bool = False):
        self.model = model
        self.client = OpenAI()
        self.use_safety = use_safety

    def run(self, system_prompt: str, user_input: str, applicable_policies: list = []) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        for step in range(MAX_STEPS):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            # Append the message exactly as returned by the API to ensure standard message dict format
            # This handles tool_calls inclusion robustly.
            messages.append(message)
            
            if not message.tool_calls:
                return message.content
                
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    kwargs = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    kwargs = {}
                
                if self.use_safety:
                    output = execute_tool_safely(tool_name, kwargs, applicable_policies)
                else:
                    try:
                        output = TOOL_FUNCTIONS[tool_name](**kwargs)
                    except Exception as e:
                        output = f"Error executing tool: {e}"
                        
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": str(output)
                })
                
        return "Max steps reached without finalizing."

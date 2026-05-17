import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

class AgentTrace:
    def __init__(self, goal: str, steps_planned: List[str], user_id: str = "anonymous", user_message: str = ""):
        self.session_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
        self.user_id = user_id
        self.user_message = user_message
        self.goal = goal
        self.steps_planned = steps_planned
        self.steps_executed: List[Dict[str, Any]] = []
        self.total_time_ms = 0
        self.outcome = "PENDING"
        self.start_time = datetime.utcnow()
    
    def add_step(self, name: str, tool_called: str, input_data: Any, output_data: Any, status: str, time_ms: int, decision: Optional[str] = None):
        step = {
            "name": name,
            "tool_called": tool_called,
            "input": input_data,
            "output": output_data,
            "status": status,
            "time_ms": time_ms
        }
        if decision:
            step["decision"] = decision
            
        self.steps_executed.append(step)
        self.total_time_ms += time_ms
    
    def complete(self, outcome: str):
        self.outcome = outcome
        elapsed = (datetime.utcnow() - self.start_time).total_seconds() * 1000
        # optionally update total_time_ms with actual elapsed if desired

    def to_json(self) -> str:
        return json.dumps({
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "user_message": self.user_message,
            "workplan": {
                "goal": self.goal,
                "steps_planned": self.steps_planned
            },
            "steps_executed": self.steps_executed,
            "summary": {
                "total_steps": len(self.steps_executed),
                "total_time_ms": self.total_time_ms,
                "outcome": self.outcome
            }
        }, indent=2)

    def to_string(self) -> str:
        lines = [
            "=== KAROO AGENT TRACE ===",
            f"Timestamp: {self.timestamp}",
            f"Session ID: {self.session_id}",
            f"User ID: {self.user_id}",
            "",
            "--- WORKPLAN ---",
            f"Goal: {self.goal}",
            "Steps planned:"
        ]
        
        for i, step in enumerate(self.steps_planned, 1):
            lines.append(f"  {i}. {step}")
            
        lines.append("")
        lines.append("--- STEP EXECUTION ---")
        lines.append("")
        
        for i, step in enumerate(self.steps_executed, 1):
            lines.append(f"[STEP {i}] {step['name']}")
            lines.append(f"  Tool called: {step['tool_called']}")
            lines.append(f"  Input: {json.dumps(step['input'])[:200]}")
            if 'decision' in step:
                lines.append(f"  Decision: {step['decision']}")
            lines.append(f"  Output: {json.dumps(step['output'])[:200]}")
            lines.append(f"  Status: {step['status']}")
            lines.append(f"  Time: {step['time_ms']}ms")
            lines.append("")
            
        lines.append("--- SUMMARY ---")
        lines.append(f"Total steps: {len(self.steps_executed)}")
        lines.append(f"Total time: {self.total_time_ms}ms")
        tools = list(set([s['tool_called'] for s in self.steps_executed]))
        lines.append(f"Tools called: {', '.join(tools)}")
        lines.append(f"Outcome: {self.outcome}")
        lines.append("")
        lines.append("=== END TRACE ===")
        
        return "\n".join(lines)

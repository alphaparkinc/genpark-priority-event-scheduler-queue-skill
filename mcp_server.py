"""MCP Stdio Server for Priority Event Scheduler Queue.
100% Python Standard Library.
"""
import sys
import json
from client import PriorityEventSchedulerQueue

scheduler = PriorityEventSchedulerQueue()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-priority-event-scheduler-queue-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "schedule_task",
                "description": "Schedule a task with priority weighting and optional future execution delay",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "payload": {},
                        "priority": {"type": "integer", "default": 10},
                        "delay_seconds": {"type": "number", "default": 0.0}
                    },
                    "required": ["task_id", "payload"]
                }
            },
            {
                "name": "peek_next_task",
                "description": "Inspect the next highest-priority task in the scheduler without removing it",
                "inputSchema": {"type": "object"}
            },
            {
                "name": "pop_ready_tasks",
                "description": "Dequeue and return tasks whose scheduled time has arrived, ordered by priority",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "batch_size": {"type": "integer", "default": 5}
                    }
                }
            },
            {
                "name": "cancel_task",
                "description": "Cancel a pending scheduled task by its unique identifier",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"}
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "get_queue_metrics",
                "description": "Return counts of pending, ready, and delayed scheduled tasks",
                "inputSchema": {"type": "object"}
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "schedule_task":
            out = scheduler.schedule_task(
                args.get("task_id"),
                args.get("payload"),
                args.get("priority", 10),
                float(args.get("delay_seconds", 0.0))
            )
        elif name == "peek_next_task":
            out = scheduler.peek_next_task()
        elif name == "pop_ready_tasks":
            out = scheduler.pop_ready_tasks(args.get("batch_size", 5))
        elif name == "cancel_task":
            out = scheduler.cancel_task(args.get("task_id", ""))
        elif name == "get_queue_metrics":
            out = scheduler.get_queue_metrics()
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()

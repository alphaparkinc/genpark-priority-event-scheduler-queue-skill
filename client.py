"""Priority Event Scheduler Queue.
100% Python Standard Library.
"""
import time
from typing import Dict, Any, List, Optional

class PriorityEventSchedulerQueue:
    """Min-heap priority event scheduler and delayed task dispatcher."""
    def __init__(self):
        self.heap: List[List[Any]] = []
        self.seq = 0
        self.task_map: Dict[str, List[Any]] = {}

    def schedule_task(self, task_id: str, payload: Any, priority: int = 10, delay_seconds: float = 0.0) -> Dict[str, Any]:
        now = time.time()
        execute_at = now + max(0.0, delay_seconds)
        self.seq += 1

        entry = [execute_at, priority, self.seq, task_id, payload, "SCHEDULED"]
        self.task_map[task_id] = entry
        self._heappush(entry)

        return {
            "status": "scheduled",
            "task_id": task_id,
            "priority": priority,
            "execute_at": execute_at,
            "delay_seconds": delay_seconds
        }

    def _heappush(self, item: List[Any]):
        self.heap.append(item)
        self._siftdown(0, len(self.heap) - 1)

    def _heappop(self) -> Optional[List[Any]]:
        lastelt = self.heap.pop()
        if self.heap:
            returnitem = self.heap[0]
            self.heap[0] = lastelt
            self._siftup(0)
            return returnitem
        return lastelt

    def _siftdown(self, startpos, pos):
        newitem = self.heap[pos]
        while pos > startpos:
            parentpos = (pos - 1) >> 1
            parent = self.heap[parentpos]
            if (newitem[0], newitem[1], newitem[2]) < (parent[0], parent[1], parent[2]):
                self.heap[pos] = parent
                pos = parentpos
                continue
            break
        self.heap[pos] = newitem

    def _siftup(self, pos):
        endpos = len(self.heap)
        startpos = pos
        newitem = self.heap[pos]
        childpos = 2 * pos + 1
        while childpos < endpos:
            rightpos = childpos + 1
            if rightpos < endpos and not ((self.heap[childpos][0], self.heap[childpos][1], self.heap[childpos][2]) <
                                          (self.heap[rightpos][0], self.heap[rightpos][1], self.heap[rightpos][2])):
                childpos = rightpos
            self.heap[pos] = self.heap[childpos]
            pos = childpos
            childpos = 2 * pos + 1
        self.heap[pos] = newitem
        self._siftdown(startpos, pos)

    def peek_next_task(self) -> Optional[Dict[str, Any]]:
        while self.heap and self.heap[0][5] == "CANCELLED":
            self._heappop()
        if not self.heap:
            return None
        top = self.heap[0]
        return {
            "task_id": top[3],
            "execute_at": top[0],
            "priority": top[1],
            "payload": top[4],
            "ready_now": time.time() >= top[0]
        }

    def pop_ready_tasks(self, batch_size: int = 5) -> List[Dict[str, Any]]:
        ready = []
        now = time.time()
        while self.heap and len(ready) < batch_size:
            top = self.heap[0]
            if top[5] == "CANCELLED":
                self._heappop()
                continue
            if top[0] > now:
                break
            item = self._heappop()
            ready.append({
                "task_id": item[3],
                "payload": item[4],
                "priority": item[1],
                "scheduled_at": item[0],
                "executed_at": now
            })
            del self.task_map[item[3]]
        return ready

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        if task_id in self.task_map:
            entry = self.task_map[task_id]
            entry[5] = "CANCELLED"
            del self.task_map[task_id]
            return {"status": "cancelled", "task_id": task_id}
        return {"status": "not_found", "task_id": task_id}

    def get_queue_metrics(self) -> Dict[str, Any]:
        now = time.time()
        active = [h for h in self.heap if h[5] != "CANCELLED"]
        ready_count = sum(1 for h in active if h[0] <= now)
        delayed_count = len(active) - ready_count
        return {
            "total_pending_tasks": len(active),
            "ready_tasks": ready_count,
            "delayed_tasks": delayed_count
        }

"""Example usage for GenPark Priority Event Scheduler Queue."""
from client import PriorityEventSchedulerQueue

def main():
    queue = PriorityEventSchedulerQueue()
    print("Scheduling agent tasks with priority ratings...")
    queue.schedule_task("sync_db", {"action": "sync"}, priority=20, delay_seconds=0.0)
    queue.schedule_task("user_alert", {"action": "notify"}, priority=1, delay_seconds=0.0)
    queue.schedule_task("daily_cleanup", {"action": "clean"}, priority=50, delay_seconds=3600.0)

    print("Peeking next task...")
    top = queue.peek_next_task()
    print(f"Top task: {top['task_id']} (Priority: {top['priority']})")

    print("
Popping ready tasks...")
    ready = queue.pop_ready_tasks(batch_size=5)
    for t in ready:
        print(f" - Executing: {t['task_id']} with priority {t['priority']}")

    metrics = queue.get_queue_metrics()
    print("
Queue Metrics:", metrics)

if __name__ == "__main__":
    main()

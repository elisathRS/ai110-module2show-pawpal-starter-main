from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler, Status


def print_tasks(label: str, tasks: list[Task]):
    print(f"\n--- {label} ---")
    if not tasks:
        print("  (none)")
    for t in tasks:
        recur = f" [{t.recurrence}]" if t.recurrence else ""
        print(f"  [{t.due_date_time.strftime('%H:%M')}] {t.pet_name}: {t.description} ({t.status.value}){recur}")


# --- Create Owner ---
owner = Owner(name="Mary", phone_number="555-1234", email="mary@email.com")

# --- Create Pets ---
buddy = Pet(name="Buddy", type="Dog", age=3, gender="Male", weight=25.0, breed="Labrador")
luna  = Pet(name="Luna",  type="Cat", age=2, gender="Female", weight=4.5,  breed="Siamese")

# --- Add Tasks OUT OF ORDER (recurrence on some) ---
buddy.add_task(Task(description="Evening walk",    due_date_time=datetime(2026, 3, 23, 18, 0), pet_name="Buddy", recurrence="daily"))
buddy.add_task(Task(description="Morning walk",    due_date_time=datetime(2026, 3, 23,  7, 0), pet_name="Buddy", recurrence="daily"))
buddy.add_task(Task(description="Vet appointment", due_date_time=datetime(2026, 3, 23, 10, 0), pet_name="Buddy"))  # one-time

luna.add_task(Task(description="Evening feeding",  due_date_time=datetime(2026, 3, 23, 18, 0), pet_name="Luna",  recurrence="daily"))   # conflicts with Buddy's Evening walk
luna.add_task(Task(description="Medicine",         due_date_time=datetime(2026, 3, 23,  7, 30), pet_name="Luna", recurrence="weekly"))
luna.add_task(Task(description="Bath time",        due_date_time=datetime(2026, 3, 23, 10, 0), pet_name="Luna"))  # conflicts with Buddy's Vet appointment
luna.add_task(Task(description="Clean litter box", due_date_time=datetime(2026, 3, 23,  8, 0), pet_name="Luna"))

# --- Register Pets with Owner ---
owner.add_pet(buddy)
owner.add_pet(luna)

# --- Run Scheduler ---
scheduler = Scheduler(owner)

# 1. All tasks sorted by time
print("=" * 40)
print("     PAWPAL+ — SORTED BY TIME")
print("=" * 40)
print_tasks("All tasks sorted by time", scheduler.sort_by_time())

# 2. Filter by pet
print_tasks("Buddy's tasks only", scheduler.filter_by_pet("Buddy"))
print_tasks("Luna's tasks only",  scheduler.filter_by_pet("Luna"))

# 3. Filter by status
print_tasks("PENDING tasks",   scheduler.filter_by_status(Status.PENDING))
print_tasks("COMPLETED tasks", scheduler.filter_by_status(Status.COMPLETED))

# 4. Conflict detection
print("\n" + "=" * 40)
print("     CONFLICT DETECTION")
print("=" * 40)
conflicts = scheduler.find_conflicts()
if conflicts:
    for warning in conflicts:
        print(warning)
else:
    print("  No conflicts found.")

# 5. Demo recurring task completion
print("\n" + "=" * 40)
print("     RECURRING TASK DEMO")
print("=" * 40)

morning_walk = buddy.tasks[1]  # "Morning walk" — daily
print(f"\nCompleting: '{morning_walk.description}' due {morning_walk.due_date_time.strftime('%Y-%m-%d %H:%M')}")
next_task = scheduler.mark_task_complete(morning_walk.id)
if next_task:
    print(f"  → Auto-created next: '{next_task.description}' due {next_task.due_date_time.strftime('%Y-%m-%d %H:%M')} [{next_task.recurrence}]")

medicine = luna.tasks[1]  # "Medicine" — weekly
print(f"\nCompleting: '{medicine.description}' due {medicine.due_date_time.strftime('%Y-%m-%d %H:%M')}")
next_task = scheduler.mark_task_complete(medicine.id)
if next_task:
    print(f"  → Auto-created next: '{next_task.description}' due {next_task.due_date_time.strftime('%Y-%m-%d %H:%M')} [{next_task.recurrence}]")

vet = buddy.tasks[2]  # "Vet appointment" — no recurrence
print(f"\nCompleting: '{vet.description}' due {vet.due_date_time.strftime('%Y-%m-%d %H:%M')}")
next_task = scheduler.mark_task_complete(vet.id)
print(f"  → No next task created (one-time): {next_task}")

print_tasks("Buddy's tasks after completions", scheduler.filter_by_pet("Buddy"))
print_tasks("Luna's tasks after completions",  scheduler.filter_by_pet("Luna"))

# 5. Full daily plan (with conflict resolution)
print("\n" + "=" * 40)
print("     PAWPAL+ — DAILY PLAN")
print("=" * 40)
plan = scheduler.generate_daily_plan()
for i, task in enumerate(plan, start=1):
    time_str = task.due_date_time.strftime("%I:%M %p")
    print(f"{i}. [{time_str}] {task.pet_name} — {task.description}  ({task.status.value})")
print("=" * 40)

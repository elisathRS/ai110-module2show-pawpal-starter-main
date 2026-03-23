from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Create Owner ---
owner = Owner(name="Mary", phone_number="555-1234", email="mary@email.com")

# --- Create Pets ---
buddy = Pet(name="Buddy", type="Dog", age=3, gender="Male", weight=25.0, breed="Labrador")
luna  = Pet(name="Luna",  type="Cat", age=2, gender="Female", weight=4.5,  breed="Siamese")

# --- Add Tasks to Buddy ---
buddy.add_task(Task(
    description="Morning walk",
    due_date_time=datetime(2026, 3, 23, 7, 0),
    pet_name="Buddy"
))
buddy.add_task(Task(
    description="Feed breakfast",
    due_date_time=datetime(2026, 3, 23, 8, 0),
    pet_name="Buddy"
))

# --- Add Tasks to Luna ---
luna.add_task(Task(
    description="Clean litter box",
    due_date_time=datetime(2026, 3, 23, 8, 0),   # same time as Buddy's breakfast — conflict!
    pet_name="Luna"
))
luna.add_task(Task(
    description="Evening feeding",
    due_date_time=datetime(2026, 3, 23, 18, 0),
    pet_name="Luna"
))

# --- Register Pets with Owner ---
owner.add_pet(buddy)
owner.add_pet(luna)

# --- Run Scheduler ---
scheduler = Scheduler(owner)
plan = scheduler.generate_daily_plan()

# --- Print Today's Schedule ---
print("=" * 40)
print("       PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 40)

for i, task in enumerate(plan, start=1):
    time_str = task.due_date_time.strftime("%I:%M %p")
    print(f"{i}. [{time_str}] {task.pet_name} — {task.description}  ({task.status.value})")

print("=" * 40)

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4


class Status(Enum):
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    description: str
    due_date_time: datetime
    pet_name: str
    id: UUID = field(default_factory=uuid4)
    status: Status = Status.PENDING
    recurrence: str | None = None  # "daily", "weekly", or None

    def mark_complete(self):
        """Mark this task as completed."""
        self.status = Status.COMPLETED

    def generate_next(self) -> "Task | None":
        """Return a new Task for the next occurrence, or None if not recurring.

        Uses timedelta to advance due_date_time by 1 day (daily) or 7 days (weekly),
        preserving the original time-of-day.
        """
        if self.recurrence == "daily":
            next_due = self.due_date_time + timedelta(days=1)
        elif self.recurrence == "weekly":
            next_due = self.due_date_time + timedelta(weeks=1)
        else:
            return None
        return Task(
            description=self.description,
            due_date_time=next_due,
            pet_name=self.pet_name,
            recurrence=self.recurrence,
        )


@dataclass
class Pet:
    name: str
    type: str
    age: int
    gender: str
    weight: float
    breed: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def list_tasks(self) -> list[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def remove_task(self, task_id: UUID):
        """Remove a task from this pet's list by its unique ID."""
        self.tasks = [t for t in self.tasks if t.id != task_id]


@dataclass
class Owner:
    name: str
    phone_number: str
    email: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def list_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets

    def remove_pet(self, pet: Pet):
        """Remove a specific pet from this owner's pet list."""
        self.pets = [p for p in self.pets if p != pet]


class Scheduler:
    def __init__(self, owner: Owner):
        """Initialize the scheduler with an owner whose pets' tasks will be managed."""
        self.owner = owner

    def collect_tasks(self) -> list[Task]:
        """Gather all tasks from all pets belonging to the owner."""
        all_tasks = []
        for pet in self.owner.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def organize_tasks(self) -> list[Task]:
        """Sort all collected tasks by due date/time, pending tasks first."""
        all_tasks = self.collect_tasks()
        return sorted(
            all_tasks,
            key=lambda t: (t.status == Status.COMPLETED, t.due_date_time)
        )

    def sort_by_time(self) -> list[Task]:
        """Sort all tasks by their due_date_time using a lambda key."""
        all_tasks = self.collect_tasks()
        return sorted(all_tasks, key=lambda t: t.due_date_time)

    def filter_by_status(self, status: Status) -> list[Task]:
        """Return only tasks matching the given Status (PENDING or COMPLETED)."""
        return [t for t in self.collect_tasks() if t.status == status]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return only tasks assigned to the given pet name."""
        return [t for t in self.collect_tasks() if t.pet_name == pet_name]

    def find_conflicts(self) -> list[str]:
        """Return warning messages for any two tasks scheduled at the same time.

        Checks all pending tasks across all pets. Compares every pair once
        (O(n²) over the pending list, which is lightweight for small schedules).
        Returns a list of human-readable warning strings — never raises.
        """
        warnings: list[str] = []
        pending = [t for t in self.collect_tasks() if t.status == Status.PENDING]
        for i, a in enumerate(pending):
            for b in pending[i + 1:]:
                if a.due_date_time == b.due_date_time:
                    time_str = a.due_date_time.strftime("%I:%M %p")
                    warnings.append(
                        f"⚠ Conflict at {time_str}: '{a.pet_name} — {a.description}'"
                        f" overlaps with '{b.pet_name} — {b.description}'"
                    )
        return warnings

    def mark_task_complete(self, task_id: UUID) -> Task | None:
        """Mark a task complete by ID. If it recurs, auto-add the next occurrence.

        Returns the newly created next Task, or None if the task is not recurring.
        """
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.id == task_id:
                    task.mark_complete()
                    next_task = task.generate_next()
                    if next_task:
                        pet.add_task(next_task)
                    return next_task
        return None

    def resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
        """If two tasks share the same due time, shift the later one by 15 minutes."""
        resolved = []
        for task in tasks:
            while any(t.due_date_time == task.due_date_time for t in resolved):
                task.due_date_time += timedelta(minutes=15)
            resolved.append(task)
        return resolved

    def generate_daily_plan(self) -> list[Task]:
        """Produce the final ordered schedule after resolving conflicts."""
        organized = self.organize_tasks()
        final_plan = self.resolve_conflicts(organized)
        return final_plan

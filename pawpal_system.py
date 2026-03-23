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

    def mark_complete(self):
        """Mark this task as completed."""
        self.status = Status.COMPLETED


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

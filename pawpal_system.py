from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    description: str
    due_date_time: datetime
    status: str = "pending"

    def mark_complete(self):
        pass


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
        pass

    def list_tasks(self):
        pass

    def remove_task(self, task: Task):
        pass


class Owner:
    def __init__(self, name: str, phone_number: str, email: str):
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        pass

    def list_pets(self):
        pass

    def remove_pet(self, pet: Pet):
        pass


class Scheduler:
    def collect_tasks(self):
        pass

    def organize_tasks(self):
        pass

    def generate_daily_plan(self):
        pass

    def resolve_conflicts(self):
        pass

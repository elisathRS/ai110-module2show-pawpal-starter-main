import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from pawpal_system import Pet, Task, Status


def test_task_mark_complete():
    task = Task(description="Feed dog", due_date_time=datetime(2026, 3, 23, 8, 0), pet_name="Buddy")
    task.mark_complete()
    assert task.status == Status.COMPLETED


def test_pet_add_task_increases_count():
    pet = Pet(name="Buddy", type="Dog", age=3, gender="Male", weight=25.0, breed="Labrador")
    task = Task(description="Walk", due_date_time=datetime(2026, 3, 23, 7, 0), pet_name="Buddy")
    pet.add_task(task)
    assert len(pet.list_tasks()) == 1

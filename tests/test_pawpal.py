import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, Status


# --- Helpers ---

def make_owner_with_two_pets():
    owner = Owner(name="Mary", phone_number="555-0000", email="mary@test.com")
    buddy = Pet(name="Buddy", type="Dog", age=3, gender="Male", weight=25.0, breed="Labrador")
    luna  = Pet(name="Luna",  type="Cat", age=2, gender="Female", weight=4.5, breed="Siamese")
    owner.add_pet(buddy)
    owner.add_pet(luna)
    return owner, buddy, luna


# --- Task tests ---

def test_task_mark_complete():
    task = Task(description="Feed dog", due_date_time=datetime(2026, 3, 23, 8, 0), pet_name="Buddy")
    task.mark_complete()
    assert task.status == Status.COMPLETED


def test_task_generate_next_daily():
    task = Task(description="Walk", due_date_time=datetime(2026, 3, 23, 7, 0), pet_name="Buddy", recurrence="daily")
    next_task = task.generate_next()
    assert next_task is not None
    assert next_task.due_date_time == datetime(2026, 3, 24, 7, 0)
    assert next_task.recurrence == "daily"


def test_task_generate_next_weekly():
    task = Task(description="Medicine", due_date_time=datetime(2026, 3, 23, 9, 0), pet_name="Luna", recurrence="weekly")
    next_task = task.generate_next()
    assert next_task is not None
    assert next_task.due_date_time == datetime(2026, 3, 30, 9, 0)


def test_task_generate_next_none_for_one_time():
    task = Task(description="Vet", due_date_time=datetime(2026, 3, 23, 10, 0), pet_name="Buddy")
    assert task.generate_next() is None


# --- Pet tests ---

def test_pet_add_task_increases_count():
    pet = Pet(name="Buddy", type="Dog", age=3, gender="Male", weight=25.0, breed="Labrador")
    task = Task(description="Walk", due_date_time=datetime(2026, 3, 23, 7, 0), pet_name="Buddy")
    pet.add_task(task)
    assert len(pet.list_tasks()) == 1


def test_pet_remove_task():
    pet = Pet(name="Buddy", type="Dog", age=3, gender="Male", weight=25.0, breed="Labrador")
    task = Task(description="Walk", due_date_time=datetime(2026, 3, 23, 7, 0), pet_name="Buddy")
    pet.add_task(task)
    pet.remove_task(task.id)
    assert len(pet.list_tasks()) == 0


# --- Scheduler: sorting ---

def test_sort_by_time_returns_chronological_order():
    owner, buddy, luna = make_owner_with_two_pets()
    buddy.add_task(Task("Evening walk", datetime(2026, 3, 23, 18, 0), "Buddy"))
    buddy.add_task(Task("Morning walk", datetime(2026, 3, 23,  7, 0), "Buddy"))
    luna.add_task( Task("Feeding",      datetime(2026, 3, 23,  8, 0), "Luna"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()
    times = [t.due_date_time for t in sorted_tasks]
    assert times == sorted(times)


# --- Scheduler: filtering ---

def test_filter_by_pet_returns_only_that_pet():
    owner, buddy, luna = make_owner_with_two_pets()
    buddy.add_task(Task("Walk",    datetime(2026, 3, 23, 7, 0), "Buddy"))
    luna.add_task( Task("Feeding", datetime(2026, 3, 23, 8, 0), "Luna"))

    scheduler = Scheduler(owner)
    buddy_tasks = scheduler.filter_by_pet("Buddy")
    assert all(t.pet_name == "Buddy" for t in buddy_tasks)
    assert len(buddy_tasks) == 1


def test_filter_by_status_pending():
    owner, buddy, luna = make_owner_with_two_pets()
    t1 = Task("Walk",    datetime(2026, 3, 23, 7, 0), "Buddy")
    t2 = Task("Feeding", datetime(2026, 3, 23, 8, 0), "Luna")
    t1.mark_complete()
    buddy.add_task(t1)
    luna.add_task(t2)

    scheduler = Scheduler(owner)
    pending = scheduler.filter_by_status(Status.PENDING)
    assert all(t.status == Status.PENDING for t in pending)
    assert len(pending) == 1


# --- Scheduler: conflict detection ---

def test_find_conflicts_detects_same_time():
    owner, buddy, luna = make_owner_with_two_pets()
    buddy.add_task(Task("Vet",     datetime(2026, 3, 23, 10, 0), "Buddy"))
    luna.add_task( Task("Bath",    datetime(2026, 3, 23, 10, 0), "Luna"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.find_conflicts()
    assert len(conflicts) == 1
    assert "10:00 AM" in conflicts[0]


def test_find_conflicts_no_conflict():
    owner, buddy, luna = make_owner_with_two_pets()
    buddy.add_task(Task("Walk",    datetime(2026, 3, 23,  7, 0), "Buddy"))
    luna.add_task( Task("Feeding", datetime(2026, 3, 23,  8, 0), "Luna"))

    scheduler = Scheduler(owner)
    assert scheduler.find_conflicts() == []


# --- Scheduler: recurring task completion ---

def test_mark_task_complete_creates_next_for_daily():
    owner, buddy, _ = make_owner_with_two_pets()
    task = Task("Walk", datetime(2026, 3, 23, 7, 0), "Buddy", recurrence="daily")
    buddy.add_task(task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task.id)

    assert task.status == Status.COMPLETED
    assert next_task is not None
    assert next_task.due_date_time == datetime(2026, 3, 24, 7, 0)
    assert next_task in buddy.tasks


def test_mark_task_complete_no_next_for_one_time():
    owner, buddy, _ = make_owner_with_two_pets()
    task = Task("Vet", datetime(2026, 3, 23, 10, 0), "Buddy")
    buddy.add_task(task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task.id)

    assert task.status == Status.COMPLETED
    assert next_task is None

import streamlit as st
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler, Status

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Persist the Owner object across reruns — only create it once per session
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", phone_number="", email="")

owner = st.session_state.owner

st.title("🐾 PawPal+")

# --- Owner Setup ---
st.subheader("Owner Info")
with st.form("owner_form"):
    owner_name  = st.text_input("Name",         value=owner.name)
    owner_phone = st.text_input("Phone number", value=owner.phone_number)
    owner_email = st.text_input("Email",        value=owner.email)
    if st.form_submit_button("Save owner"):
        owner.name         = owner_name
        owner.phone_number = owner_phone
        owner.email        = owner_email
        st.success(f"Owner '{owner.name}' saved!")

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")

if "pet_form_key" not in st.session_state:
    st.session_state.pet_form_key = 0

with st.form(f"pet_form_{st.session_state.pet_form_key}"):
    col1, col2 = st.columns(2)
    with col1:
        pet_name   = st.text_input("Pet name")
        pet_type   = st.selectbox("Type", ["Dog", "Cat", "Other"])
        pet_age    = st.number_input("Age", min_value=0, max_value=30, value=1)
    with col2:
        pet_gender = st.selectbox("Gender", ["Male", "Female"])
        pet_weight = st.number_input("Weight (lbs)", min_value=0.1, value=10.0)
        pet_breed  = st.text_input("Breed")

    if st.form_submit_button("Add pet"):
        new_pet = Pet(
            name=pet_name, type=pet_type, age=int(pet_age),
            gender=pet_gender, weight=float(pet_weight), breed=pet_breed
        )
        owner.add_pet(new_pet)
        st.session_state.pet_form_key += 1
        st.success(f"{pet_name} added!")
        st.rerun()

if owner.list_pets():
    st.markdown("**Your pets:**")
    pet_data = []
    for pet in owner.list_pets():
        icon = "🐶" if pet.type == "Dog" else "🐱" if pet.type == "Cat" else "🐾"
        pet_data.append({
            "Pet":    f"{icon} {pet.name}",
            "Type":   pet.type,
            "Breed":  pet.breed,
            "Gender": pet.gender,
            "Age":    pet.age,
            "Weight": f"{pet.weight} lbs",
        })
    st.table(pet_data)
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a Task ---
st.subheader("Add a Task")

if not owner.list_pets():
    st.warning("Add a pet first before adding tasks.")
else:
    with st.form("task_form"):
        pet_options  = {p.name: p for p in owner.list_pets()}
        selected_pet = st.selectbox("Select pet", list(pet_options.keys()))
        task_desc    = st.text_input("Task description", value="Morning walk")
        task_date    = st.date_input("Date")
        task_time    = st.time_input("Time")
        recurrence   = st.selectbox("Recurrence", ["None", "daily", "weekly"])

        if st.form_submit_button("Add task"):
            due_dt   = datetime.combine(task_date, task_time)
            new_task = Task(
                description=task_desc,
                due_date_time=due_dt,
                pet_name=selected_pet,
                recurrence=None if recurrence == "None" else recurrence,
            )
            pet_options[selected_pet].add_task(new_task)
            st.success(f"Task '{task_desc}' added to {selected_pet}!")

st.divider()

# --- View & Filter Tasks ---
st.subheader("View Tasks")

all_tasks = []
for pet in owner.list_pets():
    all_tasks.extend(pet.list_tasks())

if not all_tasks:
    st.info("No tasks yet.")
else:
    scheduler = Scheduler(owner)

    col1, col2 = st.columns(2)
    with col1:
        pet_names    = ["All pets"] + [p.name for p in owner.list_pets()]
        filter_pet   = st.selectbox("Filter by pet", pet_names)
    with col2:
        filter_status = st.selectbox("Filter by status", ["pending", "completed", "All"])

    # Apply filters — default is pending only to avoid showing completed duplicates
    if filter_pet != "All pets" and filter_status != "All":
        tasks = [t for t in scheduler.filter_by_pet(filter_pet)
                 if t.status.value == filter_status]
    elif filter_pet != "All pets":
        tasks = [t for t in scheduler.filter_by_pet(filter_pet)
                 if t.status == Status.PENDING]
    elif filter_status != "All":
        status_enum = Status.PENDING if filter_status == "pending" else Status.COMPLETED
        tasks = scheduler.filter_by_status(status_enum)
    else:
        tasks = scheduler.sort_by_time()

    if not tasks:
        st.info("No tasks match this filter.")
    else:
        for t in tasks:
            recur_label = f" 🔁 {t.recurrence}" if t.recurrence else ""
            status_icon = "✅" if t.status == Status.COMPLETED else "🕐"
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.write(
                    f"{status_icon} **[{t.due_date_time.strftime('%b %d %I:%M %p')}]** "
                    f"{t.pet_name} — {t.description}{recur_label}"
                )
            with col_b:
                if t.status == Status.PENDING:
                    if st.button("Done", key=str(t.id)):
                        next_task = scheduler.mark_task_complete(t.id)
                        if next_task:
                            st.success(
                                f"Next '{next_task.description}' scheduled for "
                                f"{next_task.due_date_time.strftime('%b %d %I:%M %p')}"
                            )
                        st.rerun()

st.divider()

# --- Schedule & Conflict Detection ---
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    if not owner.list_pets() or not any(p.list_tasks() for p in owner.list_pets()):
        st.warning("Add at least one pet and one task first.")
    else:
        scheduler = Scheduler(owner)

        # Conflict warnings
        conflicts = scheduler.find_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(warning)

        # Final plan
        plan = scheduler.generate_daily_plan()
        st.success("Schedule generated!")
        for i, task in enumerate(plan, start=1):
            time_str    = task.due_date_time.strftime("%I:%M %p")
            recur_label = f" 🔁 {task.recurrence}" if task.recurrence else ""
            status_icon = "✅" if task.status == Status.COMPLETED else "🕐"
            st.write(
                f"{i}. {status_icon} [{time_str}] **{task.pet_name}** "
                f"— {task.description} `{task.status.value}`{recur_label}"
            )

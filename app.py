import streamlit as st
import pandas as pd
from datetime import datetime, date
import pytz
import random

# ======================== НАСТРОЙКИ СТРАНИЦЫ ========================
st.set_page_config(page_title="АДС CRM ERP", page_icon="🏗️", layout="wide")

# ======================== ДАННЫЕ И РОЛИ ========================
ROLES = {
    "admin": {"name": "Администратор", "icon": "👑", "access": ["dashboard", "employees", "shifts", "timesheet", "tasks", "messenger", "admin"]},
    "director": {"name": "Директор", "icon": "💼", "access": ["dashboard", "employees", "shifts", "timesheet", "tasks", "messenger"]},
    "foreman": {"name": "Прораб", "icon": "🏗️", "access": ["dashboard", "shifts", "timesheet", "tasks", "messenger"]},
    "master": {"name": "Мастер", "icon": "🔨", "access": ["dashboard", "shifts", "timesheet", "tasks", "messenger"]},
    "supply": {"name": "Снабженец", "icon": "📦", "access": ["dashboard", "tasks", "messenger"]}
}

# ======================== ИНИЦИАЛИЗАЦИЯ STATE ========================
def init_session_state():
    if "current_user" not in st.session_state:
        st.session_state.current_user = {"name": "Алексей Админов", "role": "admin"}
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "dashboard"

    if "employees" not in st.session_state:
        st.session_state.employees = [
            {"id": 1, "name": "Иван Петров", "position": "Прораб", "status": "present", "current_object": "ЖК Север", "avatar": "👷"},
            {"id": 2, "name": "Сергей Кузнецов", "position": "Электрик", "status": "present", "current_object": "ЖК Север", "avatar": "⚡"},
            {"id": 3, "name": "Дмитрий Васильев", "position": "Мастер", "status": "present", "current_object": "Лесной", "avatar": "🔨"},
            {"id": 4, "name": "Андрей Соколов", "position": "Разнорабочий", "status": "absent", "current_object": None, "avatar": "🪣"},
        ]

    if "objects" not in st.session_state:
        st.session_state.objects = [
            {"id": 1, "name": "ЖК Север", "foreman": "Иван Петров"},
            {"id": 2, "name": "Коттеджный посёлок Лесной", "foreman": "Иван Петров"},
            {"id": 3, "name": "ТЦ Молл Парк", "foreman": "Дмитрий Васильев"},
        ]

    if "site_attendance" not in st.session_state:
        st.session_state.site_attendance = []

    if "tasks" not in st.session_state:
        st.session_state.tasks = [
            {"id": 1, "title": "Залить фундамент", "assigned_to": "Иван Петров", "assigned_by": "Админ", "priority": "high", "status": "in_progress", "due_date": "2026-05-20"},
            {"id": 2, "title": "Проверить проводку", "assigned_to": "Сергей Кузнецов", "assigned_by": "Иван Петров", "priority": "medium", "status": "pending", "due_date": "2026-05-18"},
        ]

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"from": "Иван Петров", "text": "На объекте Север закончили заливку", "time": datetime.now().strftime("%H:%M")},
        ]

# ======================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ========================
def get_moscow_time():
    return datetime.now(pytz.timezone("Europe/Moscow")).strftime("%H:%M:%S")

def get_current_date():
    return date.today().strftime("%d.%m.%Y")

def add_employee(name, position):
    new_id = max([e["id"] for e in st.session_state.employees], default=0) + 1
    st.session_state.employees.append({
        "id": new_id,
        "name": name,
        "position": position,
        "status": "present",
        "current_object": None,
        "avatar": "👷"
    })

def add_task(title, assigned_to, due_date, priority):
    new_id = max([t["id"] for t in st.session_state.tasks], default=0) + 1
    st.session_state.tasks.append({
        "id": new_id,
        "title": title,
        "assigned_to": assigned_to,
        "assigned_by": st.session_state.current_user["name"],
        "priority": priority,
        "status": "pending",
        "due_date": str(due_date)
    })

def toggle_status(emp_id):
    for emp in st.session_state.employees:
        if emp["id"] == emp_id:
            emp["status"] = "absent" if emp["status"] == "present" else "present"
            break

# ======================== ВКЛАДКИ ========================
def render_dashboard():
    st.subheader("📊 Панель управления")

    col1, col2, col3, col4 = st.columns(4)
    present_count = len([e for e in st.session_state.employees if e["status"] == "present"])
    active_objects = len(set([e["current_object"] for e in st.session_state.employees if e["current_object"]]))
    pending_tasks = len([t for t in st.session_state.tasks if t["status"] != "done"])

    col1.metric("👷 На работе", present_count, f"из {len(st.session_state.employees)}")
    col2.metric("🏗️ Активных объектов", active_objects)
    col3.metric("📋 Активных задач", pending_tasks)
    col4.metric("👥 Сотрудников", len(st.session_state.employees))

def render_employees():
    st.subheader("👥 Сотрудники")

    with st.expander("➕ Добавить сотрудника"):
        name = st.text_input("ФИО")
        position = st.text_input("Должность")
        if st.button("Добавить сотрудника") and name:
            add_employee(name, position)
            st.rerun()

    for emp in st.session_state.employees:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        col1.write(f"{emp['avatar']} **{emp['name']}**")
        col2.write(emp['position'])
        col3.write("✅ На работе" if emp['status'] == 'present' else "❌ Отсутствует")
        if col4.button("Сменить статус", key=f"emp_{emp['id']}"):
            toggle_status(emp['id'])
            st.rerun()
        st.divider()

def render_shifts():
    st.subheader("🔨 Смены")
    object_names = [obj['name'] for obj in st.session_state.objects]
    selected_object = st.selectbox("Объект", object_names)

    available = [e for e in st.session_state.employees if e['status'] == 'present']
    if available:
        selected_emp = st.selectbox(
            "Сотрудник",
            available,
            format_func=lambda e: f"{e['name']} ({e['position']})"
        )
        if st.button("Отметить на объекте"):
            st.session_state.site_attendance.append({
                "id": random.randint(1000, 9999),
                "employee_id": selected_emp['id'],
                "employee_name": selected_emp['name'],
                "object_name": selected_object,
                "date": date.today().isoformat(),
                "check_in": datetime.now().strftime("%H:%M"),
                "check_out": None,
            })
            selected_emp['current_object'] = selected_object
            st.success("Сотрудник отмечен")
            st.rerun()

def render_timesheet():
    st.subheader("📊 Табель")
    data = []
    for emp in st.session_state.employees:
        visits = [a for a in st.session_state.site_attendance if a['employee_id'] == emp['id']]
        data.append({
            "Сотрудник": emp['name'],
            "Должность": emp['position'],
            "Объект": emp['current_object'] or "—",
            "Выходов": len(visits),
            "Статус": emp['status']
        })
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

def render_tasks():
    st.subheader("📋 Задачи")

    with st.expander("➕ Новая задача"):
        title = st.text_input("Название задачи")
        assigned_to = st.selectbox("Исполнитель", [e['name'] for e in st.session_state.employees])
        due = st.date_input("Срок")
        priority = st.selectbox("Приоритет", ["high", "medium", "low"])
        if st.button("Создать задачу") and title:
            add_task(title, assigned_to, due, priority)
            st.rerun()

    for task in st.session_state.tasks:
        st.write(f"**{task['title']}** | 👤 {task['assigned_to']} | 📅 {task['due_date']} | Статус: {task['status']}")

def render_messenger():
    st.subheader("💬 Чат")

    for msg in st.session_state.messages:
        st.markdown(f"**{msg['from']}** ({msg['time']}): {msg['text']}")

    new_msg = st.text_input("Введите сообщение")
    if st.button("Отправить") and new_msg:
        st.session_state.messages.append({
            "from": st.session_state.current_user['name'],
            "text": new_msg,
            "time": datetime.now().strftime("%H:%M")
        })
        st.rerun()

def render_admin():
    st.subheader("⚙️ Администрирование")
    new_role = st.selectbox(
        "Сменить роль",
        list(ROLES.keys()),
        format_func=lambda x: f"{ROLES[x]['icon']} {ROLES[x]['name']}"
    )
    if st.button("Применить роль"):
        st.session_state.current_user['role'] = new_role
        st.rerun()

# ======================== ОСНОВНОЙ ИНТЕРФЕЙС ========================
def main():
    init_session_state()

    with st.sidebar:
        st.title("🏗️ АДС CRM")
        st.caption("Управление строительством")
        st.divider()

        user_role = st.session_state.current_user['role']
        tabs = [
            ("dashboard", "📊 Панель"),
            ("employees", "👥 Сотрудники"),
            ("shifts", "🔨 Смены"),
            ("timesheet", "📊 Табель"),
            ("tasks", "📋 Задачи"),
            ("messenger", "💬 Чат"),
            ("admin", "⚙️ Админ"),
        ]

        for tab_id, label in tabs:
            if tab_id in ROLES[user_role]['access']:
                if st.button(label, use_container_width=True):
                    st.session_state.active_tab = tab_id
                    st.rerun()

        st.divider()
        st.write(f"👤 {st.session_state.current_user['name']}")
        st.write(f"{ROLES[user_role]['icon']} {ROLES[user_role]['name']}")

    page_titles = {
        "dashboard": "📊 Панель",
        "employees": "👥 Сотрудники",
        "shifts": "🔨 Смены",
        "timesheet": "📊 Табель",
        "tasks": "📋 Задачи",
        "messenger": "💬 Чат",
        "admin": "⚙️ Админ",
    }

    header_col1, header_col2 = st.columns([3, 1])
    header_col1.title(page_titles.get(st.session_state.active_tab, "АДС CRM"))
    header_col2.markdown(
        f"**📅 {get_current_date()}**  \\n**🕒 Москва: {get_moscow_time()}**"
    )

    active_tab = st.session_state.active_tab
    if active_tab == "dashboard":
        render_dashboard()
    elif active_tab == "employees":
        render_employees()
    elif active_tab == "shifts":
        render_shifts()
    elif active_tab == "timesheet":
        render_timesheet()
    elif active_tab == "tasks":
        render_tasks()
    elif active_tab == "messenger":
        render_messenger()
    elif active_tab == "admin":
        render_admin()

if __name__ == "__main__":
    main()

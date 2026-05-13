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
    
    # Сотрудники
    if "employees" not in st.session_state:
        st.session_state.employees = [
            {"id": 1, "name": "Иван Петров", "position": "Прораб", "status": "present", "current_object": "ЖК Север", "avatar": "👷"},
            {"id": 2, "name": "Сергей Кузнецов", "position": "Электрик", "status": "present", "current_object": "ЖК Север", "avatar": "⚡"},
            {"id": 3, "name": "Дмитрий Васильев", "position": "Мастер", "status": "present", "current_object": "Лесной", "avatar": "🔨"},
            {"id": 4, "name": "Андрей Соколов", "position": "Разнорабочий", "status": "absent", "current_object": None, "avatar": "🪣"},
        ]
    
    # Объекты
    if "objects" not in st.session_state:
        st.session_state.objects = [
            {"id": 1, "name": "ЖК Север", "foreman": "Иван Петров"},
            {"id": 2, "name": "Коттеджный посёлок Лесной", "foreman": "Иван Петров"},
            {"id": 3, "name": "ТЦ Молл Парк", "foreman": "Дмитрий Васильев"},
        ]
    
    # Отметки на объектах
    if "site_attendance" not in st.session_state:
        st.session_state.site_attendance = []
    
    # Задачи
    if "tasks" not in st.session_state:
        st.session_state.tasks = [
            {"id": 1, "title": "Залить фундамент", "assigned_to": "Иван Петров", "assigned_by": "Админ", "priority": "high", "status": "in_progress", "due_date": "2026-05-20"},
            {"id": 2, "title": "Проверить проводку", "assigned_to": "Сергей Кузнецов", "assigned_by": "Иван Петров", "priority": "medium", "status": "pending", "due_date": "2026-05-18"},
        ]
    
    # Чаты
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"from": "Иван Петров", "text": "На объекте Север закончили заливку", "time": datetime.now().strftime("%H:%M")},
        ]

# ======================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ========================
def get_moscow_time():
    return datetime.now(pytz.timezone("Europe/Moscow")).strftime("%H:%M:%S")

def get_ufa_time():
    return datetime.now(pytz.timezone("Asia/Yekaterinburg")).strftime("%H:%M:%S")

def get_current_date():
    return date.today().strftime("%d.%m.%Y")

def add_employee(name, position):
    new_id = max([e["id"] for e in st.session_state.employees], default=0) + 1
    st.session_state.employees.append({
        "id": new_id, "name": name, "position": position,
        "status": "present", "current_object": None, "avatar": "👷"
    })
    st.success(f"✅ Сотрудник {name} добавлен!")

def add_task(title, assigned_to, due_date, priority):
    new_id = max([t["id"] for t in st.session_state.tasks], default=0) + 1
    st.session_state.tasks.append({
        "id": new_id, "title": title, "description": "",
        "assigned_to": assigned_to, "assigned_by": st.session_state.current_user["name"],
        "priority": priority, "status": "pending", "due_date": str(due_date)
    })
    st.success(f"📋 Задача поставлена {assigned_to}!")

def toggle_status(emp_id):
    for emp in st.session_state.employees:
        if emp["id"] == emp_id:
            emp["status"] = "absent" if emp["status"] == "present" else "present"
            break
    st.rerun()

# ======================== ОСНОВНЫЕ ВКЛАДКИ ========================
def render_dashboard():
    st.subheader("📊 Панель управления")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        present_count = len([e for e in st.session_state.employees if e["status"] == "present"])
        st.metric("👷 На работе", present_count, f"из {len(st.session_state.employees)}")
    with col2:
        active_objects = len(set([e["current_object"] for e in st.session_state.employees if e["current_object"]]))
        st.metric("🏗️ Активных объектов", active_objects)
    with col3:
        pending_tasks = len([t for t in st.session_state.tasks if t["status"] != "done"])
        st.metric("📋 Активных задач", pending_tasks)
    with col4:
        st.metric("👥 Сотрудников", len(st.session_state.employees))
    
    st.divider()
    
    # Список сотрудников на объектах
    st.subheader("📍 Сотрудники на объектах")
    objects_with_employees = {}
    for emp in st.session_state.employees:
        if emp["current_object"] and emp["status"] == "present":
            obj = emp["current_object"]
            objects_with_employees[obj] = objects_with_employees.get(obj, 0) + 1
    
    if objects_with_employees:
        for obj, count in objects_with_employees.items():
            st.info(f"🏗️ **{obj}** — {count} чел.")
    else:
        st.info("Нет сотрудников на объектах")

def render_employees():
    st.subheader("👥 Сотрудники")
    
    with st.expander("➕ Добавить сотрудника"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("ФИО")
            new_position = st.text_input("Должность")
        if st.button("✅ Добавить"):
            if new_name:
                add_employee(new_name, new_position)
                st.rerun()
    
    # Таблица сотрудников
    for emp in st.session_state.employees:
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        with col1:
            st.write(f"{emp['avatar']} **{emp['name']}**")
        with col2:
            st.write(emp['position'])
        with col3:
            status_text = "✅ На работе" if emp['status'] == 'present' else "❌ Отсутствует"
            st.write(status_text)
        with col4:
            btn_text = "❌ Уволить" if emp['status'] == 'present' else "✅ Восстановить"
            if st.button(btn_text, key=f"btn_{emp['id']}"):
                toggle_status(emp['id'])
                st.rerun()
        st.divider()

def render_shifts():
    st.subheader("🔨 Отметка на объекте")
    
    # Выбор объекта
    user_name = st.session_state.current_user["name"]
    user_role = st.session_state.current_user["role"]
    
    if user_role in ["foreman", "master"]:
        accessible_objects = [obj["name"] for obj in st.session_state.objects if obj["foreman"] == user_name]
        if not accessible_objects:
            accessible_objects = [obj["name"] for obj in st.session_state.objects]
    else:
        accessible_objects = [obj["name"] for obj in st.session_state.objects]
    
    selected_object = st.selectbox("📍 Объект", accessible_objects)
    
    # Сотрудники на объекте
    st.markdown("---")
    st.subheader(f"👷 Сотрудники на {selected_object}")
    
    today = date.today().isoformat()
    today_attendance = [a for a in st.session_state.site_attendance if a["date"] == today and a["object_name"] == selected_object]
    
    # Показываем кто на объекте
    for att in today_attendance:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"👤 {att['employee_name']}")
        with col2:
            st.write(f"🕐 {att['check_in']}")
        with col3:
            if not att.get("check_out"):
                if st.button("🏠 Уйти", key=f"out_{att['id']}"):
                    att["check_out"] = datetime.now().strftime("%H:%M")
                    st.rerun()
            else:
                st.write(f"🚪 {att['check_out']}")
    
    # Добавление сотрудника
    st.markdown("---")
    st.subheader("➕ Отметить приход")
    
    available = [e for e in st.session_state.employees if e["status"] == "present"]
    if available:
        emp_names = [f"{e['name']} ({e['position']})" for e in available]
        selected_emp = st.selectbox("Сотрудник", emp_names)
        
        if st.button("🚀 Прибыл на объект"):
            emp = next(e for e in available if f"{e['name']} ({e['position']})" == selected_emp)
            new_id = random.randint(1000, 9999)
            st.session_state.site_attendance.append({
                "id": new_id,
                "employee_id": emp["id"],
                "employee_name": emp["name"],
                "object_name": selected_object,
                "date": today,
                "check_in": datetime.now().strftime("%H:%M"),
                "check_out": None,
                "marked_by": st.session_state.current_user["name"]
            })
            emp["current_object"] = selected_object
            st.success(f"✅ {emp['name']} отмечен на {selected_object}")
            st.rerun()
    else:
        st.warning("Нет доступных сотрудников")

def render_timesheet():
    st.subheader("📊 Табель учёта")
    
    data = []
    for emp in st.session_state.employees:
        emp_attendance = [a for a in st.session_state.site_attendance if a["employee_id"] == emp["id"]]
        data.append({
            "Сотрудник": emp["name"],
            "Должность": emp["position"],
            "Объект": emp["current_object"] or "—",
            "Выходов": len(emp_attendance),
            "Статус": "✅ Работает" if emp["status"] == "present" else "❌ Отсутствует"
        })
    
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

def render_tasks():
    st.subheader("📋 Задачи")
    
    with st.expander("➕ Новая задача"):
        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Название")
            task_assigned = st.selectbox("Кому", [e["name"] for e in st.session_state.employees])
        with col2:
            task_due = st.date_input("Срок")
            task_priority = st.selectbox("Приоритет", ["high", "medium", "low"])
        if st.button("✅ Поставить"):
            if task_title:
                add_task(task_title, task_assigned, task_due, task_priority)
                st.rerun()
    
    for task in st.session_state.tasks:
        with st.container():
            priority_emoji = "🔴" if task["priority"] == "high" else "🟠" if task["priority"] == "medium" else "🟢"
            status_emoji = {"pending": "⏳", "in_progress": "🔄", "done": "✅"}.get(task["status"], "⚪")
            
            st.markdown(f"""
            <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin-bottom:10px;">
                <b>{task['title']}</b> {priority_emoji}<br>
                👤 {task['assigned_to']} | 📅 {task['due_date']}<br>
                <span>{status_emoji} {task['status']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            new_status = st.selectbox("Статус", ["pending", "in_progress", "done"],
                                     index=["pending", "in_progress", "done"].index(task["status"]),
                                     key=f"task_{task['id']}", label_visibility="collapsed")
            if new_status != task["status"]:
                task["status"] = new_status
                st.rerun()

def render_messenger():
    st.subheader("💬 Чат")
    
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.messages:
            st.markdown(f"""
            <div style="background:#f0f0f0; border-radius:10px; padding:8px; margin-bottom:8px;">
                <b>{msg['from']}</b> <span style="color:gray; font-size:12px;">{msg['time']}</span><br>
                {msg['text']}
            </div>
            """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    with col1:
        new_msg = st.text_input("Сообщение", label_visibility="collapsed", placeholder="Напишите...")
    with col2:
        if st.button("📤 Отправить"):
            if new_msg:
                st.session_state.messages.append({
                    "from": st.session_state.current_user["name"],
                    "text": new_msg,
                    "time": datetime.now().strftime("%H:%M")
                })
                st.rerun()

def render_admin():
    st.subheader("⚙️ Администрирование")
    
    new_role = st.selectbox("Роль пользователя", list(ROLES.keys()),
                           format_func=lambda x: f"{ROLES[x]['icon']} {ROLES[x]['name']}")
    if st.button("Сменить роль"):
        st.session_state.current_user["role"] = new_role
        st.rerun()
    
    st.divider()
    
    if st.button("🗑️ Сбросить все данные", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ======================== ОСНОВНОЙ ИНТЕРФЕЙС ========================
def main():
    init_session_state()
    
    # САЙДБАР
    with st.sidebar:
        st.markdown("# 🏗️ АДС CRM")
        st.caption("Управление строительством")
        st.divider()
        
        user_role = st.session_state.current_user["role"]
        
        tabs = [
            {"id": "dashboard", "label": "📊 Панель", "roles": ["admin", "director", "foreman", "master", "supply"]},
            {"id": "employees", "label": "👥 Сотрудники", "roles": ["admin", "director"]},
            {"id": "shifts", "label": "🔨 Смены", "roles": ["admin", "director", "foreman", "master"]},
            {"id": "timesheet", "label": "📊 Табель", "roles": ["admin", "director", "foreman", "master"]},
            {"id": "tasks", "label": "📋 Задачи", "roles": ["admin", "director", "foreman", "master", "supply"]},
            {"id": "messenger", "label": "💬 Чат", "roles": ["admin", "director", "foreman", "master", "supply"]},
            {"id": "admin", "label": "⚙️ Админ", "roles": ["admin"]}
        ]
        
        for tab in tabs:
            if user_role in tab["roles"]:
                if st.button(tab["label"], key=tab["id"], use_container_width=True):
                    st.session_state.active_tab = tab["id"]
                    st.rerun()
        
        st.divider()
        st.caption(f"👤 {st.session_state.current_user['name']}")
        st.caption(f"🎭 {ROLES[user_role]['icon']} {ROLES[user_role]['name']}")
    
    # ОСНОВНАЯ ОБЛАСТЬ
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
        <h1 style="font-size:28px;">{{
            "dashboard": "📊 Панель",
            "employees": "👥 Сотрудники",
            "shifts": "🔨 Смены",
            "timesheet": "📊 Табель",
            "tasks": "📋 Задачи",
            "messenger": "💬 Чат",
            "admin": "⚙️ Админ"
        }}.get(st.session_state.active_tab, "CRM")}}</h1>
        <div style="background:white; padding:8px 16px; border-radius:12px;">
            📅 {get_current_date()} | 🕒 {get_moscow_time()}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Рендер выбранной вкладки
    tab = st.session_state.active_tab
    if tab == "dashboard":
        render_dashboard()
    elif tab == "employees":
        render_employees()
    elif tab == "shifts":
        render_shifts()
    elif tab == "timesheet":
        render_timesheet()
    elif tab == "tasks":
        render_tasks()
    elif tab == "messenger":
        render_messenger()
    elif tab == "admin":
        render_admin()

if __name__ == "__main__":
    main()

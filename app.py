import streamlit as st
import pandas as pd
from datetime import datetime, date
import pytz
import random

st.set_page_config(page_title="АДС CRM Enterprise", page_icon="🏗️", layout="wide")

# ================= CUSTOM CSS =================
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: white;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: none;
    padding: 0.75rem;
    font-weight: 600;
}
.metric-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    text-align: center;
}
.chat-box {
    background: white;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

USERS = {
    "admin": {"password": "admin123", "name": "Алексей Админов", "role": "admin"},
    "director": {"password": "director123", "name": "Директор АДС", "role": "director"},
    "foreman": {"password": "foreman123", "name": "Иван Петров", "role": "foreman"},
    "master": {"password": "master123", "name": "Дмитрий Васильев", "role": "master"},
    "supply": {"password": "supply123", "name": "Снабжение АДС", "role": "supply"}
}

ROLES = {
    "admin": {"name": "Администратор", "icon": "👑"},
    "director": {"name": "Директор", "icon": "💼"},
    "foreman": {"name": "Прораб", "icon": "🏗️"},
    "master": {"name": "Мастер", "icon": "🔨"},
    "supply": {"name": "Снабженец", "icon": "📦"}
}

def init_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "dashboard"
    if "employees" not in st.session_state:
        st.session_state.employees = [
            {"id": 1, "name": "Иван Петров", "position": "Прораб", "status": "На работе", "object": "ЖК Север"},
            {"id": 2, "name": "Сергей Кузнецов", "position": "Электрик", "status": "На работе", "object": "ЖК Север"},
            {"id": 3, "name": "Дмитрий Васильев", "position": "Мастер", "status": "Выходной", "object": "—"},
        ]
    if "tasks" not in st.session_state:
        st.session_state.tasks = [
            {"title": "Фундамент", "assigned": "Иван Петров", "priority": "Высокий", "deadline": "2026-05-20", "status": "В работе"}
        ]
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"from": "Директор", "text": "Проверить объект Север", "time": "09:00"}
        ]

def moscow_time():
    return datetime.now(pytz.timezone("Europe/Moscow")).strftime("%H:%M:%S")

def ufa_time():
    return datetime.now(pytz.timezone("Asia/Yekaterinburg")).strftime("%H:%M:%S")

def dashboard():
    st.subheader("📊 Центральная панель")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👷 Сотрудники", len(st.session_state.employees))
    col2.metric("🏗️ Объекты", len(set([e['object'] for e in st.session_state.employees if e['object'] != '—'])))
    col3.metric("📋 Задачи", len(st.session_state.tasks))
    col4.metric("💬 Сообщения", len(st.session_state.messages))

    st.markdown("### 📍 Персонал по объектам")
    df = pd.DataFrame(st.session_state.employees)
    st.dataframe(df, use_container_width=True, hide_index=True)

def employees_page():
    st.subheader("👥 Управление сотрудниками")
    with st.expander("➕ Добавить сотрудника"):
        name = st.text_input("ФИО")
        position = st.text_input("Должность")
        if st.button("Добавить") and name:
            st.session_state.employees.append({
                "id": random.randint(100,999),
                "name": name,
                "position": position,
                "status": "На работе",
                "object": "—"
            })
            st.success("Сотрудник добавлен")
            st.rerun()
    st.dataframe(pd.DataFrame(st.session_state.employees), use_container_width=True, hide_index=True)

def tasks_page():
    st.subheader("📋 Управление задачами")
    with st.expander("➕ Создать задачу"):
        title = st.text_input("Название задачи")
        assigned = st.selectbox("Исполнитель", [e['name'] for e in st.session_state.employees])
        deadline = st.date_input("Дедлайн")
        priority = st.selectbox("Приоритет", ["Высокий", "Средний", "Низкий"])
        if st.button("Создать") and title:
            st.session_state.tasks.append({
                "title": title,
                "assigned": assigned,
                "priority": priority,
                "deadline": str(deadline),
                "status": "Новая"
            })
            st.success("Задача создана")
            st.rerun()

    for task in st.session_state.tasks:
        st.markdown(f"""
        <div class='chat-box'>
        <b>{task['title']}</b><br>
        👤 {task['assigned']} | 📅 {task['deadline']}<br>
        🔥 {task['priority']} | 📌 {task['status']}
        </div>
        """, unsafe_allow_html=True)

def messenger_page():
    st.subheader("💬 Корпоративный мессенджер")
    for msg in st.session_state.messages:
        st.markdown(f"""
        <div class='chat-box'>
        <b>{msg['from']}</b> ({msg['time']})<br>{msg['text']}
        </div>
        """, unsafe_allow_html=True)

    new_msg = st.text_input("Введите сообщение")
    if st.button("Отправить") and new_msg:
        st.session_state.messages.append({
            "from": st.session_state.current_user['name'],
            "text": new_msg,
            "time": datetime.now().strftime('%H:%M')
        })
        st.rerun()

def admin_page():
    st.subheader("⚙️ Администрирование")

    st.markdown("### 👤 Редактирование профиля")
    new_name = st.text_input("Изменить имя пользователя", value=st.session_state.current_user['name'])
    if st.button("💾 Сохранить имя"):
        st.session_state.current_user['name'] = new_name
        username = st.session_state.current_user.get('username')
        if username in USERS:
            USERS[username]['name'] = new_name
        st.success("Имя обновлено")
        st.rerun()

    st.divider()

    role = st.selectbox("Сменить роль", list(ROLES.keys()), format_func=lambda x: f"{ROLES[x]['icon']} {ROLES[x]['name']}")
    if st.button("Применить"):
        st.session_state.current_user['role'] = role
        st.success("Роль обновлена")
        st.rerun()

def login_page():
    st.title("🔐 Вход в АДС CRM")
    st.subheader("Авторизация сотрудников")
    username = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти"):
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.authenticated = True
            st.session_state.current_user = {
                "name": user["name"],
                "role": user["role"],
                "username": username
            }
            st.success("Успешный вход")
            st.rerun()
        else:
            st.error("Неверный логин или пароль")

    st.info("Тестовые аккаунты: admin / admin123")
    st.caption("После входа имя пользователя можно изменить в разделе Администрирование")


def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()


def main():
    init_state()

    if not st.session_state.authenticated:
        login_page()
        return

    with st.sidebar:
        st.markdown("# 🏗️ АДС")
        st.caption("Enterprise CRM ERP")
        st.divider()

        menu = {
            "dashboard": "📊 Панель",
            "employees": "👥 Сотрудники",
            "tasks": "📋 Задачи",
            "messenger": "💬 Чат",
            "admin": "⚙️ Админ"
        }

        for key, label in menu.items():
            if st.button(label):
                st.session_state.active_tab = key
                st.rerun()

        st.divider()
        user = st.session_state.current_user
        st.markdown(f"**{user['name']}**")
        st.markdown(f"{ROLES[user['role']]['icon']} {ROLES[user['role']]['name']}")
        if st.button("🚪 Выйти"):
            logout()

    header1, header2 = st.columns([3, 1])
    header1.title("АДС CRM Enterprise")
    header2.markdown(f"**Москва:** {moscow_time()}  \\n**Уфа:** {ufa_time()}")

    tab = st.session_state.active_tab
    if tab == "dashboard":
        dashboard()
    elif tab == "employees":
        employees_page()
    elif tab == "tasks":
        tasks_page()
    elif tab == "messenger":
        messenger_page()
    elif tab == "admin":
        admin_page()

if __name__ == "__main__":
    main()


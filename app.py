import streamlit as st
from datetime import datetime
import pytz

# НАСТРОЙКИ СТРАНИЦЫ
st.set_page_config(page_title="АДС CRM", page_icon="🏗️", layout="wide")

# ЗАГОЛОВОК
st.title("🏗️ АДС CRM")

# ВРЕМЯ
col1, col2 = st.columns(2)
with col1:
    moscow_time = datetime.now(pytz.timezone("Europe/Moscow")).strftime("%H:%M:%S")
    st.metric("Москва", moscow_time)
with col2:
    ufa_time = datetime.now(pytz.timezone("Asia/Yekaterinburg")).strftime("%H:%M:%S")
    st.metric("Уфа", ufa_time)

st.divider()

# ==================== СОТРУДНИКИ ====================
st.header("👷 Сотрудники")

# Инициализация
if "employees" not in st.session_state:
    st.session_state.employees = [
        {"id": 1, "name": "Иван Петров", "position": "Прораб", "status": "На работе"},
        {"id": 2, "name": "Сергей Кузнецов", "position": "Электрик", "status": "На работе"},
        {"id": 3, "name": "Дмитрий Васильев", "position": "Мастер", "status": "Не на работе"},
    ]

# Добавление сотрудника
with st.expander("➕ Добавить сотрудника"):
    new_name = st.text_input("ФИО", key="new_name")
    new_position = st.text_input("Должность", key="new_position")
    if st.button("Добавить", key="add_emp"):
        if new_name:
            new_id = len(st.session_state.employees) + 1
            st.session_state.employees.append({
                "id": new_id,
                "name": new_name,
                "position": new_position if new_position else "Сотрудник",
                "status": "На работе"
            })
            st.success(f"✅ {new_name} добавлен!")
            st.rerun()

# Таблица сотрудников
for emp in st.session_state.employees:
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        st.write(f"**{emp['name']}**")
    with col2:
        st.write(emp['position'])
    with col3:
        st.write(emp['status'])
    with col4:
        if st.button("🔄", key=f"toggle_emp_{emp['id']}"):
            if emp['status'] == "На работе":
                emp['status'] = "Не на работе"
            else:
                emp['status'] = "На работе"
            st.rerun()

st.divider()

# ==================== ЗАДАЧИ ====================
st.header("📋 Задачи")

# Инициализация задач
if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"id": 1, "title": "Залить фундамент", "assigned_to": "Иван Петров", "status": "В процессе"},
        {"id": 2, "title": "Проверить проводку", "assigned_to": "Сергей Кузнецов", "status": "Ожидает"},
    ]

# Добавление задачи
with st.expander("➕ Добавить задачу"):
    task_title = st.text_input("Название задачи", key="task_title")
    task_assigned = st.selectbox("Исполнитель", [e["name"] for e in st.session_state.employees], key="task_assigned")
    if st.button("Добавить", key="add_task"):
        if task_title:
            new_id = len(st.session_state.tasks) + 1
            st.session_state.tasks.append({
                "id": new_id,
                "title": task_title,
                "assigned_to": task_assigned,
                "status": "Ожидает"
            })
            st.success(f"✅ Задача добавлена!")
            st.rerun()

# Список задач
status_options = ["Ожидает", "В процессе", "Выполнено"]

for task in st.session_state.tasks:
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    with col1:
        st.write(f"**{task['title']}**")
    with col2:
        st.write(task['assigned_to'])
    with col3:
        # Находим индекс текущего статуса
        current_index = 0
        if task['status'] in status_options:
            current_index = status_options.index(task['status'])
        else:
            current_index = 0
        
        new_status = st.selectbox(
            "Статус",
            status_options,
            index=current_index,
            key=f"status_{task['id']}",
            label_visibility="collapsed"
        )
        if new_status != task['status']:
            task['status'] = new_status
            st.rerun()
    with col4:
        if st.button("🗑️", key=f"del_task_{task['id']}"):
            st.session_state.tasks.remove(task)
            st.rerun()

st.divider()

# ==================== ЧАТ ====================
st.header("💬 Чат")

# Инициализация чата
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"id": 1, "user": "Система", "text": "Добро пожаловать в чат!", "time": datetime.now().strftime("%H:%M")}
    ]

# Отображение чата
chat_container = st.container(height=300)
with chat_container:
    for msg in st.session_state.messages:
        st.write(f"**{msg['user']}** ({msg['time']}): {msg['text']}")

# Отправка сообщения
col1, col2 = st.columns([4, 1])
with col1:
    new_message = st.text_input("Сообщение", key="chat_msg", label_visibility="collapsed", placeholder="Введите сообщение...")
with col2:
    if st.button("📤", key="send_msg"):
        if new_message:
            new_id = len(st.session_state.messages) + 1
            st.session_state.messages.append({
                "id": new_id,
                "user": "Пользователь",
                "text": new_message,
                "time": datetime.now().strftime("%H:%M")
            })
            st.rerun()

# ==================== БОКОВОЕ МЕНЮ ====================
with st.sidebar:
    st.markdown("# 🏗️ АДС CRM")
    st.markdown("---")
    
    # Выбор роли
    if "user_role" not in st.session_state:
        st.session_state.user_role = "director"
    
    roles = {
        "admin": "👑 Администратор",
        "director": "💼 Директор",
        "foreman": "🏗️ Прораб",
        "master": "🔨 Мастер",
        "supply": "📦 Снабженец"
    }
    
    selected_role = st.selectbox(
        "Роль пользователя",
        list(roles.keys()),
        format_func=lambda x: roles[x]
    )
    
    if selected_role != st.session_state.user_role:
        st.session_state.user_role = selected_role
        st.rerun()
    
    st.markdown(f"**Текущая роль:** {roles[st.session_state.user_role]}")
    
    st.markdown("---")
    
    # Статистика
    st.markdown("### 📊 Статистика")
    st.metric("👥 Сотрудников", len(st.session_state.employees))
    st.metric("📋 Активных задач", len([t for t in st.session_state.tasks if t['status'] != 'Выполнено']))
    
    st.markdown("---")
    st.caption("© АДС Групп 2026")

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

# РАЗДЕЛ 1: СОТРУДНИКИ
st.header("👷 Сотрудники")

# Инициализация списка сотрудников
if "employees" not in st.session_state:
    st.session_state.employees = [
        {"name": "Иван Петров", "position": "Прораб", "status": "На работе"},
        {"name": "Сергей Кузнецов", "position": "Электрик", "status": "На работе"},
    ]

# Форма добавления сотрудника
with st.expander("➕ Добавить сотрудника"):
    new_name = st.text_input("ФИО", key="new_name")
    new_position = st.text_input("Должность", key="new_position")
    if st.button("Добавить", key="add_employee_btn"):
        if new_name:
            st.session_state.employees.append({
                "name": new_name,
                "position": new_position,
                "status": "На работе"
            })
            st.success(f"Сотрудник {new_name} добавлен!")
            st.rerun()

# Таблица сотрудников
for idx, emp in enumerate(st.session_state.employees):
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        st.write(f"**{emp['name']}**")
    with col2:
        st.write(emp['position'])
    with col3:
        st.write(emp['status'])
    with col4:
        if st.button("🔄", key=f"toggle_{idx}"):
            if emp['status'] == "На работе":
                emp['status'] = "Не на работе"
            else:
                emp['status'] = "На работе"
            st.rerun()

# РАЗДЕЛ 2: ЗАДАЧИ
st.header("📋 Задачи")

# Инициализация задач
if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"title": "Залить фундамент", "assigned_to": "Иван Петров", "status": "В процессе"},
    ]

# Форма добавления задачи
with st.expander("➕ Добавить задачу"):
    task_title = st.text_input("Название задачи", key="task_title")
    task_assigned = st.selectbox("Исполнитель", [e["name"] for e in st.session_state.employees], key="task_assigned")
    if st.button("Добавить задачу", key="add_task_btn"):
        if task_title:
            st.session_state.tasks.append({
                "title": task_title,
                "assigned_to": task_assigned,
                "status": "Ожидает"
            })
            st.success(f"Задача добавлена!")
            st.rerun()

# Список задач
for idx, task in enumerate(st.session_state.tasks):
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    with col1:
        st.write(f"**{task['title']}**")
    with col2:
        st.write(task['assigned_to'])
    with col3:
        statuses = ["Ожидает", "В процессе", "Выполнено"]
        new_status = st.selectbox(
            "Статус",
            statuses,
            index=statuses.index(task['status']),
            key=f"task_status_{idx}",
            label_visibility="collapsed"
        )
        if new_status != task['status']:
            task['status'] = new_status
            st.rerun()
    with col4:
        if st.button("🗑️", key=f"delete_task_{idx}"):
            st.session_state.tasks.pop(idx)
            st.rerun()

# РАЗДЕЛ 3: ЧАТ
st.header("💬 Чат")

# Инициализация чата
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"user": "Система", "text": "Чат работает!", "time": datetime.now().strftime("%H:%M")}
    ]

# Отображение чата
chat_container = st.container(height=300)
with chat_container:
    for msg in st.session_state.messages:
        st.write(f"**{msg['user']}** ({msg['time']}): {msg['text']}")

# Отправка сообщения
col1, col2 = st.columns([4, 1])
with col1:
    new_message = st.text_input("Сообщение", key="chat_input", label_visibility="collapsed", placeholder="Введите сообщение...")
with col2:
    if st.button("📤", key="send_btn"):
        if new_message:
            st.session_state.messages.append({
                "user": "Пользователь",
                "text": new_message,
                "time": datetime.now().strftime("%H:%M")
            })
            st.rerun()

# Информация в сайдбаре
with st.sidebar:
    st.markdown("# 🏗️ АДС CRM")
    st.markdown("---")
    
    # Выбор роли
    if "user_role" not in st.session_state:
        st.session_state.user_role = "admin"
    
    role = st.selectbox("Роль пользователя", ["admin", "director", "foreman", "master", "supply"])
    if role != st.session_state.user_role:
        st.session_state.user_role = role
        st.rerun()
    
    st.markdown(f"**Текущая роль:** {role}")
    st.markdown("---")
    st.caption("© АДС Групп 2026")

# Автообновление времени
st.markdown("""
<script>
setInterval(() => {
    window.location.reload();
}, 60000);
</script>
""", unsafe_allow_html=True)

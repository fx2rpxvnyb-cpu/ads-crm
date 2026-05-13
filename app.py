import streamlit as st
import pandas as pd
from datetime import datetime, date
import pytz
import random
import base64
from io import BytesIO
from PIL import Image
import json
import os

# ======================== НАСТРОЙКИ СТРАНИЦЫ ========================
st.set_page_config(page_title="АДС CRM ERP", page_icon="🏗️", layout="wide")

# ======================== ДАННЫЕ И РОЛИ ========================
ROLES = {
    "admin": {"name": "Администратор", "icon": "👑", "access": ["dashboard", "employees", "shifts", "timesheet", "tools", "projects", "tasks", "photoreports", "messenger", "video", "admin"]},
    "director": {"name": "Директор", "icon": "💼", "access": ["dashboard", "employees", "shifts", "timesheet", "tools", "projects", "tasks", "photoreports", "messenger", "video"]},
    "foreman": {"name": "Прораб", "icon": "🏗️", "access": ["dashboard", "shifts", "timesheet", "projects", "tasks", "photoreports", "messenger"]},
    "master": {"name": "Мастер", "icon": "🔨", "access": ["dashboard", "shifts", "timesheet", "tasks", "photoreports", "messenger"]},
    "supply": {"name": "Снабженец", "icon": "📦", "access": ["dashboard", "tools", "tasks", "messenger"]}
}

# ======================== ИНИЦИАЛИЗАЦИЯ STATE ========================
def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = True
    if "current_user" not in st.session_state:
        st.session_state.current_user = {"name": "Алексей Админов", "role": "admin"}
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "dashboard"
    
    # ========== ФОТООТЧЁТЫ ==========
    if "photoreports" not in st.session_state:
        # Пример существующих отчётов
        st.session_state.photoreports = [
            {
                "id": 1,
                "object_name": "ЖК Север",
                "author": "Иван Петров",
                "author_role": "Прораб",
                "date": date.today().isoformat(),
                "time": datetime.now().strftime("%H:%M"),
                "title": "Заливка фундамента",
                "description": "Завершили заливку фундамента секции А. Бетон марки М300, залито 120 кубов.",
                "photos": [],
                "tasks_completed": ["Заливка фундамента", "Установка опалубки"],
                "materials_used": {"Цемент": "5т", "Арматура": "2т", "Песок": "10т"},
                "workers_present": 8,
                "status": "completed"
            },
            {
                "id": 2,
                "object_name": "Коттеджный посёлок Лесной",
                "author": "Дмитрий Васильев",
                "author_role": "Мастер",
                "date": date.today().isoformat(),
                "time": datetime.now().strftime("%H:%M"),
                "title": "Монтаж кровли",
                "description": "Начали монтаж металлочерепицы на доме №5. Работа идёт по графику.",
                "photos": [],
                "tasks_completed": ["Монтаж обрешётки"],
                "materials_used": {"Металлочерепица": "50м²", "Утеплитель": "30м²"},
                "workers_present": 4,
                "status": "in_progress"
            }
        ]
    
    # ========== СОТРУДНИКИ ==========
    if "employees" not in st.session_state:
        st.session_state.employees = [
            {"id": 1, "name": "Иван Петров", "position": "Прораб", "department": "Строительный", "phone": "+7 (912) 345-67-89", "status": "present", "current_object": "ЖК Север", "salary": 85000, "avatar": "👷", "shift": "Дневная", "hire_date": "2020-03-15"},
            {"id": 2, "name": "Сергей Кузнецов", "position": "Электрик", "department": "Технический", "phone": "+7 (912) 345-67-90", "status": "present", "current_object": "ЖК Север", "salary": 65000, "avatar": "⚡", "shift": "Дневная", "hire_date": "2021-06-20"},
            {"id": 3, "name": "Дмитрий Васильев", "position": "Мастер", "department": "Строительный", "phone": "+7 (912) 345-67-91", "status": "present", "current_object": "Коттеджный посёлок", "salary": 75000, "avatar": "🔨", "shift": "Дневная", "hire_date": "2019-11-10"},
            {"id": 4, "name": "Андрей Соколов", "position": "Разнорабочий", "department": "Строительный", "phone": "+7 (912) 345-67-92", "status": "absent", "current_object": None, "salary": 50000, "avatar": "🪣", "shift": "Дневная", "hire_date": "2022-01-15"},
        ]
    
    # ========== ОБЪЕКТЫ ==========
    if "objects" not in st.session_state:
        st.session_state.objects = [
            {"id": 1, "name": "ЖК Север", "address": "г. Москва, ул. Северная 15", "foreman": "Иван Петров"},
            {"id": 2, "name": "Коттеджный посёлок Лесной", "address": "МО, д. Лесная", "foreman": "Иван Петров"},
            {"id": 3, "name": "ТЦ Молл Парк", "address": "г. Уфа, пр. Октября 88", "foreman": "Дмитрий Васильев"},
        ]
    
    # ========== ОТМЕТКИ НА ОБЪЕКТАХ ==========
    if "site_attendance" not in st.session_state:
        st.session_state.site_attendance = []
        today = date.today().isoformat()
        for emp in st.session_state.employees:
            if emp["current_object"] and emp["status"] == "present":
                st.session_state.site_attendance.append({
                    "id": random.randint(1000, 9999),
                    "employee_id": emp["id"],
                    "employee_name": emp["name"],
                    "object_name": emp["current_object"],
                    "date": today,
                    "check_in": "08:00",
                    "check_out": None,
                    "marked_by": "Система"
                })
    
    # ========== ОСТАЛЬНЫЕ ДАННЫЕ ==========
    if "tools" not in st.session_state:
        st.session_state.tools = [
            {"id": 1, "name": "Перфоратор Makita", "serial": "MK-2470-001", "location": "Склад №1", "status": "available"},
            {"id": 2, "name": "Шуруповёрт Bosch", "serial": "BS-18V-042", "location": "ЖК Север", "status": "in_use"},
        ]
    
    if "tasks" not in st.session_state:
        st.session_state.tasks = [
            {"id": 1, "title": "Залить фундамент", "assigned_to": "Иван Петров", "assigned_by": "Алексей Админов", "priority": "high", "status": "in_progress", "due_date": "2026-05-20", "description": "Завершить заливку до пятницы"},
        ]
    
    if "projects" not in st.session_state:
        st.session_state.projects = [
            {"id": 1, "name": "ЖК Север", "location": "Москва", "budget": 125000000, "progress": 62, "manager": "Иван Петров"},
        ]
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"from": "Иван Петров", "role": "Прораб", "text": "На объекте Север закончили заливку", "time": datetime.now().strftime("%H:%M")},
            {"from": "Система", "role": "Бот", "text": "📸 Добавлена новая функция фотоотчётов! Теперь можно загружать фото с объектов", "time": datetime.now().strftime("%H:%M")},
        ]
    
    if "timesheet" not in st.session_state:
        st.session_state.timesheet = []

# ======================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ========================
def get_moscow_time():
    return datetime.now(pytz.timezone("Europe/Moscow")).strftime("%H:%M:%S")

def get_ufa_time():
    return datetime.now(pytz.timezone("Asia/Yekaterinburg")).strftime("%H:%M:%S")

def get_current_date():
    return date.today().strftime("%d.%m.%Y")

def add_photoreport(object_name, title, description, photos, tasks_completed, materials_used, workers_present, status):
    """Добавляет новый фотоотчёт"""
    new_id = max([r["id"] for r in st.session_state.photoreports], default=0) + 1
    
    # Сохраняем фото в base64 для хранения в сессии
    photos_data = []
    for photo in photos:
        if photo is not None:
            bytes_data = photo.getvalue()
            b64 = base64.b64encode(bytes_data).decode()
            photos_data.append({
                "data": b64,
                "name": photo.name,
                "type": photo.type
            })
    
    st.session_state.photoreports.append({
        "id": new_id,
        "object_name": object_name,
        "author": st.session_state.current_user["name"],
        "author_role": ROLES[st.session_state.current_user["role"]]["name"],
        "date": date.today().isoformat(),
        "time": datetime.now().strftime("%H:%M"),
        "title": title,
        "description": description,
        "photos": photos_data,
        "tasks_completed": tasks_completed.split(",") if tasks_completed else [],
        "materials_used": dict(zip(materials_used.split(","), ["1"] * len(materials_used.split(",")))) if materials_used else {},
        "workers_present": workers_present,
        "status": status
    })
    
    # Уведомление в чат
    st.session_state.messages.append({
        "from": "🤖 Фотоотчёт",
        "role": "Бот",
        "text": f"📸 **Новый фотоотчёт!**\n{st.session_state.current_user['name']} добавил отчёт по объекту **{object_name}**\n📝 {title}",
        "time": datetime.now().strftime("%H:%M")
    })
    
    st.success("✅ Фотоотчёт добавлен!")
    st.rerun()

def get_image_html(b64_data):
    """Генерирует HTML для отображения фото"""
    return f'<img src="data:image/jpeg;base64,{b64_data}" style="max-width:100%; border-radius:12px; margin:5px 0;">'

# ======================== РЕНДЕР ФОТООТЧЁТОВ ========================
def render_photoreports():
    st.subheader("📸 Фотоотчёты с объектов")
    
    # Вкладки: создание нового и просмотр существующих
    tab1, tab2 = st.tabs(["📷 Создать отчёт", "📂 Все отчёты"])
    
    with tab1:
        st.markdown("### ➕ Добавить фотоотчёт")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Выбор объекта
            object_names = [obj["name"] for obj in st.session_state.objects]
            selected_object = st.selectbox("📍 Объект", object_names, key="report_object")
            
            # Заголовок отчёта
            report_title = st.text_input("📝 Заголовок отчёта", placeholder="Например: Заливка фундамента, Монтаж кровли...")
            
            # Описание работ
            report_description = st.text_area("📄 Описание выполненных работ", height=100, 
                                             placeholder="Что сделано? Какие возникли сложности? Что запланировано на завтра?")
            
            # Список выполненных задач
            completed_tasks = st.text_input("✅ Выполненные задачи (через запятую)", 
                                           placeholder="Заливка фундамента, Установка опалубки")
        
        with col2:
            # Загрузка фотографий
            st.markdown("**📸 Фотографии**")
            st.caption("Можно загрузить несколько фото (сделайте фото прямо с телефона!)")
            uploaded_photos = st.file_uploader(
                "Выберите фото",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                key="photo_uploader"
            )
            
            if uploaded_photos:
                st.success(f"✅ Загружено {len(uploaded_photos)} фото")
                
                # Предпросмотр
                st.markdown("**Предпросмотр:**")
                preview_cols = st.columns(min(len(uploaded_photos), 3))
                for idx, photo in enumerate(uploaded_photos[:3]):
                    with preview_cols[idx % 3]:
                        try:
                            img = Image.open(photo)
                            st.image(img, caption=f"Фото {idx+1}", use_container_width=True)
                        except:
                            st.write(f"Фото {idx+1}")
            
            # Количество работников
            workers_present = st.number_input("👷 Количество работников", min_value=0, max_value=50, value=5)
            
            # Статус работ
            report_status = st.selectbox("📊 Статус работ", 
                                        ["completed", "in_progress", "planned"],
                                        format_func=lambda x: {"completed": "✅ Завершено", "in_progress": "🔄 В процессе", "planned": "📅 Запланировано"}[x])
            
            # Расход материалов
            materials = st.text_input("📦 Использованные материалы (через запятую)", 
                                     placeholder="Бетон, Арматура, Кирпич")
        
        # Кнопка отправки
        if st.button("📤 Опубликовать фотоотчёт", type="primary", use_container_width=True):
            if not report_title:
                st.error("Введите заголовок отчёта")
            elif not uploaded_photos:
                st.error("Добавьте хотя бы одно фото")
            else:
                add_photoreport(selected_object, report_title, report_description, 
                               uploaded_photos, completed_tasks, materials, workers_present, report_status)
    
    with tab2:
        st.markdown("### 📂 Архив фотоотчётов")
        
        # Фильтры
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_object = st.selectbox("Фильтр по объекту", ["Все"] + [obj["name"] for obj in st.session_state.objects])
        with col_f2:
            filter_author = st.selectbox("Фильтр по автору", ["Все"] + list(set([r["author"] for r in st.session_state.photoreports])))
        with col_f3:
            filter_date = st.date_input("Фильтр по дате", value=None, key="filter_date")
        
        # Применяем фильтры
        filtered_reports = st.session_state.photoreports.copy()
        
        if filter_object != "Все":
            filtered_reports = [r for r in filtered_reports if r["object_name"] == filter_object]
        if filter_author != "Все":
            filtered_reports = [r for r in filtered_reports if r["author"] == filter_author]
        if filter_date:
            filtered_reports = [r for r in filtered_reports if r["date"] == filter_date.isoformat()]
        
        # Отображаем отчёты
        if not filtered_reports:
            st.info("📭 Нет фотоотчётов по выбранным критериям")
        else:
            for report in sorted(filtered_reports, key=lambda x: x["date"] + x["time"], reverse=True):
                with st.expander(f"📸 {report['title']} — {report['object_name']} ({report['date']})"):
                    col_info, col_status = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"""
                        **👤 Автор:** {report['author']} ({report['author_role']})  
                        **🕐 Время:** {report['time']}  
                        **📝 Описание:** {report['description']}
                        """)
                        
                        if report.get("tasks_completed") and report["tasks_completed"]:
                            st.markdown(f"**✅ Выполненные задачи:** {', '.join(report['tasks_completed'])}")
                        
                        if report.get("materials_used") and report["materials_used"]:
                            st.markdown(f"**📦 Материалы:** {', '.join(report['materials_used'].keys())}")
                        
                        st.markdown(f"**👷 Работников на объекте:** {report['workers_present']}")
                    
                    with col_status:
                        status_emoji = {"completed": "✅ Завершено", "in_progress": "🔄 В процессе", "planned": "📅 Запланировано"}.get(report["status"], report["status"])
                        st.markdown(f"**Статус:** {status_emoji}")
                    
                    # Отображение фотографий
                    if report.get("photos") and report["photos"]:
                        st.markdown("**📷 Фотографии:**")
                        cols = st.columns(min(len(report["photos"]), 3))
                        for idx, photo_data in enumerate(report["photos"]):
                            with cols[idx % 3]:
                                try:
                                    st.image(f"data:image/jpeg;base64,{photo_data['data']}", use_container_width=True)
                                except:
                                    st.write(f"Фото {idx+1}")
                    else:
                        # Для демо-отчётов показываем заглушку
                        st.info("📷 Фотографии будут добавлены при загрузке")

def render_dashboard():
    st.subheader("📊 Панель управления")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👷 На объектах", len([e for e in st.session_state.employees if e["status"] == "present" and e["current_object"]]), 
                 f"из {len(st.session_state.employees)} сотрудников")
    with col2:
        active_objects = len(set([e["current_object"] for e in st.session_state.employees if e["current_object"]]))
        st.metric("🏗️ Активных объектов", active_objects)
    with col3:
        today_reports = len([r for r in st.session_state.photoreports if r["date"] == date.today().isoformat()])
        st.metric("📸 Фотоотчётов сегодня", today_reports)
    with col4:
        pending_tasks = len([t for t in st.session_state.tasks if t["status"] != "done"])
        st.metric("📋 Активных задач", pending_tasks)
    
    st.divider()
    
    # Последние фотоотчёты
    st.subheader("📸 Последние фотоотчёты")
    recent_reports = sorted(st.session_state.photoreports, key=lambda x: x["date"] + x["time"], reverse=True)[:3]
    
    if recent_reports:
        cols = st.columns(min(len(recent_reports), 3))
        for idx, report in enumerate(recent_reports):
            with cols[idx % 3]:
                st.markdown(f"""
                <div style="border:1px solid #e2e8f0; border-radius:12px; padding:12px; background:white;">
                    <strong>🏗️ {report['object_name']}</strong><br>
                    <small>{report['date']} {report['time']}</small><br>
                    <strong>{report['title']}</strong><br>
                    <span style="color:#64748b;">👤 {report['author']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Пока нет фотоотчётов. Добавьте первый отчёт!")

def render_employees_admin():
    st.subheader("👥 Управление персоналом")
    
    with st.expander("➕ Добавить сотрудника", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("ФИО", key="new_name")
            new_position = st.text_input("Должность", key="new_position")
            new_department = st.text_input("Отдел", key="new_department")
        with col2:
            new_phone = st.text_input("Телефон", key="new_phone")
            new_salary = st.number_input("Зарплата", min_value=30000, value=50000, key="new_salary")
            new_shift = st.selectbox("Смена", ["Дневная", "Ночная"], key="new_shift")
        if st.button("✅ Добавить сотрудника"):
            if new_name:
                st.session_state.employees.append({
                    "id": max([e["id"] for e in st.session_state.employees], default=0) + 1,
                    "name": new_name, "position": new_position, "department": new_department,
                    "phone": new_phone, "status": "present", "current_object": None,
                    "salary": new_salary, "avatar": "👷", "shift": new_shift, "hire_date": date.today().isoformat()
                })
                st.success(f"✅ Сотрудник {new_name} добавлен!")
                st.rerun()
    
    emp_data = []
    for emp in st.session_state.employees:
        status_display = "✅ На объекте" if emp["status"] == "present" and emp["current_object"] else "⭕ В офисе" if emp["status"] == "present" else "❌ Отсутствует"
        emp_data.append({
            "ID": emp["id"],
            "Сотрудник": f"{emp['avatar']} {emp['name']}",
            "Должность": emp["position"],
            "Отдел": emp["department"],
            "Объект": emp["current_object"] or "—",
            "Статус": status_display,
        })
    
    st.dataframe(pd.DataFrame(emp_data), use_container_width=True, hide_index=True)

def render_shifts():
    st.subheader("🔨 Отметка работников на объектах")
    
    user_role = st.session_state.current_user["role"]
    user_name = st.session_state.current_user["name"]
    
    if user_role == "foreman" or user_role == "master":
        accessible_objects = [obj["name"] for obj in st.session_state.objects if obj["foreman"] == user_name]
        if not accessible_objects:
            accessible_objects = [obj["name"] for obj in st.session_state.objects]
        st.info(f"👤 Вы отвечаете за объекты: {', '.join(accessible_objects)}")
    else:
        accessible_objects = [obj["name"] for obj in st.session_state.objects]
    
    selected_object = st.selectbox("📍 Выберите объект", accessible_objects)
    
    today = date.today().isoformat()
    today_attendance = [a for a in st.session_state.site_attendance if a["date"] == today and a["object_name"] == selected_object]
    
    st.markdown("---")
    st.subheader(f"📋 Сотрудники на объекте **{selected_object}**")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if today_attendance:
            for att in today_attendance:
                cols = st.columns([2, 1, 1])
                with cols[0]:
                    st.write(f"👷 **{att['employee_name']}**")
                with cols[1]:
                    st.write(f"🕐 Пришёл: {att['check_in']}")
                with cols[2]:
                    if not att["check_out"]:
                        if st.button(f"🏠 Уйти", key=f"out_{att['id']}"):
                            att["check_out"] = datetime.now().strftime("%H:%M")
                            st.rerun()
                    else:
                        st.write(f"🚪 Ушёл: {att['check_out']}")
        else:
            st.info("Сегодня ещё никто не отмечен на этом объекте")
    
    with col2:
        st.subheader("➕ Отметить приход")
        available_employees = [e for e in st.session_state.employees if not e["current_object"] or e["current_object"] == selected_object]
        if available_employees:
            selected_emp = st.selectbox("Сотрудник", [f"{e['avatar']} {e['name']}" for e in available_employees])
            if st.button("🚀 Отметить приход", use_container_width=True):
                emp = next((e for e in available_employees if f"{e['avatar']} {e['name']}" == selected_emp), None)
                if emp:
                    new_id = random.randint(1000, 9999)
                    st.session_state.site_attendance.append({
                        "id": new_id, "employee_id": emp["id"], "employee_name": emp["name"],
                        "object_name": selected_object, "date": today,
                        "check_in": datetime.now().strftime("%H:%M"), "check_out": None,
                        "marked_by": st.session_state.current_user["name"]
                    })
                    emp["status"] = "present"
                    emp["current_object"] = selected_object
                    st.success(f"✅ {emp['name']} отмечен на объекте {selected_object}")
                    st.rerun()
        else:
            st.warning("Нет доступных сотрудников")

def render_timesheet():
    st.subheader("📊 Табель учёта рабочего времени")
    
    timesheet_data = []
    for emp in st.session_state.employees:
        emp_attendance = [a for a in st.session_state.site_attendance if a["employee_id"] == emp["id"]]
        timesheet_data.append({
            "Сотрудник": f"{emp['avatar']} {emp['name']}",
            "Должность": emp["position"],
            "Объект": emp["current_object"] or "—",
            "Дней отработано": len(emp_attendance),
            "Статус": "✅ Активен" if emp["status"] == "present" else "❌ Отсутствует"
        })
    
    st.dataframe(pd.DataFrame(timesheet_data), use_container_width=True, hide_index=True)

def render_tools():
    st.subheader("🔧 Склад инструментов")
    
    with st.expander("➕ Добавить инструмент", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Название", key="tool_name")
            new_serial = st.text_input("Серийный номер", key="tool_serial")
        with col2:
            new_location = st.text_input("Местоположение", key="tool_location")
            new_status = st.selectbox("Статус", ["available", "in_use", "maintenance"])
        if st.button("✅ Добавить инструмент"):
            if new_name:
                st.session_state.tools.append({
                    "id": max([t["id"] for t in st.session_state.tools], default=0) + 1,
                    "name": new_name, "serial": new_serial, "location": new_location, "status": new_status
                })
                st.success(f"🔧 Инструмент {new_name} добавлен!")
                st.rerun()
    
    tool_data = []
    for tool in st.session_state.tools:
        status_icon = {"available": "📦", "in_use": "🔨", "maintenance": "🔧"}.get(tool["status"], "❓")
        tool_data.append({
            "Инструмент": tool["name"],
            "Серийный номер": tool["serial"],
            "Местоположение": tool["location"],
            "Статус": f"{status_icon} {tool['status']}"
        })
    
    st.dataframe(pd.DataFrame(tool_data), use_container_width=True, hide_index=True)

def render_tasks():
    st.subheader("📋 Задачи сотрудникам")
    
    with st.expander("➕ Поставить задачу", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Название задачи", key="task_title")
            task_desc = st.text_area("Описание", key="task_desc")
        with col2:
            task_assigned = st.selectbox("Исполнитель", [e["name"] for e in st.session_state.employees], key="task_assigned")
            task_due = st.date_input("Срок выполнения", key="task_due")
            task_priority = st.selectbox("Приоритет", ["high", "medium", "low"])
        if st.button("✅ Поставить задачу"):
            if task_title:
                st.session_state.tasks.append({
                    "id": max([t["id"] for t in st.session_state.tasks], default=0) + 1,
                    "title": task_title, "description": task_desc,
                    "assigned_to": task_assigned, "assigned_by": st.session_state.current_user["name"],
                    "priority": task_priority, "status": "pending", "due_date": str(task_due)
                })
                st.success(f"📋 Задача поставлена {task_assigned}!")
                st.rerun()
    
    for task in st.session_state.tasks:
        with st.container():
            priority_emoji = "🔴" if task["priority"] == "high" else "🟠" if task["priority"] == "medium" else "🟢"
            status_emoji = {"pending": "⏳", "in_progress": "🔄", "done": "✅"}.get(task["status"], "⚪")
            st.markdown(f"""
            <div style="border:1px solid #e2e8f0; border-radius:12px; padding:12px; margin-bottom:12px; background:white;">
                <div style="display:flex; justify-content:space-between;">
                    <span><strong>{task['title']}</strong> {priority_emoji}</span>
                    <span>{status_emoji} {task['status'].replace('_', ' ').title()}</span>
                </div>
                <p style="color:#475569;">{task['description']}</p>
                <p style="color:#64748b; font-size:12px;">👤 {task['assigned_to']} | 📅 {task['due_date']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            new_status = st.selectbox("Статус", ["pending", "in_progress", "done"], 
                                     index=["pending", "in_progress", "done"].index(task["status"]),
                                     key=f"status_{task['id']}", label_visibility="collapsed")
            if new_status != task["status"]:
                task["status"] = new_status
                st.rerun()

def render_projects():
    st.subheader("🏗️ Активные проекты")
    for proj in st.session_state.projects:
        st.markdown(f"""
        <div style="border:1px solid #e2e8f0; border-radius:12px; padding:16px; margin-bottom:12px;">
            <h4>{proj['name']}</h4>
            <p>📍 {proj['location']} | 👤 {proj['manager']}</p>
            <div style="background:#e2e8f0; border-radius:10px; height:10px;">
                <div style="background:#10b981; width:{proj['progress']}%; height:10px; border-radius:10px;"></div>
            </div>
            <p>Прогресс: {proj['progress']}% | Бюджет: {proj['budget']:,} ₽</p>
        </div>
        """, unsafe_allow_html=True)

def render_messenger():
    st.subheader("💬 Корпоративный чат")
    
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.messages:
            role_icon = {"Прораб": "🏗️", "Электрик": "⚡", "Мастер": "🔨", "Бот": "🤖", "Фотоотчёт": "📸"}.get(msg.get("role", ""), "👤")
            st.markdown(f"""
            <div style="background:#f1f5f9; border-radius:12px; padding:8px 12px; margin-bottom:8px;">
                <strong>{role_icon} {msg['from']}</strong> <span style="color:#64748b; font-size:11px;">{msg['time']}</span><br>
                {msg['text']}
            </div>
            """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    with col1:
        new_msg = st.text_input("Сообщение", key="new_msg", label_visibility="collapsed", placeholder="Напишите сообщение...")
    with col2:
        if st.button("📤 Отправить"):
            if new_msg:
                st.session_state.messages.append({
                    "from": st.session_state.current_user["name"],
                    "role": ROLES[st.session_state.current_user["role"]]["name"],
                    "text": new_msg,
                    "time": datetime.now().strftime("%H:%M")
                })
                st.rerun()

def render_video():
    st.subheader("🎥 Видеоконференции")
    st.link_button("🎬 Открыть Яндекс Телемост", "https://telemost.yandex.ru/", use_container_width=True)

def render_admin():
    st.subheader("⚙️ Панель администратора")
    
    new_role = st.selectbox("Сменить роль", list(ROLES.keys()), 
                           format_func=lambda x: f"{ROLES[x]['icon']} {ROLES[x]['name']}")
    if st.button("Применить роль"):
        st.session_state.current_user["role"] = new_role
        st.rerun()
    
    if st.button("🗑️ Сбросить все данные", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ======================== ОСНОВНОЙ ИНТЕРФЕЙС ========================
def main():
    init_session_state()
    
    with st.sidebar:
        st.markdown("# 🏗️ АДС CRM ERP")
        st.caption("Управление строительством")
        st.divider()
        
        user_role = st.session_state.current_user["role"]
        
        tabs_config = [
            {"id": "dashboard", "label": "📊 Панель", "roles": ["admin", "director", "foreman", "master", "supply"]},
            {"id": "employees", "label": "👥 Сотрудники", "roles": ["admin", "director"]},
            {"id": "shifts", "label": "🔨 Смены", "roles": ["admin", "director", "foreman", "master"]},
            {"id": "timesheet", "label": "📊 Табель", "roles": ["admin", "director", "foreman", "master"]},
            {"id": "tools", "label": "🔧 Инструменты", "roles": ["admin", "director", "supply"]},
            {"id": "projects", "label": "🏗️ Проекты", "roles": ["admin", "director", "foreman"]},
            {"id": "tasks", "label": "📋 Задачи", "roles": ["admin", "director", "foreman", "master"]},
            {"id": "photoreports", "label": "📸 Фотоотчёты", "roles": ["admin", "director", "foreman", "master"]},
            {"id": "messenger", "label": "💬 Чат", "roles": ["admin", "director", "foreman", "master", "supply"]},
            {"id": "video", "label": "🎥 Телемост", "roles": ["admin", "director", "foreman", "master"]},
            {"id": "admin", "label": "⚙️ Админ", "roles": ["admin"]}
        ]
        
        for tab in tabs_config:
            if user_role in tab["roles"]:
                if st.button(f"{tab['label']}", key=tab["id"], use_container_width=True):
                    st.session_state.active_tab = tab["id"]
                    st.rerun()
        
        st.divider()
        st.caption(f"👤 {st.session_state.current_user['name']}")
        st.caption(f"🎭 {ROLES[user_role]['icon']} {ROLES[user_role]['name']}")
    
    # Основная область
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
        <div>
            <h1 style="font-size:28px; font-weight:bold;">{{
                "dashboard": "📊 Панель управления",
                "employees": "👥 Управление персоналом",
                "shifts": "🔨 Смены на объектах",
                "timesheet": "📊 Табель учёта времени",
                "tools": "🔧 Склад инструментов",
                "projects": "🏗️ Активные проекты",
                "tasks": "📋 Задачи сотрудникам",
                "photoreports": "📸 Фотоотчёты с объектов",
                "messenger": "💬 Корпоративный чат",
                "video": "🎥 Видеоконференции",
                "admin": "⚙️ Администрирование"
            }}.get(st.session_state.active_tab, "CRM")}}</h1>
        </div>
        <div style="background:white; border-radius:12px; padding:8px 16px;">
            <span>📅 {get_current_date()}</span> &nbsp;|&nbsp;
            <span>🕒 {get_moscow_time()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab = st.session_state.active_tab
    if tab == "dashboard":
        render_dashboard()
    elif tab == "employees":
        render_employees_admin()
    elif tab == "shifts":
        render_shifts()
    elif tab == "timesheet":
        render_timesheet()
    elif tab == "tools":
        render_tools()
    elif tab == "projects":
        render_projects()
    elif tab == "tasks":
        render_tasks()
    elif tab == "photoreports":
        render_photoreports()
    elif tab == "messenger":
        render_messenger()
    elif tab == "video":
        render_video()
    elif tab == "admin":
        render_admin()

if __name__ == "__main__":
    main()

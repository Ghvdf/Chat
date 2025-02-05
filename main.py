import uuid
import sqlite3
import flet as ft
from datetime import datetime
from notes import TodoApp  # Убедитесь, что этот модуль существует

def init_db():
    conn = sqlite3.connect('chat.db')
    cur = conn.cursor()
    
    # Создание таблиц
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            user_id TEXT UNIQUE
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            user_name TEXT,
            text TEXT,
            timestamp DATETIME,
            color TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id TEXT PRIMARY KEY,
            background_color TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect('chat.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()
    return user

def create_user(username, password, user_id):
    conn = sqlite3.connect('chat.db')
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (username, password, user_id) VALUES (?, ?, ?)', 
                   (username, password, user_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def main(page: ft.Page):
    page.title = "Flet Chat"
    page.horizontal_alignment = "center"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE

    init_db()

    user_id = ''
    local_user_name = ""
    auth = False

    # Элементы чата должны быть объявлены до их использования в Tabs
    chat = ft.ListView(
        expand=True,
        auto_scroll=True,
        spacing=10,
        padding=20,
        height=400,
        width=1500,
    )

    new_message = ft.TextField(
        label="Ваше сообщение",
        width=650,
        border=ft.InputBorder.OUTLINE,
    )

    clear_button = ft.IconButton(ft.icons.DELETE, width=50)
    send_button = ft.IconButton(ft.icons.SEND, width=50)

    chat_row = ft.Row(
        [clear_button, new_message, send_button],
        alignment=ft.MainAxisAlignment.CENTER
    )

    selected_color = ft.colors.INDIGO_500

    def close_dlg(e):
        color_dlg.open = False
        page.update()

    def open_dlg(e):
        page.dialog = color_dlg
        page.dialog.open = True
        page.update()

    def select_color(e, color):
        nonlocal selected_color, user_id
        selected_color = color
        
        # Сохраняем цвет в настройки пользователя
        conn = sqlite3.connect('chat.db')
        cur = conn.cursor()
        cur.execute('''
            INSERT OR REPLACE INTO user_settings 
            (user_id, background_color) 
            VALUES (?, ?)
        ''', (user_id, color))
        conn.commit()
        conn.close()
        
        color_dlg.open = False
        page.update()   

    color = [
                    ft.colors.RED_500,
                    ft.colors.PINK_500,
                    ft.colors.PURPLE_500,
                    ft.colors.DEEP_PURPLE_500,
                    ft.colors.INDIGO_500,
                    ft.colors.BLUE_500,
                    ft.colors.CYAN_500,
                    ft.colors.TEAL_500,
                    ft.colors.GREEN_500,
                    ft.colors.LIME_500,
                    ft.colors.AMBER_500,
                    ft.colors.ORANGE_500,
                    ft.colors.WHITE
                ]    

    color_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text('Выберите цвет заднего фона'),
        content=ft.GridView(
            runs_count=4,
            max_extent=50,
            child_aspect_ratio=1.0,
            spacing=5,
            run_spacing=5,
            controls=[
                ft.Container(
                    ft.IconButton(
                        icon=ft.icons.CIRCLE,
                        icon_size=40,
                        icon_color=colors,
                        on_click=lambda e, c=colors: select_color(e, c),
                    )
                ) for colors in color
            ]
        ),
        actions=[ft.TextButton('Закрыть', on_click=close_dlg), 
        ],
          
    )


    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Чат",
                content=ft.Column([
                    ft.Container(
                        content=chat,
                        border=ft.border.all(1, ft.colors.BLUE_100), # Обводка 
                        border_radius=5,
                        padding=10,
                        bgcolor=selected_color # Цвет заднего фона 
                    ),
                    chat_row
                ])
            ),
            ft.Tab(
                text='Заметки',
                icon=ft.icons.NOTES,
                content=TodoApp(),
            ),
            ft.Tab(
                text="Настройки",
                icon=ft.icons.SETTINGS,
                content=ft.Column([
                    ft.ElevatedButton(text='Выбрать цвет фона сообщений', on_click=open_dlg),
                ], spacing=20)
            )
        ],
        expand=True
    )

    def handle_route_change(route):
        nonlocal auth
        
        if page.route == '/chat' and not auth:
            page.go('/')
            return

        page.views.clear()
        
        if page.route == "/":
            page.views.append(
                ft.View(
                    route="/",
                    controls=[
                        ft.Text(value='Авторизация', size=30),
                        inputField_name,
                        inputField_password,
                        button,
                        reg_button,
                        error_text,
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        
        elif page.route == "/chat":
            page.views.append(
                ft.View(
                    route="/chat",
                    controls=[
                        ft.Container(
                            content=tabs,
                            width=800,
                            height=600,
                            padding=20
                        )
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        
        page.update()


    def submit(e):
        nonlocal auth, user_id, local_user_name, selected_color
        username = inputField_name.value.strip()
        password = inputField_password.value.strip()
        
        if not username or not password:
            error_text.visible = True
            page.update()
            return
        
        user = get_user(username)
        if user is None:
            new_user_id = str(uuid.uuid4())[:8]
            if create_user(username, password, new_user_id):
                user_id = new_user_id
                local_user_name = username
                auth = True
                error_text.visible = False
                
                # Загрузка настроек по умолчанию
                selected_color = ft.colors.INDIGO_500
                page.go("/chat")
            else:
                error_text.value = "Имя пользователя занято!"
                error_text.visible = True
        else:
            if password == user[2]:
                user_id = user[3]
                local_user_name = username
                auth = True
                error_text.visible = False
                
                # Загрузка сохраненных настроек
                conn = sqlite3.connect('chat.db')
                cur = conn.cursor()
                cur.execute('SELECT background_color FROM user_settings WHERE user_id = ?', (user_id,))
                setting = cur.fetchone()
                selected_color = setting[0] if setting else ft.colors.INDIGO_500
                conn.close()
                
                # Загрузка истории сообщений
                conn = sqlite3.connect('chat.db')
                cur = conn.cursor()
                cur.execute('''
                    SELECT user_id, user_name, text, timestamp, color 
                    FROM messages 
                    ORDER BY timestamp
                ''')
                messages = cur.fetchall()
                conn.close()
                
                # Отображение истории
                for msg in messages:
                    on_message({
                        "user_id": msg[0],
                        "user_name": msg[1],
                        "text": msg[2],
                        "timestamp": msg[3],
                        "color": msg[4]
                    })
                
                page.go("/chat")
            else:
                error_text.value = "Неверный пароль!"
                error_text.visible = True
        
        page.update()


    inputField_name = ft.TextField(
        label="Username",
        border=ft.InputBorder.UNDERLINE,
        prefix_icon=ft.icons.PERSON,
        width=400
    )

    inputField_password = ft.TextField(
        label="Password",
        border=ft.InputBorder.UNDERLINE,
        prefix_icon=ft.icons.LOCK,
        password=True,
        can_reveal_password=True,
        width=400
    )

    button = ft.ElevatedButton(
        text='Подтвердить',
        width=200,
        on_click=submit
    )

    reg_button = ft.ElevatedButton(
        text= 'Зарегистрироваться',
        width=200,
        on_click=submit,
    )

    error_text = ft.Text(
        value="Invalid username or password!",
        color="red",
        visible=False
    )

    def on_message(msg: dict):
        nonlocal selected_color
        display_name = "Вы" if msg["user_id"] == user_id else msg["user_name"]
        # Генерация аватарки на основе имени
        avatar = ft.Container(
            content=ft.Text(
                display_name[0].upper(),  # Первая буква имени
                size=20,
                color=ft.colors.WHITE, # Цвет текста на аве
                weight=ft.FontWeight.BOLD,
            ),
            width=40,
            height=40,
            bgcolor=ft.colors.BLUE_700, # Задный фон аватарки
            border_radius=20,
            alignment=ft.alignment.center
        )
        message_text = ft.Container(
                    content=ft.Text(
                        msg["text"],
                            color=ft.colors.BLACK if selected_color == ft.colors.WHITE else ft.colors.WHITE,
                            size=14,
                            max_lines=None,  # Неограниченное количество строк
                            overflow=ft.TextOverflow.CLIP,
                    ),
                    padding=ft.padding.symmetric(horizontal=15, vertical=10),
                    bgcolor=selected_color if msg["user_id"] == user_id else ft.colors.BLUE_700,
                    border_radius=10,
                    width=500, 
                            )
        
        # Создание элемента сообщения с аватаркой
        message_container = ft.Container(
            content=ft.Row(
                controls=[
                    avatar,
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        display_name,
                                        color=ft.colors.WHITE,
                                        weight=ft.FontWeight.BOLD,
                                        size=14
                                    ),
                                    ft.Text(
                                        msg["timestamp"],
                                        color=ft.colors.WHITE54,
                                        size=12,
                                    ),
                                    ft.Text(
                                        value=f'ID: {msg["user_id"]}', 
                                        size=13,
                                        color=ft.colors.WHITE54,
                                    )
                                ],
                                spacing=10
                            ),
                            message_text
                        ],
                        spacing=5,
                        horizontal_alignment='spasebettwen'
                    )
                ],
                spacing=7
            ),
            padding=ft.padding.symmetric(vertical=5)
        )
        

        # Выравнивание сообщений
        if msg["user_id"] == user_id:
            message_container.animate_opacity = 100
            message_container.opacity = 0
            message_container.opacity = 1
            message_container.content.alignment = ft.MainAxisAlignment.END
            message_container.content.controls.reverse()
            page.update()
        
        chat.controls.append(message_container)
        page.update()

    def clear_chat(e):
        chat.controls.clear()
        page.update()

    page.pubsub.subscribe(on_message)

    def send_click(e):
        nonlocal local_user_name, user_id, selected_color
        if new_message.value.strip() and local_user_name:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Сохраняем сообщение в БД
            conn = sqlite3.connect('chat.db')
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO messages 
                (user_id, user_name, text, timestamp, color)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, local_user_name, new_message.value, timestamp, selected_color))
            conn.commit()
            conn.close()
            
            page.pubsub.send_all({
                "text": new_message.value,
                "user_name": local_user_name,
                "user_id": user_id,
                "timestamp": timestamp,
                "color": selected_color,
            })
            new_message.value = ""
            page.update()

    # Назначаем обработчики после объявления всех элементов
    send_button.on_click = send_click
    clear_button.on_click = clear_chat
    new_message.on_submit = send_click

    page.on_route_change = handle_route_change
    page.on_view_pop = lambda _: page.go("/")
    page.go(page.route)

ft.app(target=main, view=ft.WEB_BROWSER)

import flet as ft
from flet import *
from datetime import datetime
import uuid


class Task(ft.Column):
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.display_task = ft.Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )
        self.controls = [self.display_view, self.edit_view]

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_status_change(self)

    def delete_clicked(self, e):
        self.task_delete(self)

class TodoApp(ft.Column):
    # application's root control is a Column containing all other controls
    def __init__(self):
        super().__init__()
        self.new_task = ft.TextField(
            hint_text="Введите текст", on_submit=self.add_clicked, expand=True
        )
        self.tasks = ft.Column()

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="Все"), ft.Tab(text="Активные"), ft.Tab(text="Завершенные")],
        )

        self.items_left = ft.Text("0 заметок")

        self.width = 600
        self.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        icon=ft.icons.ADD, on_click=self.add_clicked
                    ),
                ],
            ),
            ft.Column(
                spacing=25,
                controls=[
                    self.filter,
                    self.tasks,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.items_left,
                            ft.OutlinedButton(
                                text="Очистить", on_click=self.clear_clicked
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def add_clicked(self, e):
        if self.new_task.value:
            task = Task(self.new_task.value, self.task_status_change, self.task_delete)
            self.tasks.controls.append(task)
            self.new_task.value = ""
            self.new_task.focus()
            self.update()

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def tabs_changed(self, e):
        self.update()

    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                self.task_delete(task)

    def before_update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "Все"
                or (status == "Активные" and task.completed == False)
                or (status == "Завершенные" and task.completed)
            )
            if not task.completed:
                count += 1
        self.items_left.value = f"{count} активных заметок"

def main(page: ft.Page):
    page.title = "Flet Chat"
    page.horizontal_alignment = "center"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE


    user_id = str(uuid.uuid4())[:8]
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
        nonlocal selected_color
        selected_color = color
        color_dlg.open = False
        page.update()   


    color_palette = [
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

    # Создаем сетку цветов
    color_grid = ft.GridView(
        runs_count=4,
        max_extent=50,
        child_aspect_ratio=1.0,
        spacing=5,
        run_spacing=5,
    )

    for color in color_palette:
        color_grid.controls.append(
            ft.Container(
                content=ft.IconButton(
                    icon=ft.icons.CIRCLE,
                    icon_size=40,
                    icon_color=color,
                    on_click=lambda e, c=color: select_color(e, c),
                ),
                alignment=ft.alignment.center,
            )
        )
     

    color_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text('Выберите цвет заднего фона'),
        content=color_grid,
        actions=[
            ft.TextButton('Закрыть', on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
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
                        border=ft.border.all(1, ft.colors.BLUE_100),
                        border_radius=5,
                        padding=10,
                        #bgcolor='pink'
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

                    ft.ElevatedButton(text='Открыть',on_click=open_dlg)
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
                        ft.Text(value='Login', size=30),
                        inputField_name,
                        inputField_password,
                        button,
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
        nonlocal auth
        if inputField_name.value.strip() == "" or inputField_password.value.strip() == "":
            error_text.visible = True
            page.update()
        else:
            error_text.visible = False
            auth = True
            page.go("/chat")

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
        text="Submit",
        width=200,
        on_click=submit
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
                color=ft.colors.WHITE,
                weight=ft.FontWeight.BOLD,
            ),
            width=40,
            height=40,
            bgcolor=ft.colors.BLUE_700,
            border_radius=20,
            alignment=ft.alignment.center
        )
        message_text = ft.Container(
                    content=ft.Text(
                        msg["text"],
                            color=ft.colors.BLACK if selected_color == ft.colors.WHITE else ft.colors.WHITE,
                            size=14,
                            max_lines=None,  # Неограниченное количество строк
                            overflow=ft.TextOverflow.FADE,
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
                spacing=10
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
        nonlocal local_user_name
        local_user_name = inputField_name.value.strip()
        
        if new_message.value.strip() and local_user_name:
            page.pubsub.send_all({
                "text": new_message.value,
                "user_name": local_user_name,
                "user_id": user_id,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
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
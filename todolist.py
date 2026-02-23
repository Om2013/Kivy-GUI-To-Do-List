from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from datetime import datetime

# ---------------- Screen Manager ----------------
sm = ScreenManager(transition=SlideTransition())

# ---------------- DASHBOARD SCREEN ----------------
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        
        # Title
        title = Label(
            text="TO-DO LIST APP",
            size_hint=(1, 0.1),
            pos_hint={"top": 1},
            color=(0, 1, 0, 1)
        )
        self.layout.add_widget(title)

        # Date
        today = datetime.now()
        date_label = Label(
            text=today.strftime("%A, %d %B %Y"),
            size_hint=(1, 0.05),
            pos_hint={'center_x': 0.5, 'top': 0.9},
            color=(0,1,0,1)
        )
        self.layout.add_widget(date_label)

        # Scrollable Grid for tasks
        scroll = ScrollView(
            size_hint=(0.95, 0.7),
            pos_hint={'center_x':0.5, 'center_y':0.45}
        )
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        # Header row
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        header.add_widget(Label(text="OBJECTIVE", bold=True))
        header.add_widget(Label(text="DEADLINE", bold=True))
        header.add_widget(Label(text="PRIORITY", bold=True))
        header.add_widget(Label(text="DONE", bold=True))
        self.grid.add_widget(header)

        scroll.add_widget(self.grid)
        self.layout.add_widget(scroll)

        # Add Task Button
        add_btn = Button(
            text="Add Task",
            size_hint=(0.4, 0.1),
            pos_hint={"center_x": 0.5, "y": 0.05}
        )
        add_btn.bind(on_press=self.go_to_add)  
        self.layout.add_widget(add_btn)

        self.add_widget(self.layout)

    def go_to_add(self, instance):
        sm.transition.direction = "left"
        sm.current = "AddTask"

    def add_task_label(self, objective, deadline, priority):
        # Row layout for a task
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=5)

        obj_label = Label(text=objective)
        dead_label = Label(text=deadline)
        pri_label = Label(text=priority)

        done_btn = Button(text="Done", size_hint_x=0.2)
        def remove_task(instance):
            self.grid.remove_widget(row)
        done_btn.bind(on_press=remove_task)

        row.add_widget(obj_label)
        row.add_widget(dead_label)
        row.add_widget(pri_label)
        row.add_widget(done_btn)

        self.grid.add_widget(row)

# ---------------- ADD TASK SCREEN ----------------
class AddTaskScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        title = Label(text="ADD NEW TASK", size_hint=(1, 0.1), color=(0,1,0,1))
        layout.add_widget(title)

        # Objective
        obj_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.obj_input = TextInput(size_hint=(0.7,1))
        obj_box.add_widget(Label(text="Objective:", size_hint=(0.3,1)))
        obj_box.add_widget(self.obj_input)
        layout.add_widget(obj_box)

        # Deadline
        dead_box = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        self.dead_input = TextInput(size_hint=(0.7,1))
        dead_box.add_widget(Label(text="Deadline:", size_hint=(0.3,1)))
        dead_box.add_widget(self.dead_input)
        layout.add_widget(dead_box)

        # Priority
        priority_box = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        self.priority_spinner = Spinner(
            text="Select Priority",
            values=("High","Medium","Low"),
            size_hint=(0.7,1)
        )
        priority_box.add_widget(Label(text="Priority:", size_hint=(0.3,1)))
        priority_box.add_widget(self.priority_spinner)
        layout.add_widget(priority_box)

        # Buttons
        btn_box = BoxLayout(orientation='horizontal', size_hint=(1,0.15), spacing=20)
        save_btn = Button(text="Save Task")
        back_btn = Button(text="Back")
        back_btn.bind(on_press=self.go_back)  
        save_btn.bind(on_press=self.save_task)
        btn_box.add_widget(back_btn)
        btn_box.add_widget(save_btn)
        layout.add_widget(btn_box)

        self.add_widget(layout)

    def go_back(self, instance):
        sm.transition.direction = "right"
        sm.current = "Dashboard"

    def save_task(self, instance):
        objective = self.obj_input.text.strip()
        deadline = self.dead_input.text.strip()
        priority = self.priority_spinner.text

        if objective:
            dashboard = sm.get_screen("Dashboard")
            dashboard.add_task_label(objective, deadline, priority)

        # Clear inputs
        self.obj_input.text = ""
        self.dead_input.text = ""
        self.priority_spinner.text = "Select Priority"

        # Go back to Dashboard
        sm.transition.direction = "right"
        sm.current = "Dashboard"

# ---------------- ADD SCREENS ----------------
dashboard_screen = DashboardScreen(name="Dashboard")
addtask_screen = AddTaskScreen(name="AddTask")

sm.add_widget(dashboard_screen)
sm.add_widget(addtask_screen)

# ---------------- APP ----------------
class TodoApp(App):
    def build(self):
        return sm

if __name__ == "__main__":
    TodoApp().run()
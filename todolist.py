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
import firebase_admin
from firebase_admin import credentials, db
import random

# ---------------- FIREBASE SETUP ----------------
cred = credentials.Certificate("todolist-json.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://todolist-kivy-default-rtdb.firebaseio.com/"
})
tasks_ref = db.reference("tasks")

# ---------------- SCREEN MANAGER ----------------
sm = ScreenManager(transition=SlideTransition())

# ---------------- DASHBOARD SCREEN ----------------
class DashboardScreen(Screen):
    def __init__(self):
        super().__init__()
        self.layout = FloatLayout()

        self.grid = GridLayout(cols=4, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))

        for header in ["OBJECTIVE", "DEADLINE", "PRIORITY", "DONE"]:
            self.grid.add_widget(Label(text=header, size_hint_y=None, height=30, bold=True))

        # scrollview
        scroll = ScrollView(size_hint=(0.95, 0.7), pos_hint={"center_x":0.5, "center_y":0.45})
        scroll.add_widget(self.grid)
        self.layout.add_widget(scroll)
        
        # add task button
        add_btn = Button(text="Add Task", size_hint=(0.4,0.1), pos_hint={"center_x":0.5, "y":0.05})
        add_btn.bind(on_press=self.go_to_add)
        self.layout.add_widget(add_btn)
        self.add_widget(self.layout)

    def go_to_add(self, instance):
        sm.transition.direction = "left"
        sm.current = "AddTask"

    def add_task_label(self, objective, deadline, priority, task_id=None):
        obj_label = Label(text=str(objective), size_hint_y=None, height=30)
        dead_label = Label(text=str(deadline), size_hint_y=None, height=30)
        pri_label = Label(text=str(priority), size_hint_y=None, height=30)
        done_btn = Button(text="Done", size_hint_y=None, height=30)

        def remove_task(instance):
            self.grid.remove_widget(obj_label)
            self.grid.remove_widget(dead_label)
            self.grid.remove_widget(pri_label)
            self.grid.remove_widget(done_btn)
            if task_id:
                db.reference(f"tasks/{task_id}").delete()

        done_btn.bind(on_press=remove_task)
        self.grid.add_widget(obj_label)
        self.grid.add_widget(dead_label)
        self.grid.add_widget(pri_label)
        self.grid.add_widget(done_btn)

# ---------------- ADD TASK SCREEN ----------------
class AddTaskScreen(Screen):
    def __init__(self):
        super().__init__()
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        layout.add_widget(Label(text="ADD NEW TASK", size_hint=(1,0.1), color=(0,1,0,1)))

        # Objective
        obj_box = BoxLayout(orientation="horizontal", size_hint=(1,0.1))
        self.obj_input = TextInput(size_hint=(0.7,1))
        obj_box.add_widget(Label(text="Objective:", size_hint=(0.3,1)))
        obj_box.add_widget(self.obj_input)
        layout.add_widget(obj_box)

        # Deadline
        dead_box = BoxLayout(orientation="horizontal", size_hint=(1,0.1))
        self.dead_input = TextInput(size_hint=(0.7,1))
        dead_box.add_widget(Label(text="Deadline:", size_hint=(0.3,1)))
        dead_box.add_widget(self.dead_input)
        layout.add_widget(dead_box)

        # Priority
        priority_box = BoxLayout(orientation="horizontal", size_hint=(1,0.1))
        self.priority_spinner = Spinner(text="Select Priority", values=("High","Medium","Low"), size_hint=(0.7,1))
        priority_box.add_widget(Label(text="Priority:", size_hint=(0.3,1)))
        priority_box.add_widget(self.priority_spinner)
        layout.add_widget(priority_box)

        # Buttons
        btn_box = BoxLayout(orientation="horizontal", size_hint=(1,0.15), spacing=20)
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
            task_id = random.randint(1000,999999)
            tasks_ref.update({str(task_id): {"objective":objective,"deadline":deadline,"priority":priority,"done":False}})
            dashboard = sm.get_screen("Dashboard")

            # Print everything
            print(f"Task ID: {task_id}")
            print(f"Objective: {objective}")
            print(f"Deadline: {deadline}")
            print(f"Priority: {priority}")
            print(f"Done: False")
            print("-" * 20)

        dashboard.add_task_label(objective, deadline, priority, task_id=task_id)
        self.obj_input.text = ""
        self.dead_input.text = ""
        self.priority_spinner.text = "Select Priority"
        sm.transition.direction = "right"
        sm.current = "Dashboard"


# ---------------- ADD SCREENS ----------------
dashboard_screen = DashboardScreen()
dashboard_screen.name = "Dashboard"
addtask_screen = AddTaskScreen()
addtask_screen.name = "AddTask"
sm.add_widget(dashboard_screen)
sm.add_widget(addtask_screen)

# ---------------- APP ----------------
class TodoApp(App):
    def build(self):
        tasks = tasks_ref.get()
        if tasks:
            dashboard = sm.get_screen("Dashboard")

            for task_id, task_data in tasks.items():
                dashboard.add_task_label(
                    task_data.get("objective"),
                    task_data.get("deadline"),
                    task_data.get("priority"),
                    task_id=task_id
                )
        return sm

if __name__ == "__main__":
    TodoApp().run()

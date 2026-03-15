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

cred = credentials.Certificate("todolist-kivy-firebase-adminsdk-fbsvc-38397b7250.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://your-db.firebaseio.com/"
})

tasks_ref = db.reference("tasks")

# ---------------- SCREEN MANAGER ----------------

sm = ScreenManager(transition=SlideTransition())

# ---------------- DASHBOARD SCREEN ----------------

class DashboardScreen(Screen):

    def __init__(self):
        super().__init__()

        self.layout = FloatLayout()

        title = Label(
            text="TO-DO LIST APP",
            size_hint=(1, 0.1),
            pos_hint={"top": 1},
            color=(0, 1, 0, 1)
        )
        self.layout.add_widget(title)

        today = datetime.now()
        date_label = Label(
            text=today.strftime("%A, %d %B %Y"),
            size_hint=(1, 0.05),
            pos_hint={"center_x": 0.5, "top": 0.9},
            color=(0,1,0,1)
        )
        self.layout.add_widget(date_label)

        scroll = ScrollView(
            size_hint=(0.95, 0.7),
            pos_hint={"center_x":0.5,"center_y":0.45}
        )

        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))

        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)

        header.add_widget(Label(text="OBJECTIVE"))
        header.add_widget(Label(text="DEADLINE"))
        header.add_widget(Label(text="PRIORITY"))
        header.add_widget(Label(text="DONE"))

        self.grid.add_widget(header)

        scroll.add_widget(self.grid)
        self.layout.add_widget(scroll)

        add_btn = Button(
            text="Add Task",
            size_hint=(0.4,0.1),
            pos_hint={"center_x":0.5,"y":0.05}
        )

        add_btn.bind(on_press=self.go_to_add)
        self.layout.add_widget(add_btn)

        self.add_widget(self.layout)

    def go_to_add(self, instance):
        sm.transition.direction = "left"
        sm.current = "AddTask"

    def add_task_label(self, objective, deadline, priority):

        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=30, spacing=5)

        obj_label = Label(text=str(objective))
        dead_label = Label(text=str(deadline))
        pri_label = Label(text=str(priority))

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

    def __init__(self):
        super().__init__()

        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        title = Label(text="ADD NEW TASK", size_hint=(1,0.1), color=(0,1,0,1))
        layout.add_widget(title)

        obj_box = BoxLayout(orientation="horizontal", size_hint=(1,0.1))
        self.obj_input = TextInput(size_hint=(0.7,1))
        obj_box.add_widget(Label(text="Objective:", size_hint=(0.3,1)))
        obj_box.add_widget(self.obj_input)
        layout.add_widget(obj_box)

        dead_box = BoxLayout(orientation="horizontal", size_hint=(1,0.1))
        self.dead_input = TextInput(size_hint=(0.7,1))
        dead_box.add_widget(Label(text="Deadline:", size_hint=(0.3,1)))
        dead_box.add_widget(self.dead_input)
        layout.add_widget(dead_box)

        priority_box = BoxLayout(orientation="horizontal", size_hint=(1,0.1))

        self.priority_spinner = Spinner(
            text="Select Priority",
            values=("High","Medium","Low"),
            size_hint=(0.7,1)
        )

        priority_box.add_widget(Label(text="Priority:", size_hint=(0.3,1)))
        priority_box.add_widget(self.priority_spinner)

        layout.add_widget(priority_box)

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

            tasks_ref.update({
                str(task_id):{
                    "objective":objective,
                    "deadline":deadline,
                    "priority":priority,
                    "done":False
                }
            })

            dashboard = sm.get_screen("Dashboard")
            dashboard.add_task_label(objective, deadline, priority)

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

        # Step 1: Access Firebase tasks node
        tasks_reference = db.reference("tasks")

        # Step 2: Fetch tasks
        tasks = tasks_reference.get()

        # Step 3: Check if tasks exist
        if tasks:

            dashboard = sm.get_screen("Dashboard")

            # Step 4: Loop through tasks
            for task_id, task_data in tasks.items():

                # Step 5: Safely read fields
                objective = task_data.get("objective")
                deadline = task_data.get("deadline")
                priority = task_data.get("priority")
                done = task_data.get("done")

                # Print to terminal
                print("Task ID:", task_id)
                print("Objective:", objective)
                print("Deadline:", deadline)
                print("Priority:", priority)
                print("Done:", done)
                print("---------------------")

                # Show on dashboard
                dashboard.add_task_label(objective, deadline, priority)

        else:
            print("No tasks found in Firebase")

        return sm


if __name__ == "__main__":
    TodoApp().run()

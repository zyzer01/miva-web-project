from datetime import datetime
import os

class Task:
    """
    Represents a single task in the Todo List Manager.
    Contains all task-related properties and methods for serialization/deserialization.
    """
    def __init__(self, task_id, task_name, task_status="Active", time_created=None, time_finished=None):
        """
        Initialize a new Task object with the given properties.
        If time_created is not provided, uses current time.
        """
        self.task_id = task_id
        self.task_name = task_name
        self.task_status = task_status
        self.time_created = time_created if time_created else datetime.now()
        self.time_finished = time_finished

    def to_string(self):
        """
        Converts the task object to a string format for file storage.
        Returns a pipe-separated string of all task properties.
        """
        return f"{self.task_id}|{self.task_name}|{self.task_status}|{self.time_created}|{self.time_finished}"

    @staticmethod
    def from_string(line):
        """
        Creates a Task object from a string (used when loading from file).
        Expects a pipe-separated string containing all task properties.
        Returns a new Task object.
        """
        task_id, task_name, task_status, time_created, time_finished = line.strip().split('|')
        time_created = datetime.fromisoformat(time_created)
        time_finished = None if time_finished == "None" else datetime.fromisoformat(time_finished)
        return Task(int(task_id), task_name, task_status, time_created, time_finished)

class TodoListManager:
    """
    Main class that manages the Todo List application.
    Handles all task operations and file management.
    """
    def __init__(self):
        """
        Initialize the Todo List Manager with empty task lists and default values.
        Sets up the basic structure for task management.
        """
        self.active_tasks = []
        self.completed_tasks = []
        self.deleted_tasks = []
        self.user_name = ""
        self.next_task_id = 1
        
    def initialize(self):
        """
        Performs all necessary initialization steps:
        1. Gets or sets up user name
        2. Loads existing tasks from files
        3. Updates the next available task ID
        """
        self.get_user_name()
        self.load_tasks()
        self.update_next_task_id()
        
    def get_user_name(self):
        """
        Retrieves or prompts for user name:
        - First tries to read from names.txt
        - If file doesn't exist, asks user for name and creates file
        Updates self.user_name with the result
        """
        try:
            with open('names.txt', 'r') as file:
                self.user_name = file.readline().strip()
        except FileNotFoundError:
            self.user_name = input("Please enter your name: ").strip()
            with open('names.txt', 'w') as file:
                file.write(self.user_name)
                
    def load_tasks(self):
        """
        Loads all tasks from their respective files:
        - Active.txt for active tasks
        - Completed.txt for completed tasks
        - Deleted.txt for deleted tasks
        """
        self.active_tasks = self.load_task_file('Active.txt')
        self.completed_tasks = self.load_task_file('Completed.txt')
        self.deleted_tasks = self.load_task_file('Deleted.txt')
        
    def load_task_file(self, filename):
        """
        Loads tasks from a specific file.
        Returns an empty list if file doesn't exist.
        Args:
            filename: Name of the file to load tasks from
        Returns:
            List of Task objects
        """
        tasks = []
        try:
            with open(filename, 'r') as file:
                for line in file:
                    tasks.append(Task.from_string(line))
        except FileNotFoundError:
            pass
        return tasks
        
    def save_tasks(self):
        """
        Saves all task lists to their respective files.
        Called after any modification to tasks to ensure persistence.
        """
        self.save_task_file('Active.txt', self.active_tasks)
        self.save_task_file('Completed.txt', self.completed_tasks)
        self.save_task_file('Deleted.txt', self.deleted_tasks)
        
    def save_task_file(self, filename, tasks):
        """
        Saves a specific task list to a file.
        Args:
            filename: Name of the file to save to
            tasks: List of Task objects to save
        """
        with open(filename, 'w') as file:
            for task in tasks:
                file.write(task.to_string() + '\n')
                
    def update_next_task_id(self):
        """
        Updates the next_task_id based on existing tasks.
        Ensures new tasks always get a unique ID by finding the maximum
        existing ID and adding 1.
        """
        all_tasks = self.active_tasks + self.completed_tasks + self.deleted_tasks
        if all_tasks:
            self.next_task_id = max(task.task_id for task in all_tasks) + 1
        else:
            self.next_task_id = 1
            
    def add_task(self):
        """
        Handles the process of adding a new task:
        1. Prompts user for task name
        2. Creates new Task object with next available ID
        3. Adds to active tasks and saves
        """
        task_name = input("Enter task name: ").strip()
        task = Task(self.next_task_id, task_name)
        self.active_tasks.append(task)
        self.next_task_id += 1
        self.save_tasks()
        print("Task added successfully!")
        
    def view_tasks(self, task_list, status):
        """
        Displays tasks from a specific task list.
        Args:
            task_list: List of tasks to display
            status: Status of tasks being displayed (for header)
        """
        if not task_list:
            print(f"No {status.lower()} tasks found.")
            return
        print(f"\n{status} Tasks:")
        print("-" * 80)
        for task in task_list:
            print(f"ID: {task.task_id} | Name: {task.task_name} | Created: {task.time_created}")
            if task.time_finished:
                print(f"Completed: {task.time_finished}")
        print("-" * 80)
        
    def edit_task_name(self):
        """
        Handles the process of editing a task name:
        1. Shows active tasks
        2. Prompts for task ID
        3. If found, prompts for new name
        4. Updates task and saves changes
        """
        self.view_tasks(self.active_tasks, "Active")
        if not self.active_tasks:
            return
        
        task_id = input("Enter task ID to edit: ")
        try:
            task_id = int(task_id)
            task = next((t for t in self.active_tasks if t.task_id == task_id), None)
            if task:
                new_name = input("Enter new task name: ").strip()
                task.task_name = new_name
                self.save_tasks()
                print("Task name updated successfully!")
            else:
                print("Task not found!")
        except ValueError:
            print("Invalid task ID!")
            
    def mark_task_complete(self):
        """
        Handles marking a task as complete:
        1. Shows active tasks
        2. Prompts for task ID
        3. If found, updates status, adds completion time
        4. Moves task to completed list and saves
        """
        self.view_tasks(self.active_tasks, "Active")
        if not self.active_tasks:
            return
            
        task_id = input("Enter task ID to mark as complete: ")
        try:
            task_id = int(task_id)
            task = next((t for t in self.active_tasks if t.task_id == task_id), None)
            if task:
                task.task_status = "Completed"
                task.time_finished = datetime.now()
                self.completed_tasks.append(task)
                self.active_tasks.remove(task)
                self.save_tasks()
                print("Task marked as complete!")
            else:
                print("Task not found!")
        except ValueError:
            print("Invalid task ID!")
            
    def delete_task(self):
        """
        Handles deleting a task:
        1. Shows active tasks
        2. Prompts for task ID
        3. If found, changes status to Deleted
        4. Moves task to deleted list and saves
        """
        self.view_tasks(self.active_tasks, "Active")
        if not self.active_tasks:
            return
            
        task_id = input("Enter task ID to delete: ")
        try:
            task_id = int(task_id)
            task = next((t for t in self.active_tasks if t.task_id == task_id), None)
            if task:
                task.task_status = "Deleted"
                self.deleted_tasks.append(task)
                self.active_tasks.remove(task)
                self.save_tasks()
                print("Task deleted successfully!")
            else:
                print("Task not found!")
        except ValueError:
            print("Invalid task ID!")
            
    def run(self):
        """
        Main program loop:
        1. Initializes the manager
        2. Displays welcome message
        3. Shows menu and handles user input
        4. Continues until user chooses to exit
        """
        self.initialize()
        print(f"\nHello {self.user_name}, Your Todo List Manager here 👋")
        print("How may I help you today?\n")
        
        while True:
            print("\nMenu")
            print("-" * 20)
            print("1. Add task")
            print("2. View active tasks")
            print("3. View completed tasks")
            print("4. View deleted tasks")
            print("5. Edit task name")
            print("6. Mark task as complete")
            print("7. Delete task")
            print("8. Exit program")
            
            choice = input("\nSelect an option: ")
            
            if choice == "1":
                self.add_task()
            elif choice == "2":
                self.view_tasks(self.active_tasks, "Active")
            elif choice == "3":
                self.view_tasks(self.completed_tasks, "Completed")
            elif choice == "4":
                self.view_tasks(self.deleted_tasks, "Deleted")
            elif choice == "5":
                self.edit_task_name()
            elif choice == "6":
                self.mark_task_complete()
            elif choice == "7":
                self.delete_task()
            elif choice == "8":
                print("Thank you for using Todo List Manager. Goodbye!")
                break
            else:
                print("Invalid option! Please try again.")

if __name__ == "__main__":
    todo_manager = TodoListManager()
    todo_manager.run()

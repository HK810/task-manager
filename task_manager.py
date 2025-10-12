#!/usr/bin/env python3

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class TaskManager:
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks = self.load_tasks()
        self.next_id = self.get_next_id()

    def load_tasks(self) -> List[Dict]:
        """Load tasks from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def save_tasks(self) -> None:
        """Save tasks to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def get_next_id(self) -> int:
        """Get the next available task ID"""
        if not self.tasks:
            return 1
        return max(task['id'] for task in self.tasks) + 1

    def add_task(self, title: str, description: str = "", priority: str = "medium") -> Dict:
        """Add a new task"""
        task = {
            'id': self.next_id,
            'title': title,
            'description': description,
            'priority': priority,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        return task

    def update_task(self, task_id: int, **kwargs) -> Optional[Dict]:
        """Update an existing task"""
        for task in self.tasks:
            if task['id'] == task_id:
                for key, value in kwargs.items():
                    if key in task:
                        task[key] = value
                task['updated_at'] = datetime.now().isoformat()
                self.save_tasks()
                return task
        return None

    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                del self.tasks[i]
                self.save_tasks()
                return True
        return False

    def get_task(self, task_id: int) -> Optional[Dict]:
        """Get a specific task by ID"""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None

    def list_tasks(self, status: str = None, priority: str = None) -> List[Dict]:
        """List tasks with optional filtering"""
        filtered_tasks = self.tasks.copy()
        
        if status:
            filtered_tasks = [task for task in filtered_tasks if task['status'] == status]
        
        if priority:
            filtered_tasks = [task for task in filtered_tasks if task['priority'] == priority]
        
        return sorted(filtered_tasks, key=lambda x: x['id'])

    def get_stats(self) -> Dict:
        """Get task statistics"""
        total = len(self.tasks)
        pending = len([t for t in self.tasks if t['status'] == 'pending'])
        completed = len([t for t in self.tasks if t['status'] == 'completed'])
        
        priority_stats = {}
        for task in self.tasks:
            priority = task['priority']
            priority_stats[priority] = priority_stats.get(priority, 0) + 1
        
        return {
            'total': total,
            'pending': pending,
            'completed': completed,
            'by_priority': priority_stats
        }

    def search_tasks(self, query: str) -> List[Dict]:
        """Search tasks by title or description"""
        query = query.lower()
        return [task for task in self.tasks 
                if query in task['title'].lower() or query in task['description'].lower()]

def display_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("           TASK MANAGER")
    print("="*50)
    print("1. Add Task")
    print("2. List Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Search Tasks")
    print("6. View Statistics")
    print("7. Exit")
    print("="*50)

def display_tasks(tasks: List[Dict], title: str = "Tasks"):
    """Display tasks in a formatted way"""
    print(f"\n{title}:")
    print("-" * 60)
    
    if not tasks:
        print("No tasks found.")
        return
    
    for task in tasks:
        status_icon = "✓" if task['status'] == 'completed' else "○"
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
        
        print(f"{status_icon} [{task['id']}] {priority_icon} {task['title']}")
        if task['description']:
            print(f"    {task['description']}")
        print(f"    Status: {task['status'].title()} | Priority: {task['priority'].title()}")
        print(f"    Created: {task['created_at'][:19]}")
        print()

def get_task_input():
    """Get task input from user"""
    title = input("Enter task title: ").strip()
    if not title:
        print("Title cannot be empty!")
        return None
    
    description = input("Enter task description (optional): ").strip()
    
    print("Priority levels: high, medium, low")
    priority = input("Enter priority (default: medium): ").strip().lower()
    if priority not in ['high', 'medium', 'low']:
        priority = 'medium'
    
    return {'title': title, 'description': description, 'priority': priority}

def main():
    """Main application loop"""
    print("Welcome to Task Manager!")
    task_manager = TaskManager()
    
    while True:
        display_menu()
        
        try:
            choice = input("Enter your choice (1-7): ").strip()
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        
        if choice == '1':
            # Add Task
            task_data = get_task_input()
            if task_data:
                task = task_manager.add_task(**task_data)
                print(f"\n✅ Task added successfully! ID: {task['id']}")
        
        elif choice == '2':
            # List Tasks
            print("\nFilter options:")
            print("1. All tasks")
            print("2. Pending tasks")
            print("3. Completed tasks")
            print("4. By priority")
            
            filter_choice = input("Choose filter (1-4): ").strip()
            
            if filter_choice == '1':
                tasks = task_manager.list_tasks()
                display_tasks(tasks, "All Tasks")
            elif filter_choice == '2':
                tasks = task_manager.list_tasks(status='pending')
                display_tasks(tasks, "Pending Tasks")
            elif filter_choice == '3':
                tasks = task_manager.list_tasks(status='completed')
                display_tasks(tasks, "Completed Tasks")
            elif filter_choice == '4':
                priority = input("Enter priority (high/medium/low): ").strip().lower()
                if priority in ['high', 'medium', 'low']:
                    tasks = task_manager.list_tasks(priority=priority)
                    display_tasks(tasks, f"{priority.title()} Priority Tasks")
                else:
                    print("Invalid priority!")
            else:
                print("Invalid choice!")
        
        elif choice == '3':
            # Update Task
            try:
                task_id = int(input("Enter task ID to update: "))
                task = task_manager.get_task(task_id)
                
                if not task:
                    print("Task not found!")
                    continue
                
                print(f"\nCurrent task: {task['title']}")
                print("What would you like to update?")
                print("1. Title")
                print("2. Description")
                print("3. Status")
                print("4. Priority")
                
                update_choice = input("Choose field (1-4): ").strip()
                
                if update_choice == '1':
                    new_title = input("Enter new title: ").strip()
                    if new_title:
                        task_manager.update_task(task_id, title=new_title)
                        print("✅ Title updated!")
                
                elif update_choice == '2':
                    new_desc = input("Enter new description: ").strip()
                    task_manager.update_task(task_id, description=new_desc)
                    print("✅ Description updated!")
                
                elif update_choice == '3':
                    print("Status options: pending, completed")
                    new_status = input("Enter new status: ").strip().lower()
                    if new_status in ['pending', 'completed']:
                        task_manager.update_task(task_id, status=new_status)
                        print("✅ Status updated!")
                    else:
                        print("Invalid status!")
                
                elif update_choice == '4':
                    print("Priority options: high, medium, low")
                    new_priority = input("Enter new priority: ").strip().lower()
                    if new_priority in ['high', 'medium', 'low']:
                        task_manager.update_task(task_id, priority=new_priority)
                        print("✅ Priority updated!")
                    else:
                        print("Invalid priority!")
                else:
                    print("Invalid choice!")
                    
            except ValueError:
                print("Invalid task ID!")
        
        elif choice == '4':
            # Delete Task
            try:
                task_id = int(input("Enter task ID to delete: "))
                if task_manager.delete_task(task_id):
                    print("✅ Task deleted successfully!")
                else:
                    print("❌ Task not found!")
            except ValueError:
                print("Invalid task ID!")
        
        elif choice == '5':
            # Search Tasks
            query = input("Enter search query: ").strip()
            if query:
                results = task_manager.search_tasks(query)
                display_tasks(results, f"Search Results for '{query}'")
            else:
                print("Please enter a search query!")
        
        elif choice == '6':
            # View Statistics
            stats = task_manager.get_stats()
            print("\n📊 Task Statistics:")
            print("-" * 30)
            print(f"Total Tasks: {stats['total']}")
            print(f"Pending: {stats['pending']}")
            print(f"Completed: {stats['completed']}")
            print("\nBy Priority:")
            for priority, count in stats['by_priority'].items():
                print(f"  {priority.title()}: {count}")
        
        elif choice == '7':
            print("Thank you for using Task Manager. Goodbye!")
            break
        
        else:
            print("Invalid choice! Please enter 1-7.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()

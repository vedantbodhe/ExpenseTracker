import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
import json


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")

        # Load saved data
        self.load_data()

        # Other variables
        #self.expenses = []

        # UI Elements
        self.setup_ui()

    def setup_ui(self):

        style = ttk.Style(self.root)
        style.configure("BudgetAdjustment.Treeview", foreground="green")
        style.configure("NegativeExpense.Treeview", foreground="red")

        # Monthly Budget
        tk.Label(self.root, text="Monthly Budget:").grid(row=0, column=0)
        self.budget_entry = tk.Entry(self.root)
        self.budget_entry.grid(row=0, column=1)
        self.budget_entry.insert(0, str(self.budget))

        # Expense Name
        tk.Label(self.root, text="Expense Name:").grid(row=1, column=0)
        self.expense_name_entry = tk.Entry(self.root)
        self.expense_name_entry.grid(row=1, column=1)

        # Expense Amount
        tk.Label(self.root, text="Amount:").grid(row=2, column=0)
        self.expense_amount_entry = tk.Entry(self.root)
        self.expense_amount_entry.grid(row=2, column=1)

        # Frequency
        tk.Label(self.root, text="Frequency:").grid(row=3, column=0)
        self.frequency_var = tk.StringVar(value="Monthly")
        tk.OptionMenu(self.root, self.frequency_var, "Daily", "Weekly", "Monthly", "One Time").grid(row=3, column=1)

        # Buttons
        tk.Button(self.root, text="Set Budget", command=self.set_budget).grid(row=4, column=0)
        tk.Button(self.root, text="Reset Budget", command=self.reset_budget).grid(row=5, column=0)
        tk.Button(self.root, text="Add Expense", command=self.add_expense).grid(row=4, column=1)
        tk.Button(self.root, text="Save State", command=self.save_data).grid(row=6, column=0)
        tk.Button(self.root, text="Show Expenses", command=self.show_expenses).grid(row=5, column=1)

        # Remaining Budget
        self.remaining_label = tk.Label(self.root, text="")
        self.remaining_label.grid(row=7, column=0, columnspan=2)
        self.update_remaining_budget()

        # Configure row and column weights for scalability
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_rowconfigure(6, weight=1)
        self.root.grid_rowconfigure(7, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Adjust widgets to fill the grid cell
        self.budget_entry.grid(sticky="ew")
        self.expense_name_entry.grid(sticky="ew")
        self.expense_amount_entry.grid(sticky="ew")
        self.remaining_label.grid(sticky="ew")

    def set_budget(self):
        try:
            self.budget = float(self.budget_entry.get())
            self.update_remaining_budget()
        except ValueError:
            messagebox.showerror("Error", "Invalid budget value")

    def reset_budget(self):
        try:
            new_budget = float(self.budget_entry.get())
            budget_change = new_budget - self.budget
            self.budget = new_budget

            # Record the budget change as a special expense entry
            self.expenses.append({
                "name": "Budget Adjustment",
                "amount": budget_change,
                "frequency": "Adjustment"
            })

            self.update_remaining_budget()
            self.save_data()
        except ValueError:
            messagebox.showerror("Error", "Invalid budget value")

    def add_expense(self):
        expense_name = self.expense_name_entry.get()
        expense_amount_entry = self.expense_amount_entry.get()
        frequency = self.frequency_var.get()

        # Check if the expense name is empty
        if not expense_name.strip():
            messagebox.showerror("Error", "Please enter an expense name")
            return

        # Validate and convert the expense amount
        try:
            expense_amount = float(expense_amount_entry)
            if expense_amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount. Please enter a valid number.")
            return

        # Add the expense and update the budget
        self.expenses.append({
            "name": expense_name,
            "amount": expense_amount,
            "frequency": frequency
        })

        # Deduct the expense amount from the budget for 'One Time' expenses
        if frequency == "One Time":
            self.budget -= expense_amount

        self.update_remaining_budget()
        self.save_data()

    def update_remaining_budget(self):
        self.remaining_label.config(text=f"Remaining Budget: {self.budget}")

    def show_expenses(self):
        new_window = Toplevel(self.root)
        new_window.title("Expenses")

        tree = ttk.Treeview(new_window, columns=("Name", "Amount", "Frequency"), show='headings')
        tree.heading("Name", text="Name")
        tree.heading("Amount", text="Amount")
        tree.heading("Frequency", text="Frequency")

        for expense in self.expenses:
            if expense["name"] == "Budget Adjustment":
                # Use the BudgetAdjustment style for budget adjustments
                tree.insert('', tk.END, values=(expense["name"], expense["amount"], expense["frequency"]),
                            tags=("budget_adjustment",))
            else:
                # Use the NegativeExpense style for negative expenses (deductions)
                color = "negative_expense" if expense["amount"] else ""
                tree.insert('', tk.END, values=(expense["name"], expense["amount"], expense["frequency"]),
                            tags=(color,))

        tree.tag_configure("budget_adjustment", foreground="green")
        tree.tag_configure("negative_expense", foreground="red")

        tree.pack(expand=True, fill='both')

    def save_data(self):
        data = {
            "budget": self.budget,
            "expenses": self.expenses
        }
        with open("expense_tracker_data.json", "w") as file:
            json.dump(data, file)

    def load_data(self):
        try:
            with open("expense_tracker_data.json", "r") as file:
                data = json.load(file)
                self.budget = data.get("budget", 0.0)
                self.expenses = data.get("expenses", [])
                print(self.expenses)
        except (FileNotFoundError, json.JSONDecodeError):
            self.budget = 0.0
            self.expenses = []


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

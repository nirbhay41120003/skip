import json
from datetime import datetime

class Transaction:
    def __init__(self, transaction_id, customer_name, amount, transaction_type, description, created_at):
        self.id = transaction_id
        self.customer_name = customer_name
        self.amount = amount
        self.type = transaction_type
        self.description = description
        self.created_at = created_at

class Customer:
    def __init__(self, customer_id, name, balance=0):
        self.id = customer_id
        self.name = name
        self.balance = balance

class LedgerManager:
    def __init__(self):
        self.transactions = []
        self.customers = []
        self.next_transaction_id = 1
        self.next_customer_id = 1
    
    def add_transaction(self, customer_name, amount, transaction_type, description, created_at=None):
        # Find or create customer
        customer = next((c for c in self.customers if c.name == customer_name), None)
        if not customer:
            customer = Customer(self.next_customer_id, customer_name)
            self.customers.append(customer)
            self.next_customer_id += 1
        
        # Adjust amount based on type
        if transaction_type in ['debit', 'expense']:
            amount = -abs(amount)
        else:
            amount = abs(amount)
        
        # Update customer balance
        customer.balance += amount
        
        # Create transaction
        transaction = Transaction(
            self.next_transaction_id,
            customer_name,
            amount,
            transaction_type,
            description,
            created_at or datetime.now().isoformat()
        )
        self.transactions.append(transaction)
        self.next_transaction_id += 1
        return transaction
    
    def calculate_total_balance(self):
        return sum(t.amount for t in self.transactions)
    
    def get_filtered_transactions(self, transaction_type=None, start_date=None, end_date=None, customer_name=None):
        filtered = self.transactions.copy()
        
        if transaction_type and transaction_type != "All":
            filtered = [t for t in filtered if t.type == transaction_type.lower()]
        
        if start_date:
            filtered = [t for t in filtered if datetime.fromisoformat(t.created_at).date() >= start_date]
        
        if end_date:
            filtered = [t for t in filtered if datetime.fromisoformat(t.created_at).date() <= end_date]
        
        if customer_name:
            filtered = [t for t in filtered if customer_name.lower() in t.customer_name.lower()]
        
        return filtered
    
    def get_top_customers(self, limit=5):
        customer_totals = {}
        for t in self.transactions:
            if t.type in ['sale', 'credit']:
                customer_totals[t.customer_name] = customer_totals.get(t.customer_name, 0) + t.amount
        
        return sorted(
            [{"name": k, "amount": v} for k, v in customer_totals.items()],
            key=lambda x: x["amount"],
            reverse=True
        )[:limit]
    
    def generate_business_insights(self):
        total_balance = self.calculate_total_balance()
        sales = sum(t.amount for t in self.transactions if t.type == 'sale')
        expenses = sum(abs(t.amount) for t in self.transactions if t.type == 'expense')
        credit = sum(t.amount for t in self.transactions if t.type == 'credit')
        debit = sum(abs(t.amount) for t in self.transactions if t.type == 'debit')
        
        return {
            "total_balance": total_balance,
            "total_sales": sales,
            "total_expenses": expenses,
            "total_credit": credit,
            "total_debit": debit,
            "net_profit": sales - expenses,
            "top_customers": self.get_top_customers()
        }
    
    def export_data(self, filename):
        data = {
            "transactions": [vars(t) for t in self.transactions],
            "customers": [vars(c) for c in self.customers],
            "next_ids": {
                "transaction": self.next_transaction_id,
                "customer": self.next_customer_id
            }
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_data(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.transactions = [Transaction(**t) for t in data["transactions"]]
        self.customers = [Customer(**c) for c in data["customers"]]
        self.next_transaction_id = data["next_ids"]["transaction"]
        self.next_customer_id = data["next_ids"]["customer"]
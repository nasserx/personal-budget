import json
import os


class BudgetManager:
    """Manages income, categories, and expenses data stored in data.json."""

    def __init__(self, data_file="core/data/data.json"):
        """Initialize BudgetManager with data file path."""
        self.data_file = data_file
        self.data = self._load()

    # Basic operations
    def _load(self):
        """Load data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        """Save data to JSON file."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    # Monthly income
    def set_monthly_income(self, value: float):
        """Set the monthly income value."""
        self.data["monthly_income"] = float(value)
        return self._save()

    def get_monthly_income(self) -> float:
        """Get the current monthly income."""
        return float(self.data.get("monthly_income", 0.0))

    # Categories
    def get_categories(self):
        """Return the list of categories."""
        return self.data.get("categories", [])

    def add_category(self, name: str, percentage: float):
        """Add a new category with a percentage of the income."""
        name = name.strip()
        if not name:
            raise ValueError("اسم الفئة مطلوب.")
        if percentage <= 0 or percentage > 100:
            raise ValueError("النسبة يجب أن تكون بين 0 و 100.")

        cats = self.data.setdefault("categories", [])
        for c in cats:
            if c["name"].strip() == name:
                raise ValueError("فئة بهذا الاسم موجودة مسبقاً.")

        total = sum(c["percentage"] for c in cats) + percentage
        if total > 100:
            raise ValueError(f"إجمالي النسب ({total:.1f}%) يتجاوز 100%. الرجاء تعديل النسب.")

        cats.append({"name": name, "percentage": float(percentage), "sub": []})
        return self._save()

    def delete_category(self, name: str):
        """Delete a category by its name."""
        cats = self.data.get("categories", [])
        new_cats = [c for c in cats if c["name"] != name]
        self.data["categories"] = new_cats
        return self._save()

    def update_category(self, old_name: str, new_name: str, new_percentage: float):
        """Update category name or percentage with validation."""
        cats = self.data.get("categories", [])
        found = False
        total_except_old = sum(c["percentage"] for c in cats if c["name"] != old_name)
        if total_except_old + new_percentage > 100:
            raise ValueError(f"إجمالي النسب ({total_except_old + new_percentage:.1f}%) يتجاوز 100٪.")

        for c in cats:
            if c["name"] == old_name:
                c["name"] = new_name.strip() or old_name
                c["percentage"] = float(new_percentage)
                found = True
                break

        if not found:
            raise ValueError("الفئة المراد تعديلها غير موجودة.")

        self.data["categories"] = cats
        return self._save()

    # Expenses
    def add_expense(self, category_name: str, expense_name: str, amount: float):
        """Add a new expense to a category."""
        if amount <= 0:
            raise ValueError("المبلغ يجب أن يكون أكبر من الصفر.")
        for c in self.data.get("categories", []):
            if c["name"] == category_name:
                c["sub"].append({"name": expense_name.strip(), "amount": float(amount)})
                return self._save()
        raise ValueError("الفئة غير موجودة.")

    def update_expense(self, category_name: str, old_expense: str, new_name: str, new_amount: float):
        """Update an existing expense within a category."""
        for c in self.data.get("categories", []):
            if c["name"] == category_name:
                for s in c["sub"]:
                    if s["name"] == old_expense:
                        s["name"] = new_name.strip() or old_expense
                        s["amount"] = float(new_amount)
                        return self._save()
        raise ValueError("المصروف غير موجود.")

    def delete_expense(self, category_name: str, expense_name: str):
        """Delete an expense from a category."""
        for c in self.data.get("categories", []):
            if c["name"] == category_name:
                c["sub"] = [s for s in c["sub"] if s["name"] != expense_name]
                return self._save()
        raise ValueError("المصروف غير موجود.")

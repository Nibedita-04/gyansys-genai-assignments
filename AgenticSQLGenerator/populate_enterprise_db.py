import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "database/enterprise.db"
random.seed(42)

def random_date(start_year=2022):
    start = datetime(start_year, 1, 1)
    end = datetime(2024, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

# Populate the database with dummy data for testing
def populate_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # REGIONS
    regions = [
        ("North", "India"),
        ("South", "India"),
        ("West", "India"),
        ("Europe", "Germany"),
        ("APAC", "Singapore"),
    ]
    cursor.executemany("INSERT INTO regions (region_name, country) VALUES (?, ?)", regions)

    # CUSTOMERS
    cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune"]
    customers = []
    for i in range(150):
        customers.append((
            f"Customer_{i}",
            f"customer{i}@mail.com",
            f"+91-90000{i:04}",
            random.choice(cities),
            "State_" + str(random.randint(1, 5)),
            "India",
            random.randint(1, 5),
            random_date().strftime("%Y-%m-%d")
        ))
    cursor.executemany("""
        INSERT INTO customers 
        (name, email, phone, city, state, country, region_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, customers)

    # CATEGORIES
    categories = ["Personal Care", "Home Care", "Foods", "Beverages",
                  "Health", "Beauty", "Cleaning", "Laundry"]
    cursor.executemany(
        "INSERT INTO categories (category_name) VALUES (?)",
        [(c,) for c in categories]
    )

    # SUPPLIERS
    suppliers = [(f"Supplier_{i}", "India") for i in range(20)]
    cursor.executemany(
        "INSERT INTO suppliers (supplier_name, country) VALUES (?, ?)",
        suppliers
    )

    # PRODUCTS
    products = []
    for i in range(100):
        price = round(random.uniform(50, 500), 2)
        cost = round(price * random.uniform(0.5, 0.8), 2)
        products.append((
            f"Product_{i}",
            random.randint(1, 8),
            random.randint(1, 20),
            price,
            cost,
            random_date(2021).strftime("%Y-%m-%d")
        ))
    cursor.executemany("""
        INSERT INTO products
        (product_name, category_id, supplier_id, price, cost, launch_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, products)

    # WAREHOUSES
    warehouses = [(f"Warehouse_{i}", random.choice(cities), "India") for i in range(10)]
    cursor.executemany(
        "INSERT INTO warehouses (warehouse_name, city, country) VALUES (?, ?, ?)",
        warehouses
    )

    # INVENTORY
    inventory = []
    for product_id in range(1, 101):
        for warehouse_id in range(1, 11):
            inventory.append((
                product_id,
                warehouse_id,
                random.randint(0, 1000),
                random_date().strftime("%Y-%m-%d")
            ))
    cursor.executemany("""
        INSERT INTO inventory
        (product_id, warehouse_id, stock_quantity, last_updated)
        VALUES (?, ?, ?, ?)
    """, inventory)

    # ORDERS
    orders = []
    for i in range(200):
        orders.append((
            random.randint(1, 150),
            random_date().strftime("%Y-%m-%d"),
            0,
            random.choice(["Completed", "Pending", "Cancelled"])
        ))
    cursor.executemany("""
        INSERT INTO orders
        (customer_id, order_date, total_amount, status)
        VALUES (?, ?, ?, ?)
    """, orders)

    # ORDER ITEMS
    order_items = []
    for order_id in range(1, 201):
        for _ in range(random.randint(1, 3)):
            product_id = random.randint(1, 100)
            quantity = random.randint(1, 10)
            unit_price = cursor.execute(
                "SELECT price FROM products WHERE id = ?",
                (product_id,)
            ).fetchone()[0]

            order_items.append((
                order_id,
                product_id,
                quantity,
                unit_price
            ))

            # Update total_amount
            cursor.execute("""
                UPDATE orders
                SET total_amount = total_amount + ?
                WHERE id = ?
            """, (quantity * unit_price, order_id))

    cursor.executemany("""
        INSERT INTO order_items
        (order_id, product_id, quantity, unit_price)
        VALUES (?, ?, ?, ?)
    """, order_items)

    # EMPLOYEES
    departments = ["Sales", "Marketing", "Operations", "HR", "Finance"]
    employees = []
    for i in range(50):
        employees.append((
            f"Employee_{i}",
            random.choice(departments),
            random.randint(1, 5),
            random_date(2018).strftime("%Y-%m-%d"),
            random.randint(30000, 120000)
        ))
    cursor.executemany("""
        INSERT INTO employees
        (employee_name, department, region_id, hire_date, salary)
        VALUES (?, ?, ?, ?, ?)
    """, employees)

    conn.commit()
    conn.close()
    print("Database populated successfully!")


if __name__ == "__main__":
    populate_database()
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS warehouses;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS employees;

CREATE TABLE regions (
    id INTEGER PRIMARY KEY,
    region_name TEXT,
    country TEXT
);

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    region_id INTEGER,
    created_at TEXT,
    FOREIGN KEY(region_id) REFERENCES regions(id)
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    category_name TEXT
);

CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY,
    supplier_name TEXT,
    country TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    product_name TEXT,
    category_id INTEGER,
    supplier_id INTEGER,
    price REAL,
    cost REAL,
    launch_date TEXT,
    FOREIGN KEY(category_id) REFERENCES categories(id),
    FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    total_amount REAL,
    status TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE warehouses (
    id INTEGER PRIMARY KEY,
    warehouse_name TEXT,
    city TEXT,
    country TEXT
);

CREATE TABLE inventory (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    warehouse_id INTEGER,
    stock_quantity INTEGER,
    last_updated TEXT,
    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(warehouse_id) REFERENCES warehouses(id)
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    employee_name TEXT,
    department TEXT,
    region_id INTEGER,
    hire_date TEXT,
    salary REAL,
    FOREIGN KEY(region_id) REFERENCES regions(id)
);
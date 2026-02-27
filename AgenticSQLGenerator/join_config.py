JOIN_GRAPH = {
    # Direct joins
    ("orders", "customers"): [
        "orders.customer_id = customers.customer_id"
    ],

    ("order_items", "orders"): [
        "order_items.order_id = orders.order_id"
    ],

    ("order_items", "products"): [
        "order_items.product_id = products.product_id"
    ],

    # Indirect joins (bridge tables)
    ("products", "orders"): {
        "bridge": "order_items",
        "path": [
            "products.product_id = order_items.product_id",
            "order_items.order_id = orders.order_id"
        ]
    }
}
1) Users
    - id
    - password
    - username
    - is__active
    - created_at
    - last_login

2) Roles
    - id
    - name (admin, operations, support)

3) role_permissions
    - role_id
    - pernission_id

4) user_roles
    - user_id
    - role_id

5) Products
    - id
    - name
    - sku
    - price
    - is_active
    - created_at

6) Orders
    - id
    - customer_email
    - status (pending, paid, shipped, refunded)
    - total_amount
    - created_at
    - updated_at

7) Order_items
    - id
    - order_id
    - product_id
    - quantity
    - price_at_purchase

8) Inventory
    - product_id
    - quantity_available
    - quantity_reserved 

9) Audit Logs
    - id
    - acted_user_id
    - action (shipped, returned)
    - entity_type (order)
    - entity_id
    - before_state
    - after_state
    - bulk_operation_id
    - created_at


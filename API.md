endpoint: 
 - POST api/orders/bulk-ship

The backend must check and validate all requests swnt by the front end and return a list of successes and failures, and the reason why there is a failure.

Request Body
    {
    "orderIds": [101, 102, 103, 104]
    }

    Validation rules:

    - orderIds must be a non-empty array

    - IDs must be unique

    - Max length (example): 100 orders

    - If invalid → 400

Backend Processing Logic (per order)

For each order ID:

    - Load order

    - If order not found → fail

    - If status ≠ paid → fail

    - If already shipped or refunded → fail

    - Check inventory for all order items

    - If any item lacks inventory → fail

    - If all checks pass:

    - Deduct / reserve inventory

    - Update order status → shipped

    - Write audit log entry

    - Each order is processed independently.


Response style: 

{
  "summary": {
    "total": 4,
    "shipped": 2,
    "failed": 2
  },
  "results": {
    "success": [
      { "orderId": 101 },
      { "orderId": 102 }
    ],
    "failed": [
      {
        "orderId": 103,
        "reason": "Order already shipped"
      },
      {
        "orderId": 104,
        "reason": "Order not paid"
      }
    ]
  }
}

Status codes: 
    - 200 -> processed
    - 400 -> invalid inputs
    - 401 -> unauthenticated
    - 403 -> forbidden
    - 500 -> unexpected server error
partial failure is not an error

Auditing:
    for successful shipments: 
        - Actor user ID
        - order ID
        - old status
        - new status
        - bulk operation ID
        - timestamp

Frontend can only:
    - send orders
    - show confrimtation of shipment
    - update UI to show successful orders only
    - display failures with reasoning
    - show partial success

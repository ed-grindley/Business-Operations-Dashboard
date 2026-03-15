Order states: 
    - pending
    - paid
    - shipped
    - returned

Valid Transactions: 
    - pending -> paid
    - paid -> shipped
    - paid -> failed
    - shipped -> refunded

Bulk shipping musts: 
    - order must be paid
    - there must be inventory
    - order cannot be already shipped/refunded



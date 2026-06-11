"""Database Schema Documentation - CHUNK 2

# Database Architecture

## Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INVENTORY SYSTEM                             │
└─────────────────────────────────────────────────────────────────────┘


                            ┌──────────────┐
                            │   COMPANY    │
                            ├──────────────┤
                            │ id (PK)      │
                            │ name         │
                            └──────┬───────┘
                                   │
                                   │ 1:N
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
              ┌─────────────┐            ┌──────────────┐
              │   MEDICINE  │            │   SHELF      │
              ├─────────────┤            ├──────────────┤
              │ id (PK)     │            │ id (PK)      │
              │ name        │            │ shelf_name   │
              │ salt        │            └──────┬───────┘
              │ company_id  │ (FK)               │
              │ location_id │ (FK) ──┐          │ 1:N
              │ stock       │        │          │
              │ min_stock   │        │      ┌───┴──────┐
              │ purchase_pr │        │      │   BOX    │
              │ selling_pr  │        │      ├──────────┤
              │ expiry_date │        │      │ id (PK)  │
              │ barcode     │        │      │ shelf_id │
              └─────────────┘        │      │ box_name │
                    │                │      └──────────┘
                    │                │
                    │ N:N (via      │
                    │ junction)     │
                    │                └───> (Location)
                    │
         ┌──────────┴─────────────┐
         │                        │
    ┌─────────────────┐  ┌─────────────────────┐
    │ALTERNATE        │  │    MEDICINE (Alt)   │
    │MEDICINE         │  │                     │
    ├─────────────────┤  └─────────────────────┘
    │ id (PK)         │
    │ medicine_id(FK) │
    │ alt_med_id (FK) │
    │ salt_match_pct  │
    │ notes           │
    └─────────────────┘


                    ┌──────────────────────────────────┐
                    │      BILLING SYSTEM              │
                    └──────────────────────────────────┘

                         ┌───────────┐
                         │   BILL    │
                         ├───────────┤
                         │ id (PK)   │
                         │ bill_no   │
                         │ date      │
                         │ total     │
                         │ user_id   │ (FK) ──> User
                         │ status    │
                         └─────┬─────┘
                               │
                               │ 1:N
                               │
                         ┌─────────────┐
                         │  BILL_ITEM  │
                         ├─────────────┤
                         │ id (PK)     │
                         │ bill_id(FK) │
                         │ medicine_id │ (FK) ──> Medicine
                         │ quantity    │
                         │ price       │
                         │ subtotal    │
                         └─────────────┘


                    ┌──────────────────────────────────┐
                    │      AUDIT LOGGING               │
                    └──────────────────────────────────┘

                       ┌──────────────┐
                       │  AUDIT_LOG   │
                       ├──────────────┤
                       │ id (PK)      │
                       │ user_id (FK) │──> User
                       │ action       │
                       │ medicine_id  │ (FK) ──> Medicine
                       │ old_value    │
                       │ new_value    │
                       │ description  │
                       │ ip_address   │
                       │ timestamp    │
                       └──────────────┘
```

---

## Tables Detailed Schema

### 1. COMPANY
Stores pharmaceutical manufacturers.

| Column | Type | Constraint | Purpose |
|--------|------|-----------|----------|
| id | BIGINT | PK, AUTO | Unique identifier |
| name | VARCHAR(255) | UNIQUE, NOT NULL | Company name (e.g., Cipla) |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- `INDEX(name)` - Fast company name searches

**Example Data:**
```
Cipla
Dr. Reddy's
Lupin
Sun Pharma
```

---

### 2. SHELF
Top-level storage organization.

| Column | Type | Constraint | Purpose |
|--------|------|-----------|----------|
| id | BIGINT | PK, AUTO | Unique identifier |
| shelf_name | VARCHAR(10) | UNIQUE, NOT NULL | Shelf code (A, B, C) |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- `INDEX(shelf_name)` - Fast shelf lookups

**Example Data:**
```
A
B
C
D
```

---

### 3. BOX
Second-level storage organization within shelves.

| Column | Type | Constraint | Purpose |
|--------|------|-----------|----------|
| id | BIGINT | PK, AUTO | Unique identifier |
| shelf_id | BIGINT | FK(SHELF), NOT NULL | Parent shelf reference |
| box_name | VARCHAR(10) | NOT NULL | Box code within shelf (A1, A2) |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Constraints:**
- `UNIQUE(shelf_id, box_name)` - Unique boxes per shelf

**Indexes:**
- `INDEX(shelf_id, box_name)` - Fast location lookups

**Example Data:**
```
Shelf A > A1
Shelf A > A2
Shelf B > B1
Shelf B > B2
```

**Location Code:** A1 means Shelf A, Box 1

---

### 4. MEDICINE
Core inventory table - stores all medicine information.

| Column | Type | Constraint | Purpose |
|--------|------|-----------|----------|
| id | BIGINT | PK, AUTO | Unique identifier |
| medicine_name | VARCHAR(255) | NOT NULL | Medicine name (Dolo 650) |
| company_id | BIGINT | FK(COMPANY), NOT NULL | Manufacturer |
| salt_composition | VARCHAR(500) | NOT NULL | Active ingredient (Paracetamol 650mg) |
| location_id | BIGINT | FK(BOX), NOT NULL | Storage location (Shelf > Box) |
| stock_quantity | INT | NOT NULL, DEFAULT 0 | Current stock |
| minimum_stock | INT | NOT NULL, DEFAULT 10 | Low stock alert threshold |
| purchase_price | DECIMAL(10,2) | NOT NULL | Cost per unit |
| selling_price | DECIMAL(10,2) | NOT NULL | Sale price per unit |
| expiry_date | DATE | NOT NULL | Medicine expiry date |
| barcode | VARCHAR(100) | UNIQUE, NULL | Barcode for quick search |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Constraints:**
- `UNIQUE(medicine_name, company_id, expiry_date)` - Avoid duplicates
- `CHECK(stock_quantity >= 0)` - Stock cannot be negative
- `CHECK(minimum_stock >= 0)` - Minimum must be non-negative

**Indexes:**
- `INDEX(medicine_name)` - Medicine name search
- `INDEX(salt_composition)` - Salt-based search
- `INDEX(company_id)` - Company filter
- `INDEX(barcode)` - Barcode lookup
- `INDEX(expiry_date)` - Expiry alerts
- `INDEX(stock_quantity)` - Low stock queries

**Example Data:**
```
Medicine: Dolo 650
Company: Cipla
Salt: Paracetamol 650mg
Location: A2
Stock: 100
Min Stock: 20
Purchase: ₹2.50
Selling: ₹5.00
Profit Margin: 100%
Expiry: 2026-12-31
```

---

### 5. ALTERNATE_MEDICINE
Links medicines with same/similar salt composition.

| Column | Type | Constraint | Purpose |
|--------|------|-----------|----------|
| id | BIGINT | PK, AUTO | Unique identifier |
| medicine_id | BIGINT | FK(MEDICINE), NOT NULL | Original medicine |
| alternate_medicine_id | BIGINT | FK(MEDICINE), NOT NULL | Substitute medicine |
| salt_match_percentage | INT | NOT NULL, DEFAULT 100 | Salt match % (0-100) |
| notes | TEXT | NULLABLE | Additional info |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Constraints:**
- `UNIQUE(medicine_id, alternate_medicine_id)` - No duplicate links
- `CHECK(salt_match_percentage BETWEEN 0 AND 100)` - Valid percentage

**Indexes:**
- `INDEX(medicine_id)` - Find alternatives for medicine
- `INDEX(alternate_medicine_id)` - Reverse lookup

**Example Data:**
```
Original: Dolo 650
Alternatives:
  - Paracip 650 (100% salt match)
  - Crocin Advance (95% salt match)
  - Acetaminophen 650 (85% salt match)
```

---

### 6. BILL
Customer transaction/invoice record.

| Column | Type | Constraint | Purpose |
|--------|------|-----------|----------|
| id | BIGINT | PK, AUTO | Unique identifier |
| bill_number | VARCHAR(50) | UNIQUE, NOT NULL | Unique bill ID (BILL-2024-001) |
| date | TIMESTAMP | NOT NULL, AUTO NOW | Bill creation time |
| total_amount | DECIMAL(12,2) | NOT NULL, DEFAULT 0 | Total bill value |
| created_by_id | BIGINT | FK(AUTH_USER), NOT NULL | Staff member who created |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending/finalized/cancelled |
| created_at | TIMESTAMP | NOT NULL | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

**Indexes:**
- `INDEX(bill_number)` - Bill lookup
- `INDEX(date)` - Date-based reports
- `INDEX(status)` - Status filtering
- `INDEX(created_by_id, date)` - User's bills

**Example Data:**
```
Bill Number: BILL-2024-001
Date: 2024-06-11 14:30:00
Total: ₹500.00
Created By: pharmacist1
Status: finalized
```

---

### 7. BILL_ITEM
Individual line items in a bill.

| Column | Type | Constraint | Purpose |
|--------|------|-----------|----------|
| id | BIGINT | PK, AUTO | Unique identifier |
| bill_id | BIGINT | FK(BILL), NOT NULL | Parent bill |
| medicine_id | BIGINT | FK(MEDICINE), NOT NULL | Medicine sold |
| quantity | INT | NOT NULL | Units sold |
| price | DECIMAL(10,2) | NOT NULL | Unit price at sale |
| subtotal | DECIMAL(12,2) | NOT NULL | quantity × price |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Constraints:**
- `CHECK(quantity > 0)` - Must sell at least 1
- `CHECK(price >= 0)` - Price non-negative

**Indexes:**
- `INDEX(bill_id)` - Get bill items
- `INDEX(medicine_id)` - Track medicine sales

**Example Data:**
```
Bill: BILL-2024-001
  - Dolo 650: 2 × ₹5.00 = ₹10.00
  - Aspirin 500: 1 × ₹3.00 = ₹3.00
  - Cough Syrup: 1 × ₹20.00 = ₹20.00
Total: ₹33.00
```

---

### 8. AUDIT_LOG
Complete audit trail for all changes.

| Column | Type | Constraint | Purpose |
|--------|------|-----------|----------|
| id | BIGINT | PK, AUTO | Unique identifier |
| user_id | BIGINT | FK(AUTH_USER), NULL | User who made change |
| action | VARCHAR(50) | NOT NULL | Action type (stock_added, etc) |
| medicine_id | BIGINT | FK(MEDICINE), NULL | Affected medicine |
| old_value | TEXT | NULLABLE | Previous value (JSON) |
| new_value | TEXT | NULLABLE | New value (JSON) |
| description | TEXT | NULLABLE | Human-readable description |
| ip_address | VARCHAR(45) | NULLABLE | User IP address |
| created_at | TIMESTAMP | NOT NULL | Action timestamp |
| updated_at | TIMESTAMP | NOT NULL | Record update time |

**Actions Tracked:**
- stock_added, stock_removed
- medicine_created, medicine_updated, medicine_deleted
- bill_created, bill_finalized, bill_cancelled
- alternate_added
- price_changed, expiry_updated

**Indexes:**
- `INDEX(user_id, created_at)` - User's activities
- `INDEX(action, created_at)` - Action reports
- `INDEX(medicine_id)` - Medicine history
- `INDEX(created_at)` - Timeline queries

**Example Data:**
```json
{
  "action": "stock_added",
  "medicine": "Dolo 650",
  "old_value": {"stock": 100},
  "new_value": {"stock": 150},
  "description": "Stock added: 50 units",
  "user": "pharmacist1",
  "timestamp": "2024-06-11 14:30:00"
}
```

---

## Key Features

### ✅ Stock Tracking
- Real-time stock quantity
- Low stock alerts (below minimum_stock)
- Automatic deduction on bill finalization

### ✅ Medicine Location
- Hierarchical: Shelf → Box
- Easy physical location finding
- Example: "A2" = Shelf A, Box 2

### ✅ Search Capabilities
- By medicine name
- By salt composition
- By company
- By barcode
- By location

### ✅ Alternate Medicines
- Same salt, different company
- Percentage-based matching
- Suggests alternatives when out of stock

### ✅ Billing
- Transaction tracking
- Status management (pending → finalized)
- Automatic subtotal calculation
- User accountability

### ✅ Audit Trail
- All changes logged
- Before/after values
- User tracking
- IP logging
- Timestamp tracking

---

## Relationships Summary

```
Company ←1:N→ Medicine

Shelf ←1:N→ Box ←1:N→ Medicine

Medicine ←N:N→ AlternateMedicine (via junction)

User ←1:N→ Bill ←1:N→ BillItem →N:1← Medicine

User ←1:N→ AuditLog →N:1← Medicine
```

---

## Future Extensions

Architecture supports:
- Multi-store expansion (add store_id)
- Supplier management (add Supplier table)
- Purchase orders (add PurchaseOrder table)
- Inventory adjustments (log in AuditLog)
- Stock transfers (log in AuditLog)
- Barcode scanning (already field ready)

---

## Performance Considerations

### Indexing Strategy
- ✅ Frequent search fields indexed
- ✅ Foreign keys indexed for joins
- ✅ Date fields indexed for range queries
- ✅ Composite indexes for common filters

### Query Optimization
- Stock queries filter by location
- Audit logs partition by date ranges
- Bills retrieved with pagination
- Expiry alerts use indexed date field

### Caching Opportunities
- Company list (rarely changes)
- Shelf/Box structure
- Medicine with low stock
- Recent bills (Redis cache)

---

**Status: ✅ DATABASE SCHEMA READY FOR MIGRATION**
"""

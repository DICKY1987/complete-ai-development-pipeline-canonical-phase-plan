---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-EXAMPLE_SAGA_PATTERN-068
---

# Example 05: SAGA Pattern - Distributed Transactions

**Pattern**: SAGA with compensation and rollback  
**Complexity**: Advanced  
**Estimated Duration**: 8-12 minutes (success), +3-5 min (rollback)  
**Tool**: Aider with SAGA orchestration

---

## Purpose

This example demonstrates **the SAGA pattern for distributed transactions**. Use this pattern when you need to:

- Coordinate operations across multiple services
- Ensure consistency without distributed locks
- Implement reversible workflows
- Handle partial failures gracefully
- Maintain system integrity during errors

---

## What This Example Demonstrates

✅ **SAGA Pattern**
- Forward transaction flow
- Compensation (rollback) logic
- Orchestration vs choreography

✅ **Compensation Actions**
- Automatic rollback on failure
- Reverse-order execution
- Retry logic for compensations

✅ **Distributed Consistency**
- Eventually consistent operations
- Idempotent implementations
- Transaction isolation

---

## SAGA Pattern Explained

### What is SAGA?

**SAGA** = **S**equence of **A**ctions with **G**uaranteed **A**tomicity

Instead of a single ACID transaction across services, SAGA breaks it into:
1. **Local transactions** (each service commits independently)
2. **Compensation actions** (undo operations if later steps fail)

---

### Example Scenario: User Registration with Payment

**Happy Path** (all steps succeed):
```
Step 1: Create User Account    [UserService.create_account()]
  ↓ SUCCESS
Step 2: Process Payment         [PaymentService.charge()]
  ↓ SUCCESS
Step 3: Send Confirmation       [NotificationService.send()]
  ↓ SUCCESS
✓ SAGA Complete
```

**Failure Path** (payment fails):
```
Step 1: Create User Account    [UserService.create_account()]
  ↓ SUCCESS (user_id=123)
Step 2: Process Payment         [PaymentService.charge()]
  ✗ FAILED (insufficient funds)
  
SAGA ROLLBACK TRIGGERED:
  
Compensation 1: Refund (skip - payment never succeeded)
  ↓
Compensation 2: Delete Account  [UserService.delete_account(user_id=123)]
  ↓ SUCCESS
✓ SAGA Rolled Back - System Consistent
```

---

## Architecture

### Forward Flow (Success Path)

```
┌─────────────────┐
│ UserService     │
│ create_account()│
└────────┬────────┘
         │ user_id=123
         ▼
┌─────────────────┐
│ PaymentService  │
│ charge(123)     │
└────────┬────────┘
         │ transaction_id=456
         ▼
┌─────────────────┐
│NotificationSvc  │
│ send(123, 456)  │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │SUCCESS │
    └────────┘
```

### Rollback Flow (Compensation)

```
         ✗ FAILURE
         │
         ▼
┌──────────────────┐
│ Rollback Manager │
└────────┬─────────┘
         │ Reverse Order
         ▼
┌─────────────────┐
│NotificationSvc  │
│ cancel(notif_id)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PaymentService  │
│ refund(txn_id)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ UserService     │
│ delete(user_id) │
└────────┬────────┘
         │
         ▼
  ┌──────────────┐
  │ ROLLED BACK  │
  └──────────────┘
```

---

## Step Configuration with Compensation

### Step with Compensation Action

```json
{
  "id": "step-02-payment-service",
  "description": "Process payment",
  
  "tasks": [
    "Add PaymentService.charge() method",
    "Add PaymentService.refund() compensation"
  ],
  
  "compensation": {
    "enabled": true,
    "action": "refund",  // Method to call for rollback
    
    "parameters": {
      "transaction_id": "${step_output.transaction_id}",
      "amount": "${step_output.amount}"
    },
    
    "timeout": 60,  // Compensation timeout
    "retries": 5    // Retry failed compensations
  }
}
```

**Key concepts**:
- Each step that modifies state needs a compensation
- Compensation receives output from original step
- Compensations are retried if they fail
- Compensations execute in reverse order

---

## Execution Scenarios

### Scenario 1: Complete Success

```
$ python scripts/run_workstream.py --ws-id ws-example-05-saga-pattern

[INFO] Starting SAGA: ws-example-05-saga-pattern
[INFO] SAGA Mode: orchestration

=== Forward Transaction ===

[INFO] Step 1/4: Create user service
✓ UserService created
  Output: {user_id: 123}

[INFO] Step 2/4: Create payment service  
✓ PaymentService created
  Output: {transaction_id: 456, amount: 99.99}

[INFO] Step 3/4: Create notification service
✓ NotificationService created
  Output: {notification_id: 789}

[INFO] Step 4/4: Create SAGA coordinator
✓ SagaCoordinator created

=== SAGA Complete ===
✓ All steps succeeded
✓ No compensation needed
✓ Transaction committed

Duration: 10m 23s
Compensations: 0
```

---

### Scenario 2: Failure with Rollback

```
$ python scripts/run_workstream.py --ws-id ws-example-05-saga-pattern

[INFO] Starting SAGA: ws-example-05-saga-pattern

=== Forward Transaction ===

[INFO] Step 1/4: Create user service
✓ UserService created
  Output: {user_id: 123}
  Compensation registered: delete_account(123)

[INFO] Step 2/4: Create payment service
✓ PaymentService created
  Output: {transaction_id: 456, amount: 99.99}
  Compensation registered: refund(456, 99.99)

[INFO] Step 3/4: Create notification service
✗ NotificationService FAILED
  Error: SMTP connection timeout
  
=== SAGA Rollback Initiated ===

[WARN] Rolling back 2 completed steps...
[INFO] Rollback order: reverse (3 → 2 → 1)

[INFO] Compensation 2/2: Refund payment
  Calling: PaymentService.refund(456, 99.99)
✓ Refund successful
  Refund ID: REF-789

[INFO] Compensation 1/2: Delete user account
  Calling: UserService.delete_account(123)
✓ Account deleted

=== SAGA Rolled Back ===
✓ All compensations succeeded
✓ System returned to consistent state

Duration: 12m 45s (including rollback)
Compensations: 2/2 successful
Final State: ROLLED_BACK
```

---

### Scenario 3: Compensation Failure

```
[INFO] Starting rollback...

[INFO] Compensation 2/2: Refund payment
✗ Refund FAILED (attempt 1/5)
  Error: Payment gateway timeout
[WARN] Retrying in 2s...
✗ Refund FAILED (attempt 2/5)
[WARN] Retrying in 4s...
✓ Refund succeeded (attempt 3/5)

[INFO] Compensation 1/2: Delete user account
✓ Account deleted

=== SAGA Rolled Back ===
✓ All compensations eventually succeeded
⚠  Compensation 1 required 3 retries

Duration: 15m 12s
Compensations: 2/2 successful (with retries)
```

---

### Scenario 4: Partial Rollback (Compensation Fails Permanently)

```
[INFO] Starting rollback...

[INFO] Compensation 2/2: Refund payment
✗ Refund FAILED (all 5 attempts exhausted)
  Error: Payment gateway permanently down
  
[ERROR] Compensation failed permanently!
[ERROR] Partial rollback - manual intervention required

=== SAGA Partially Rolled Back ===
✗ Compensation failed: refund(456, 99.99)
✓ Remaining compensations: 1/1 successful

[CRITICAL] Manual action required:
  - Transaction 456 could not be refunded
  - User account 123 has been deleted
  - Please refund $99.99 manually

Incident ID: INC-2023-11-22-001
Assigned to: ops@team.com
```

---

## Generated Code Examples

### examples/user_service.py

```python
"""User Service with Account Management."""

from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """User account."""
    user_id: int
    email: str
    created_at: datetime
    deleted: bool = False


class UserService:
    """User account management service."""
    
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.next_id = 1
    
    def create_account(self, email: str) -> Dict:
        """
        Create user account.
        
        Returns:
            Dict with user_id for compensation
        """
        user_id = self.next_id
        self.next_id += 1
        
        user = User(
            user_id=user_id,
            email=email,
            created_at=datetime.now()
        )
        
        self.users[user_id] = user
        
        print(f"✓ User account created: {user_id}")
        return {"user_id": user_id}
    
    def delete_account(self, user_id: int, reason: str = "user_request") -> None:
        """
        COMPENSATION: Delete user account.
        
        This is idempotent - safe to call multiple times.
        """
        if user_id not in self.users:
            print(f"⚠ User {user_id} not found (already deleted?)")
            return  # Idempotent - not an error
        
        user = self.users[user_id]
        user.deleted = True
        
        print(f"✓ User account deleted: {user_id} (reason: {reason})")
```

### examples/payment_service.py

```python
"""Payment Service with Charge and Refund."""

from typing import Dict
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class Transaction:
    """Payment transaction."""
    transaction_id: int
    user_id: int
    amount: float
    status: str  # "charged", "refunded", "failed"
    timestamp: datetime


class PaymentService:
    """Payment processing service."""
    
    def __init__(self):
        self.transactions: Dict[int, Transaction] = {}
        self.next_txn_id = 1
    
    def charge(self, user_id: int, amount: float) -> Dict:
        """
        Charge user account.
        
        Returns:
            Dict with transaction_id and amount for compensation
        """
        txn_id = self.next_txn_id
        self.next_txn_id += 1
        
        # Simulate payment processing
        txn = Transaction(
            transaction_id=txn_id,
            user_id=user_id,
            amount=amount,
            status="charged",
            timestamp=datetime.now()
        )
        
        self.transactions[txn_id] = txn
        
        print(f"✓ Payment charged: ${amount} (txn: {txn_id})")
        return {
            "transaction_id": txn_id,
            "amount": amount
        }
    
    def refund(
        self,
        transaction_id: int,
        amount: float,
        reason: str = "saga_rollback"
    ) -> None:
        """
        COMPENSATION: Refund payment.
        
        This is idempotent - safe to call multiple times.
        """
        if transaction_id not in self.transactions:
            print(f"⚠ Transaction {transaction_id} not found")
            return  # Idempotent
        
        txn = self.transactions[transaction_id]
        
        if txn.status == "refunded":
            print(f"⚠ Transaction {transaction_id} already refunded")
            return  # Idempotent
        
        txn.status = "refunded"
        
        print(f"✓ Payment refunded: ${amount} (txn: {transaction_id}, reason: {reason})")
```

### examples/saga_coordinator.py

```python
"""SAGA Coordinator for Orchestration."""

from typing import List, Callable, Dict, Optional
from dataclasses import dataclass


@dataclass
class CompensationAction:
    """Compensation action definition."""
    step_id: str
    action: Callable
    parameters: Dict


class SagaCoordinator:
    """Orchestrates SAGA transactions."""
    
    def __init__(self):
        self.compensations: List[CompensationAction] = []
        self.executed_steps: List[str] = []
    
    def execute_saga(
        self,
        steps: List[Callable],
        compensations: List[Optional[CompensationAction]]
    ) -> bool:
        """
        Execute SAGA with automatic rollback on failure.
        
        Returns:
            True if SAGA succeeded, False if rolled back
        """
        try:
            # Forward transaction
            for i, step in enumerate(steps):
                print(f"\n[Step {i+1}/{len(steps)}]")
                
                # Execute step
                result = step()
                self.executed_steps.append(f"step-{i+1}")
                
                # Register compensation if provided
                if compensations[i]:
                    self.compensations.append(compensations[i])
                    print(f"  Compensation registered: {compensations[i].action.__name__}")
            
            print("\n✓ SAGA Complete - All steps succeeded")
            return True
            
        except Exception as e:
            print(f"\n✗ SAGA Failed: {e}")
            print("Initiating rollback...")
            
            self.rollback()
            return False
    
    def rollback(self) -> None:
        """Execute compensations in reverse order."""
        if not self.compensations:
            print("No compensations to execute")
            return
        
        print(f"\nRolling back {len(self.compensations)} step(s)...")
        
        # Execute in reverse order
        for comp in reversed(self.compensations):
            try:
                print(f"  Compensating: {comp.action.__name__}")
                comp.action(**comp.parameters)
                print(f"  ✓ Compensation succeeded")
                
            except Exception as e:
                print(f"  ✗ Compensation failed: {e}")
                # In production, this would trigger alerts
        
        print("\n✓ Rollback complete")
```

---

## Best Practices

### ✅ SAGA Design Principles

1. **Idempotency**
   - All operations (forward and compensation) must be idempotent
   - Safe to retry on failure
   - No side effects on duplicate calls

2. **Compensatable**
   - Every state change must have a compensation
   - Compensations must not fail (or retry indefinitely)
   - Partial rollback acceptable if documented

3. **Isolation**
   - Don't read uncommitted changes from other SAGAs
   - Use versioning or timestamps to detect conflicts
   - Implement optimistic locking where needed

4. **Durability**
   - Log all operations and compensations
   - Persist SAGA state for crash recovery
   - Keep audit trail for compliance

---

### ⚠️ Common Pitfalls

1. **Non-idempotent compensations** → Duplicate rollbacks cause issues
2. **Missing compensations** → Can't fully rollback
3. **Compensations that can fail** → System left in inconsistent state
4. **Reading uncommitted data** → Dirty reads from in-flight SAGAs

---

## Next Steps

You've now completed all 5 examples! Review:
- Example 01: Simple Task (basics)
- Example 02: Parallel Execution (performance)
- Example 03: Error Handling (resilience)
- Example 04: Multi-Phase (long-running)
- Example 05: SAGA Pattern (distributed)

---

**Last Updated**: 2025-11-22  
**Difficulty**: ⭐⭐⭐ Advanced  
**Execution Time**: 8-12 minutes (success), +3-5 min (rollback)  
**Success Rate**: ~75% (intentionally demonstrates rollback scenarios)

# Schema Adapter

### A migration ledger, not a compatibility badge

This contract answers a narrow question: **can every required field in a target schema be traced to a declared source path?** It records that answer as a field-by-field bridge that reviewers can reconstruct.

#### Bridge anatomy

- Two schema URLs are frozen on different origins.
- The owner names an independent mapping author.
- Required target paths are enumerated before a mapping exists.
- Each target becomes either one canonical binding or an unmapped index—never both.
- `lossy_indexes` must be derived from the binding flags, so lossy coercion cannot be hidden.

The mapping file must live on a third origin. Validators retrieve all three artifacts and commit their SHA-256 digests with the complete bindings. A public, evidence-backed challenge can reopen a mapped bridge; a fresh author revision is then required.

#### State diagram

`REGISTERED` → `MAPPED` → `CERTIFIED`

`REGISTERED` → `BLOCKED` → revised mapping

`MAPPED` → `CHALLENGED` → revised mapping

#### Verification kit

```text
genvm-lint contracts/contract.py
python -m pytest -q
```

Tests cover complete and incomplete mappings, role/origin rules, permissionless certification, and an adversarial leader that drops a target binding. The `evidence/` cards document the two live writes expected after deployment.

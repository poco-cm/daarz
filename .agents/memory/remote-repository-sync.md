---
name: Remote repository synchronization
description: Safe handling when the configured remote has an independent initial history.
---

When a configured remote already contains an unrelated initial commit, merge the remote history before pushing local work. Resolve only genuine content conflicts, preserve both histories, and avoid force-pushing because it can erase user-owned remote work.

**Why:** The remote may be initialized independently from the local workspace, so a direct push can be rejected even when the local changes are complete.

**How to apply:** Fetch the target branch, inspect both histories, merge with unrelated histories when appropriate, resolve conflicts deliberately, then push normally.
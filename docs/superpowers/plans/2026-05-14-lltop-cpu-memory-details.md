# lltop CPU Core and Memory Header Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or implement these steps directly with TDD in this session. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show individual CPU core utilization and label memory/swap columns in the System panel.

**Architecture:** Keep the single-file Python CLI. Add small pure functions for `/proc/stat` parsing and CPU percentage calculation so they can be unit tested. Extend `collect_system()` and `render_snapshot()` to include CPU core rows and memory/swap column headers.

**Tech Stack:** Python 3 standard library, `/proc/stat`, `unittest`, remote install via `scp` to `ubt26`.

---

### Task 1: Add Failing Tests

**Files:**
- Modify: `/Users/cass/git/lltop/tests/test_lltop.py`

- [ ] **Step 1: Add test for CPU percentage calculation**

```python
def test_cpu_percentages_from_proc_stat_samples(self):
    lltop = load_lltop()
    before = {
        "cpu0": [100, 0, 100, 800, 0, 0, 0, 0, 0, 0],
        "cpu1": [200, 0, 100, 700, 0, 0, 0, 0, 0, 0],
    }
    after = {
        "cpu0": [150, 0, 150, 900, 0, 0, 0, 0, 0, 0],
        "cpu1": [220, 0, 120, 860, 0, 0, 0, 0, 0, 0],
    }

    self.assertEqual(lltop.cpu_percentages(before, after), [("0", 50), ("1", 20)])
```

- [ ] **Step 2: Add test for memory/swap headers and CPU rendering**

```python
def test_system_panel_shows_cpu_cores_and_memory_headers(self):
    lltop = load_lltop()
    snapshot = self.sample_snapshot()
    snapshot["system"]["cpu_cores"] = [("0", 50), ("1", 20)]
    snapshot["system"]["swap"] = "Swap: 8.0Gi 811Mi 7.2Gi"

    output = lltop.render_snapshot(snapshot, width=100, height=32)

    self.assertIn("CPU cores:", output)
    self.assertIn("00 [#####-----] 50%", output)
    self.assertIn("01 [##--------] 20%", output)
    self.assertIn("Memory columns: total used free shared buff/cache available", output)
    self.assertIn("Swap columns: total used free", output)
```

- [ ] **Step 3: Run tests and verify they fail**

Run: `python3 -m unittest discover -s tests -v`

Expected: FAIL because `cpu_percentages()` and the rendered headers do not exist yet.

### Task 2: Implement CPU Core and Memory Header Rendering

**Files:**
- Modify: `/Users/cass/git/lltop/lltop`

- [ ] **Step 1: Add `/proc/stat` parser and percentage calculator**

Add `parse_proc_stat(text)`, `read_proc_stat(path=Path("/proc/stat"))`, and `cpu_percentages(before, after)`.

- [ ] **Step 2: Add CPU collection to `collect_system()`**

Read `/proc/stat`, sleep briefly, read again, calculate percentages, and store as `cpu_cores`.

- [ ] **Step 3: Add CPU core row rendering**

Render cores as compact rows of four cores per line using 10-wide bars.

- [ ] **Step 4: Add memory and swap column headers**

Add labels before existing `Mem:` and `Swap:` rows.

- [ ] **Step 5: Run tests and syntax checks**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

Run: `python3 -m py_compile lltop`

Expected: exit 0.

### Task 3: Remote Install, Verify, Commit

**Files:**
- Install: `/home/cass/.local/bin/lltop` on `ubt26`
- Commit: `/Users/cass/git/lltop`

- [ ] **Step 1: Install and smoke test remotely**

Run: `scp lltop ubt26:/home/cass/.local/bin/lltop && ssh ubt26 'chmod +x ~/.local/bin/lltop && python3 -m py_compile ~/.local/bin/lltop && ~/.local/bin/lltop --once'`

Expected: output contains `CPU cores:`, `Memory columns:`, and `Swap columns:`.

- [ ] **Step 2: Commit changes**

Run: `git status --short && git diff --stat && git add . && git commit -m "Show CPU cores and memory headers" && git status --short`

Expected: commit succeeds and working tree is clean.

### Self-Review

- Spec coverage: individual CPU cores and memory/swap column headers are covered.
- Placeholder scan: no placeholders remain.
- Type consistency: helper names are consistent across test and implementation steps.

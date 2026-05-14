# lltop Side-by-Side System Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or implement these steps directly with TDD in this session. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the System area less cramped by rendering CPU and Memory/IO as side-by-side subpanels on wide terminals.

**Architecture:** Keep the single-file Python CLI and plain-text renderer. Add pure helper functions that compose text blocks side-by-side, then use them from `render_snapshot()` when terminal width is at least 120 columns. Keep the existing stacked layout as a narrow fallback.

**Tech Stack:** Python 3 standard library, `unittest`, remote install via `scp` to `ubt26`.

---

### Task 1: Add Failing Layout Tests

**Files:**
- Modify: `/Users/cass/git/lltop/tests/test_lltop.py`

- [ ] **Step 1: Add side-by-side helper test**

```python
def test_join_columns_places_blocks_side_by_side(self):
    lltop = load_lltop()

    output = lltop.join_columns(["left", "cpu"], ["right", "mem"], left_width=8, gap=" | ")

    self.assertEqual(output, ["left     | right", "cpu      | mem"])
```

- [ ] **Step 2: Add wide System layout test**

```python
def test_wide_system_panel_uses_side_by_side_subpanels(self):
    lltop = load_lltop()
    snapshot = self.sample_snapshot()
    snapshot["system"].update({
        "cpu_cores": [(str(index), 10 * index) for index in range(4)],
        "swap": "Swap: 8.0Gi 811Mi 7.2Gi",
        "vmstat": "r 1 b 0 free 1 KiB in 2 cs 3 cpu 4u/5s/91i",
        "iostat": "nvme0n1 r/s 1 w/s 2 read 3 KiB/s write 4 KiB/s util 5%",
    })

    output = lltop.render_snapshot(snapshot, width=140, height=40)

    self.assertIn("+-- CPU ", output)
    self.assertIn("+-- Memory / IO ", output)
    self.assertIn("+-- CPU ", output.splitlines()[15])
    self.assertIn("+-- Memory / IO ", output.splitlines()[15])
```

- [ ] **Step 3: Add narrow fallback test**

```python
def test_narrow_system_panel_uses_stacked_layout(self):
    lltop = load_lltop()
    snapshot = self.sample_snapshot()
    snapshot["system"]["cpu_cores"] = [("0", 50), ("1", 20)]

    output = lltop.render_snapshot(snapshot, width=100, height=32)

    self.assertIn("+-- System ", output)
    self.assertNotIn("+-- Memory / IO ", output)
```

- [ ] **Step 4: Run tests and verify they fail**

Run: `python3 -m unittest discover -s tests -v`

Expected: FAIL because `join_columns()` and the wide System layout do not exist yet.

### Task 2: Implement Two-Column System Rendering

**Files:**
- Modify: `/Users/cass/git/lltop/lltop`

- [ ] **Step 1: Add `join_columns()`**

Add a pure helper that pads the left column to a fixed width and joins matching rows from each block.

- [ ] **Step 2: Split System content into CPU and Memory/IO blocks**

Create `system_cpu_lines(system)` and `system_memory_io_lines(system)` helpers using the existing CPU, memory, vmstat, and iostat formatting.

- [ ] **Step 3: Update `render_snapshot()`**

If width is at least 120, render a single `System` section containing two side-by-side subpanel headers. Otherwise preserve the existing stacked `System` output.

- [ ] **Step 4: Run tests and syntax checks**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

Run: `python3 -m py_compile lltop`

Expected: exit 0.

### Task 3: Remote Install, Verify, Commit

**Files:**
- Install: `/home/cass/.local/bin/lltop` on `ubt26`
- Commit: `/Users/cass/git/lltop`

- [ ] **Step 1: Install and smoke test remotely**

Run: `scp lltop ubt26:/home/cass/.local/bin/lltop && ssh ubt26 'chmod +x ~/.local/bin/lltop && python3 -m py_compile ~/.local/bin/lltop && COLUMNS=160 ~/.local/bin/lltop --once'`

Expected: output contains side-by-side `+-- CPU` and `+-- Memory / IO` headers.

- [ ] **Step 2: Commit changes**

Run: `git status --short && git diff --stat && git add . && git commit -m "Split system panel into columns" && git status --short`

Expected: commit succeeds and working tree is clean.

### Self-Review

- Spec coverage: wide side-by-side layout and narrow fallback are covered.
- Placeholder scan: no placeholders remain.
- Type consistency: helper names are consistent across test and implementation steps.

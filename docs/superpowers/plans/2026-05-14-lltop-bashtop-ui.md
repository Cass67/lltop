# lltop Bashtop UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or implement these steps directly with TDD in this session. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `lltop` from a plain text dashboard to a bashtop-style terminal UI with colored panels and semantic meter colors.

**Architecture:** Keep the single-file Python CLI. Preserve `render_snapshot()` as a plain-text renderer for `--once` and tests, while adding small style helper functions used by the curses live view. Use no third-party dependencies.

**Tech Stack:** Python 3 standard library, `curses`, `unittest`, remote install via `scp` to `ubt26`.

---

### Task 1: Add Style Tests

**Files:**
- Modify: `/Users/cass/git/lltop/tests/test_lltop.py`

- [ ] **Step 1: Add failing tests for meter severity and panel rendering**

```python
def test_meter_style_thresholds(self):
    lltop = load_lltop()

    self.assertEqual(lltop.meter_style(10), "good")
    self.assertEqual(lltop.meter_style(74), "good")
    self.assertEqual(lltop.meter_style(75), "warn")
    self.assertEqual(lltop.meter_style(89), "warn")
    self.assertEqual(lltop.meter_style(90), "bad")
    self.assertEqual(lltop.meter_style(None), "muted")

def test_render_snapshot_uses_ascii_panels(self):
    lltop = load_lltop()
    output = lltop.render_snapshot(self.sample_snapshot(), width=100, height=30)

    self.assertIn("+-- GPU ", output)
    self.assertIn("+-- llama.cpp ", output)
    self.assertIn("+-- API ", output)
    self.assertIn("+-- System ", output)
    self.assertIn("+-- Recent log ", output)
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `python3 -m unittest discover -s tests -v`

Expected: FAIL because `meter_style` and boxed panel output do not exist yet.

### Task 2: Implement Bashtop-Style Rendering

**Files:**
- Modify: `/Users/cass/git/lltop/lltop`

- [ ] **Step 1: Add minimal style helpers**

```python
def meter_style(percent: int | float | None) -> str:
    if percent is None:
        return "muted"
    pct = clamp(float(percent), 0.0, 100.0)
    if pct >= 90.0:
        return "bad"
    if pct >= 75.0:
        return "warn"
    return "good"

def section(title: str, lines: list[str], width: int) -> list[str]:
    header = f"+-- {title} "
    header += "-" * max(0, width - len(header))
    return [header, *lines]
```

- [ ] **Step 2: Update `render_snapshot()` to use panel headers**

Build sections for GPU, llama.cpp, API, System, and Recent log, then concatenate them with blank lines. Keep content ASCII and preserve existing data.

- [ ] **Step 3: Add curses color initialization and line style mapping**

Create `init_colors()` and `line_attr(line)` helpers. Use cyan/blue for header, magenta for panel titles, green/yellow/red for meter severity, red for errors, dim for command/log details.

- [ ] **Step 4: Update `draw()` to apply color attributes**

Replace `stdscr.addstr(row, 0, line)` with `stdscr.addstr(row, 0, line, line_attr(line))` after initializing colors.

- [ ] **Step 5: Run tests and syntax checks**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

Run: `python3 -m py_compile lltop`

Expected: exit 0.

### Task 3: Remote Install and Smoke Test

**Files:**
- Install: `/home/cass/.local/bin/lltop` on `ubt26`

- [ ] **Step 1: Install updated script**

Run: `scp lltop ubt26:/home/cass/.local/bin/lltop && ssh ubt26 'chmod +x ~/.local/bin/lltop'`

Expected: exit 0.

- [ ] **Step 2: Remote syntax check**

Run: `ssh ubt26 'python3 -m py_compile ~/.local/bin/lltop'`

Expected: exit 0.

- [ ] **Step 3: Remote one-shot smoke test**

Run: `ssh ubt26 '~/.local/bin/lltop --once'`

Expected: output contains boxed sections for GPU, llama.cpp, API, System, and Recent log.

### Self-Review

- Spec coverage: bashtop dark styling, panels, semantic meter colors, plain `--once`, remote install, and verification are covered.
- Placeholder scan: no placeholders remain.
- Type consistency: helper names are consistent across tests and implementation steps.

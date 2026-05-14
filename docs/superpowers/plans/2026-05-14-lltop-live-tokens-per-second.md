# lltop Live Tokens Per Second Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or implement these steps directly with TDD in this session. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show live generation tokens/sec and last completed eval tokens/sec in the `llama.cpp` panel.

**Architecture:** Poll llama.cpp `/slots` each refresh and track decoded token deltas per `(slot id, task id)` in a small in-memory tracker. Parse recent llama.cpp log timing lines for the last completed eval throughput. Keep metrics optional and degrade to `n/a` when endpoints or logs are unavailable.

**Tech Stack:** Python 3 standard library, llama.cpp `/slots` endpoint, llama.cpp log files, `unittest`.

---

### Task 1: Add Failing Tests

**Files:**
- Modify: `/Users/cass/git/lltop/tests/test_lltop.py`

- [ ] **Step 1: Add slots parser test**

```python
def test_parse_slots_extracts_decoded_counts(self):
    lltop = load_lltop()
    body = '[{"id":0,"is_processing":true,"id_task":7,"next_token":[{"n_decoded":42}]},{"id":1,"is_processing":false,"id_task":8,"next_token":[{"n_decoded":3}]}]'

    self.assertEqual(
        lltop.parse_slots(body),
        [
            {"id": 0, "task": 7, "is_processing": True, "decoded": 42},
            {"id": 1, "task": 8, "is_processing": False, "decoded": 3},
        ],
    )
```

- [ ] **Step 2: Add live TPS tracker test**

```python
def test_tps_tracker_computes_live_decode_rate(self):
    lltop = load_lltop()
    tracker = lltop.TpsTracker()

    first = [{"id": 0, "task": 7, "is_processing": True, "decoded": 10}]
    second = [{"id": 0, "task": 7, "is_processing": True, "decoded": 70}]

    self.assertIsNone(tracker.update(first, now=100.0)["live_tps"])
    self.assertEqual(
        tracker.update(second, now=103.0),
        {"live_tps": 20.0, "active_slots": 1, "total_slots": 1},
    )
```

- [ ] **Step 3: Add log parser test**

```python
def test_parse_last_eval_tps_ignores_prompt_eval(self):
    lltop = load_lltop()
    lines = [
        "prompt eval time = 100.00 ms / 100 tokens (1.00 ms per token, 1000.00 tokens per second)",
        "       eval time = 2000.00 ms / 100 tokens (20.00 ms per token, 50.00 tokens per second)",
    ]

    self.assertEqual(lltop.parse_last_eval_tps(lines), 50.0)
```

- [ ] **Step 4: Add render test**

```python
def test_llama_panel_shows_token_throughput(self):
    lltop = load_lltop()
    snapshot = self.sample_snapshot()
    snapshot["tps"] = {"live_tps": 58.9, "active_slots": 1, "total_slots": 4, "last_eval_tps": 59.5}

    output = lltop.render_snapshot(snapshot, width=120, height=32)

    self.assertIn("tokens/sec: live 58.9", output)
    self.assertIn("active slots 1/4", output)
    self.assertIn("last eval 59.5", output)
```

- [ ] **Step 5: Run tests and verify they fail**

Run: `python3 -m unittest discover -s tests -v`

Expected: FAIL because TPS parser/tracker/rendering are missing.

### Task 2: Implement TPS Collection and Rendering

**Files:**
- Modify: `/Users/cass/git/lltop/lltop`

- [ ] **Step 1: Add JSON import and slot parser**

Parse `/slots` JSON into `id`, `task`, `is_processing`, and `decoded` values.

- [ ] **Step 2: Add `TpsTracker`**

Store previous decoded counts keyed by `(slot id, task id)` and return live decoded-token deltas per second.

- [ ] **Step 3: Add last eval tok/s parser**

Parse newest log lines for the most recent non-prompt `eval time` line and extract `tokens per second`.

- [ ] **Step 4: Add TPS collection to snapshots**

Poll `/slots` with a larger read limit than API health/model calls, update the tracker, attach last eval tok/s, and add `tps` to snapshots.

- [ ] **Step 5: Render TPS in the llama.cpp panel**

Add `tokens/sec: live ... active slots ... last eval ...` after the PID row and before the command row.

### Task 3: README, Verification, Remote Install, Commit

**Files:**
- Modify: `/Users/cass/git/lltop/README.md`
- Install: `/home/cass/.local/bin/lltop` on `ubt26`

- [ ] **Step 1: Update README features**

Mention live tokens/sec from `/slots` and last eval tokens/sec from llama logs.

- [ ] **Step 2: Run local verification**

Run: `python3 -m unittest discover -s tests -v`
Expected: all tests pass.

Run: `python3 -m py_compile lltop`
Expected: exit 0.

- [ ] **Step 3: Install and smoke test remotely**

Run: `./install.sh --prefix /tmp/lltop-tps-test && /tmp/lltop-tps-test/bin/lltop --once`
Expected: output contains `tokens/sec`.

Run: `scp lltop ubt26:/home/cass/.local/bin/lltop && ssh ubt26 'chmod +x ~/.local/bin/lltop && ~/.local/bin/lltop --once'`
Expected: output contains `tokens/sec`.

- [ ] **Step 4: Commit changes**

Run: `git status --short && git diff --stat && git add . && git commit -m "Show llama token throughput" && git status --short`

Expected: commit succeeds and working tree is clean.

### Self-Review

- Spec coverage: live `/slots` TPS, last completed eval TPS, rendering, README, verification, remote install, and commit are covered.
- Placeholder scan: no placeholders remain.
- Type consistency: `TpsTracker`, `parse_slots`, `parse_last_eval_tps`, and `tps` snapshot keys are consistent.

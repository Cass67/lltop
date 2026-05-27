# Multi-GPU Display Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Display both AMD and NVIDIA GPUs in `lltop`.

**Architecture:** Keep this as a small script-level change. Add helpers to collect a list of AMD and NVIDIA GPU metric dictionaries, keep `collect_gpu()` as the snapshot entry point, and update rendering to handle multiple entries while tolerating source failures.

**Tech Stack:** Python standard library, `unittest`, sysfs fixtures, mocked command output.

---

### Task 1: Add Multi-GPU Collection Tests

**Files:**

- Modify: `tests/test_lltop.py`

**Step 1: Write failing tests**

Add a test that creates two AMD-like `card*/device` fixtures and asserts `collect_gpu(root)` returns `gpus` with both AMD devices. Add a second test that monkey-patches `lltop.run_command` to return sample `nvidia-smi` CSV output and asserts a NVIDIA GPU entry is parsed with name `Tesla P40`, utilization, VRAM bytes, temperature, power, and clocks.

**Step 2: Run tests to verify failure**

Run: `python -m pytest tests/test_lltop.py -q`

Expected: FAIL because `collect_gpu()` currently returns only one AMD dictionary and has no NVIDIA parser.

### Task 2: Implement Collectors

**Files:**

- Modify: `lltop:119-142`

**Step 1: Add helpers**

Add `collect_amd_gpus(drm_root)` returning a list of dictionaries. Add `collect_nvidia_gpus()` using `run_command()` with `nvidia-smi` query arguments and parsing CSV rows.

**Step 2: Update `collect_gpu()`**

Make it return `{"gpus": [...]}` when any GPU is found, otherwise `{"error": ...}`. Include `vendor`, `name`, and `source` fields on each GPU entry.

**Step 3: Run tests**

Run: `python -m pytest tests/test_lltop.py -q`

Expected: the new collection tests pass; rendering tests may still need updates for the new shape.

### Task 3: Update Rendering

**Files:**

- Modify: `lltop:613-644`
- Modify: `tests/test_lltop.py`

**Step 1: Write rendering expectations**

Update sample snapshots to use `{"gpu": {"gpus": [...]}}`. Add a rendering test that includes one AMD and one NVIDIA entry and asserts both `Radeon` and `Tesla P40` appear.

**Step 2: Render multiple GPUs**

Update the GPU section in `render_snapshot()` to iterate over `gpu.get("gpus") or []`. For each device, render a label line plus the existing metric lines. Keep compatibility only if needed by tests inside this repo; no external compatibility layer is required.

**Step 3: Run tests**

Run: `python -m pytest tests/test_lltop.py -q`

Expected: PASS.

### Task 4: Update README

**Files:**

- Modify: `README.md:3-22`

**Step 1: Update documentation**

Change AMD-only wording to multi-GPU wording. Mention AMD sysfs and optional `nvidia-smi` for NVIDIA metrics.

**Step 2: Final verification**

Run: `python -m pytest tests/test_lltop.py -q`

Expected: PASS.

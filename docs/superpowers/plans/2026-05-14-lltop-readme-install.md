# lltop README and Installer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or implement these steps directly with TDD in this session. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add user-facing documentation and a simple installer script for `lltop`.

**Architecture:** Keep installation outside the Python monitor. Add a small Bash `install.sh` that copies `lltop` into `${PREFIX:-$HOME/.local}/bin/lltop`, with `--dry-run`, `--prefix`, and `--help`. Add a README that explains purpose, requirements, install, usage, options, and development verification.

**Tech Stack:** Bash, Python `unittest`, Markdown.

---

### Task 1: Add Installer Tests

**Files:**
- Create: `/Users/cass/git/lltop/tests/test_install.py`

- [ ] **Step 1: Write failing installer tests**

```python
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "install.sh"


class InstallTests(unittest.TestCase):
    def test_dry_run_prints_target_without_installing(self):
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp)
            result = subprocess.run(
                [str(INSTALL), "--dry-run", "--prefix", str(prefix)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(str(prefix / "bin" / "lltop"), result.stdout)
            self.assertFalse((prefix / "bin" / "lltop").exists())

    def test_installs_executable_to_prefix_bin(self):
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp)
            result = subprocess.run(
                [str(INSTALL), "--prefix", str(prefix)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            target = prefix / "bin" / "lltop"
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.exists())
            self.assertTrue(target.stat().st_mode & 0o111)
            self.assertIn("installed", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `python3 -m unittest tests.test_install -v`

Expected: FAIL because `install.sh` does not exist yet.

### Task 2: Implement `install.sh`

**Files:**
- Create: `/Users/cass/git/lltop/install.sh`

- [ ] **Step 1: Add installer script**

Implement strict Bash script with `--help`, `--dry-run`, and `--prefix`. Resolve the repo directory from `BASH_SOURCE[0]`, create `$prefix/bin`, copy `lltop`, chmod executable, and print the target.

- [ ] **Step 2: Run installer checks**

Run: `bash -n install.sh`

Expected: exit 0.

Run: `python3 -m unittest tests.test_install -v`

Expected: both installer tests pass.

### Task 3: Add README

**Files:**
- Create: `/Users/cass/git/lltop/README.md`

- [ ] **Step 1: Write README**

Include overview, requirements, install command, usage commands, CLI options, monitored data, remote usage on `ubt26`, development test commands, and note that no third-party packages are required.

- [ ] **Step 2: Check README content exists**

Run: `test -s README.md`

Expected: exit 0.

### Task 4: Verify, Install Remotely, Commit

**Files:**
- Modify: repo state under `/Users/cass/git/lltop`
- Install: `/home/cass/.local/bin/lltop` on `ubt26`

- [ ] **Step 1: Run full verification**

Run: `python3 -m unittest discover -s tests -v`
Expected: all tests pass.

Run: `python3 -m py_compile lltop`
Expected: exit 0.

Run: `bash -n install.sh`
Expected: exit 0.

- [ ] **Step 2: Verify remote install script path**

Run: `scp -r README.md install.sh lltop ubt26:/tmp/lltop-install-test/ && ssh ubt26 'cd /tmp/lltop-install-test && ./install.sh --prefix "$HOME/.local" && "$HOME/.local/bin/lltop" --once'`

Expected: install succeeds and one-shot dashboard renders.

- [ ] **Step 3: Commit changes**

Run: `git status --short && git diff --stat && git add . && git commit -m "Add README and installer" && git status --short`

Expected: commit succeeds and working tree is clean.

### Self-Review

- Spec coverage: README, installer, dry-run, prefix install, help, verification, and commit are covered.
- Placeholder scan: no placeholders remain.
- Type consistency: `install.sh`, `README.md`, and test paths are consistent.

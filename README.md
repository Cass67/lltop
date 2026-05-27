# lltop

`lltop` is a terminal dashboard for watching a local `llama.cpp` server, GPU usage, CPU cores, memory, disk IO, and recent llama logs from one screen.

It is built for the current `ubt26` llama.cpp setup, but the paths and API URL can be overridden with command-line options.

## Features

- AMD and NVIDIA GPU utilization, VRAM, memory busy, clocks, temperature, and power from `/sys/class/drm` and `nvidia-smi`.
- `llama-server` PID, CPU usage, RSS, runtime, and launch command.
- llama.cpp API health, model endpoint status, live tokens/sec from `/slots`, and last eval tokens/sec from logs.
- Per-core CPU bars from `/proc/stat`.
- Memory, swap, `vmstat`, and `iostat` summaries.
- Recent `llama-*.log` lines from the llama.cpp directory.
- Bashtop-style colored `curses` UI with a plain `--once` output mode.

## Requirements

- Linux with Python 3 and the standard library `curses` module.
- AMD GPU sysfs metrics under `/sys/class/drm/card*/device` or NVIDIA metrics from `nvidia-smi`.
- `llama.cpp` logs in `/home/cass/llama.cpp` by default.
- Optional system tools used when available: `free`, `vmstat`, `iostat`, `pgrep`, `ps`, `nvidia-smi`.
- No third-party Python packages are required.

## Install

From the repo root:

```bash
./install.sh
```

This installs `lltop` to:

```text
$HOME/.local/bin/lltop
```

Install somewhere else:

```bash
./install.sh --prefix /usr/local
```

Preview the install target without writing files:

```bash
./install.sh --dry-run
```

If `$HOME/.local/bin` is not on your `PATH`, run it by full path or add it to your shell profile.

## Usage

Interactive dashboard:

```bash
lltop
```

One-shot text snapshot:

```bash
lltop --once
```

Run on `ubt26` over SSH:

```bash
ssh -t ubt26 '~/.local/bin/lltop'
```

One-shot remote snapshot:

```bash
ssh ubt26 '~/.local/bin/lltop --once'
```

## Options

```text
--once              print one dashboard snapshot and exit
--interval SECONDS  refresh interval, default: 1.0
--drm-root PATH     DRM sysfs root, default: /sys/class/drm
--llama-dir PATH    llama.cpp directory containing llama-*.log, default: /home/cass/llama.cpp
--base-url URL      llama.cpp server base URL, default: http://127.0.0.1:8080
```

## Keys

```text
q  quit
r  refresh now
```

## Development

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Check Python syntax:

```bash
python3 -m py_compile lltop
```

Check installer syntax:

```bash
bash -n install.sh
```

Install to a temporary prefix for testing:

```bash
tmp=$(mktemp -d)
./install.sh --prefix "$tmp"
"$tmp/bin/lltop" --once
```

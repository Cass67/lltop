# lltop

`lltop` is a terminal dashboard for watching a local `llama.cpp` server, GPU usage, CPU cores, memory, disk I/O, and recent model logs.

It pairs well with [`local_llm`](https://github.com/cass67/local_llm), which can generate `llama.cpp` launchers that write the `model.log` file shown in the Recent log panel.

## Features

- `llama-server` process status, CPU, RSS, runtime, and launch command.
- llama.cpp API health and model endpoint status.
- Live tokens/sec from `/slots` plus last eval tokens/sec parsed from logs.
- AMD and NVIDIA GPU metrics when available.
- Per-core CPU, memory, swap, `vmstat`, and `iostat` summaries.
- Recent `model.log` lines from the llama.cpp directory, with legacy `llama-*.log` fallback.
- Interactive curses UI and plain `--once` snapshot mode.

## Install

```bash
./install.sh
```

This installs:

```text
~/.local/bin/lltop
```

Install elsewhere:

```bash
./install.sh --prefix /usr/local
```

Preview without writing:

```bash
./install.sh --dry-run
```

## Usage

Interactive dashboard:

```bash
lltop
```

One-shot snapshot:

```bash
lltop --once
```

Run on a remote model host over SSH:

```bash
ssh -t <host> '~/.local/bin/lltop'
```

## Options

```text
--once              print one dashboard snapshot and exit
--interval SECONDS  refresh interval in seconds
--drm-root PATH     DRM sysfs root, default: /sys/class/drm
--llama-dir PATH    llama.cpp directory containing model.log, default: /home/cass/llama.cpp
--base-url URL      llama.cpp server base URL, default: http://127.0.0.1:8080
```

## Logs

`lltop` prefers:

```text
~/llama.cpp/model.log
```

That file is written by current [`local_llm`](https://github.com/cass67/local_llm) generated launchers. If `model.log` is missing, `lltop` falls back to older `llama-*.log` files so older setups still show logs.

If the Recent log panel still shows an old `llama-*.log`, update/redeploy your `local_llm` launchers and restart the model service on the host:

```bash
ssh <host> 'systemctl --user restart llama-server.service'
```

## Development

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Check syntax:

```bash
python3 -m py_compile lltop
bash -n install.sh
```

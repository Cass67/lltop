import importlib.util
from importlib.machinery import SourceFileLoader
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "lltop"


def load_lltop():
    if not SCRIPT.exists():
        raise AssertionError(f"missing executable script: {SCRIPT}")
    loader = SourceFileLoader("lltop_script", str(SCRIPT))
    spec = importlib.util.spec_from_loader("lltop_script", loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LltopTests(unittest.TestCase):
    def sample_snapshot(self):
        return {
            "hostname": "ubt26",
            "time": "12:34:56",
            "gpu": {
                "path": "/sys/class/drm/card2/device",
                "gpu_busy_percent": 37,
                "mem_busy_percent": 12,
                "vram_used": 10729029632,
                "vram_total": 21458059264,
                "temp_c": 46.0,
                "power_w": 10.0,
                "sclk": "S: 2475Mhz *",
                "mclk": "1: 1249Mhz *",
            },
            "llama": {
                "pid": "1234",
                "cpu_percent": "82.5",
                "rss": "18.2g",
                "etime": "01:02:03",
                "cmd": "./build/bin/llama-server -c 49152 --alias qwen3-coder",
            },
            "api": {"health": "ok", "models": "qwen3-coder"},
            "system": {"load": "1.00 0.75 0.50", "mem": "Mem: 1 2 3"},
            "logs": ["main: server is listening", "slot 0 idle"],
        }

    def test_format_bytes_uses_binary_units(self):
        lltop = load_lltop()

        self.assertEqual(lltop.format_bytes(0), "0.0 B")
        self.assertEqual(lltop.format_bytes(1024), "1.0 KiB")
        self.assertEqual(lltop.format_bytes(21458059264), "20.0 GiB")

    def test_bar_clamps_percent_and_fills_width(self):
        lltop = load_lltop()

        self.assertEqual(lltop.bar(-10, 10), "[----------]")
        self.assertEqual(lltop.bar(50, 10), "[#####-----]")
        self.assertEqual(lltop.bar(150, 10), "[##########]")

    def test_meter_style_thresholds(self):
        lltop = load_lltop()

        self.assertEqual(lltop.meter_style(10), "good")
        self.assertEqual(lltop.meter_style(74), "good")
        self.assertEqual(lltop.meter_style(75), "warn")
        self.assertEqual(lltop.meter_style(89), "warn")
        self.assertEqual(lltop.meter_style(90), "bad")
        self.assertEqual(lltop.meter_style(None), "muted")

    def test_muted_palette_uses_readable_color(self):
        lltop = load_lltop()

        muted = lltop.style_palette()["muted"]

        self.assertEqual(muted["foreground"], "cyan")
        self.assertFalse(muted["dim"])

    def test_summarize_iostat_compacts_long_device_row(self):
        lltop = load_lltop()
        row = "nvme0n1 8.04 610.05 5.11 38.87 0.15 75.92 9.43 778.72 16.79 64.03 9.77 82.57 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00"

        summary = lltop.summarize_iostat(row)

        self.assertEqual(summary, "nvme0n1 r/s 8.04 w/s 9.43 read 610.05 KiB/s write 778.72 KiB/s util 0.00%")

    def test_summarize_vmstat_uses_correct_cpu_columns(self):
        lltop = load_lltop()
        row = "1 0 830536 17758792 63748 39660764 0 0 0 124 4957 5259 1 2 97 0 0 0"

        summary = lltop.summarize_vmstat(row)

        self.assertEqual(summary, "r 1 b 0 free 17758792 KiB in 4957 cs 5259 cpu 1u/2s/97i")

    def test_find_amd_gpu_device_reads_sysfs_metrics(self):
        lltop = load_lltop()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            intel = root / "card1" / "device"
            amd = root / "card2" / "device"
            intel.mkdir(parents=True)
            amd.mkdir(parents=True)
            (intel / "vendor").write_text("0x8086\n")
            (amd / "vendor").write_text("0x1002\n")
            (amd / "gpu_busy_percent").write_text("37\n")
            (amd / "mem_busy_percent").write_text("12\n")
            (amd / "mem_info_vram_total").write_text("21458059264\n")
            (amd / "mem_info_vram_used").write_text("10729029632\n")
            hwmon = amd / "hwmon" / "hwmon4"
            hwmon.mkdir(parents=True)
            (hwmon / "temp1_input").write_text("46000\n")
            (hwmon / "power1_average").write_text("10000000\n")

            gpu = lltop.collect_gpu(root)

        self.assertEqual(gpu["path"], str(amd))
        self.assertEqual(gpu["gpu_busy_percent"], 37)
        self.assertEqual(gpu["mem_busy_percent"], 12)
        self.assertEqual(gpu["vram_used"], 10729029632)
        self.assertEqual(gpu["vram_total"], 21458059264)
        self.assertEqual(gpu["temp_c"], 46.0)
        self.assertEqual(gpu["power_w"], 10.0)

    def test_render_snapshot_contains_gpu_llama_api_and_logs(self):
        lltop = load_lltop()
        snapshot = self.sample_snapshot()

        output = lltop.render_snapshot(snapshot, width=100, height=24)

        self.assertIn("lltop ubt26 12:34:56", output)
        self.assertIn("GPU", output)
        self.assertIn("37%", output)
        self.assertIn("10.0 GiB / 20.0 GiB", output)
        self.assertIn("llama.cpp", output)
        self.assertIn("PID 1234", output)
        self.assertIn("API", output)
        self.assertIn("qwen3-coder", output)
        self.assertIn("Recent log", output)
        self.assertIn("slot 0 idle", output)

    def test_render_snapshot_uses_ascii_panels(self):
        lltop = load_lltop()

        output = lltop.render_snapshot(self.sample_snapshot(), width=100, height=30)

        self.assertIn("+-- GPU ", output)
        self.assertIn("+-- llama.cpp ", output)
        self.assertIn("+-- API ", output)
        self.assertIn("+-- System ", output)
        self.assertIn("+-- Recent log ", output)


if __name__ == "__main__":
    unittest.main()

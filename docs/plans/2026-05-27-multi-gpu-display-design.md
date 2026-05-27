# Multi-GPU Display Design

## Goal

Show both installed GPUs in `lltop`: the Radeon 7900 XT from AMD sysfs metrics and the NVIDIA Tesla P40 from `nvidia-smi` metrics.

## Approved Approach

Collect all AMD GPUs from `/sys/class/drm` and all NVIDIA GPUs from `nvidia-smi`, then render them in the existing `GPU` section as a compact block per device.

## Data Collection

- AMD entries keep the existing sysfs fields: utilization, memory busy, VRAM usage, temperature, power, and active clocks.
- NVIDIA entries use `nvidia-smi --query-gpu=name,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw,clocks.sm,clocks.mem --format=csv,noheader,nounits`.
- If one source is unavailable, `lltop` still displays GPUs from the other source.
- If neither source finds a GPU, the GPU section shows a single error line.

## Rendering

The existing `GPU` panel remains. Each detected card gets its own label line with vendor/name and path/index, followed by the familiar utilization, VRAM, temperature, power, and clock lines where available.

## Testing

Tests will simulate AMD sysfs data and mocked `nvidia-smi` output. Rendering tests will assert that both cards appear without requiring physical GPU hardware.

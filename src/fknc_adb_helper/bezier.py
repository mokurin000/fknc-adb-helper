import subprocess
import time
import numpy as np
import random
from typing import List, Tuple

from fknc_adb_helper.utils import adb_command_prefix


def sigmoid_ease(t: np.ndarray, k: float = 10.0) -> np.ndarray:
    """Sigmoid ease-in-out function"""
    return 1.0 / (1.0 + np.exp(-k * (t - 0.5)))


def run_adb_command(args: List[str]) -> None:
    """Run adb shell input command and raise if it fails"""
    try:
        subprocess.run(
            adb_command_prefix() + ["shell", "input"] + args,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"ADB command failed: {' '.join(args)}")
        print(f"Error: {e.stderr.strip()}")
        raise


def generate_natural_swipe_points(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    ctrl1: Tuple[float, float] = None,
    ctrl2: Tuple[float, float] = None,
    n_points: int = 38,
    total_duration_ms: float = 1350.0,
    k_sigmoid: float = 8.5,
    pos_jitter_px: float = 1.4,
    time_jitter_pct: float = 0.18,
    random_seed: int = None,
) -> List[Tuple[int, int, int]]:
    """
    Generate realistic swipe motion events:
      - Cubic Bézier curve
      - Sigmoid ease-in-out timing
      - Small position + timing jitter
    Returns list of (x, y, delay_ms_after_this_move)
    """
    if random_seed is not None:
        random.seed(random_seed)

    if ctrl1 is None:
        ctrl1 = (x1 + 0.28 * (x2 - x1), y1 + 0.28 * (y2 - y1) - 120)
    if ctrl2 is None:
        ctrl2 = (x1 + 0.72 * (x2 - x1), y1 + 0.72 * (y2 - y1) + 100)

    P0 = np.array([x1, y1])
    P1 = np.array(ctrl1)
    P2 = np.array(ctrl2)
    P3 = np.array([x2, y2])

    # t values for the MOVE points (excluding DOWN and final UP)
    t_raw = np.linspace(0.0, 1.0, n_points + 2)[1:-1]  # shape: (n_points,)
    eased_t = sigmoid_ease(t_raw, k=k_sigmoid)
    eased_t = np.sort(eased_t)

    # Ideal positions along the curve
    positions = []
    for t in eased_t:
        u = 1.0 - t
        pos = u**3 * P0 + 3 * u**2 * t * P1 + 3 * u * t**2 * P2 + t**3 * P3
        positions.append(pos)

    # Time intervals (including from 0→first and last→1)
    t_full = np.concatenate(([0.0], eased_t, [1.0]))
    t_steps = np.diff(t_full)  # shape: (n_points + 1,)

    # Delays AFTER each MOVE → take intervals 1 through n_points
    ideal_delays_ms = t_steps[1:] * total_duration_ms  # now exactly n_points values

    result = []
    for i, (ideal_x, ideal_y) in enumerate(positions):
        # Position jitter (slightly asymmetric in y — common for finger wobble)
        jx = random.uniform(-pos_jitter_px, pos_jitter_px)
        jy = random.uniform(-pos_jitter_px * 1.4, pos_jitter_px * 1.4)
        x = round(ideal_x + jx)
        y = round(ideal_y + jy)

        # Timing jitter
        base_delay = ideal_delays_ms[i]
        jitter_factor = random.uniform(-time_jitter_pct, time_jitter_pct)
        delay = round(base_delay * (1.0 + jitter_factor))
        delay = max(4, delay)  # avoid zero or negative delays

        result.append((x, y, delay))

    return result


def perform_natural_swipe(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    duration_ms: float = 1350.0,
    verbose: bool = True,
) -> None:
    """
    Execute a human-like swipe using adb + monotonic timing to avoid drift
    """
    points = generate_natural_swipe_points(
        x1,
        y1,
        x2,
        y2,
        n_points=38,
        total_duration_ms=duration_ms,
        k_sigmoid=8.5,
        pos_jitter_px=1.4,
        time_jitter_pct=0.18,
        # random_seed=42   # uncomment for consistent behavior during testing
    )

    if verbose:
        print(f"Starting natural swipe from ({x1},{y1}) → ({x2},{y2})")
        print(f"Total planned duration: ~{duration_ms:.0f} ms")
        print(f"MOVE events: {len(points)}")

    # DOWN
    run_adb_command(["downtouch", str(x1), str(y1)])
    if verbose:
        print(f"DOWN {x1} {y1}")

    # Timing reference
    start_time = time.monotonic()
    cumulative_planned = 0.0

    for i, (x, y, delay_ms) in enumerate(points, 1):
        # Send MOVE
        run_adb_command(["motionevent", "MOVE", str(x), str(y)])

        cumulative_planned += delay_ms
        if verbose:
            print(
                f"MOVE {x:4d} {y:4d}   +{delay_ms:3d} ms   (cum planned ~{cumulative_planned:4.0f} ms)"
            )

        # Calculate when we should wake for the *next* event
        fraction_done = i / len(points)
        ideal_next_wake = start_time + (duration_ms / 1000.0) * fraction_done
        sleep_time = ideal_next_wake - time.monotonic()

        if sleep_time > 0:
            time.sleep(sleep_time)
        elif verbose and sleep_time < -0.012:
            print(f"  ⚠️ lag {sleep_time * 1000:+.1f} ms")

    # UP at final coordinates
    run_adb_command(["motionevent", "UP", str(x2), str(y2)])
    if verbose:
        actual_duration_ms = (time.monotonic() - start_time) * 1000
        print(f"UP   {x2} {y2}")
        print(f"Actual duration: {actual_duration_ms:.0f} ms")


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Example: full-screen upward scroll on typical 1080p-ish phone
    perform_natural_swipe(
        x1=540, y1=1850, x2=540, y2=350, duration_ms=1350.0, verbose=True
    )

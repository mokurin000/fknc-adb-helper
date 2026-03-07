import time
import subprocess

def fetch_screenshot() -> bytes:
    # hard-coded for 1920x1080
    for x, y in [
        (1804, 149),  # Close
        (1773, 89),  # Store
        (1805, 381),  # Tools
    ]:
        subprocess.call(["adb", "shell", "input", "tap", f"{x}", f"{y}"])
        time.sleep(1)
    out = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    return out

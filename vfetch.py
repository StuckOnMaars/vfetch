#!/usr/bin/env python3
"""
vfetch - A modern, animated system info tool for Debian-based Linux systems.
Like Neofetch, but with gradients, animations, and full customizability.
"""

import os
import sys
import time
import json
import argparse
import platform
import subprocess
import shutil
import socket
import threading
from pathlib import Path
from datetime import datetime

# ─── Graceful dependency handling ─────────────────────────────────────────────
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    from rich.console import Console
    from rich.text import Text
    from rich.live import Live
    from rich.columns import Columns
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# ─── Config paths ─────────────────────────────────────────────────────────────
CONFIG_DIR  = Path.home() / ".config" / "vfetch"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOGO_FILE   = CONFIG_DIR / "logo.txt"

# ─── Built-in themes ──────────────────────────────────────────────────────────
THEMES = {
    "cyberpunk": {
        "primary":    "#FF00FF",
        "secondary":  "#00FFFF",
        "accent":     "#FFFF00",
        "bar_full":   "#FF00FF",
        "bar_empty":  "#1a0020",
        "label":      "#00FFFF",
        "value":      "#FFFFFF",
        "border":     "#FF00FF",
        "title":      "#FFFF00",
        "gradient":   ["#FF00FF", "#CC00FF", "#9900FF", "#6600FF", "#00FFFF"],
    },
    "nord": {
        "primary":    "#88C0D0",
        "secondary":  "#81A1C1",
        "accent":     "#EBCB8B",
        "bar_full":   "#88C0D0",
        "bar_empty":  "#2E3440",
        "label":      "#81A1C1",
        "value":      "#ECEFF4",
        "border":     "#4C566A",
        "title":      "#88C0D0",
        "gradient":   ["#88C0D0", "#81A1C1", "#5E81AC", "#88C0D0", "#8FBCBB"],
    },
    "dracula": {
        "primary":    "#BD93F9",
        "secondary":  "#FF79C6",
        "accent":     "#50FA7B",
        "bar_full":   "#BD93F9",
        "bar_empty":  "#282A36",
        "label":      "#FF79C6",
        "value":      "#F8F8F2",
        "border":     "#6272A4",
        "title":      "#50FA7B",
        "gradient":   ["#BD93F9", "#FF79C6", "#FF5555", "#FFB86C", "#50FA7B"],
    },
    "gruvbox": {
        "primary":    "#FABD2F",
        "secondary":  "#83A598",
        "accent":     "#B8BB26",
        "bar_full":   "#FABD2F",
        "bar_empty":  "#282828",
        "label":      "#83A598",
        "value":      "#EBDBB2",
        "border":     "#504945",
        "title":      "#FABD2F",
        "gradient":   ["#FABD2F", "#FE8019", "#FB4934", "#B8BB26", "#83A598"],
    },
    "catppuccin": {
        "primary":    "#CBA6F7",
        "secondary":  "#89DCEB",
        "accent":     "#A6E3A1",
        "bar_full":   "#CBA6F7",
        "bar_empty":  "#1E1E2E",
        "label":      "#89DCEB",
        "value":      "#CDD6F4",
        "border":     "#585B70",
        "title":      "#CBA6F7",
        "gradient":   ["#CBA6F7", "#F38BA8", "#FAB387", "#A6E3A1", "#89DCEB"],
    },
    "monochrome": {
        "primary":    "#FFFFFF",
        "secondary":  "#AAAAAA",
        "accent":     "#FFFFFF",
        "bar_full":   "#FFFFFF",
        "bar_empty":  "#333333",
        "label":      "#AAAAAA",
        "value":      "#FFFFFF",
        "border":     "#555555",
        "title":      "#FFFFFF",
        "gradient":   ["#FFFFFF", "#DDDDDD", "#BBBBBB", "#999999", "#777777"],
    },
}

# ─── Built-in ASCII logos ──────────────────────────────────────────────────────
LOGOS = {
    "ubuntu": """
         _
     ---(_)
 _/  ---  \\
(_) |   |
  \\  --- _/
     ---(_)
""",
    "debian": """
  _____
 /  __ \\
|  /    |
|  \\___-
\\-____  \\
""",
    "generic": """
  ██╗   ██╗
  ██║   ██║
  ╚██╗ ██╔╝
   ╚████╔╝
    ╚═══╝
""",
    "arch": """
      /\\
     /  \\
    / /\\ \\
   / ____ \\
  /_/    \\_\\
""",
    "pop": """
 ____
|  _ \\
| |_) |
|  __/
|_|
""",
}

# ─── Default config ────────────────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "theme": "cyberpunk",
    "modules": ["os", "kernel", "uptime", "cpu", "gpu", "ram", "disk", "shell", "terminal", "resolution", "battery", "network"],
    "animations": True,
    "animation_speed": 0.012,
    "logo": "auto",
    "custom_logo": None,
    "gradient_text": True,
    "bar_width": 20,
    "bar_style": "smooth",   # smooth | block | ascii
    "live_refresh": 1.0,
    "show_icons": True,
    "compact": False,
    "color_blocks": True,
}

# ─── Icons (Unicode) ──────────────────────────────────────────────────────────
ICONS = {
    "os":         "󰻀",
    "kernel":     "",
    "uptime":     "󱎫",
    "cpu":        "",
    "gpu":        "󰍹",
    "ram":        "",
    "disk":       "󰋊",
    "shell":      "",
    "terminal":   "",
    "resolution": "󰹑",
    "battery":    "",
    "network":    "󰀂",
    "separator":  "─",
}

# ─── Fallback icons if font not available ─────────────────────────────────────
ICONS_ASCII = {
    "os":         "OS",
    "kernel":     "KN",
    "uptime":     "UP",
    "cpu":        "CP",
    "gpu":        "GP",
    "ram":        "RM",
    "disk":       "DK",
    "shell":      "SH",
    "terminal":   "TM",
    "resolution": "RES",
    "battery":    "BAT",
    "network":    "NET",
}


# ══════════════════════════════════════════════════════════════════════════════
#  SYSTEM INFO COLLECTORS
# ══════════════════════════════════════════════════════════════════════════════

def get_os_info():
    try:
        with open("/etc/os-release") as f:
            info = {}
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    info[k] = v.strip('"')
        return info.get("PRETTY_NAME", platform.system())
    except Exception:
        return platform.system()


def get_kernel():
    return platform.uname().release


def get_uptime():
    if HAS_PSUTIL:
        boot = psutil.boot_time()
        uptime_sec = time.time() - boot
        hours, rem = divmod(int(uptime_sec), 3600)
        minutes = rem // 60
        if hours >= 24:
            days = hours // 24
            hours = hours % 24
            return f"{days}d {hours}h {minutes}m"
        return f"{hours}h {minutes}m"
    try:
        with open("/proc/uptime") as f:
            secs = float(f.read().split()[0])
        hours, rem = divmod(int(secs), 3600)
        minutes = rem // 60
        return f"{hours}h {minutes}m"
    except Exception:
        return "N/A"


def get_cpu():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    model = line.split(":")[1].strip()
                    # Shorten common patterns
                    model = model.replace("(R)", "").replace("(TM)", "").replace("  ", " ")
                    break
            else:
                model = platform.processor() or "Unknown CPU"
    except Exception:
        model = platform.processor() or "Unknown CPU"

    # CPU count
    cores = os.cpu_count() or 1
    model = f"{model} ({cores} cores)"

    # Usage %
    usage = 0.0
    if HAS_PSUTIL:
        usage = psutil.cpu_percent(interval=0.1)
    else:
        try:
            with open("/proc/stat") as f:
                line = f.readline().split()
            idle1 = int(line[4])
            total1 = sum(int(x) for x in line[1:])
            time.sleep(0.1)
            with open("/proc/stat") as f:
                line = f.readline().split()
            idle2 = int(line[4])
            total2 = sum(int(x) for x in line[1:])
            usage = 100.0 * (1 - (idle2 - idle1) / (total2 - total1))
        except Exception:
            pass
    return model, usage


def get_gpu():
    gpus = []
    # Try nvidia-smi first
    if shutil.which("nvidia-smi"):
        try:
            out = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,utilization.gpu", "--format=csv,noheader,nounits"],
                stderr=subprocess.DEVNULL, timeout=2
            ).decode().strip()
            for line in out.splitlines():
                parts = line.split(",")
                name = parts[0].strip()
                util = float(parts[1].strip()) if len(parts) > 1 else 0
                gpus.append((name, util))
        except Exception:
            pass

    # Fallback to lspci
    if not gpus and shutil.which("lspci"):
        try:
            out = subprocess.check_output(
                ["lspci"], stderr=subprocess.DEVNULL, timeout=2
            ).decode()
            for line in out.splitlines():
                low = line.lower()
                if "vga" in low or "3d" in low or "display" in low:
                    # Extract device name after the colon
                    part = line.split(":", 2)[-1].strip()
                    # Remove common prefixes
                    for skip in ["Advanced Micro Devices, Inc.", "[AMD/ATI]", "NVIDIA Corporation", "Intel Corporation"]:
                        part = part.replace(skip, "").strip()
                    gpus.append((part[:48], None))
                    break
        except Exception:
            pass

    return gpus if gpus else None


def get_ram():
    if HAS_PSUTIL:
        vm = psutil.virtual_memory()
        used = vm.used / (1024**3)
        total = vm.total / (1024**3)
        pct = vm.percent
    else:
        try:
            info = {}
            with open("/proc/meminfo") as f:
                for line in f:
                    k, v = line.split(":", 1)
                    info[k.strip()] = int(v.split()[0]) * 1024
            total_b = info.get("MemTotal", 0)
            avail_b = info.get("MemAvailable", 0)
            used_b  = total_b - avail_b
            used    = used_b / (1024**3)
            total   = total_b / (1024**3)
            pct     = 100 * used_b / total_b if total_b else 0
        except Exception:
            return 0, 0, 0
    return used, total, pct


def get_disk(path="/"):
    if HAS_PSUTIL:
        disk = psutil.disk_usage(path)
        used  = disk.used  / (1024**3)
        total = disk.total / (1024**3)
        pct   = disk.percent
    else:
        try:
            st = os.statvfs(path)
            total = st.f_blocks * st.f_frsize / (1024**3)
            free  = st.f_bavail * st.f_frsize / (1024**3)
            used  = total - free
            pct   = 100 * used / total if total else 0
        except Exception:
            return 0, 0, 0
    return used, total, pct


def get_shell():
    shell = os.environ.get("SHELL", "")
    if shell:
        return Path(shell).name
    return "unknown"


def get_terminal():
    for var in ["TERM_PROGRAM", "TERMINAL", "TERM"]:
        val = os.environ.get(var)
        if val:
            return val
    return "unknown"


def get_resolution():
    # Try xrandr
    if shutil.which("xrandr"):
        try:
            out = subprocess.check_output(
                ["xrandr", "--current"], stderr=subprocess.DEVNULL, timeout=2
            ).decode()
            for line in out.splitlines():
                if "*" in line:
                    parts = line.split()
                    for p in parts:
                        if "x" in p and p[0].isdigit():
                            return p.split("+")[0]
        except Exception:
            pass
    # Try /sys for framebuffer
    try:
        with open("/sys/class/graphics/fb0/virtual_size") as f:
            dims = f.read().strip().replace(",", "x")
            return dims
    except Exception:
        pass
    return "N/A"


def get_battery():
    if HAS_PSUTIL:
        try:
            bat = psutil.sensors_battery()
            if bat:
                status = "Charging ⚡" if bat.power_plugged else "Discharging"
                return bat.percent, status
        except Exception:
            pass
    # Fallback via /sys
    try:
        base = Path("/sys/class/power_supply")
        for entry in base.iterdir():
            cap_file = entry / "capacity"
            stat_file = entry / "status"
            if cap_file.exists():
                cap = int(cap_file.read_text().strip())
                status = stat_file.read_text().strip() if stat_file.exists() else "Unknown"
                return cap, status
    except Exception:
        pass
    return None


def get_network():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        hostname = "unknown"
        local_ip = "N/A"

    # Public IP - quick, no external library needed
    public_ip = None
    try:
        import urllib.request
        with urllib.request.urlopen("https://api.ipify.org", timeout=1) as r:
            public_ip = r.read().decode().strip()
    except Exception:
        pass

    return local_ip, public_ip


# ══════════════════════════════════════════════════════════════════════════════
#  RENDERING
# ══════════════════════════════════════════════════════════════════════════════

def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def lerp_color(c1, c2, t):
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    return r, g, b


def ansi_rgb(r, g, b, bg=False):
    code = 48 if bg else 38
    return f"\033[{code};2;{r};{g};{b}m"


RESET = "\033[0m"
BOLD  = "\033[1m"


def gradient_line(text, colors_hex, bold=True):
    """Render a string with a smooth gradient across the given hex colors."""
    if not colors_hex:
        return text
    rgb_colors = [hex_to_rgb(c) for c in colors_hex]
    n = len(text)
    if n == 0:
        return text
    result = BOLD if bold else ""
    for i, char in enumerate(text):
        t_global = i / max(n - 1, 1)
        # Map t_global to segment
        seg_count = len(rgb_colors) - 1
        seg_idx = min(int(t_global * seg_count), seg_count - 1)
        t_local = t_global * seg_count - seg_idx
        r, g, b = lerp_color(rgb_colors[seg_idx], rgb_colors[min(seg_idx+1, len(rgb_colors)-1)], t_local)
        result += ansi_rgb(r, g, b) + char
    result += RESET
    return result


def color(text, hex_color, bold=False):
    r, g, b = hex_to_rgb(hex_color)
    prefix = BOLD if bold else ""
    return f"{prefix}{ansi_rgb(r, g, b)}{text}{RESET}"


def make_bar(pct, width, theme, style="smooth"):
    filled = int(round(pct / 100 * width))
    empty  = width - filled

    fr, fg, fb = hex_to_rgb(theme["bar_full"])
    er, eg, eb = hex_to_rgb(theme["bar_empty"])

    if style == "smooth":
        # Use gradient for the filled portion
        gradient = theme.get("gradient", [theme["bar_full"]])
        rgb_stops = [hex_to_rgb(c) for c in gradient]
        bar = ""
        for i in range(filled):
            t = i / max(width - 1, 1)
            seg_count = len(rgb_stops) - 1
            seg_idx = min(int(t * seg_count), seg_count - 1)
            t_local = t * seg_count - seg_idx
            r, g, b = lerp_color(rgb_stops[seg_idx], rgb_stops[min(seg_idx+1, len(rgb_stops)-1)], t_local)
            bar += ansi_rgb(r, g, b) + "█"
        bar += ansi_rgb(er, eg, eb) + "░" * empty + RESET
    elif style == "block":
        bar = (ansi_rgb(fr, fg, fb) + "▓" * filled +
               ansi_rgb(er, eg, eb) + "░" * empty + RESET)
    else:  # ascii
        bar = (ansi_rgb(fr, fg, fb) + "#" * filled +
               ansi_rgb(er, eg, eb) + "-" * empty + RESET)

    return "[" + bar + "]"


def typewriter(text, delay=0.012):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")
    sys.stdout.flush()


def print_line(text, animate=False, delay=0.012):
    if animate:
        typewriter(text, delay)
    else:
        print(text)


def detect_logo():
    os_id = ""
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("ID="):
                    os_id = line.split("=")[1].strip().strip('"').lower()
                    break
    except Exception:
        pass
    if "ubuntu" in os_id:
        return "ubuntu"
    if "pop" in os_id:
        return "pop"
    if "debian" in os_id:
        return "debian"
    if "arch" in os_id:
        return "arch"
    return "generic"


def get_logo_lines(config):
    # Custom file?
    if config.get("custom_logo") and Path(config["custom_logo"]).exists():
        logo_text = Path(config["custom_logo"]).read_text()
    elif LOGO_FILE.exists():
        logo_text = LOGO_FILE.read_text()
    else:
        logo_key = config.get("logo", "auto")
        if logo_key == "auto":
            logo_key = detect_logo()
        logo_text = LOGOS.get(logo_key, LOGOS["generic"])
    return [l for l in logo_text.split("\n")]


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN RENDERER
# ══════════════════════════════════════════════════════════════════════════════

class VFetch:
    def __init__(self, config, args):
        self.config = config
        self.args   = args
        self.theme  = THEMES.get(config.get("theme", "cyberpunk"), THEMES["cyberpunk"])
        self.animate = config.get("animations", True) and not args.no_animation
        self.speed   = config.get("animation_speed", 0.012)
        self.bar_w   = config.get("bar_width", 20)
        self.bar_style = config.get("bar_style", "smooth")
        self.icons   = ICONS if config.get("show_icons", True) else ICONS_ASCII
        self.modules = config.get("modules", list(DEFAULT_CONFIG["modules"]))

        if args.minimal:
            self.modules = ["os", "kernel", "cpu", "ram", "disk"]
            self.animate = False

    def _label(self, key):
        icon = self.icons.get(key, "")
        label_text = key.upper()
        if icon:
            label_text = f"{icon}  {label_text}"
        return color(label_text, self.theme["label"], bold=True)

    def _value(self, text):
        return color(str(text), self.theme["value"])

    def _bar(self, pct):
        return make_bar(pct, self.bar_w, self.theme, self.bar_style)

    def collect(self):
        """Collect all system info upfront."""
        data = {}
        mods = self.modules

        if "os"         in mods: data["os"]         = get_os_info()
        if "kernel"     in mods: data["kernel"]      = get_kernel()
        if "uptime"     in mods: data["uptime"]      = get_uptime()
        if "cpu"        in mods: data["cpu"]         = get_cpu()
        if "gpu"        in mods: data["gpu"]         = get_gpu()
        if "ram"        in mods: data["ram"]         = get_ram()
        if "disk"       in mods: data["disk"]        = get_disk()
        if "shell"      in mods: data["shell"]       = get_shell()
        if "terminal"   in mods: data["terminal"]    = get_terminal()
        if "resolution" in mods: data["resolution"]  = get_resolution()
        if "battery"    in mods: data["battery"]     = get_battery()
        if "network"    in mods: data["network"]     = get_network()

        return data

    def format_rows(self, data):
        """Return list of rendered strings for each info row."""
        rows = []
        sep = color("  " + "─" * 36, self.theme["border"])
        gradient = self.theme.get("gradient", [self.theme["primary"]])

        for mod in self.modules:
            if mod not in data:
                continue
            val = data[mod]

            if mod == "os":
                rows.append(f"  {self._label('os')}  {self._value(val)}")

            elif mod == "kernel":
                rows.append(f"  {self._label('kernel')}  {self._value(val)}")

            elif mod == "uptime":
                rows.append(f"  {self._label('uptime')}  {self._value(val)}")

            elif mod == "cpu":
                model, usage = val
                bar = self._bar(usage)
                pct_str = color(f"{usage:5.1f}%", self.theme["accent"])
                rows.append(f"  {self._label('cpu')}  {self._value(model)}")
                rows.append(f"  {'':>12}  {bar} {pct_str}")

            elif mod == "gpu":
                if val:
                    for name, util in val:
                        rows.append(f"  {self._label('gpu')}  {self._value(name)}")
                        if util is not None:
                            bar = self._bar(util)
                            pct_str = color(f"{util:5.1f}%", self.theme["accent"])
                            rows.append(f"  {'':>12}  {bar} {pct_str}")
                else:
                    rows.append(f"  {self._label('gpu')}  {self._value('Not detected')}")

            elif mod == "ram":
                used, total, pct = val
                bar = self._bar(pct)
                mem_str = f"{used:.1f} GiB / {total:.1f} GiB"
                pct_str = color(f"{pct:5.1f}%", self.theme["accent"])
                rows.append(f"  {self._label('ram')}  {self._value(mem_str)}")
                rows.append(f"  {'':>12}  {bar} {pct_str}")

            elif mod == "disk":
                used, total, pct = val
                bar = self._bar(pct)
                disk_str = f"{used:.1f} GiB / {total:.1f} GiB"
                pct_str = color(f"{pct:5.1f}%", self.theme["accent"])
                rows.append(f"  {self._label('disk')}  {self._value(disk_str)}")
                rows.append(f"  {'':>12}  {bar} {pct_str}")

            elif mod == "shell":
                rows.append(f"  {self._label('shell')}  {self._value(val)}")

            elif mod == "terminal":
                rows.append(f"  {self._label('terminal')}  {self._value(val)}")

            elif mod == "resolution":
                rows.append(f"  {self._label('resolution')}  {self._value(val)}")

            elif mod == "battery":
                if val:
                    pct_val, status = val
                    bar = self._bar(pct_val)
                    stat_str = color(f"{pct_val:.0f}% ({status})", self.theme["accent"])
                    rows.append(f"  {self._label('battery')}  {bar} {stat_str}")
                # skip if no battery

            elif mod == "network":
                local_ip, public_ip = val
                rows.append(f"  {self._label('network')}  {self._value(local_ip)}" +
                             (f"  {color('pub:', self.theme['secondary'])} {self._value(public_ip)}" if public_ip else ""))

        # Color swatches
        if self.config.get("color_blocks", True):
            rows.append("")
            swatches = ""
            for clr in self.theme.get("gradient", [self.theme["primary"]]):
                r, g, b = hex_to_rgb(clr)
                swatches += ansi_rgb(r, g, b, bg=True) + "   " + RESET
            rows.append("  " + swatches)

        return rows

    def get_header(self):
        user = os.environ.get("USER", os.environ.get("LOGNAME", "user"))
        host = socket.gethostname()
        title = f"{user}@{host}"
        gradient = self.theme.get("gradient", [self.theme["primary"]])
        return gradient_line(title, gradient)

    def render_frame(self, data):
        """Produce the full output as a list of lines (ANSI-colored)."""
        logo_lines  = get_logo_lines(self.config)
        info_rows   = self.format_rows(data)
        gradient    = self.theme.get("gradient", [self.theme["primary"]])

        # Colorize logo with gradient
        colored_logo = []
        for i, line in enumerate(logo_lines):
            t = i / max(len(logo_lines) - 1, 1)
            stops = [hex_to_rgb(c) for c in gradient]
            seg = len(stops) - 1
            seg_i = min(int(t * seg), seg - 1) if seg > 0 else 0
            t_l = t * seg - seg_i if seg > 0 else 0
            r, g, b = lerp_color(stops[seg_i], stops[min(seg_i+1, len(stops)-1)], t_l)
            colored_logo.append(ansi_rgb(r, g, b) + BOLD + line + RESET)

        lines = []
        # Header
        lines.append("")
        lines.append("  " + self.get_header())
        lines.append("  " + color("─" * len(f"{os.environ.get('USER','user')}@{socket.gethostname()}"), self.theme["border"]))
        lines.append("")

        # Combine logo + info side by side
        logo_w = max((len(l.rstrip()) for l in logo_lines), default=0) + 4
        max_rows = max(len(colored_logo), len(info_rows))

        for i in range(max_rows):
            logo_part = colored_logo[i] if i < len(colored_logo) else ""
            raw_logo  = logo_lines[i] if i < len(logo_lines) else ""
            info_part = info_rows[i]  if i < len(info_rows)  else ""

            # Pad logo to fixed width (using raw len for spacing)
            pad = logo_w - len(raw_logo)
            lines.append(logo_part + " " * pad + info_part)

        lines.append("")
        return lines

    def print_once(self, animate=None):
        if animate is None:
            animate = self.animate
        data  = self.collect()
        lines = self.render_frame(data)

        # Clear screen for cleaner output
        os.system("clear")

        for line in lines:
            print_line(line, animate=animate, delay=self.speed)

    def run_live(self):
        """Refresh every N seconds until Ctrl-C."""
        interval = self.config.get("live_refresh", 1.0)
        # First render animated, subsequent ones not
        self.print_once(animate=False)
        try:
            while True:
                time.sleep(interval)
                data  = self.collect()
                lines = self.render_frame(data)
                os.system("clear")
                for line in lines:
                    print(line)
        except KeyboardInterrupt:
            print(color("\n  Exiting vfetch live mode.", self.theme["secondary"]))


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════════════════

def load_config(path=None):
    cfg_path = Path(path) if path else CONFIG_FILE
    config = dict(DEFAULT_CONFIG)
    if cfg_path.exists():
        try:
            with open(cfg_path) as f:
                user_cfg = json.load(f)
            config.update(user_cfg)
        except Exception as e:
            print(f"[vfetch] Warning: could not parse config: {e}", file=sys.stderr)
    return config


def write_default_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"[vfetch] Default config written to {CONFIG_FILE}")


# ══════════════════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        prog="vfetch",
        description="vfetch – Modern, animated system info tool",
    )
    p.add_argument("--no-animation",  action="store_true", help="Disable typewriter animation")
    p.add_argument("--theme",         metavar="NAME",      help=f"Color theme ({', '.join(THEMES)})")
    p.add_argument("--config",        metavar="PATH",      help="Path to config file")
    p.add_argument("--live",          action="store_true", help="Refresh stats every second")
    p.add_argument("--minimal",       action="store_true", help="Show only core info")
    p.add_argument("--list-themes",   action="store_true", help="List available themes")
    p.add_argument("--init-config",   action="store_true", help="Write default config and exit")
    return p.parse_args()


def check_deps():
    missing = []
    if not HAS_PSUTIL:
        missing.append("psutil")
    if not HAS_RICH:
        missing.append("rich")
    if missing:
        print(f"[vfetch] Optional deps missing (install for best experience): {', '.join(missing)}", file=sys.stderr)
        print(f"[vfetch] Run: pip install {' '.join(missing)}", file=sys.stderr)


def main():
    args = parse_args()

    if args.list_themes:
        print("Available themes:")
        for name in THEMES:
            t = THEMES[name]
            swatches = ""
            for clr in t.get("gradient", [t["primary"]]):
                r, g, b = hex_to_rgb(clr)
                swatches += ansi_rgb(r, g, b, bg=True) + "   " + RESET
            print(f"  {name:<15} {swatches}")
        return

    if args.init_config:
        write_default_config()
        return

    check_deps()
    config = load_config(args.config)

    # CLI overrides
    if args.theme:
        if args.theme in THEMES:
            config["theme"] = args.theme
        else:
            print(f"[vfetch] Unknown theme '{args.theme}'. Use --list-themes.", file=sys.stderr)

    vf = VFetch(config, args)

    if args.live:
        vf.run_live()
    else:
        vf.print_once()


if __name__ == "__main__":
    main()

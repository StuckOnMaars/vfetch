# vfetch ⚡

> **Modern, animated system info tool for Debian-based Linux**
> Like Neofetch — but with gradients, typewriter animations, live mode, and full customizability.

```
  ██╗   ██╗███████╗███████╗████████╗ ██████╗██╗  ██╗
  ██║   ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝██║  ██║
  ██║   ██║█████╗  █████╗     ██║   ██║     ███████║
  ╚██╗ ██╔╝██╔══╝  ██╔══╝     ██║   ██║     ██╔══██║
   ╚████╔╝ ██║     ███████╗   ██║   ╚██████╗██║  ██║
    ╚═══╝  ╚═╝     ╚══════╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
```

---

##  Features

- **OS / Kernel / Uptime / CPU / GPU / RAM / Disk / Shell / Terminal / Resolution / Battery / Network**
- **Smooth gradient bars** for CPU, RAM, Disk usage
- **Typewriter animation** on startup (configurable speed)
- **6 built-in themes**: `cyberpunk`, `nord`, `dracula`, `gruvbox`, `catppuccin`, `monochrome`
- **Live mode** — refreshes stats every second (`--live`)
- **ASCII logo auto-detection** for Ubuntu, Debian, Pop!_OS, Arch
- **Fully customizable** via `~/.config/vfetch/config.json`
- **GPU detection** via `nvidia-smi` or `lspci`
- **Battery info** for laptops
- **Color swatches** at the bottom (terminal palette preview)
- Graceful fallback if `psutil` / `rich` not installed

---

##  Installation

### Quick install (recommended)

```bash
git clone https://github.com/StuckOnMaarz/vfetch.git
cd vfetch
chmod +x install.sh
./install.sh
```

### Manual install

```bash
pip install psutil rich
sudo cp vfetch.py /usr/local/bin/vfetch
sudo chmod +x /usr/local/bin/vfetch
```

---

##  Usage

```bash
vfetch                          # Normal run with animations
vfetch --no-animation           # Skip typewriter effect
vfetch --theme dracula          # Use a specific theme
vfetch --live                   # Refresh every second (Ctrl-C to exit)
vfetch --minimal                # OS, Kernel, CPU, RAM, Disk only
vfetch --list-themes            # Show all available themes with color preview
vfetch --config ~/my.json       # Use a custom config file
vfetch --init-config            # Write default config to ~/.config/vfetch/
```

---

##  Themes

| Theme        | Colors                                |
|--------------|---------------------------------------|
| `cyberpunk`  | Magenta → Cyan → Yellow               |
| `nord`       | Arctic blue palette                   |
| `dracula`    | Purple → Pink → Green                 |
| `gruvbox`    | Warm gold → Orange → Tan              |
| `catppuccin` | Lavender → Sky → Mint                 |
| `monochrome` | White → Grey                          |

Preview all themes:
```bash
vfetch --list-themes
```

---

##  Configuration

Config file lives at: `~/.config/vfetch/config.json`

```json
{
  "theme": "cyberpunk",
  "modules": ["os", "kernel", "uptime", "cpu", "gpu", "ram", "disk",
               "shell", "terminal", "resolution", "battery", "network"],
  "animations": true,
  "animation_speed": 0.012,
  "logo": "auto",
  "custom_logo": null,
  "gradient_text": true,
  "bar_width": 20,
  "bar_style": "smooth",
  "live_refresh": 1.0,
  "show_icons": true,
  "compact": false,
  "color_blocks": true
}
```

### Config options

| Key              | Type    | Default      | Description                                      |
|------------------|---------|--------------|--------------------------------------------------|
| `theme`          | string  | `cyberpunk`  | Color theme name                                 |
| `modules`        | array   | (all)        | Which modules to show, in order                  |
| `animations`     | bool    | `true`       | Enable typewriter animation                      |
| `animation_speed`| float   | `0.012`      | Seconds per character (lower = faster)           |
| `logo`           | string  | `auto`       | `auto`, `ubuntu`, `debian`, `arch`, `generic`    |
| `custom_logo`    | string  | `null`       | Path to a custom ASCII art `.txt` file           |
| `gradient_text`  | bool    | `true`       | Gradient colors on the username@hostname header  |
| `bar_width`      | int     | `20`         | Width of progress bars in characters             |
| `bar_style`      | string  | `smooth`     | `smooth`, `block`, or `ascii`                    |
| `live_refresh`   | float   | `1.0`        | Seconds between refreshes in live mode           |
| `show_icons`     | bool    | `true`       | Show Unicode icons next to labels                |
| `color_blocks`   | bool    | `true`       | Show color swatches at the bottom                |

### Custom ASCII logo

Create any text file with your ASCII art and set:

```json
{
  "custom_logo": "/home/yourname/.config/vfetch/logo.txt"
}
```

Or simply place a `logo.txt` in `~/.config/vfetch/` — it will be used automatically.

---

##  Dependencies

| Package  | Required | Purpose                        |
|----------|----------|--------------------------------|
| `psutil` | Optional | Accurate CPU/RAM/Disk/Battery  |
| `rich`   | Optional | Enhanced terminal output       |

Without these, vfetch falls back to `/proc` filesystem reads. Install them for the best experience:

```bash
pip install psutil rich
```

---

##  Supported Systems

- Ubuntu 20.04+
- Debian 11+
- Pop!_OS 22.04+
- Linux Mint
- Any Debian-based distro with Python 3.8+

---

##  Performance

- Cold start: **~80–150ms** without GPU detection
- With `nvidia-smi`: add ~50ms
- Live mode: near-instant refresh (reads `/proc` directly)

---

##  License

MIT — do whatever you want with it.

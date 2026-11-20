# 🎬 Video2X Web Studio

> **A modern, high-performance Web UI built with clean MVC architecture (FastAPI + TailwindCSS + Lucide Icons) for AI Video Super-Resolution and Frame Interpolation powered by Video2X v6.2.0.**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![TailwindCSS](https://img.shields.io/badge/Frontend-TailwindCSS-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Lucide Icons](https://img.shields.io/badge/Icons-Lucide%20Icons-F56565?logo=lucide&logoColor=white)](https://lucide.dev/)
[![Video2X](https://img.shields.io/badge/Engine-Video2X%20v6.2.0-E50914?logo=github)](https://github.com/k4yt3x/video2x)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)

---

## 📖 Overview

**Video2X Web Studio** transforms the command-line AI upscaler [Video2X](https://github.com/k4yt3x/video2x) into a production-grade web application. Designed for both local workstations and Cloud GPU environments (such as **Kaggle** and **Google Colab**), it provides an intuitive drag-and-drop dashboard, real-time progress streaming via Server-Sent Events (SSE), in-browser side-by-side video previews, and zero-configuration public sharing via Cloudflare Tunnels.

---

## 🏛️ MVC Architecture

The project strictly follows the **Model-View-Controller (MVC)** architectural pattern to ensure clean separation of concerns, high maintainability, and scalability:

```text
VIDEO2X/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application setup, template & static mounts
│   ├── models/                     # [M] MODEL: Pydantic schemas & data validation
│   │   ├── __init__.py
│   │   ├── video.py                # VideoMetadata, ProcessingOptions, TaskProgress, TaskResult
│   │   └── system.py               # GPUInfo, SystemEnvInfo
│   ├── controllers/                # [C] CONTROLLER: Request routers & API endpoints
│   │   ├── __init__.py
│   │   ├── home_controller.py      # Serves Single Page UI (GET /)
│   │   ├── video_controller.py     # Upload, probe (ffprobe), stream preview, download
│   │   ├── task_controller.py      # Start/abort processing, SSE live stream (/stream)
│   │   └── system_controller.py    # Hardware monitor (nvidia-smi, Vulkan ICD status)
│   ├── services/                   # SERVICE: Business logic & OS process execution
│   │   ├── __init__.py
│   │   ├── video2x_service.py      # Subprocess execution, regex progress parser, crash guard
│   │   ├── ffmpeg_service.py       # Video inspection (codec, resolution, fps, duration)
│   │   └── system_service.py       # NVIDIA GPU & Vulkan system detection
│   └── views/                      # [V] VIEW: User interface templates & assets
│       ├── templates/
│       │   ├── base.html           # Master layout with TailwindCSS CDN & Lucide Icons CDN
│       │   └── index.html          # Reactive dark-themed dashboard
│       └── static/
│           ├── css/
│           │   └── style.css       # Custom animations, progress glow, terminal scrollbars
│           └── js/
│               └── app.js          # Client-side controller (drag-drop, SSE, video player)
├── run.py                          # Application entry point with Cloudflare Tunnel support
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules (cache, venv, outputs)
├── video2x-kaggle.ipynb            # Interactive CLI/Notebook workflow for Kaggle
└── README.md                       # Project documentation
```

---

## ✨ Key Features

* **⚡ Real-Time Progress Streaming (SSE):**
  Uses Server-Sent Events (`/api/tasks/stream`) to broadcast per-frame progress (`frame=X/Y`, percentage, current FPS, elapsed time, and ETA) as well as live terminal logs directly from `video2x` and `ffmpeg` without polling.
* **🧠 All Video2X v6.2.0 AI Engines Supported:**
  * **Real-ESRGAN:**
    * `realesr-animevideov3` (Fast anime video upscaling: 2x, 3x, 4x).
    * `realesrgan-plus-anime` (Ultra-detailed anime upscaling: 4x).
    * `realesrgan-plus` (Real-world / live-action video enhancement: 4x).
  * **Anime4K (libplacebo):** Real-time high-speed GLSL shaders (`anime4k-v4-a`, `anime4k-v4.1-gan`, etc.).
  * **RIFE:** Deep learning optical flow frame interpolation (2x or 4x frame rate multiplication, e.g. 30 FPS ➡️ 60 / 120 FPS).
* **🎛️ Full FFmpeg Encoder Controls:**
  * **Video Codecs:** `libx264` (CPU H.264), `h264_nvenc` (NVIDIA NVENC hardware acceleration), `libx265`.
  * **Rate Control:** Constant Rate Factor (CRF slider from 14 to 28) or explicit bitrate.
  * **Presets:** From `ultrafast` to `veryslow`.
  * **Pixel Format:** Standard `yuv420p` for maximum hardware & browser compatibility.
* **🎥 In-Browser Video Player & Before/After Comparison:**
  * Drag & drop video upload with live percentage progress bar.
  * Direct filesystem path inspection (e.g. `/kaggle/input/...`) using `ffprobe`.
  * Built-in HTML5 media player supporting range requests for instant playback.
  * Side-by-side comparison cards (Resolution, File Size, FPS, Duration).
* **🌐 Zero-Config Public Sharing:**
  Includes a built-in Cloudflare Tunnel runner (`--share`), generating a secure public HTTPS URL (`https://xxxx.trycloudflare.com`) without opening firewall ports, configuring routers, or registering accounts.
* **🛡️ Headless Vulkan & Crash-Resilient Guard:**
  Detects and handles the known Video2X 6.2.0 headless cleanup issue (Exit code 139 / SIGSEGV occurring during `vkDestroyDevice()` after the video is 100% written), ensuring the task is properly marked as completed when the output file is valid.

---

## 🚀 Quick Start

### 1. Local Machine (Linux / Windows with NVIDIA GPU)

#### Prerequisites:
* Python 3.10+
* [FFmpeg 7](https://ffmpeg.org/) (providing `libavcodec.so.61`)
* NVIDIA GPU Driver with Vulkan support
* [Video2X v6.2.0](https://github.com/k4yt3x/video2x/releases/tag/6.2.0) installed and added to `PATH`

#### Installation:
```bash
# Clone the repository
git clone https://github.com/conghoa004/VIDEO2X.git
cd VIDEO2X

# Install Python requirements
pip install -r requirements.txt

# Start the Web UI server
python run.py --port 7860
```
Open your web browser and navigate to: **`http://localhost:7860`**.

---

### 2. Cloud GPU Deployment (Kaggle & Google Colab)

Run the full Video2X Web Studio on free cloud GPUs (**NVIDIA Tesla T4 x2** or **P100**) with public HTTPS access.

#### ⚙️ Mandatory Kaggle Notebook Settings:
Before running, configure your Kaggle Notebook via the **Settings** panel on the right:
1. **Accelerator:** Select **GPU T4 x2** (or **GPU P100**).
2. **Internet:** Toggle to **ON** (required to download packages, models, and Cloudflare Tunnel).

---

#### 📦 Cell 1: Install Video2X, FFmpeg 7 & NVIDIA Vulkan Driver (~1.5 min)
Create a new code cell and run this script to install all system packages, configure Vulkan ICD for NVIDIA GPU, and verify the setup:

```python
import os
import re
import json
import subprocess
from pathlib import Path

print("⏳ [1/4] Installing FFmpeg 7 and Vulkan development packages...")
!apt-get update -yqq
!apt-get install -yqq software-properties-common
!add-apt-repository -y ppa:ubuntuhandbook1/ffmpeg7
!apt-get update -yqq
!apt-get install -yqq --no-install-recommends libvulkan1 libvulkan-dev vulkan-tools ffmpeg mesa-vulkan-drivers

print("\n⏳ [2/4] Detecting & installing NVIDIA Vulkan graphics driver (libnvidia-gl)...")
driver_ver = '535'
try:
    smi_out = subprocess.check_output('nvidia-smi', shell=True).decode()
    m = re.search(r'Driver Version:\s*(\d+)', smi_out)
    if m:
        driver_ver = m.group(1)
        print(f"🔍 Detected Driver Version: {driver_ver}")
except Exception:
    pass

!apt-get install -yqq --no-install-recommends libnvidia-gl-{driver_ver} || !apt-get install -yqq --no-install-recommends libnvidia-gl-535

print("\n⏳ [3/4] Configuring Vulkan ICD for NVIDIA GPU...")
icd_dir = Path("/usr/share/vulkan/icd.d")
icd_dir.mkdir(parents=True, exist_ok=True)
with open(icd_dir / "nvidia_icd.json", "w") as f:
    json.dump({
        "file_format_version": "1.0.0",
        "ICD": {
            "library_path": "libGLX_nvidia.so.0",
            "api_version": "1.3.0"
        }
    }, f, indent=4)

!cp -f /usr/share/vulkan/icd.d/nvidia_icd.json /etc/vulkan/icd.d/ 2>/dev/null || true
os.environ["VK_ICD_FILENAMES"] = "/usr/share/vulkan/icd.d/nvidia_icd.json"
os.environ["__NV_PRIME_RENDER_OFFLOAD"] = "1"
os.environ["__VK_LAYER_NV_optimus"] = "NVIDIA_only"
!ldconfig

print("\n⏳ [4/4] Installing Video2X v6.2.0...")
deb_file = "/tmp/video2x.deb"
!wget -q -O {deb_file} https://github.com/k4yt3x/video2x/releases/download/6.2.0/video2x-linux-ubuntu2204-amd64.deb
!apt-get install -yqq {deb_file} || (dpkg -i {deb_file} && apt-get install -fyqq)

print("\n🔍 Validating Vulkan & Video2X:")
!vulkaninfo --summary 2>/dev/null | grep -E "deviceName|driverName" || true
!video2x --version
print("\n✅ Setup completed successfully! NVIDIA GPU is ready for Vulkan.")
```

---

#### 🚀 Cell 2: Clone Repo, Install Python Dependencies & Launch Web Studio
In the next code cell, clone the repository, install Python packages, and launch the server. It will automatically initialize Cloudflare Tunnel and display your public HTTPS link:

```python
%cd /kaggle/working
!rm -rf VIDEO2X
!git clone https://github.com/conghoa004/VIDEO2X.git
%cd /kaggle/working/VIDEO2X
!pip install -q -r requirements.txt

# Launch FastAPI Web Studio (automatically launches Cloudflare Tunnel on Kaggle)
!python run.py --port 7860
```

---

#### 🌐 Step 3: Access the Web UI
Once Cell 2 starts, look for the public URL in the cell output:

```text
=================================================================
🚀 GIAO DIỆN WEB CÔNG KHAI ĐÃ SẴN SÀNG:
👉 https://xxxx.trycloudflare.com
=================================================================
```

Click the **`https://xxxx.trycloudflare.com`** link to open Video2X Web Studio in your browser on desktop or mobile. The Vulkan indicator badge in the header will display **`⚡ Tesla T4 (NVIDIA)`**, confirming hardware acceleration is active!

---

#### 💡 Kaggle Usage Tips:
* **Direct Kaggle Dataset Inputs:** You can process videos directly from Kaggle Datasets by clicking **+ Add Input** (top right) and pasting the file path (e.g. `/kaggle/input/<dataset-name>/<video>.mp4`) into the **Đường dẫn trên máy chủ** field in the Web UI.
* **Outputs:** Upscaled videos are stored in `/kaggle/working/output/`. You can download them directly via the Web UI's **Tải video kết quả** button or from the Kaggle **Output** sidebar.
* **Exit code 139 (SIGSEGV) note:** When a video reaches 100%, Video2X may exit with code 139 due to Vulkan destructor cleanup in headless containers. The Web UI automatically recognizes this and marks the video as successful since the output file has already been completely written.

---

## ⚙️ CLI Options for `run.py`

| Flag | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `--host` | `str` | `0.0.0.0` | IP address to bind the HTTP server to |
| `--port` | `int` | `7860` | Network port to listen on |
| `--reload` | `flag` | `False` | Enable auto-reload for local development |
| `--share` | `flag` | `False` | Automatically download and launch Cloudflare Tunnel for public HTTPS access |

---

## 🛠️ Tech Stack

* **Backend:** [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [Asyncio](https://docs.python.org/3/library/asyncio.html), [Pydantic v2](https://docs.pydantic.dev/).
* **Frontend:** [TailwindCSS](https://tailwindcss.com/) (CDN), [Lucide Icons](https://lucide.dev/) (CDN), [Jinja2 Templates](https://jinja.palletsprojects.com/).
* **Core Engine:** [Video2X v6.2.0](https://github.com/k4yt3x/video2x), [FFmpeg 7](https://ffmpeg.org/), Vulkan API.
* **Tunneling:** [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) (cloudflared).

---

## 📄 License & Acknowledgments

* **Video2X:** Copyright © [K4YT3X](https://github.com/k4yt3x) (Licensed under the [ISC License](https://opensource.org/licenses/ISC)).
* **Real-ESRGAN:** Copyright © [Xintao Wang et al.](https://github.com/xinntao/Real-ESRGAN) (BSD 3-Clause License).
* **Anime4K:** Copyright © [bloc97](https://github.com/bloc97/Anime4K) (MIT License).
* **RIFE:** Real-Time Intermediate Flow Estimation for Video Frame Interpolation (Megvii Technology).

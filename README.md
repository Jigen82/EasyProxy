# 🚀 EasyProxy

**Universal HLS/M3U8 Proxy & Stream Extractor**
A powerful, lightweight proxy server designed to handle HLS, M3U8, and DASH (MPD) streams. It includes specialized extractors for popular streaming services, DRM support, and an integrated DVR system.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Features

- **🌐 Universal Proxy**: Seamlessly handles HLS, M3U8, MPD (DASH), and static video files.
- **🔓 DRM Support**: ClearKey decryption via FFmpeg transcoding or legacy mode.
- **🔐 Specialized Extractors**: Native support for Vavoo, DaddyliveHD, Sportsonline, VixSrc, DoodStream, MaxStream, and more.
- **📼 Integrated DVR**: Record live streams while watching or schedule background recordings.
- **🛠️ Playlist Builder**: Web interface to combine, manage, and proxy entire M3U playlists.
- **☁️ Cloud Ready**: Optimized for HuggingFace, Render, Koyeb, and other free-tier platforms.
- **🛡️ Cloudflare Bypass**: Integrated with FlareSolverr and Byparr for bot protection bypass.

---

## 🚀 Quick Start

### 🐳 Docker (Recommended)
The **Full** version includes the proxy plus FlareSolverr and Byparr for maximum compatibility.

```bash
# Light Version (Proxy Only - Default)
docker run -d -p 7860:7860 --name EasyProxy ghcr.io/realbestia1/easyproxy:latest

# Full Version (Proxy + Solvers)
docker run -d -p 7860:7860 --name EasyProxy ghcr.io/realbestia1/easyproxy:full

# Full Version + Cloudflare WARP (Bypass IP blocks)
docker run -d --name EasyProxy --cap-add=NET_ADMIN --device /dev/net/tun -e ENABLE_WARP=true -p 7860:7860 ghcr.io/realbestia1/easyproxy:full
```

### 🐍 Python (Local)

#### Prerequisites (All Platforms)
- **Python 3.11+**
- **Git** (for cloning dependencies)
- **FFmpeg** (for stream recording/remuxing)

#### 🪟 Windows Setup
The easiest way to get the **Full** experience (Proxy + Solvers) on Windows:
1. Clone the repository and enter the folder.
2. Run **`start_full.bat`**.
*This script automatically handles FlareSolverr, Byparr, patches, and dependencies.*

#### 🐧 Linux / macOS Setup
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```
2. **Start EasyProxy**:
   ```bash
   python app.py
   ```
*Note: For "Full" mode on Linux, you must start FlareSolverr and Byparr manually or use the [Docker](#-docker) version.*

*Access the dashboard at `http://localhost:7860`*

---

## 📦 Deployment Options

| Method | Description |
| :--- | :--- |
| **Light (Default)** | Standard `docker build .` uses the base `Dockerfile`. |
| **Full** | Use `Dockerfile.full` for a monolithic build with solvers included. |
| **Docker Compose** | Run the complete stack (Proxy + Solvers) with `docker-compose up -d`. |
| **HuggingFace** | Use `Dockerfile-hf` for seamless deployment on HF Spaces. |
| **Termux** | Support for Android via Python & FFmpeg. |

---

## ⚙️ Configuration

Configure the server via a `.env` file. See `.env.example` for all options.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `PORT` | Server port | `7860` |
| `API_PASSWORD` | Optional password for API endpoints | `ep` |
| `FLARESOLVERR_URL` | URL for FlareSolverr (Not needed in Full version) | `http://localhost:8191` |
| `FLARESOLVERR_TIMEOUT` | Timeout for FlareSolverr requests (seconds) | `30` |
| `BYPARR_URL` | URL for Byparr (Not needed in Full version) | `http://localhost:8192` |
| `DVR_ENABLED` | Enable recording features | `false` |
| `ENABLE_WARP` | Enable integrated Cloudflare WARP (Full version only) | `false` |
| `WARP_LICENSE_KEY` | Optional WARP+ license key | - |

### 🛡️ Cloudflare WARP Integration
The **Full** version includes an integrated Cloudflare WARP client to bypass IP-based blocks. When enabled, all outgoing traffic (including FlareSolverr and Byparr) is automatically routed through the Cloudflare network.

**Requirements:**
To function correctly, the container needs elevated network permissions:
- **Docker Compose:** Handled automatically in the provided `docker-compose.yml`.
- **Docker Run:** You must add `--cap-add=NET_ADMIN --device /dev/net/tun`.

**Example command:**
```bash
docker run -d --name easyproxy --cap-add=NET_ADMIN --device /dev/net/tun -e ENABLE_WARP=true -p 7860:7860 ghcr.io/realbestia1/easyproxy:full
```

---

## 📖 API Usage
For detailed API documentation and testing, use the built-in **Interactive Docs** available at:
- `http://localhost:7860/docs` (Swagger UI)
- `http://localhost:7860/redoc` (ReDoc)

### 📺 Streaming Proxy
Prefix any stream URL with the proxy endpoint to handle headers and DRM.
```
http://localhost:7860/proxy/manifest.m3u8?url=<URL>
```
**Options:**
- `&clearkey=KID:KEY`: Provide keys for DASH streams.
- `&h_<Header Name>=<Value>`: Pass custom headers (e.g., `&h_User-Agent=VLC`).

### 🔍 Stream Extractor
Extract direct video links from supported websites.
```
http://localhost:7860/extractor/video?d=<URL>&redirect_stream=true
```
*Tip: Open `http://localhost:7860/extractor` in your browser for a list of all parameters and supported hosts.*

### 📼 DVR & Recordings
Manage your recordings via the `/recordings` web UI or API.
- `/record?url=<URL>&name=<NAME>`: Start recording and watch simultaneously.
- `/api/recordings/start`: Trigger a background recording.

---

## 🛠️ Integrated Tools
- **Playlist Builder** (`/builder`): A visual tool to create custom M3U playlists with proxied links.
- **Server Info** (`/info`): Check status, public IP, and version information.

---

## 🤝 Contributing
Contributions are welcome!
1. **Fork** the repository.
2. **Commit** your changes (features, extractors, or bug fixes).
3. **Open a Pull Request** to the main branch.

*Found a bug? Open an [Issue](https://github.com/realbestia1/EasyProxy/issues)!*

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

<div align="center">
  <p><b>⭐ If this project helped you, please give it a star! ⭐</b></p>
</div>

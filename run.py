#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Runner cho Video2X FastAPI Web UI.
Hỗ trợ chạy cục bộ hoặc tạo Cloudflare Tunnel công khai khi chạy trên Kaggle/Colab.
"""

import os
import sys
import time
import shutil
import urllib.request
import argparse
import subprocess
import uvicorn


def setup_cloudflare_tunnel(port: int) -> subprocess.Popen:
    """Tải và khởi chạy Cloudflare Tunnel (cloudflared) để tạo link HTTPS công khai miễn phí."""
    binary_name = "cloudflared.exe" if os.name == "nt" else "cloudflared"
    cloudflared_path = shutil.which(binary_name) or os.path.abspath(f"./{binary_name}")

    if not os.path.exists(cloudflared_path) and not shutil.which(binary_name):
        print("🌐 Đang tải Cloudflare Tunnel (cloudflared)...")
        if os.name == "nt":
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        else:
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"

        try:
            urllib.request.urlretrieve(url, cloudflared_path)
            if os.name != "nt":
                os.chmod(cloudflared_path, 0o755)
            print("✅ Tải cloudflared thành công!")
        except Exception as e:
            print(f"⚠️ Không thể tải cloudflared: {e}")
            return None

    print(f"📡 Đang mở đường truyền công khai cho cổng {port}...")
    cmd = [cloudflared_path, "tunnel", "--url", f"http://127.0.0.1:{port}"]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Lọc tìm URL public
        tunnel_url = None
        start = time.time()
        while time.time() - start < 15:
            line = proc.stdout.readline()
            if line:
                if "trycloudflare.com" in line:
                    for part in line.split():
                        if "trycloudflare.com" in part and part.startswith("http"):
                            tunnel_url = part.strip()
                            break
                    if tunnel_url:
                        break

        if tunnel_url:
            print("\n" + "=" * 65)
            print(f"🚀 GIAO DIỆN WEB CÔNG KHAI ĐÃ SẴN SÀNG:")
            print(f"👉 {tunnel_url}")
            print("=" * 65 + "\n")
        else:
            print("⚠️ Chưa bắt được URL Cloudflare. Hãy kiểm tra terminal output bên dưới.")

        return proc
    except Exception as e:
        print(f"⚠️ Lỗi khởi động Cloudflare Tunnel: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Khởi chạy Video2X FastAPI Web UI")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Địa chỉ host lắng nghe (mặc định: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=7860, help="Cổng máy chủ (mặc định: 7860)")
    parser.add_argument("--share", action="store_true", help="Tạo link HTTPS công khai (Cloudflare Tunnel)")
    parser.add_argument("--reload", action="store_true", help="Chế độ Auto-Reload khi phát triển")
    args = parser.parse_args()

    # Tự động bật share khi phát hiện môi trường Kaggle
    is_kaggle = os.path.exists("/kaggle")
    should_share = args.share or is_kaggle

    tunnel_proc = None
    if should_share:
        tunnel_proc = setup_cloudflare_tunnel(args.port)

    print("\n" + "=" * 65)
    print(f"🎬 Video2X FastAPI Web UI đang chạy tại: http://{args.host}:{args.port}")
    print(f"📁 Thư mục Templates: app/views/templates")
    print(f"🎨 Framework: TailwindCSS CDN + Lucide Icons CDN")
    print("=" * 65 + "\n")

    try:
        uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)
    finally:
        if tunnel_proc and tunnel_proc.poll() is None:
            tunnel_proc.terminate()


if __name__ == "__main__":
    main()

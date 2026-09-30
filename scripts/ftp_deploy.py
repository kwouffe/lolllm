#!/usr/bin/env python3
"""Deploy site/ to OVHCloud FTP via HTTP CONNECT proxy tunnel."""

import ftplib
import os
import socket
import sys
from pathlib import Path

FTP_HOST = os.environ.get("FTP_HOST", "ftp.cluster129.hosting.ovh.net")
FTP_PORT = int(os.environ.get("FTP_PORT", "21"))
FTP_USER = os.environ["FTP_USER"]
FTP_PASS = os.environ["FTP_PASS"]
PROXY_HOST = os.environ.get("FTP_PROXY_HOST", "REDACTED-INTERNAL-PROXY")
PROXY_PORT = int(os.environ.get("FTP_PROXY_PORT", "3128"))
SITE_DIR = Path(__file__).parent.parent / "site"
REMOTE_ROOT = "/"


def connect_via_proxy(ftp_host: str, ftp_port: int, proxy_host: str, proxy_port: int) -> socket.socket:
    """Open a raw TCP tunnel through an HTTP CONNECT proxy."""
    s = socket.create_connection((proxy_host, proxy_port), timeout=30)
    connect_req = (
        f"CONNECT {ftp_host}:{ftp_port} HTTP/1.1\r\n"
        f"Host: {ftp_host}:{ftp_port}\r\n"
        f"Proxy-Connection: keep-alive\r\n\r\n"
    )
    s.sendall(connect_req.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk:
            break
        resp += chunk
    first_line = resp.split(b"\r\n")[0].decode()
    if "200" not in first_line:
        raise ConnectionError(f"Proxy CONNECT failed: {first_line}")
    print(f"  Proxy tunnel established → {ftp_host}:{ftp_port}")
    return s


def make_dirs(ftp: ftplib.FTP, remote_path: str) -> None:
    parts = [p for p in remote_path.split("/") if p]
    for i in range(len(parts)):
        d = "/" + "/".join(parts[: i + 1])
        try:
            ftp.mkd(d)
        except ftplib.error_perm:
            pass


def upload_dir(ftp: ftplib.FTP, local_dir: Path, remote_dir: str) -> int:
    count = 0
    for item in sorted(local_dir.iterdir()):
        remote_path = f"{remote_dir}/{item.name}".replace("//", "/")
        if item.is_dir():
            make_dirs(ftp, remote_path)
            count += upload_dir(ftp, item, remote_path)
        else:
            with item.open("rb") as f:
                ftp.storbinary(f"STOR {remote_path}", f)
            print(f"  ↑ {remote_path}")
            count += 1
    return count


def main() -> None:
    print(f"Connecting via proxy {PROXY_HOST}:{PROXY_PORT} → {FTP_HOST}:{FTP_PORT}")
    try:
        sock = connect_via_proxy(FTP_HOST, FTP_PORT, PROXY_HOST, PROXY_PORT)
        ftp = ftplib.FTP()
        ftp.connect(source_address=None)  # placeholder, we override below
        ftp.sock = sock
        ftp.file = sock.makefile("r", encoding="latin-1")
        ftp.welcome = ftp.getresp()
        print(f"  {ftp.welcome.strip()}")
    except Exception as e:
        print(f"Proxy tunnel failed ({e}), trying direct connection...")
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=30)

    ftp.login(FTP_USER, FTP_PASS)
    ftp.set_pasv(True)
    print(f"  Logged in as {FTP_USER}")
    print(f"  Uploading {SITE_DIR} → {FTP_HOST}{REMOTE_ROOT}")

    count = upload_dir(ftp, SITE_DIR, REMOTE_ROOT)
    ftp.quit()
    print(f"\nDone — {count} file(s) uploaded.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess

def run_ampy(port, *args):
    cmd = ["ampy", "--port", port] + list(args)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc

def make_remote_dir(port, remote_dir):
    # ignore "File exists" errors
    res = run_ampy(port, "mkdir", remote_dir)
    if res.returncode != 0 and "exists" not in res.stderr.lower():
        print(f"[!] mkdir {remote_dir} failed: {res.stderr.strip()}", file=sys.stderr)

def put_file(port, local_path, remote_path):
    res = run_ampy(port, "put", local_path, remote_path)
    if res.returncode != 0:
        print(f"[!] put {local_path} → {remote_path} failed: {res.stderr.strip()}", file=sys.stderr)

def main():
    p = argparse.ArgumentParser(description="Upload entire project to ESP32 via ampy")
    p.add_argument("--port",    "-p", required=True, help="Serial port (e.g. /dev/ttyUSB0)")
    p.add_argument("--src",     "-s", default=".",    help="Local project root")
    p.add_argument("--exclude", "-e", action="append",
                   help="Filename patterns to skip (can repeat)")
    args = p.parse_args()

    port = args.port
    src_root = os.path.abspath(args.src)
    me = os.path.basename(__file__)

    for dirpath, dirnames, filenames in os.walk(src_root):
        # compute remote directory path
        rel_dir = os.path.relpath(dirpath, src_root)
        if rel_dir == ".":
            remote_dir = "/"
        else:
            remote_dir = "/" + rel_dir.replace(os.sep, "/")
            make_remote_dir(port, remote_dir)

        for fn in filenames:
            if fn == me:
                continue
            if args.exclude and any(fn.endswith(pat) for pat in args.exclude):
                continue

            local_file  = os.path.join(dirpath, fn)
            # remote path: join remote_dir + filename
            if remote_dir == "/":
                remote_file = "/" + fn
            else:
                remote_file = remote_dir + "/" + fn

            print(f"→ uploading {local_file} → {remote_file}")
            put_file(port, local_file, remote_file)

    print("Done.")

if __name__ == "__main__":
    main()

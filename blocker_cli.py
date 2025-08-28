import os
import psutil
import time
import subprocess
import threading
import argparse
from datetime import datetime, timedelta

# Path to hosts file (Windows)
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT = "127.0.0.1"
STATE_FILE = "blocker_state.txt"

blocked_websites = []
blocked_apps = []
running = True
end_time = None


def expand_website_variants(website: str):
    website = website.strip().lower()
    website = website.replace("https://", "").replace("http://", "").replace("www.", "")
    return [f"{website}.com", f"www.{website}.com"]


def expand_app_variants(app: str):
    app = app.strip()
    base = app.replace(".exe", "")
    return [f"{base}.exe", f"{base.capitalize()}.exe", f"{base.lower()}.exe"]


def block_websites():
    while running:
        with open(HOSTS_PATH, "r+") as file:
            content = file.read()
            for website in blocked_websites:
                if website not in content:
                    file.write(f"{REDIRECT} {website}\n")
        time.sleep(5)


def block_apps():
    while running:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in blocked_apps:
                    proc.kill()
                    print(f"Killed {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        time.sleep(3)


def unblock_websites():
    if not blocked_websites:
        return
    with open(HOSTS_PATH, "r") as file:
        lines = file.readlines()
    with open(HOSTS_PATH, "w") as file:
        for line in lines:
            if not any(website in line for website in blocked_websites):
                file.write(line)
    subprocess.run("ipconfig /flushdns", shell=True)
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


def timer_countdown(minutes):
    global running, end_time
    end_time = datetime.now() + timedelta(minutes=minutes)

    # Save end time for status check
    with open(STATE_FILE, "w") as f:
        f.write(end_time.strftime("%Y-%m-%d %H:%M:%S"))

    seconds = minutes * 60
    while seconds > 0 and running:
        mins, secs = divmod(seconds, 60)
        print(f"\rTime left: {mins:02d}:{secs:02d}", end="")
        time.sleep(1)
        seconds -= 1

    running = False
    unblock_websites()
    print("\nTime's up! Blocking stopped.")


def show_status():
    if not os.path.exists(STATE_FILE):
        print("No active blocking session.")
        return

    with open(STATE_FILE, "r") as f:
        end_str = f.read().strip()
        end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")

    remaining = end_time - datetime.now()
    if remaining.total_seconds() <= 0:
        print("No active blocking session.")
    else:
        mins, secs = divmod(int(remaining.total_seconds()), 60)
        print(f"Blocking active. Time left: {mins:02d}:{secs:02d}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Website & App Blocker")
    parser.add_argument("--sites", type=str, default="", help="Comma separated websites (e.g. instagram,facebook)")
    parser.add_argument("--apps", type=str, default="", help="Comma separated applications (e.g. chrome,steam)")
    parser.add_argument("--time", type=int, help="Blocking duration in minutes")
    parser.add_argument("--unblock", action="store_true", help="Unblock immediately and stop blocking")
    parser.add_argument("--status", action="store_true", help="Show remaining time")

    args = parser.parse_args()

    if args.unblock:
        unblock_websites()
        print("Websites and apps unblocked immediately.")
        exit(0)

    if args.status:
        show_status()
        exit(0)

    if not args.time:
        print("Error: --time is required when starting a blocking session.")
        exit(1)

    if args.sites:
        for site in args.sites.split(","):
            blocked_websites.extend(expand_website_variants(site.strip()))

    if args.apps:
        for app in args.apps.split(","):
            blocked_apps.extend(expand_app_variants(app.strip()))

    print("\nBlocking started...")
    print(f"Websites: {blocked_websites}")
    print(f"Applications: {blocked_apps}")
    print(f"Duration: {args.time} minutes\n")

    # Start blocking
    threading.Thread(target=block_websites, daemon=True).start()
    threading.Thread(target=block_apps, daemon=True).start()
    timer_countdown(args.time)
# Website & App Blocker (Command Line)

A simple Python script to block **websites** and **applications** for a fixed duration, similar to Cold Turkey.  
It works by editing the Windows **hosts file** to block websites and killing blocked applications using **psutil**.

---

## Features
- Block websites across all browsers  
- Block applications (kills running processes)  
- Set blocking duration with a timer
- Automatically unblocks when the timer ends  
- Manual **unblock immediately** option
- Check remaining time with `--status`
  

---
## Commands
- python blocker_cli.py --sites youtube,twitter,facebook,instagram,twitch --apps steam,discord --time 60
- python blocker_cli.py --status
- python blocker_cli.py --unblock

## Requirements
- Python 3.7+  
- Install dependencies:
- On Windows, you must run this script as Administrator because it modifies the hosts file.
```bash


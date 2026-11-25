#!/usr/bin/env python3
"""
Unofficial Linux driver for the Ocypus Gamma A40 Digital display
(USB 1a2c:434d).

EXPERIMENTAL SOFTWARE, provided "as is" without warranty of any kind. Use at
your own risk. Not affiliated with Ocypus. See README.md for the disclaimer.

The frame format was taken from a USB capture of the official Ocypus Digital
software: Output report ID 0x07 on interface 1, 64 bytes in total, resent once
per second.
    report[0] = 0x07        (Report ID)
    report[1] = 0xFF        (header)
    report[2] = 0xFF        (header)
    report[3] = 0x00        (unknown, always 0 in captures)
    report[4] = tens digit of the temperature
    report[5] = ones digit of the temperature
    rest      = 0x00

Usage:
  sudo python ocypus_gamma.py            # show the CPU temperature
  sudo python ocypus_gamma.py --test 43  # show the number 43 for 15 seconds
"""
import argparse
import glob
import sys
import time

import hid

VID, PID, IFACE = 0x1A2C, 0x434D, 1
REPORT_ID = 0x07
REPORT_LEN = 64
INTERVAL = 1.0


def find_cpu_sensor():
    """Find the AMD (k10temp) or Intel (coretemp) sensor in /sys/class/hwmon."""
    for name_file in sorted(glob.glob("/sys/class/hwmon/hwmon*/name")):
        try:
            name = open(name_file).read().strip()
        except OSError:
            continue
        if name in ("k10temp", "coretemp"):
            base = name_file.rsplit("/", 1)[0]
            return base + "/temp1_input"
    return None


def read_temp(path):
    with open(path) as f:
        return int(f.read().strip()) / 1000.0


def make_frame(temp):
    value = max(0, min(99, int(round(temp))))
    frame = [0] * REPORT_LEN
    frame[0] = REPORT_ID
    frame[1] = 0xFF
    frame[2] = 0xFF
    frame[4] = value // 10
    frame[5] = value % 10
    return frame


def open_dev():
    for info in hid.enumerate(VID, PID):
        if info.get("interface_number") == IFACE:
            dev = hid.device()
            dev.open_path(info["path"])
            return dev
    sys.exit("Cooler (interface 1) not found. Run with sudo and make sure no "
             "virtual machine has the device attached.")


def send(dev, temp):
    n = dev.write(make_frame(temp))
    if n < 0:
        raise OSError("device rejected the report")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", type=int, metavar="N",
                    help="show the number N (0-99) for 15 seconds and exit")
    args = ap.parse_args()

    dev = open_dev()
    try:
        if args.test is not None:
            print(f"Sending {args.test} for 15 seconds. What does the cooler show?")
            end = time.time() + 15
            while time.time() < end:
                send(dev, args.test)
                time.sleep(INTERVAL)
            return

        sensor = find_cpu_sensor()
        if not sensor:
            sys.exit("No CPU temperature sensor found in /sys/class/hwmon")
        print(f"Sensor: {sensor}. Stop with Ctrl+C")
        while True:
            temp = read_temp(sensor)
            send(dev, temp)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            send(dev, 0)
        finally:
            dev.close()


if __name__ == "__main__":
    main()

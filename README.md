[README.md](https://github.com/user-attachments/files/35409558/README.md)
# ocypus-gamma-linux

Unofficial Linux driver for the temperature display of the **Ocypus Gamma A40 ARGB WH
(Digital)** CPU cooler (USB `1a2c:434d`). Ocypus only ships a Windows program;
this small script shows your CPU temperature on the cooler under Linux.


Developed by cruprs12 with the assistance of Claude (Anthropic).
The protocol was reverse-engineered and verified on real hardware by the author.



[Protocol description](PROTOCOL.md)

> **EXPERIMENTAL SOFTWARE.** Read the [Disclaimer](#disclaimer) before use.

## What it does

- Reads the CPU temperature (`k10temp` for AMD, `coretemp` for Intel) from
  `/sys/class/hwmon`.
- Sends it to the cooler once per second as a 64-byte HID output report.
- Shows the value in whatever unit the cooler shows by default (°C in testing).

Not supported: GPU temperature, usage, °C/°F selection, lighting.

## Install

Requires Python 3 and the `hidapi` Python module (`import hid`).

```bash
sudo mkdir -p /opt/ocypus-gamma
sudo python -m venv /opt/ocypus-gamma/venv
sudo /opt/ocypus-gamma/venv/bin/pip install hidapi
sudo cp ocypus_gamma.py /opt/ocypus-gamma/
```

On some systems building `hidapi` needs the system libraries `libusb` and
`hidapi` (Arch: `pacman -S libusb hidapi`).

Test that the display reacts (shows `43` for 15 seconds):

```bash
sudo /opt/ocypus-gamma/venv/bin/python /opt/ocypus-gamma/ocypus_gamma.py --test 43
```

Run it for real (Ctrl+C to stop):

```bash
sudo /opt/ocypus-gamma/venv/bin/python /opt/ocypus-gamma/ocypus_gamma.py
```

Start at boot:

```bash
sudo cp ocypus-gamma.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ocypus-gamma.service
```

## Notes

- The service runs as root, because it needs access to the USB device. A udev
  rule plus an unprivileged user or systemd sandboxing would be a good
  improvement (not done yet).
- If the display stays dark, check `systemctl status ocypus-gamma.service`
  and that no virtual machine has the cooler attached.

## Help wanted

See "Not known yet" in [PROTOCOL.md](PROTOCOL.md): °C/°F selection, hundreds
digit, other models. Pull requests and USB captures welcome.

## Disclaimer

This project is **experimental** and is provided **"as is", without warranty of
any kind**, express or implied. It was created by reverse engineering and has
been tested on a single device only (Ocypus Gamma A40 Digital on Arch Linux
with an AMD CPU). It sends data to a USB device and its service runs with root
privileges.

**The author is not responsible and accepts no liability for any damage, data
loss, hardware malfunction, or any other harm** resulting from the use or
misuse of this software or its documentation. You use it entirely **at your
own risk**.

This project is **not affiliated with, endorsed by, or supported by Ocypus**.
"Ocypus" and "Gamma A40" are used only to identify the compatible device and
belong to their respective owners. Using this software may void your warranty.

## License

MIT, see [LICENSE](LICENSE).

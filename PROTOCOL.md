# Ocypus Gamma A40 Digital — display protocol

Reverse-engineered by capturing USB traffic (usbmon) of the official Windows
software running in a virtual machine with the cooler passed through.
Verified on one device: USB `1a2c:434d` ("USB Gaming Keyboard").

## Device

- Two HID interfaces. The display is on **interface 1**.
- Interface 1 report descriptor: vendor usage page `0xFF01`, report ID `0x07`,
  63 data bytes (Output and Feature both declared). No IN data is useful.
- The host talks to it with control transfers on endpoint 0:
  `SET_REPORT` (bmRequestType `0x21`, bRequest `0x09`), wValue `0x0207`
  (type Output, ID 7), wIndex `1`, wLength `64`. This is what `hidapi`'s
  `write()` produces on Linux.

## Frame (64 bytes, sent once per second)

| Offset | Value | Meaning |
|-------:|:-----:|---------|
| 0 | `0x07` | Report ID |
| 1 | `0xFF` | header |
| 2 | `0xFF` | header |
| 3 | `0x00` | unknown (always 0 in captures) |
| 4 | 0–9 | tens digit |
| 5 | 0–9 | ones digit |
| 6–63 | `0x00` | unused |

Example, 32 degrees: `07 ff ff 00 03 02 00 00 ... 00`.

Observed in the capture:
- With no sensor data the official software sent only the header
  (`07 ff ff 00 00 ...`).
- Switching the official software from °C to °F changed only the digits
  (0 °C became 32); no byte besides offsets 4 and 5 differed.

## Not known yet

- How the display decides between `C` and `F` (nothing in the frame changed
  besides the digits).
- Whether offset 3 is a hundreds digit. The display's maximum is 199.
- What other values do. Sending large or random bytes shows `199C`.
- Other models (Iota A40, AIO pumps) were not tested; their frames may differ.

---
This document is provided "as is", without warranty. It describes
observations of one device; use it at your own risk. See the Disclaimer in
[README.md](README.md).

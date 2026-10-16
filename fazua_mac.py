#!/usr/bin/env python3
"""macOS/Linux port of FazuaUnlocker (quezzas/FazuaUnlocker, MIT).

Only the Win32 HID transport is replaced by hidapi. Protocol, CRC, packet
builders and the read/write flow are imported unchanged from fazua_unlock.py.

  python fazua_mac.py --read-only        # read config, no writes
  python fazua_mac.py 35 --dry-run       # show the write packet, send nothing
"""
import sys

import hid
import fazua_unlock as fu


class MacFazuaHID:
    """hidapi transport with the same interface as fu.FazuaHID."""

    def __init__(self):
        self.dev = None
        self.path = "hidapi"

    def open(self):
        devs = hid.enumerate(fu.FAZUA_VID, fu.FAZUA_PID)
        if not devs:
            raise RuntimeError("No Fazua HID device (10C4:1001). Plugged in, battery on?")
        if len(devs) > 1:
            raise RuntimeError("Multiple Fazua HID devices - ambiguous.")
        self.dev = hid.device()
        self.dev.open_path(devs[0]["path"])
        self.dev.set_nonblocking(False)

    def close(self):
        if self.dev:
            self.dev.close()
            self.dev = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *a):
        self.close()

    def set_num_input_buffers(self, n=64):
        pass  # Windows-only IOCTL; hidapi on macOS queues reports itself

    def write(self, data: bytes, timeout_ms: int = 1000) -> int:
        if len(data) != fu.PACKET_LEN:
            raise ValueError(f"expected {fu.PACKET_LEN} bytes, got {len(data)}")
        # data[0] is the HID report ID (0x00), same convention as Win32 WriteFile.
        n = self.dev.write(list(data))
        if n < 0:
            raise OSError("hid write failed")
        return n

    def read(self, timeout_ms: int = 1000) -> bytes:
        r = self.dev.read(fu.PACKET_LEN, timeout_ms)
        if not r:
            raise TimeoutError(f"ReadFile timed out after {timeout_ms}ms")
        b = bytes(r)
        # hidapi on macOS strips report ID 0; Windows ReadFile includes it.
        if len(b) == fu.PACKET_LEN - 1:
            b = b"\x00" + b
        if len(b) != fu.PACKET_LEN:
            raise fu.ProtocolError(f"short HID read: got {len(b)} bytes: {b.hex()}")
        return b


fu.FazuaHID = MacFazuaHID
fu._find_device_path = lambda: "hidapi"

if __name__ == "__main__":
    sys.exit(fu.main())

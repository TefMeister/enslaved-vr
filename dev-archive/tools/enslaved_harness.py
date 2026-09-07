#!/usr/bin/env python3
"""enslaved_harness.py - drive and observe Enslaved: Odyssey to the West from outside the game.

Written 2026-09-07 for the /lm lane. No harness script survived the 2026-09-02/03
sessions - only their outputs - so this is a rebuild, committed this time.

Traps this works around, all paid for in earlier sessions on this exact game
(see ai-game-control-profiles/profiles/enslaved.json -> hazards):

  * capture with BitBlt from the SCREEN DC, never PrintWindow: PrintWindow serves
    a stale DWM-cached frame the moment the game stops presenting (paused, menu,
    loading) with no error at all.
  * SendInput with SCANCODES; the arrow/navigation block needs
    KEYEVENTF_EXTENDEDKEY or scancode 0x50 is numpad-2 and the menu ignores it
    silently.
  * ESC is NOT a neutral key here - it opens the pause menu and the game stops
    presenting. Read the screen after any key you are not certain about.
  * NEW JOURNEY sits two rows below CONTINUE JOURNEY on the main menu, and
    CHAPTER SELECT resets the last checkpoint. Navigate -> capture -> VERIFY the
    highlight -> only then commit. Never blind key-count past a destructive row.
  * whole-frame mean-luma difference is too blunt to score anything in this game
    (grass and water); use it only as a coarse "is the screen changing" signal.

Usage:
  find                     window handle, title, client rect
  shot PATH                one capture of the client area
  key NAME [count]         scancode key press(es)
  mouse DX DY [steps]      relative mouse movement (camera)
  diff A B                 mean absolute luma difference (coarse motion signal)
  watch N [ms] PREFIX      N captures, report frame-to-frame difference series
"""
import ctypes
import ctypes.wintypes as wt
import sys
import time

user32 = ctypes.WinDLL("user32", use_last_error=True)
TITLE_SUBSTR = "enslav"

KEYS = {
    "ENTER": (0x1C, False), "ESC": (0x01, False), "ESCAPE": (0x01, False),
    "SPACE": (0x39, False), "TAB": (0x0F, False),
    "UP": (0x48, True), "DOWN": (0x50, True), "LEFT": (0x4B, True), "RIGHT": (0x4D, True),
    "W": (0x11, False), "A": (0x1E, False), "S": (0x1F, False), "D": (0x20, False),
    "E": (0x12, False), "Q": (0x10, False), "F": (0x21, False),
    "F1": (0x3B, False), "F2": (0x3C, False), "F3": (0x3D, False), "F4": (0x3E, False),
    "F5": (0x3F, False), "F6": (0x40, False), "F7": (0x41, False), "F8": (0x42, False),
    "F9": (0x43, False), "F10": (0x44, False), "F11": (0x57, False), "F12": (0x58, False),
}

KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP, KEYEVENTF_SCANCODE = 0x0001, 0x0002, 0x0008
MOUSEEVENTF_MOVE = 0x0001
INPUT_KEYBOARD, INPUT_MOUSE = 1, 0


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD), ("dwFlags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ctypes.POINTER(wt.ULONG))]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wt.LONG), ("dy", wt.LONG), ("mouseData", wt.DWORD),
                ("dwFlags", wt.DWORD), ("time", wt.DWORD),
                ("dwExtraInfo", ctypes.POINTER(wt.ULONG))]


class _IU(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("pad", ctypes.c_byte * 32)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wt.DWORD), ("u", _IU)]


def _send_key(scan, ext, up):
    f = KEYEVENTF_SCANCODE | (KEYEVENTF_EXTENDEDKEY if ext else 0) | (KEYEVENTF_KEYUP if up else 0)
    i = INPUT(type=INPUT_KEYBOARD, u=_IU(ki=KEYBDINPUT(0, scan, f, 0, None)))
    if user32.SendInput(1, ctypes.byref(i), ctypes.sizeof(INPUT)) != 1:
        raise OSError("SendInput key failed: %d" % ctypes.get_last_error())


def _send_mouse(dx, dy):
    i = INPUT(type=INPUT_MOUSE, u=_IU(mi=MOUSEINPUT(int(dx), int(dy), 0, MOUSEEVENTF_MOVE, 0, None)))
    if user32.SendInput(1, ctypes.byref(i), ctypes.sizeof(INPUT)) != 1:
        raise OSError("SendInput mouse failed: %d" % ctypes.get_last_error())


def find_window():
    out = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            n = user32.GetWindowTextLengthW(hwnd)
            if n:
                b = ctypes.create_unicode_buffer(n + 1)
                user32.GetWindowTextW(hwnd, b, n + 1)
                if TITLE_SUBSTR in b.value.lower():
                    out.append((hwnd, b.value))
        return True

    user32.EnumWindows(cb, 0)
    return out


def need_window():
    w = find_window()
    if not w:
        sys.exit("NO WINDOW matching %r - is the game running?" % TITLE_SUBSTR)
    return w[0]


def client_rect(hwnd):
    r = wt.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(r))
    p = wt.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(p))
    return (p.x, p.y, p.x + r.right, p.y + r.bottom)


def focus(hwnd):
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    return user32.GetForegroundWindow() == hwnd


def press(name, count=1, hold=0.09, gap=0.22):
    hwnd, _ = need_window()
    if not focus(hwnd):
        print("WARN: could not foreground the window; input may go elsewhere")
    scan, ext = KEYS[name.upper()]
    for _ in range(count):
        _send_key(scan, ext, False)
        time.sleep(hold)
        _send_key(scan, ext, True)
        time.sleep(gap)


def grab(path=None):
    from PIL import ImageGrab
    hwnd, _ = need_window()
    focus(hwnd)
    img = ImageGrab.grab(bbox=client_rect(hwnd), all_screens=True)
    if path:
        img.save(path)
    return img


def luma_diff(a, b):
    import numpy as np
    A = np.asarray(a.convert("L"), dtype=np.float64)
    B = np.asarray(b.convert("L"), dtype=np.float64)
    if A.shape != B.shape:
        return float("nan")
    return float(np.abs(A - B).mean())


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    c = sys.argv[1]

    if c == "find":
        w = find_window()
        for h, t in w:
            print("hwnd=0x%X  title=%r  client=%s" % (h, t, client_rect(h)))
        if not w:
            print("NO WINDOW matching %r" % TITLE_SUBSTR)

    elif c == "shot":
        grab(sys.argv[2])
        print("saved", sys.argv[2])

    elif c == "key":
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        press(sys.argv[2], n)
        print("sent %s x%d" % (sys.argv[2], n))

    elif c == "mouse":
        dx, dy = int(sys.argv[2]), int(sys.argv[3])
        steps = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        hwnd, _ = need_window()
        focus(hwnd)
        for _ in range(steps):
            _send_mouse(dx, dy)
            time.sleep(0.02)
        print("mouse %+d,%+d x%d" % (dx, dy, steps))

    elif c == "diff":
        from PIL import Image
        print("%.3f" % luma_diff(Image.open(sys.argv[2]), Image.open(sys.argv[3])))

    elif c == "watch":
        n = int(sys.argv[2])
        iv = float(sys.argv[3]) / 1000.0 if len(sys.argv) > 3 else 0.4
        prefix = sys.argv[4] if len(sys.argv) > 4 else None
        prev, series = None, []
        for i in range(n):
            img = grab("%s%02d.png" % (prefix, i) if prefix else None)
            if prev is not None:
                series.append(luma_diff(prev, img))
            prev = img
            time.sleep(iv)
        print("frame-to-frame luma diff series:")
        print("  " + " ".join("%.1f" % v for v in series))
        if series:
            import statistics
            print("  mean %.2f  max %.2f  min %.2f"
                  % (statistics.mean(series), max(series), min(series)))

    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()

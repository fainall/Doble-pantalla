import ctypes
from ctypes import wintypes

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000

INPUT_MOUSE = 0

SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


class _INPUTunion(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTunion)]


user32 = ctypes.windll.user32


def _virtual_rect():
    return (
        user32.GetSystemMetrics(SM_XVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_YVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_CXVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_CYVIRTUALSCREEN),
    )


def _send(x, y, flags):
    vx, vy, vw, vh = _virtual_rect()
    # 65535 = absolute coord max for virtual desktop range
    nx = int((x - vx) * 65535 / max(1, vw - 1))
    ny = int((y - vy) * 65535 / max(1, vh - 1))
    inp = INPUT(
        type=INPUT_MOUSE,
        u=_INPUTunion(
            mi=MOUSEINPUT(
                dx=nx, dy=ny, mouseData=0,
                dwFlags=flags | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK,
                time=0, dwExtraInfo=None,
            )
        ),
    )
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def mouse_move(x, y):
    _send(x, y, MOUSEEVENTF_MOVE)


def mouse_down(x, y):
    _send(x, y, MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTDOWN)


def mouse_up(x, y):
    _send(x, y, MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTUP)

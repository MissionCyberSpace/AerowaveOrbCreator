"""
Aerowave Orb Creator
====================
Keep these files next to this script (or inside an "assets" folder beside it):

    aerowave.png, orbcreator.png, Orangeorb.png      - the three logo components
    orbcreatorjingle.wav                              - intro jingle
    saved.wav                                         - "orb saved" sound
    darkbutton.png, ecobutton.png, aquabutton.png,
    dorficbutton.png                                  - UI selector orbs
    exittext.png, exitjingle.wav                      - exit animation

The chosen UI theme, the last folder you saved to and your 10 most recent colours are
remembered in config.aero
(created next to this script).
Requires: Pillow, numpy   ->   pip install pillow numpy
"""
import os
import sys
import json
import math
import time
import wave
import colorsys
import subprocess
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFilter, ImageTk, ImageChops, ImageFont, ImageEnhance

try:
    from PIL import ImageGrab
except Exception:                                   # pragma: no cover
    ImageGrab = None

try:
    import numpy as np
    HAVE_NUMPY = True
except Exception:                                   # pragma: no cover
    np = None
    HAVE_NUMPY = False

try:
    import winsound
except ImportError:                                 # not on Windows
    winsound = None

APP_NAME = "Aerowave Orb Creator"
CONFIG_NAME = "config.aero"

THEMES = {
    "Dark": {
        "ui_top": "#2b2b2b", "ui_bot": "#2b2b2b",
        "layer_top": "#3a3a3a", "layer_bot": "#3a3a3a",
        "btn_top": (74, 74, 74), "btn_bot": (58, 58, 58), "btn_mid": None, "btn_outline": None,
        "btn_fg": "white", "radius": 5, "fg": "white", 
        "layer_bg": "#4a4a4a", "layer_sel": "#5a7fa0", "panel_bg": "#2b2b2b"
    },
    "Aqua": {
        "ui_top": "#c8e0e0", "ui_bot": "#28a4c0",
        "layer_top": "#28a4c0", "layer_bot": "#c8e0e0",
        "btn_top": (240, 252, 248), "btn_bot": (64, 156, 176), "btn_mid": (120, 200, 216), "btn_outline": (8, 96, 120),
        "btn_fg": "black", "radius": 15, "fg": "black", 
        "layer_bg": "#79CBE8", "layer_sel": "#D2F0F9", "panel_bg": None
    },
    "Eco": {
        "ui_top": "#c5d7bd", "ui_bot": "#73a663",
        "layer_top": "#73a663", "layer_bot": "#c5d7bd",
        "btn_top": (158, 207, 141), "btn_bot": (76, 125, 59), "btn_mid": None, "btn_outline": (36, 125, 0),
        "btn_fg": "white", "radius": 8, "fg": "black", 
        "layer_bg": "#90B971", "layer_sel": "#407323", "panel_bg": None
    },
    # DORFic = Daylight, Orange, Red, Futurism, Graphic: white/grey surfaces with vivid orange accents (Special Thanks to Richard Likes Computers for information help on the aesthetic colours and design)
    "DORFic": {
        "ui_top": "#F7F8FA", "ui_bot": "#BCC1C9",
        "layer_top": "#FF7A1A", "layer_bot": "#FFB468",
        "btn_top": (255, 178, 96), "btn_bot": (214, 82, 0), "btn_mid": (255, 124, 28), "btn_outline": (150, 56, 0),
        "btn_fg": "white", "radius": 9, "fg": "#23262B",
        "layer_bg": "#F2F3F6", "layer_sel": "#FF6600", "layer_fg": "#2A2D33", "layer_sel_fg": "white",
        "panel_bg": None, "decor": "dorfic"
    }
}

# Order + artwork used by the UI Selector drop-down
THEME_ORDER = ["Dark", "Eco", "Aqua", "DORFic"]
THEME_ORBS = {"Dark": "darkbutton.png", "Eco": "ecobutton.png", "Aqua": "aquabutton.png", "DORFic": "dorficbutton.png"}

# Frosted "Aero glass" look of the drop-down and the pop-ups, per UI theme
GLASS = {
    "Dark": dict(tint=(16, 18, 22), tint_a=0.62, tint_grad=0.22, blur=10, gloss=0.16, shadow=165,
                 border_dark=190, border_light=110, text=(255, 255, 255), sub=(190, 198, 212),
                 accent=(96, 165, 240), dim=0.52, pill=(255, 255, 255),
                 entry_bg="#1E2024", entry_fg="#F2F2F2", edge="#585D66", list_bg="#1B1D21", list_alt="#22252A",
                 list_fg="#E8E8E8", list_sel="#3F73B0", list_sel_fg="#FFFFFF", list_head="#2B2E34"),
    "Aqua": dict(tint=(170, 228, 240), tint_a=0.50, tint_grad=0.16, blur=10, gloss=0.34, shadow=120,
                 border_dark=130, border_light=210, text=(6, 48, 66), sub=(22, 86, 106),
                 accent=(0, 165, 215), dim=0.70, pill=(255, 255, 255),
                 entry_bg="#F2FBFD", entry_fg="#06303F", edge="#3FA0BC", list_bg="#EEF9FC", list_alt="#E0F3F8",
                 list_fg="#06303F", list_sel="#0A8FB5", list_sel_fg="#FFFFFF", list_head="#BEE3EC"),
    "Eco": dict(tint=(150, 205, 130), tint_a=0.52, tint_grad=0.16, blur=10, gloss=0.30, shadow=130,
                border_dark=140, border_light=200, text=(14, 52, 10), sub=(36, 86, 26),
                accent=(46, 165, 24), dim=0.68, pill=(255, 255, 255),
                entry_bg="#F4FAF0", entry_fg="#14320E", edge="#5E9A45", list_bg="#F1F8EC", list_alt="#E6F1DE",
                list_fg="#14320E", list_sel="#407323", list_sel_fg="#FFFFFF", list_head="#C5DBB9"),
    "DORFic": dict(tint=(244, 246, 250), tint_a=0.60, tint_grad=0.14, blur=10, gloss=0.42, shadow=120,
                   border_dark=125, border_light=235, text=(34, 37, 43), sub=(112, 118, 130),
                   accent=(255, 102, 0), dim=0.72, pill=(255, 255, 255),
                   entry_bg="#FFFFFF", entry_fg="#22252B", edge="#B0B5BE", list_bg="#FAFAFC", list_alt="#F0F1F4",
                   list_fg="#22252B", list_sel="#FF6600", list_sel_fg="#FFFFFF", list_head="#E3E5EA"),
}


# ======================================================================================
#  Files, config, sound
# ======================================================================================
def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def asset_path(name):
    """Find a bundled file next to the program, in ./assets, or inside a PyInstaller bundle."""
    folders = [app_dir(), os.path.join(app_dir(), "assets")]
    if getattr(sys, "_MEIPASS", None):
        folders += [sys._MEIPASS, os.path.join(sys._MEIPASS, "assets")]
    folders.append(os.getcwd())
    for f in folders:
        p = os.path.join(f, name)
        if os.path.isfile(p):
            return p
    return None


def _config_locations():
    locs = [os.path.join(app_dir(), CONFIG_NAME)]
    locs.append(os.path.join(os.path.expanduser("~"), ".aerowave_orb_creator", CONFIG_NAME))
    return locs


def load_config():
    for p in _config_locations():
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            continue
    return {}


def save_config(cfg):
    for p in _config_locations():
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            tmp = p + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            os.replace(tmp, p)
            return True
        except Exception:
            continue
    return False


class Sound:
    """Fire-and-forget WAV playback (winsound on Windows, afplay / aplay elsewhere)."""

    @staticmethod
    def play(path):
        if not path or not os.path.isfile(path):
            return False
        try:
            if winsound is not None:
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return True
            if sys.platform == "darwin":
                subprocess.Popen(["afplay", path])
                return True
            for cmd in (["paplay"], ["aplay", "-q"], ["play", "-q"]):
                try:
                    subprocess.Popen(cmd + [path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    @staticmethod
    def duration(path):
        try:
            with wave.open(path, "rb") as w:
                return w.getnframes() / float(w.getframerate())
        except Exception:
            return 0.0


# ======================================================================================
#  Small helpers
# ======================================================================================
def clamp01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def smooth(x):
    x = clamp01(x)
    return x * x * (3.0 - 2.0 * x)


def ease_out_quart(x):
    x = clamp01(x)
    return 1.0 - (1.0 - x) ** 4


def get_font(size, bold=False):
    names = (["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]
             if bold else ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"])
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except Exception:
            continue
    return ImageFont.load_default()


def hex_to_rgb(h):
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)


# ======================================================================================
#  Live aurora background (all math: ribbons, shafts, caustics, flare, bubbles, i farted)
# ======================================================================================
def _sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def left_geometry(u, t):
    """Top edge and width of the left sweeping green/yellow sheet (u = 0..1 across the screen)."""
    wob = 0.012 * np.sin(5.0 * u + 0.7 * t) + 0.007 * np.sin(11.0 * u - 1.1 * t + 1.3)
    top = 0.30 + 0.56 * np.clip(u / 0.64, 0, 1) ** 1.75 + wob * (1 - u)
    width = 0.06 + 0.50 * (1.0 - np.clip(u / 0.80, 0, 1)) ** 1.4
    return top, width


def right_geometry(v, t):
    """Edge position and width of the thin blue/cyan ribbon on the right (v = 0..1 down the screen)."""
    wob2 = 0.010 * np.sin(4.0 * v - 0.8 * t) + 0.006 * np.sin(9.0 * v + 0.9 * t)
    gx = 1.04 - 0.30 * np.clip(v / 0.98, 0, 1) ** 1.9 + wob2
    wr = 0.020 + 0.075 * _sstep(0.1, 0.95, v)
    return gx, wr


class Aurora:
    """SOFT layer of the aurora (water gradient, light shafts, caustics, glows, bloom).
    Rendered with numpy at a low internal resolution because everything here is naturally blurry.
    The razor-sharp parts (fibre strands, edges, flare streaks, bubbles) are drawn at native resolution
    by AuroraDetail."""

    def __init__(self, w=480, h=270):
        F = np.float32
        self.F = F
        self.w, self.h = int(w), int(h)
        w, h = self.w, self.h
        self.aspect = w / h
        self.u1 = ((np.arange(w) + 0.5) / w).astype(F)
        self.v1 = ((np.arange(h) + 0.5) / h).astype(F)

        # base gradient: green/yellow on the left, blue on the right
        sv = np.array([0.0, 0.40, 0.62, 0.88, 1.0])
        L = np.array([(9, 99, 74), (17, 133, 62), (111, 154, 65), (209, 206, 49), (225, 225, 60)]) / 255.0
        R = np.array([(13, 93, 104), (27, 124, 156), (35, 149, 186), (69, 189, 224), (80, 205, 235)]) / 255.0
        v1 = self.v1.astype(np.float64)
        Lc = np.stack([np.interp(v1, sv, L[:, k]) for k in range(3)], -1).astype(F)
        Rc = np.stack([np.interp(v1, sv, R[:, k]) for k in range(3)], -1).astype(F)
        wl = ((1.0 - self.u1) ** 1.7).astype(F)
        base = Rc[:, None, :] * (1 - wl[None, :, None]) + Lc[:, None, :] * wl[None, :, None]
        belly = np.exp(-((self.u1 - 0.5) / 0.28) ** 2)[None, :, None] * np.array([-0.02, 0.05, 0.0], F)
        self.base = (base + belly).astype(F)

        # low-res caustic grid
        self.hs = int(h * 0.88)
        self.cw, self.ch = max(8, w // 3), max(8, self.hs // 3)
        cu = (np.arange(self.cw) + 0.5) / self.cw
        cv = (np.arange(self.ch) + 0.5) / self.ch * 0.88
        self.cx = np.repeat((cu[None, :] * self.aspect * 2 * math.pi * 0.55).astype(F), self.ch, 0)
        self.cy = np.repeat((cv[:, None] * 2 * math.pi * 0.55).astype(F), self.cw, 1)
        vs = self.v1[:self.hs, None]
        self.cmask = ((1.0 - _sstep(0.35, 0.95, vs)) * (0.35 + 0.65 * _sstep(0.0, 0.5, vs))).astype(F) * np.ones((1, w), F)

        # static 1-D helpers
        u = self.u1
        self.left_w = left_geometry(u, 0.0)[1].astype(F)
        self.left_soft_amp = _sstep(3.0, 6.0, self.left_w * h * 2 * math.pi / 53.0).astype(F)
        self.left_edge_fade = (1.0 - _sstep(0.50, 0.70, u)).astype(F)
        self.left_in_fade = (1.0 - _sstep(0.55, 0.85, u)).astype(F)
        self.floor_prof = _sstep(0.845, 1.0, self.v1).astype(F)

        self.shafts = [   # x, width, strength, phase, slope
            (0.10, 0.060, 0.55, 0.3, 0.05), (0.265, 0.004, 1.10, 1.1, 0.03), (0.285, 0.050, 0.55, 2.0, 0.04),
            (0.42, 0.035, 0.50, 3.1, 0.06), (0.55, 0.075, 0.45, 4.0, 0.10), (0.68, 0.030, 0.40, 5.3, 0.08),
            (0.80, 0.055, 0.45, 0.8, 0.05), (0.93, 0.040, 0.35, 2.7, 0.02),
        ]
        self.c_white = np.array([1.0, 1.0, 0.97], F)
        self.c_green = np.array([0.55, 0.95, 0.32], F)
        self.c_cyan = np.array([0.35, 0.88, 1.0], F)
        # (rgb x layer) mixing matrix with the tone-map constant folded in, and the pre-scaled base colour planes
        self._mix = (np.stack([self.c_white, self.c_green, self.c_cyan], axis=1) * F(-1.55)).astype(F)
        self._base_neg = np.ascontiguousarray((self.base * F(-1.55)).transpose(2, 0, 1)).astype(F)
        self._layers = np.zeros((3, h, w), F)

    # ----------------------------------------------------------------------------
    def _caustics(self, t):
        px, py = self.cx - 250.0, self.cy - 250.0
        ix, iy = px, py
        c = np.ones_like(px)
        inten = 0.006
        for n in range(4):
            tt = t * (1.0 - 3.5 / (n + 1.0))
            ix, iy = px + np.cos(tt - ix) + np.sin(tt + iy), py + np.sin(tt - iy) + np.cos(tt + ix)
            dx = px / (np.sin(ix + tt) / inten + 1e-6)
            dy = py / (np.cos(iy + tt) / inten + 1e-6)
            c += 1.0 / np.sqrt(dx * dx + dy * dy + 1e-9)
        c = c * 0.25
        c = np.abs(1.17 - np.abs(c) ** 1.4)
        c = np.minimum(c ** 8, 1.5)
        im = Image.fromarray(c.astype(self.F), "F").resize((self.w, self.hs), Image.BILINEAR)
        return np.asarray(im, dtype=self.F)

    def _shafts(self, t):
        w, hs = self.w, self.hs
        v = self.v1[:hs, None]
        out = np.zeros((hs, w), self.F)
        for (x, wd, st, ph, sl) in self.shafts:
            wd2 = wd * (1.0 + 0.25 * math.sin(0.31 * t + ph))
            cx0 = x + 0.018 * math.sin(0.23 * t + ph)
            lo = int(max(0, (cx0 - abs(sl) * 0.6 - wd2 * 3.2) * w))
            hi = int(min(w, (cx0 + abs(sl) * 0.6 + wd2 * 3.2) * w) + 1)
            if hi <= lo:
                continue
            uu = self.u1[None, lo:hi]
            cx = cx0 + sl * (v - 0.4)
            g = np.exp(-(((uu - cx) / wd2) ** 2))
            fl = 0.65 + 0.35 * np.sin(v * 9.0 + ph - 0.55 * t) * np.sin(v * 3.1 - 0.27 * t + ph * 2)
            out[:, lo:hi] += g * fl * (st * (0.75 + 0.25 * math.sin(0.4 * t + ph * 1.7)))
        out *= (1.0 - _sstep(0.30, 0.85, self.v1[:hs]))[:, None] * 0.55
        return out

    def _left_sheet(self, t, G, Wl):
        w, h = self.w, self.h
        c1, r0 = int(w * 0.86), int(h * 0.24)
        u = self.u1[None, :c1]
        v = self.v1[r0:, None]
        top = left_geometry(u, t)[0]
        q = (v - top) / self.left_w[None, :c1]
        inside = _sstep(-0.02, 0.06, q) * (1.0 - _sstep(0.55, 1.15, q)) * self.left_in_fade[None, :c1]
        amp = self.left_soft_amp[None, :c1]
        s2 = (0.5 + 0.5 * np.cos(q * 53.0 - 0.6 * t + 1.7)) ** 3
        qc = np.clip(q, 0, 1)
        G[r0:, :c1] += inside * (0.22 + 0.30 * s2 * amp) * (0.45 + 0.95 * qc)
        edge = np.exp(-((q / 0.022) ** 2)) * self.left_edge_fade[None, :c1]
        G[r0:, :c1] += edge * 1.1
        Wl[r0:, :c1] += edge * 0.25

    def _right_ribbon(self, t, C, Wl):
        w = self.w
        c0 = int(w * 0.50)
        u = self.u1[None, c0:]
        v = self.v1[:, None]
        gx, wr = right_geometry(v, t)
        qr = (gx - u) / wr
        gate = _sstep(0.0, 0.25, v)
        inr = _sstep(-0.05, 0.1, qr) * (1.0 - _sstep(0.7, 1.3, qr)) * gate
        amp = _sstep(3.2, 6.5, wr * w * 2 * math.pi / 17.0)
        sr2 = (0.5 + 0.5 * np.cos(qr * 17.0 + 0.7 * t)) ** 3
        C[:, c0:] += inr * (0.14 + 0.30 * sr2 * amp)
        edge = np.exp(-((qr / 0.05) ** 2)) * gate
        C[:, c0:] += edge * 0.85
        Wl[:, c0:] += edge * 0.35

    def _horizon(self, t, Wl, C):
        h = self.h
        r0 = int(h * 0.66)
        u = self.u1[None, :]
        v = self.v1[r0:, None]
        hy = 0.865 + 0.010 * np.sin(6.2 * u + 0.5 * t)
        xm1 = 0.35 + 0.65 * np.exp(-(((u - 0.52) / 0.50) ** 2))
        xm2 = 0.25 + 0.75 * np.exp(-(((u - 0.55) / 0.40) ** 2))
        band = np.exp(-(((v - hy) / 0.020) ** 2)) * xm1
        wide = np.exp(-(((v - hy) / 0.075) ** 2)) * xm2
        Wl[r0:] += band * (1.2 * (0.85 + 0.15 * math.sin(0.9 * t)))
        C[r0:] += wide * 0.55
        Wl[r0:] += self.floor_prof[r0:, None] * 0.20
        bx = 0.54 + 0.02 * math.sin(0.35 * t)
        d2 = ((u - bx) * self.aspect) ** 2 + ((v - 0.875) * 1.9) ** 2
        Wl[r0:] += np.exp(-d2 / 0.012) * (0.9 + 0.1 * math.sin(1.3 * t))
        C[r0:] += np.exp(-d2 / 0.08) * 0.35

    def render(self, t, gain=1.0):
        """Returns a small PIL RGB image of the soft aurora at time t (seconds)."""
        F = self.F
        w, h, hs = self.w, self.h, self.hs
        L = self._layers                       # (3, h, w): white, green, cyan light layers
        L.fill(0.0)
        Wl, G, C = L[0], L[1], L[2]
        C[:hs] += self._shafts(t) * 0.80
        C[:hs] += self._caustics(t * 0.55) * self.cmask * 0.20
        self._left_sheet(t, G, Wl)
        self._right_ribbon(t, C, Wl)
        self._horizon(t, Wl, C)
        # light layers -> RGB in one matrix product, then filmic tone map 1 - exp(-1.55 x) done in place
        x = np.dot(self._mix, L.reshape(3, -1)).reshape(3, h, w)
        x += self._base_neg
        np.expm1(x, out=x)
        x *= F(-255.0 * gain * (0.97 + 0.03 * math.sin(0.3 * t)))
        x += 0.5
        np.clip(x, 0.0, 255.0, out=x)
        return Image.fromarray(np.ascontiguousarray(x.transpose(1, 2, 0)).astype(np.uint8), "RGB")


class AuroraDetail:
    """SHARP layer of the aurora, drawn at the screen's native resolution as anti-aliased vector curves:
    the fibre strands of both ribbons, their bright edges, the horizon flare streaks and the bubbles.
    Each curve is evaluated analytically per pixel column (or row) and splatted with a thin gaussian profile,
    so cost grows with screen *width*, not screen area."""

    TAPS = (-2, -1, 0, 1, 2)

    def __init__(self, W, H):
        F = np.float32
        self.W, self.H = int(W), int(H)
        self.scale = max(0.75, self.H / 1080.0)
        self.sig = 1.15 * self.scale                     # thin line half-width in pixels
        self.inv_sig2 = np.float32(1.0 / (self.sig * self.sig))
        self.u = ((np.arange(self.W) + 0.5) / self.W).astype(np.float64)
        self.v = ((np.arange(self.H) + 0.5) / self.H).astype(np.float64)

        # left sheet columns (strands fade out where they get too dense to draw cleanly)
        wl = left_geometry(self.u, 0.0)[1]
        pitch = wl * self.H * 2 * math.pi / 150.0
        self.l_amp = (_sstep(2.8 * self.scale, 5.8 * self.scale, pitch) * (1.0 - _sstep(0.55, 0.85, self.u))).astype(np.float64)
        self.l_cols = np.nonzero(self.l_amp > 0.01)[0]
        self.l_w = wl[self.l_cols]
        self.l_a = self.l_amp[self.l_cols]
        self.l_edge_cols = np.nonzero(self.u < 0.74)[0]
        self.l_edge_fade = (1.0 - _sstep(0.50, 0.70, self.u[self.l_edge_cols]))

        # right ribbon rows
        _, wr = right_geometry(self.v, 0.0)
        pitch_r = wr * self.W * 2 * math.pi / 40.0
        self.r_gate = _sstep(0.0, 0.25, self.v)
        self.r_amp = _sstep(2.8 * self.scale, 5.8 * self.scale, pitch_r) * self.r_gate
        self.r_rows = np.arange(self.H)
        self.all_cols = np.arange(self.W)

        self.streaks = [(0.80, 0.5, 0.6), (0.835, 0.35, -0.8), (0.915, 0.4, 0.7), (0.955, 0.25, -0.5)]
        rng = np.random.default_rng(7)
        self.bubbles = [(rng.uniform(0.03, 0.97), rng.uniform(0, 1), rng.uniform(0.010, 0.042),
                         rng.uniform(0.010, 0.030), rng.uniform(0, 6.28)) for _ in range(12)]
        self.col_green = np.array([0.70, 1.00, 0.55], F)
        self.col_cyan = np.array([0.60, 0.95, 1.00], F)
        self.col_white = np.array([1.00, 1.00, 0.97], F)

    # ----------------------------------------------------------------------------
    def _splat(self, flat, mstride, jstride, M, major, center, strength, cosf, color):
        """Screen-blend thin anti-aliased curves into flat (H*W, 3) uint8.
        pixel index = minor * mstride + major * jstride;  center/strength/cosf: (strands, len(major))."""
        F = np.float32
        center = center.astype(F)
        strength = strength.astype(F)
        cosf = cosf.astype(F)
        color = (color * F(1.55)).astype(F)
        for par in (0, 1):                                      # alternate strands so neighbours never collide
            c, st, cs = center[par::2], strength[par::2], cosf[par::2]
            si, ci = np.nonzero(st > 0.012)                     # only pixels where a line is actually visible
            if si.size == 0:
                continue
            cc, s, cv = c[si, ci], st[si, ci], cs[si, ci]
            mj = major[ci] * jstride
            base = np.floor(cc).astype(np.int32)
            for k in self.TAPS:
                r = base + k
                d = (r.astype(F) + F(0.5) - cc) * cv
                w = s * np.exp(-(d * d) * self.inv_sig2)
                ok = (r >= 0) & (r < M) & (w > 0.012)
                if not ok.any():
                    continue
                idx = r[ok] * mstride + mj[ok]
                px = flat[idx].astype(F)
                x = w[ok][:, None] * color[None, :]
                px += (x / (1.0 + x)) * (F(255.0) - px)
                px += F(0.5)
                flat[idx] = px.astype(np.uint8)

    def _left(self, frame, flat, t, gain):
        cols = self.l_cols
        if cols.size < 4:
            return
        H, W = self.H, self.W
        top, _ = left_geometry(self.u[cols], t)
        S = 33
        j = np.arange(S, dtype=np.float64)[:, None]
        q = ((2 * math.pi * j - 0.9 * t + 7.5) % 202.5) / 150.0 - 0.05            # (S,1), drifts toward the top edge
        y = (top[None, :] + q * self.l_w[None, :]) * H
        st = (0.62 * gain) * self.l_a[None, :] * (0.45 + 0.95 * np.clip(q, 0, 1)) \
             * _sstep(-0.02, 0.06, q) * (1.0 - _sstep(0.55, 1.15, q))
        slope = np.gradient(y, axis=1)
        self._splat(flat, W, 1, H, cols, y, st, 1.0 / np.sqrt(1.0 + slope * slope), self.col_green)
        # bright crisp core on the sheet's top edge
        ec = self.l_edge_cols
        te, _ = left_geometry(self.u[ec], t)
        ye = (te * H)[None, :]
        se = ((0.85 * gain) * self.l_edge_fade)[None, :]
        sl = np.gradient(ye, axis=1)
        self._splat(flat, W, 1, H, ec, ye, se, 1.0 / np.sqrt(1.0 + sl * sl), self.col_white * 0.9 + self.col_green * 0.4)

    def _right(self, frame, flat, t, gain):
        H, W = self.H, self.W
        gx, wr = right_geometry(self.v, t)
        S = 9
        j = np.arange(S, dtype=np.float64)[:, None]
        qr = ((2 * math.pi * j + 1.2 * t + 4.0) % 56.0) / 40.0 - 0.1
        x = (gx[None, :] - qr * wr[None, :]) * W
        st = (0.62 * gain) * self.r_amp[None, :] * _sstep(-0.05, 0.1, qr) * (1.0 - _sstep(0.7, 1.3, qr))
        slope = np.gradient(x, axis=1)
        self._splat(flat, 1, W, W, self.r_rows, x, st, 1.0 / np.sqrt(1.0 + slope * slope), self.col_cyan)
        xe = (gx * W)[None, :]
        se = ((0.80 * gain) * self.r_gate)[None, :]
        sl = np.gradient(xe, axis=1)
        self._splat(flat, 1, W, W, self.r_rows, xe, se, 1.0 / np.sqrt(1.0 + sl * sl), self.col_white * 0.9 + self.col_cyan * 0.3)

    def _streaks(self, frame, flat, t, gain):
        H, W = self.H, self.W
        cols = self.all_cols
        u = self.u
        ys, ss = [], []
        for k, (yy, amp, sp) in enumerate(self.streaks):
            ys.append((yy + 0.006 * np.sin(u * 7.0 + sp * t + k)) * H)
            ss.append((0.62 * amp * gain) * np.exp(-(((u - 0.5 - 0.08 * math.sin(0.3 * t + k)) / 0.45) ** 2)))
        y = np.array(ys)
        st = np.array(ss)
        sl = np.gradient(y, axis=1)
        self._splat(flat, W, 1, H, cols, y, st, 1.0 / np.sqrt(1.0 + sl * sl), self.col_white)

    def _bubbles(self, frame, t, gain):
        H, W = self.H, self.W
        for (bx, by0, r, sp, ph) in self.bubbles:
            by = 1.12 - ((by0 + t * sp) % 1.25)
            x = bx + 0.012 * math.sin(0.5 * t + ph)
            cx, cy, rp = x * W, by * H, r * H
            x0, x1 = int(max(0, cx - rp * 1.6 - 2)), int(min(W, cx + rp * 1.6 + 2))
            y0, y1 = int(max(0, cy - rp * 1.6 - 2)), int(min(H, cy + rp * 1.6 + 2))
            if x1 <= x0 or y1 <= y0:
                continue
            uu = (np.arange(x0, x1, dtype=np.float32) + 0.5 - cx)[None, :]
            vv = (np.arange(y0, y1, dtype=np.float32) + 0.5 - cy)[:, None]
            d = np.sqrt(uu * uu + vv * vv)
            rim = np.exp(-(((d - rp) / max(1.3 * self.scale, rp * 0.045)) ** 2)) * 0.42
            fill = (1.0 - _sstep(rp * 0.2, rp, d)) * 0.05 * (d < rp)
            hl = np.exp(-(((uu + rp * 0.30) ** 2 + (vv + rp * 0.38) ** 2) / (rp * rp * 0.035))) * 0.45
            fade = 0.55 * float(np.clip(1.0 - abs(by - 0.5) * 0.9, 0.2, 1.0)) * gain
            lay = ((rim + fill + hl) * fade).astype(np.float32)
            px = frame[y0:y1, x0:x1].astype(np.float32)
            xx = lay[..., None] * np.array([0.8, 1.0, 1.0], np.float32) * np.float32(1.55)
            px += (xx / (1.0 + xx)) * (255.0 - px)
            frame[y0:y1, x0:x1] = (px + 0.5).astype(np.uint8)

    def apply(self, frame, t, gain):
        if gain <= 0.004:
            return
        flat = frame.reshape(-1, 3)                         # contiguous view, no copy
        self._left(frame, flat, t, gain)
        self._right(frame, flat, t, gain)
        self._streaks(frame, flat, t, gain)
        self._bubbles(frame, t, gain)


class AuroraHD:
    """Full-resolution aurora = soft low-res layer (bicubic-stretched) + native-resolution vector detail."""

    def __init__(self, W, H, soft_width):
        self.size = (int(W), int(H))
        sh = max(8, int(round(soft_width * H / W)))
        self.soft = Aurora(soft_width, sh)
        self.detail = AuroraDetail(W, H)

    def render(self, t, gain=1.0):
        low = self.soft.render(t, gain)
        frame = np.array(low.resize(self.size, Image.BILINEAR))
        self.detail.apply(frame, t, gain)
        return Image.fromarray(frame, "RGB")


# --------------------------------------------------------------------------------------
#  Blue "streak" background used by the exit animation (Windows-XP-style luminous bundles)
# --------------------------------------------------------------------------------------
XP_BUNDLES = [   # v at u=0, slope, width, brightness, phase
    (0.06, 0.58, 0.030, 1.00, 0.0),
    (0.20, 0.54, 0.045, 0.85, 1.7),
    (0.36, 0.50, 0.055, 0.70, 3.1),
    (0.58, 0.38, 0.070, 0.45, 4.4),
    (0.76, 0.26, 0.060, 0.38, 5.6),
]


def xp_geometry(b, u, t):
    """Centre line, half-width and along-the-streak brightness of one bundle (u = 0..1 across the screen)."""
    a, m, w0, br, ph = b
    centre = a + m * u + 0.030 * np.sin(2.4 * u + ph + 0.30 * t) + 0.012 * np.sin(6.1 * u - 0.45 * t + 2 * ph)
    width = w0 * (1.0 + 0.9 * u)
    along = br * (0.30 + 0.70 * np.exp(-(u / 0.5) ** 2)) * (1.0 - 0.55 * _sstep(0.8, 1.0, u))
    return centre, width, along


class BlueAurora:
    """Soft layer: navy-to-royal-blue gradient, broad luminous streak bundles, top-left bloom."""

    def __init__(self, w=416, h=234):
        F = np.float32
        self.F = F
        self.w, self.h = int(w), int(h)
        self.aspect = self.w / self.h
        self.u1 = ((np.arange(self.w) + 0.5) / self.w).astype(F)
        self.v1 = ((np.arange(self.h) + 0.5) / self.h).astype(F)
        U, V = self.u1[None, :], self.v1[:, None]
        s = np.clip(0.50 * V + 0.55 * (1.0 - U) - 0.12, 0.0, 1.0)
        stops = np.array([0.0, 0.38, 0.72, 1.0])
        cols = np.array([(62, 88, 212), (14, 80, 216), (4, 32, 152), (2, 10, 94)], dtype=np.float64) / 255.0
        base = np.stack([np.interp(s, stops, cols[:, k]) for k in range(3)], -1)         # target on-screen colour
        self._base_neg = np.ascontiguousarray(np.log(1.0 - np.clip(base, 0, 0.985)).transpose(2, 0, 1)).astype(F)  # = -1.55 * linear
        c_cyan = np.array([0.55, 0.88, 1.0], F)
        c_blue = np.array([0.20, 0.50, 1.0], F)
        self._mix = (np.stack([c_cyan, c_blue], axis=1) * F(-1.55)).astype(F)
        self._layers = np.zeros((2, self.h, self.w), F)

    def render(self, t, gain=1.0):
        F = self.F
        w, h = self.w, self.h
        L = self._layers
        L.fill(0.0)
        K, B = L[0], L[1]
        V = self.v1[:, None]
        for b in XP_BUNDLES:
            c, wd, br = xp_geometry(b, self.u1, t)
            d = (V - c[None, :]) / wd[None, :]
            g = np.exp(-d * d)
            tex = 0.55 + 0.45 * np.cos(d * 5.5 + 0.35 * t + b[4])
            lum = g * tex * br[None, :]
            B += lum * 0.9
            K += lum * lum * 1.3
        U = self.u1[None, :]
        K += 0.80 * np.exp(-((((U - 0.06) * self.aspect) ** 2) / 0.10 + ((V - 0.10) ** 2) / 0.035))      # top-left bloom
        B += 0.10 * np.exp(-(((V - (0.45 + 0.30 * U)) / 0.25) ** 2))                                          # broad haze
        x = np.dot(self._mix, L.reshape(2, -1)).reshape(3, h, w)
        x += self._base_neg
        np.expm1(x, out=x)
        x *= F(-255.0 * gain * (0.97 + 0.03 * math.sin(0.35 * t)))
        x += 0.5
        np.clip(x, 0.0, 255.0, out=x)
        return Image.fromarray(np.ascontiguousarray(x.transpose(1, 2, 0)).astype(np.uint8), "RGB")


class BlueDetail(AuroraDetail):
    """Native-resolution fine light fibres inside each streak bundle (reuses AuroraDetail's anti-aliased splatter)."""
    FIBERS = 14

    def __init__(self, W, H):
        self.W, self.H = int(W), int(H)
        self.scale = max(0.75, self.H / 1080.0)
        self.sig = 1.05 * self.scale
        self.inv_sig2 = np.float32(1.0 / (self.sig * self.sig))
        self.u = ((np.arange(self.W) + 0.5) / self.W).astype(np.float64)
        self.cols = np.nonzero(self.u < 0.95)[0]
        self.uc = self.u[self.cols]
        self.col_fiber = np.array([0.72, 0.93, 1.0], np.float32)

    def apply(self, frame, t, gain):
        if gain <= 0.004:
            return
        H, W, S = self.H, self.W, self.FIBERS
        flat = frame.reshape(-1, 3)
        j = np.arange(S, dtype=np.float64)[:, None]
        for bi, b in enumerate(XP_BUNDLES):
            c, wd, br = xp_geometry(b, self.uc, t)
            drift = 0.045 * t * (1 if bi % 2 == 0 else -1) + b[4] * 0.1
            q = ((j * 2.7 / S + drift + 1.35) % 2.7) - 1.35                       # fibres drift slowly across the bundle like my farts drift through the air lol :P
            y = (c[None, :] + q * wd[None, :]) * H
            st = (0.42 * gain) * br[None, :] * np.exp(-(q / 0.75) ** 2) * (1.0 - _sstep(0.78, 0.95, self.uc))[None, :]
            slope = np.gradient(y, axis=1)
            self._splat(flat, W, 1, H, self.cols, y, st, 1.0 / np.sqrt(1.0 + slope * slope), self.col_fiber)


class BlueHD:
    """Full-resolution XP-style blue streak background = soft layer + native-resolution fibres."""

    def __init__(self, W, H, soft_width=416):
        self.size = (int(W), int(H))
        self.soft = BlueAurora(soft_width, max(8, int(round(soft_width * H / W))))
        self.detail = BlueDetail(W, H)

    def render(self, t, gain=1.0):
        frame = np.array(self.soft.render(t, gain).resize(self.size, Image.BILINEAR))
        self.detail.apply(frame, t, gain)
        return Image.fromarray(frame, "RGB")


class StaticBackdrop:
    """Fallback if numpy is missing: a calm Vista-coloured gradient (still fades in)."""

    def __init__(self, w=480, h=270, colors=((12, 120, 80), (13, 100, 110), (225, 225, 60), (80, 205, 235))):
        self.w, self.h = w, h
        tl, tr, bl, br = colors
        hm = Image.linear_gradient("L").rotate(90).resize((w, h))
        vm = Image.linear_gradient("L").resize((w, h))
        top = Image.composite(Image.new("RGB", (w, h), tr), Image.new("RGB", (w, h), tl), hm.point(lambda p: 255 - p))
        bot = Image.composite(Image.new("RGB", (w, h), br), Image.new("RGB", (w, h), bl), hm.point(lambda p: 255 - p))
        self.img = Image.composite(bot, top, vm)

    def render(self, t, gain=1.0):
        if gain >= 0.999:
            return self.img
        return Image.blend(Image.new("RGB", self.img.size, (0, 0, 0)), self.img, gain)


# ======================================================================================
#  Intro: aurora fades in -> logo glides in with the jingle -> dissolves into the editor
# ======================================================================================
class AeroIntro:
    BG_FADE = 1.5          # seconds for the aurora to fade in from black
    LOGO_START = 1.0       # logo + jingle begin here
    SLIDE_DUR = 2.3        # seconds each logo piece takes to glide into place
    STAGGER = 0.16         # delay between orb -> "Aerowave" -> "Orb Creator"
    FADE_OUT = 1.0         # dissolve into the editor
    AURORA_FPS = 24        # aurora update rate (logo motion updates every tick)
    SLIDE_FRAC = 0.036     # slide distance as a fraction of screen width aka just a smidge
    WIDTHS = (512, 416, 320)   # internal width of the SOFT aurora layer, best first (detail is always native resolution)
    RENDER_BUDGET_MS = 30.0         # whole-aurora budget per frame

    # Reference layout of the full logo on a 1920x1080 canvas (measured from Aerowave_Orb_Creator.png)
    REF_W, REF_H = 1920, 1080
    ORB_SIZE, ORB_POS = 931, (47, 56)
    AEROWAVE_POS = (522, 523)
    ORBCREATOR_POS = (584, 681)

    def __init__(self, root):
        self.root = root
        self.sw, self.sh = root.winfo_screenwidth(), root.winfo_screenheight()
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.geometry(f"{self.sw}x{self.sh}+0+0")
        self.win.configure(bg="black")
        try:
            self.win.attributes("-topmost", True)
        except tk.TclError:
            pass
        self.canvas = tk.Canvas(self.win, width=self.sw, height=self.sh, bg="black", highlightthickness=0, bd=0)
        self.canvas.pack()
        self.win.update()
        try:
            self.win.lift()
            self.win.focus_force()
        except tk.TclError:
            pass
        self.running = False
        self.on_done = None
        self._bg = None
        self._bg_t = 0.0
        self._prepare()

    # -------------------------------------------------------------------------
    def _make_aurora(self, quality):
        w = self.WIDTHS[quality]
        if HAVE_NUMPY:
            return AuroraHD(self.sw, self.sh, w)
        return StaticBackdrop(w, max(8, int(round(w * self.sh / self.sw))))

    def _load_layer(self, filename, pos, size=None, crop_to_alpha=False):
        path = asset_path(filename)
        if not path:
            return None
        s = min(self.sw / self.REF_W, self.sh / self.REF_H)
        ox = (self.sw - self.REF_W * s) / 2.0
        oy = (self.sh - self.REF_H * s) / 2.0
        img = Image.open(path).convert("RGBA")
        if size is not None:                              # orb: scale the whole 1080px square, then trim
            target = max(1, int(round(size * s)))
            img = img.resize((target, target), Image.LANCZOS)
            x, y = pos[0] * s + ox, pos[1] * s + oy
        else:
            if abs(s - 1.0) > 1e-6:
                img = img.resize((max(1, int(round(img.width * s))), max(1, int(round(img.height * s)))), Image.LANCZOS)
            x, y = pos[0] * s + ox, pos[1] * s + oy
        x, y = int(round(x)), int(round(y))
        if crop_to_alpha:
            bb = img.getchannel("A").point(lambda p: 255 if p > 0 else 0).getbbox()
            if bb:
                img = img.crop(bb)
                x, y = x + bb[0], y + bb[1]
        pad = 2                                           # transparent margin so sub-pixel shifts never clip
        padded = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
        padded.paste(img, (pad, pad))
        return padded.convert("RGBa"), x - pad, y - pad

    def _calibrate(self):
        """Pick the sharpest aurora size this PC can compute within the frame budget (done during the black screen)."""
        if not HAVE_NUMPY:
            return 0
        for q in range(len(self.WIDTHS)):
            a = self._make_aurora(q)
            a.render(0.5)
            t0 = time.perf_counter()
            for k in range(3):
                a.render(1.0 + k * 0.1)
            ms = (time.perf_counter() - t0) * 1000.0 / 3.0
            if ms <= self.RENDER_BUDGET_MS or q == len(self.WIDTHS) - 1:
                return q
        return len(self.WIDTHS) - 1

    def _prepare(self):
        self.quality = self._calibrate()
        self.aurora = self._make_aurora(self.quality)
        self.slide_px = max(8, int(self.sw * self.SLIDE_FRAC))
        self.layers = []
        specs = [
            ("Orangeorb.png", self.ORB_POS, self.ORB_SIZE, True, -1, 0.0),
            ("aerowave.png", self.AEROWAVE_POS, None, False, +1, self.STAGGER),
            ("orbcreator.png", self.ORBCREATOR_POS, None, False, +1, self.STAGGER * 2),
        ]
        for fn, pos, size, crop, direction, delay in specs:       # draw order: orb behind, text in front
            res = self._load_layer(fn, pos, size, crop)
            if res:
                img, x, y = res
                self.layers.append(dict(img=img, x=x, y=y, dir=direction, delay=delay))
        self.jingle = asset_path("orbcreatorjingle.wav")
        dur = Sound.duration(self.jingle) if self.jingle else 0.0
        logo_done = self.LOGO_START + self.STAGGER * 2 + self.SLIDE_DUR
        audio_end = self.LOGO_START + dur
        self.t_fade0 = max(logo_done, audio_end) + 0.12
        self.photo = ImageTk.PhotoImage(Image.new("RGB", (self.sw, self.sh), (0, 0, 0)))
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

    # -------------------------------------------------------------------------
    def start(self, on_done=None):
        self.on_done = on_done
        self.running = True
        self.sound_started = False
        self.ema = None
        self.last_q_change = 0.0
        self.t0 = time.perf_counter()
        self._tick()

    def _compose(self, t):
        # The aurora drifts slowly, so it only needs ~24 updates/s; the logo glide still updates every tick.
        if self._bg is None or (t - self._bg_t) >= 1.0 / self.AURORA_FPS:
            gain = smooth(t / self.BG_FADE)
            r0 = time.perf_counter()
            low = self.aurora.render(t, gain)
            self.render_ms = (time.perf_counter() - r0) * 1000.0
            self._bg = low if low.size == (self.sw, self.sh) else low.resize((self.sw, self.sh), Image.BICUBIC)
            self._bg_t = t
        frame = self._bg.copy()
        for L in self.layers:
            p = (t - self.LOGO_START - L["delay"]) / self.SLIDE_DUR
            if p <= 0.0:
                continue
            p = clamp01(p)
            slide = (1.0 - ease_out_quart(p)) * self.slide_px * L["dir"]
            opacity = smooth(p / 0.55)
            px = L["x"] + slide
            ix = math.floor(px)
            fx = px - ix
            im = L["img"]
            if fx > 0.004:                                  # sub-pixel glide (premultiplied, so no halos)
                im = im.transform(im.size, Image.AFFINE, (1, 0, -fx, 0, 1, 0), Image.BILINEAR)
            im = im.convert("RGBA")
            if opacity < 0.999:
                im.putalpha(im.getchannel("A").point(lambda v, o=opacity: int(v * o + 0.5)))
            frame.paste(im, (ix, L["y"]), im)
        return frame

    def _tick(self):
        if not self.running:
            return
        started = time.perf_counter()
        t = started - self.t0
        if not self.sound_started and t >= self.LOGO_START:
            self.sound_started = True
            Sound.play(self.jingle)
        try:
            self.photo.paste(self._compose(t))
        except Exception:
            pass

        if t >= self.t_fade0:
            k = clamp01((t - self.t_fade0) / self.FADE_OUT)
            try:
                self.win.attributes("-alpha", max(0.0, 1.0 - smooth(k)))
            except tk.TclError:
                k = 1.0                                      # no window alpha on this platform: just cut
            if k >= 1.0:
                self._finish()
                return

        ft = getattr(self, "render_ms", 0.0)                  # judge only the aurora math (not the screen paste)
        self.ema = ft if self.ema is None else self.ema * 0.9 + ft * 0.1
        if HAVE_NUMPY and self.ema > self.RENDER_BUDGET_MS * 1.8 and self.quality < len(self.WIDTHS) - 1 and (t - self.last_q_change) > 1.0:
            self.quality += 1
            self.last_q_change = t
            self.aurora = self._make_aurora(self.quality)
            self._bg = None
            self.ema = None
        delay = max(1, int(16 - (time.perf_counter() - started) * 1000))
        self.root.after(delay, self._tick)

    def _finish(self):
        self.running = False
        try:
            self.win.destroy()
        except tk.TclError:
            pass
        if self.on_done:
            self.on_done()


class AeroOutro:
    """Exit animation: dissolves over the editor into the blue streak background with "See you later!",
    plays exitjingle.wav, then fades to black and quits."""
    FADE_IN = 1.0          # dissolve from the editor into the outro
    SOUND_AT = 0.15        # jingle starts as the dissolve begins
    HOLD_PAD = 0.20        # pause after the jingle finishes
    FADE_BLACK = 1.3       # fade to black
    AURORA_FPS = 24
    SOFT_WIDTH = 416
    TEXT_FRAC = 0.42       # text width as a fraction of the screen width

    def __init__(self, root, on_done):
        self.root, self.on_done = root, on_done
        self.sw, self.sh = root.winfo_screenwidth(), root.winfo_screenheight()
        self.win = tk.Toplevel(root)
        self.win.withdraw()
        self.win.overrideredirect(True)
        self.win.geometry(f"{self.sw}x{self.sh}+0+0")
        self.win.configure(bg="black")
        self.has_alpha = True
        try:
            self.win.attributes("-alpha", 0.0)
            self.win.attributes("-topmost", True)
        except tk.TclError:
            self.has_alpha = False
        self.canvas = tk.Canvas(self.win, width=self.sw, height=self.sh, bg="black", highlightthickness=0, bd=0)
        self.canvas.pack()
        if HAVE_NUMPY:
            self.bg = BlueHD(self.sw, self.sh, self.SOFT_WIDTH)
        else:
            self.bg = StaticBackdrop(self.SOFT_WIDTH, max(8, int(round(self.SOFT_WIDTH * self.sh / self.sw))),
                                     colors=((78, 104, 222), (24, 100, 224), (3, 16, 108), (8, 44, 168)))
        self._prepare_text()
        self.jingle = asset_path("exitjingle.wav")
        dur = Sound.duration(self.jingle) if self.jingle else 0.0
        self.t_black0 = max(self.SOUND_AT + dur + self.HOLD_PAD, self.FADE_IN + 0.3)
        self.photo = ImageTk.PhotoImage(Image.new("RGB", (self.sw, self.sh), (0, 0, 0)))
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self._bg_frame, self._bg_t, self._bg_gain = None, 0.0, -1.0
        self.sound_started = False
        self.running = False
        self.photo.paste(self._compose(0.0))              # first frame is ready before the window becomes visible
        self.win.deiconify()
        self.win.update()
        try:
            self.win.lift()
            self.win.focus_force()
        except tk.TclError:
            pass

    def _prepare_text(self):
        self.text_layer, self.text_pos = None, (0, 0)
        p = asset_path("exittext.png")
        if not p:
            return
        try:
            src = Image.open(p).convert("RGBA")
            alpha = src.getchannel("A")
            tw = max(8, int(self.sw * self.TEXT_FRAC))
            th = max(2, int(round(src.height * tw / src.width)))
            alpha = alpha.resize((tw, th), Image.LANCZOS)
            pad = int(tw * 0.06)
            canvas_a = Image.new("L", (tw + pad * 2, th + pad * 2), 0)
            canvas_a.paste(alpha, (pad, pad))
            white = Image.new("RGBA", canvas_a.size, (255, 255, 255, 0))
            white.putalpha(canvas_a)                                              # same lettering, recoloured white
            glow = Image.new("RGBA", canvas_a.size, (120, 200, 255, 0))
            glow.putalpha(canvas_a.filter(ImageFilter.GaussianBlur(max(3, tw * 0.012))).point(lambda v: min(255, int(v * 1.6))))
            self.text_layer = Image.alpha_composite(glow, white)
            self.text_pos = ((self.sw - self.text_layer.width) // 2, int(self.sh * 0.5 - self.text_layer.height / 2))
        except Exception:
            self.text_layer = None

    def _black_gain(self, t):
        return 1.0 if t <= self.t_black0 else 1.0 - smooth((t - self.t_black0) / self.FADE_BLACK)

    def _compose(self, t):
        g = self._black_gain(t)
        if self._bg_frame is None or (t - self._bg_t) >= 1.0 / self.AURORA_FPS or abs(g - self._bg_gain) > 0.02:
            low = self.bg.render(t, g)
            self._bg_frame = low if low.size == (self.sw, self.sh) else low.resize((self.sw, self.sh), Image.BICUBIC)
            self._bg_t, self._bg_gain = t, g
        frame = self._bg_frame.copy()
        if self.text_layer is not None:
            lay = self.text_layer
            if g < 0.999:
                lay = lay.copy()
                lay.putalpha(lay.getchannel("A").point(lambda v, k=g: int(v * k + 0.5)))
            frame.paste(lay, self.text_pos, lay)
        return frame

    def start(self):
        self.running = True
        self.t0 = time.perf_counter()
        self._tick()

    def _tick(self):
        if not self.running:
            return
        started = time.perf_counter()
        t = started - self.t0
        if not self.sound_started and t >= self.SOUND_AT:
            self.sound_started = True
            Sound.play(self.jingle)
        try:
            self.photo.paste(self._compose(t))
        except Exception:
            pass
        if self.has_alpha and t <= self.FADE_IN + 0.1:
            try:
                self.win.attributes("-alpha", smooth(t / self.FADE_IN))
            except tk.TclError:
                self.has_alpha = False
        if t >= self.t_black0 + self.FADE_BLACK + 0.1:
            self.running = False
            self.on_done()
            return
        self.root.after(max(1, int(16 - (time.perf_counter() - started) * 1000)), self._tick)


# ======================================================================================
#  Aero glass drawing helpers (drop-down + pop-ups)
# ======================================================================================
def glass_panel(base, box, radius, st, shadow=True, ss=3):
    """Composite a frosted Aero-glass panel (shadow, blur-behind, tint, sheen, bevel) onto an RGB image."""
    W, H = base.size
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    out = base.copy()

    if shadow:
        m = 60
        sx0, sy0, sx1, sy1 = max(0, x0 - m), max(0, y0 - m), min(W, x1 + m), min(H, y1 + m)
        reg = out.crop((sx0, sy0, sx1, sy1))
        sm = Image.new("L", reg.size, 0)
        ImageDraw.Draw(sm).rounded_rectangle([x0 - sx0, y0 - sy0 + 9, x1 - sx0, y1 - sy0 + 9], radius=radius, fill=st["shadow"])
        sm = sm.filter(ImageFilter.GaussianBlur(16))
        out.paste(Image.composite(Image.new("RGB", reg.size, (0, 0, 0)), reg, sm), (sx0, sy0))

    # blur-behind
    pad = 24
    bx0, by0, bx1, by1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    frost = base.crop((bx0, by0, bx1, by1)).filter(ImageFilter.GaussianBlur(st["blur"]))
    frost = frost.crop((x0 - bx0, y0 - by0, x0 - bx0 + w, y0 - by0 + h))

    # tint (a touch stronger toward the bottom)
    ta = Image.linear_gradient("L").resize((w, h))
    ta = ta.point(lambda p: int(255 * max(0.0, min(1.0, st["tint_a"] + (p / 255.0 - 0.5) * st["tint_grad"]))))
    glass = Image.composite(Image.new("RGB", (w, h), st["tint"]), frost, ta)

    # diagonal sheen + soft top light, drawn supersampled
    S = ss
    sheen = Image.new("L", (w * S, h * S), 0)
    sd = ImageDraw.Draw(sheen)
    sd.polygon([(0, 0), (int(w * S * 0.66), 0), (int(w * S * 0.22), h * S), (0, h * S)], fill=255)
    sheen = sheen.resize((w, h), Image.LANCZOS)
    fade = Image.linear_gradient("L").resize((w, h)).point(lambda p: int(255 - p * 0.80))
    sheen = ImageChops.multiply(sheen, fade).point(lambda p: int(p * st["gloss"]))
    glass = Image.composite(Image.new("RGB", (w, h), (255, 255, 255)), glass, sheen)
    top = Image.linear_gradient("L").resize((w, h)).point(lambda p: int(max(0, 255 - p * 2.4) * st["gloss"] * 0.55))
    glass = Image.composite(Image.new("RGB", (w, h), (255, 255, 255)), glass, top)

    # double bevel border
    decor = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    dd = ImageDraw.Draw(decor)
    dd.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=radius * S, outline=(0, 0, 0, st["border_dark"]), width=S)
    dd.rounded_rectangle([S, S, w * S - 1 - S, h * S - 1 - S], radius=max(1, radius - 1) * S,
                         outline=(255, 255, 255, st["border_light"]), width=S)
    decor = decor.resize((w, h), Image.LANCZOS)
    panel = glass.convert("RGBA")
    panel.alpha_composite(decor)

    mk = Image.new("L", (w * S, h * S), 0)
    ImageDraw.Draw(mk).rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=radius * S, fill=255)
    mk = mk.resize((w, h), Image.LANCZOS)
    out.paste(panel.convert("RGB"), (x0, y0), mk)
    return out


def make_dim(snapshot, st):
    """Blurred, darkened copy of a screenshot (backdrop behind modal pop-ups)."""
    small = snapshot.resize((max(1, snapshot.width // 3), max(1, snapshot.height // 3)), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(2))
    blurred = small.resize(snapshot.size, Image.BILINEAR)
    return ImageEnhance.Brightness(blurred).enhance(st["dim"])


def badge_orb(size, color, glyph):
    """Small glossy status orb with a check mark ('ok') or exclamation mark ('err')."""
    S = 4
    N = size * S
    base = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    mask = Image.new("L", (N, N), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, N - 1, N - 1], fill=255)
    grad = Image.radial_gradient("L").resize((N, N), Image.BILINEAR)         # 0 centre -> 255 edge
    dark = tuple(int(c * 0.62) for c in color)
    light = tuple(min(255, int(c + (255 - c) * 0.35)) for c in color)
    orb = Image.composite(Image.new("RGB", (N, N), dark), Image.new("RGB", (N, N), light), grad.point(lambda p: min(255, int(p * 1.15))))
    base.paste(orb, (0, 0), mask)
    hl = Image.new("L", (N, N), 0)
    ImageDraw.Draw(hl).ellipse([N * 0.14, N * 0.05, N * 0.86, N * 0.52], fill=255)
    hl = ImageChops.multiply(hl, Image.linear_gradient("L").resize((N, N)).point(lambda p: 255 - p)).point(lambda p: int(p * 0.62))
    hl = ImageChops.multiply(hl, mask)
    base = Image.composite(Image.new("RGBA", (N, N), (255, 255, 255, 255)), base, hl)
    d = ImageDraw.Draw(base)
    lw = max(2, int(N * 0.115))
    if glyph == "ok":
        pts = [(N * 0.27, N * 0.52), (N * 0.43, N * 0.68), (N * 0.74, N * 0.33)]
        d.line(pts, fill=(255, 255, 255, 255), width=lw, joint="curve")
        for p in (pts[0], pts[-1]):
            d.ellipse([p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2], fill=(255, 255, 255, 255))
    else:
        d.line([(N * 0.5, N * 0.24), (N * 0.5, N * 0.60)], fill=(255, 255, 255, 255), width=lw)
        r = lw * 0.62
        d.ellipse([N * 0.5 - r, N * 0.76 - r, N * 0.5 + r, N * 0.76 + r], fill=(255, 255, 255, 255))
    ring = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([0, 0, N - 1, N - 1], outline=(255, 255, 255, 190), width=max(2, S))
    base.alpha_composite(ring)
    return base.resize((size, size), Image.LANCZOS)


def wrap_text(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def ellipsize(draw, text, font, max_w):
    if draw.textlength(text, font=font) <= max_w:
        return text
    stem, ext = os.path.splitext(text)
    while stem and draw.textlength(stem + "…" + ext, font=font) > max_w:
        stem = stem[:-1]
    return stem + "…" + ext


def make_icon(kind, size=18):
    """Tiny file-browser icons drawn with PIL: 'folder', 'drive' or 'png'."""
    S = 4
    N = size * S
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(1, S // 2)
    if kind == "folder":
        d.rounded_rectangle([N * .06, N * .20, N * .44, N * .44], radius=N * .06, fill=(226, 160, 38, 255))
        d.rounded_rectangle([N * .06, N * .30, N * .94, N * .84], radius=N * .08, fill=(255, 200, 72, 255), outline=(196, 132, 20, 255), width=lw)
        d.rounded_rectangle([N * .10, N * .34, N * .90, N * .50], radius=N * .06, fill=(255, 226, 134, 255))
    elif kind == "drive":
        d.rounded_rectangle([N * .06, N * .30, N * .94, N * .74], radius=N * .10, fill=(176, 182, 194, 255), outline=(110, 116, 128, 255), width=lw)
        d.rectangle([N * .14, N * .52, N * .58, N * .60], fill=(120, 126, 138, 255))
        d.ellipse([N * .74, N * .46, N * .84, N * .58], fill=(70, 200, 90, 255))
    else:
        d.rounded_rectangle([N * .18, N * .06, N * .82, N * .94], radius=N * .08, fill=(255, 255, 255, 255), outline=(150, 156, 168, 255), width=lw)
        d.ellipse([N * .30, N * .28, N * .70, N * .68], fill=(255, 110, 20, 255))
        d.ellipse([N * .38, N * .34, N * .56, N * .46], fill=(255, 224, 196, 255))
    return im.resize((size, size), Image.LANCZOS)


def human_size(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return ("%d %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0
    return "%.1f TB" % n


def hsv_wheel(D, v):
    """RGBA colour wheel: hue = angle, saturation = radius (white centre), brightness = v. Anti-aliased edge."""
    R = D / 2.0
    if HAVE_NUMPY:
        ys, xs = np.mgrid[0:D, 0:D].astype(np.float32)
        dx, dy = xs + 0.5 - R, ys + 0.5 - R
        r = np.sqrt(dx * dx + dy * dy)
        sat = np.clip(r / R, 0.0, 1.0)
        hue = (np.arctan2(-dy, dx) / (2 * np.pi)) % 1.0
        h6 = hue * 6.0
        i = np.floor(h6).astype(np.int32) % 6
        f = h6 - np.floor(h6)
        V = np.full_like(sat, v)
        p, q, t = v * (1 - sat), v * (1 - f * sat), v * (1 - (1 - f) * sat)
        rr = np.choose(i, [V, q, p, p, t, V])
        gg = np.choose(i, [t, V, V, q, p, p])
        bb = np.choose(i, [p, p, t, V, V, q])
        a = np.clip(R - r + 0.5, 0.0, 1.0)
        return Image.fromarray((np.stack([rr, gg, bb, a], -1) * 255.0 + 0.5).astype(np.uint8), "RGBA")
    n = 100                                                       # no numpy: coarse grid + smooth resize
    small = Image.new("RGB", (n, n))
    px = small.load()
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - n / 2.0, y + 0.5 - n / 2.0
            r = min(1.0, math.hypot(dx, dy) / (n / 2.0))
            h = (math.atan2(-dy, dx) / (2 * math.pi)) % 1.0
            px[x, y] = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, r, v))
    img = small.resize((D, D), Image.BICUBIC).convert("RGBA")
    mask = Image.new("L", (D * 3, D * 3), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, D * 3 - 1, D * 3 - 1], fill=255)
    img.putalpha(mask.resize((D, D), Image.LANCZOS))
    return img


def wheel_ring(D, pad):
    """Bevelled rim drawn around the colour wheel (RGBA, size D + 2*pad)."""
    S = 3
    N = (D + 2 * pad) * S
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, R = N / 2.0, D / 2.0 * S
    d.ellipse([c - R - S * 2, c - R - S * 2, c + R + S * 2, c + R + S * 2], outline=(0, 0, 0, 150), width=S * 2)
    d.ellipse([c - R + S, c - R + S, c + R - S, c + R - S], outline=(255, 255, 255, 190), width=S)
    return im.resize((D + 2 * pad, D + 2 * pad), Image.LANCZOS)


def swatch_image(rgb, w, h, radius):
    """Glossy rounded colour swatch (RGBA)."""
    S = 3
    base = Image.new("RGBA", (w, h), tuple(rgb) + (255,))
    gl = Image.linear_gradient("L").resize((w, h)).point(lambda p: int(max(0, 255 - p * 2.0) * 0.34))
    white = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    white.putalpha(gl)
    base = Image.alpha_composite(base, white)
    border = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(border)
    bd.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=radius * S, outline=(0, 0, 0, 150), width=S)
    bd.rounded_rectangle([S, S, w * S - 1 - S, h * S - 1 - S], radius=max(1, radius - 1) * S, outline=(255, 255, 255, 120), width=S)
    base.alpha_composite(border.resize((w, h), Image.LANCZOS))
    mask = Image.new("L", (w * S, h * S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=radius * S, fill=255)
    base.putalpha(mask.resize((w, h), Image.LANCZOS))
    return base


def empty_slot_image(w, h, radius, col):
    S = 3
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=radius * S, fill=tuple(col) + (26,), outline=tuple(col) + (90,), width=S)
    return im.resize((w, h), Image.LANCZOS)


def brightness_bar(w, h, rgb):
    """Rounded black -> colour gradient bar (RGBA) for the brightness slider."""
    S = 3
    mask = Image.new("L", (w, h), 0)
    grad = Image.linear_gradient("L").rotate(90).resize((w, h))                   # 0 on the left -> 255 on the right
    bar = Image.composite(Image.new("RGB", (w, h), tuple(rgb)), Image.new("RGB", (w, h), (0, 0, 0)), grad).convert("RGBA")
    big = Image.new("L", (w * S, h * S), 0)
    ImageDraw.Draw(big).rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=(h // 2) * S, fill=255)
    bar.putalpha(big.resize((w, h), Image.LANCZOS))
    rim = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=(h // 2) * S, outline=(0, 0, 0, 150), width=S)
    rd.rounded_rectangle([S, S, w * S - 1 - S, h * S - 1 - S], radius=max(1, h // 2 - 1) * S, outline=(255, 255, 255, 110), width=S)
    bar.alpha_composite(rim.resize((w, h), Image.LANCZOS))
    return bar


def create_gradient_rect(width, height, color_top, color_bottom, radius, outline_color=None, mid_color=None, flipped=False):
    if flipped:
        color_top, color_bottom = color_bottom, color_top

    base = Image.new('RGBA', (width, height), (0,0,0,0))
    if width <= 0 or height <= 0: return base
    grad = Image.new('RGBA', (1, height))
    
    for y in range(height):
        if mid_color:
            if y < height / 2:
                prog = y / (height / 2)
                c1, c2 = color_top, mid_color
            else:
                prog = (y - height / 2) / (height / 2)
                c1, c2 = mid_color, color_bottom
        else:
            prog = y / height
            c1, c2 = color_top, color_bottom
            
        r = int(c1[0] + (c2[0] - c1[0]) * prog)
        g = int(c1[1] + (c2[1] - c1[1]) * prog)
        b = int(c1[2] + (c2[2] - c1[2]) * prog)
        grad.putpixel((0, y), (r, g, b, 255))
        
    grad = grad.resize((width, height))
    
    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, width-1, height-1], radius=radius, fill=255)
    
    grad.putalpha(mask)
    
    if outline_color:
        out_img = Image.new('RGBA', (width, height), (0,0,0,0))
        out_draw = ImageDraw.Draw(out_img)
        out_draw.rounded_rectangle([0, 0, width-1, height-1], radius=radius, outline=outline_color, width=1)
        grad = Image.alpha_composite(grad, out_img)
        
    return grad

def dorfic_swoosh(w, hr, ss=2):
    """DORFic-kit style bundle of fine orange/amber strands sweeping up from the lower left (RGBA)."""
    W, H = w * ss, hr * ss
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    xs = list(range(0, W + 1, 4))

    def curve(sv):
        pts = []
        for x in xs:
            u = x / float(W)
            a0 = 0.68 - 0.50 * ((lambda a: a * a * (3 - 2 * a))(min(1.0, u * 1.05))) ** 1.15 + 0.04 * math.sin(u * 7.5 + 0.6)
            wd = 0.40 * (1.0 - u) ** 1.3 + 0.035
            pts.append((x, (a0 + sv * wd) * H))
        return pts

    top, bot = curve(0.0), curve(1.0)
    d.polygon(top + bot[::-1], fill=(255, 130, 30, 30))         # faint glossy body between the outer strands
    N = 34
    for k in range(N):
        sv = k / float(N - 1)
        if k % 7 == 3:
            col = (176, 182, 192)                                 # cool grey "infrastructure" strand (at this point I'm just showin' off lol)
        elif sv < 0.5:
            f = sv / 0.5
            col = (255, int(102 + (160 - 102) * f), int(0 + 40 * f))
        else:
            f = (sv - 0.5) / 0.5
            col = (255, int(160 + (212 - 160) * f), int(40 + 60 * f))
        d.line(curve(sv), fill=col + (205 if k % 7 != 3 else 150,), width=ss)
    d.line(top, fill=(255, 102, 0, 245), width=ss * 3)           # bold signature orange edge
    d.line(bot, fill=(255, 176, 60, 220), width=ss * 2)
    img = img.resize((w, hr), Image.LANCZOS)
    fade = Image.linear_gradient("L").rotate(90).resize((w, hr))   # fade out toward the right edge
    ramp = fade.point(lambda p: 255 if p < 190 else max(0, 255 - (p - 190) * 4))
    img.putalpha(ImageChops.multiply(img.getchannel("A"), ramp))
    return img


class GradientPanel(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0, **kwargs)
        self.color_top = "#000000"
        self.color_bot = "#000000"
        self.decor = None
        self.decor_top = 0
        self._decor_cache = {}
        self.bind("<Configure>", self._on_resize)
        self.grad_img = None
        
    def set_colors(self, top, bot, decor=None):
        self.color_top = top
        self.color_bot = bot
        self.decor = decor
        self._draw_gradient()

    def set_decor_top(self, y):
        """Top of the empty area under the widgets (decorations are drawn only there)."""
        y = int(y)
        if abs(y - self.decor_top) >= 6:
            self.decor_top = y
            if self.decor:
                self._draw_gradient()
        
    def _on_resize(self, event):
        self._draw_gradient()

    def _with_decor(self, img, w, h):
        try:
            top = self.decor_top + 16
            hr = h - top - 8
            if self.decor != "dorfic" or self.decor_top <= 0 or hr < 110:
                return img
            key = (w, hr)
            if key not in self._decor_cache:
                self._decor_cache.clear()
                self._decor_cache[key] = dorfic_swoosh(w, hr)
            out = img.convert("RGBA")
            out.alpha_composite(self._decor_cache[key], (0, top))
            return out.convert("RGB")
        except Exception:
            return img
        
    def _draw_gradient(self):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 2 or h < 2: return
        
        img = Image.new('RGB', (1, h))
        r1, g1, b1 = int(self.color_top[1:3], 16), int(self.color_top[3:5], 16), int(self.color_top[5:7], 16)
        r2, g2, b2 = int(self.color_bot[1:3], 16), int(self.color_bot[3:5], 16), int(self.color_bot[5:7], 16)
        
        for y in range(h):
            prog = y / h
            img.putpixel((0, y), (int(r1 + (r2 - r1) * prog), int(g1 + (g2 - g1) * prog), int(b1 + (b2 - b1) * prog)))
            
        img = img.resize((w, h))
        if self.decor:
            img = self._with_decor(img, w, h)
        self.grad_img = ImageTk.PhotoImage(img)
        self.delete("grad")
        self.create_image(0, 0, anchor=tk.NW, image=self.grad_img, tags="grad")
        self.tag_lower("grad")

class OrbLayer:
    def __init__(self, name, layer_type, visible=True):
        self.name = name
        self.type = layer_type
        self.visible = visible
        self.x = 250
        self.y = 250
        self.scale = 1.0
        self.scale_x = 1.0  
        self.scale_y = 1.0  
        self.color = (33, 150, 243)
        self.custom_grad_color = None
        self.glow_opacity = 220
        self.grad_y_scale = 1.0
        self.grad_y_offset = 0
        
class OrbCreator:
    # Screens shorter than this get the compact (controls beside the canvas) arrangement (which may need some extra debugging as I haven't really tested it just yet ;))
    COMPACT_BELOW = 850

    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        
        self.canvas_size = 500
        self.orb_radius = 150
        self.layers = []
        self.selected_layer = None
        
        # Interaction state
        self.dragging = False
        self.scaling = False
        self.scaling_x = False
        self.scaling_y = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.snap_threshold = 15
        self.scale_handles = []
        
        self.preview_photo = None 
        self.btn_images = {}
        self.btn_images_flipped = {}

        # Saved UI theme (config.aero)
        self.config = load_config()
        start_theme = self.config.get("theme", "Dark")
        if start_theme not in THEMES:
            start_theme = "Dark"
        self.current_theme = start_theme
        
        self.labels = []
        self.scales = []
        self.managed_buttons = []
        self.managed_button_labels = []
        self.left_widgets = []
        self.right_widgets = []

        # Overlays (UI selector drop-down / pop-up dialog)
        self.dd = None
        self.dlg = None
        self.fsd = None
        self.cpk = None
        self._orb_src = {}
        self._orb_cache = {}
        self._keep = []
        
        self.compact = self.root.winfo_screenheight() < self.COMPACT_BELOW
        self.setup_ui()
        self.apply_theme(start_theme)
        if "theme" not in self.config or self.config.get("theme") != start_theme:
            self.config["theme"] = start_theme
            save_config(self.config)

        # Always fullscreen, never windowed
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.bind("<Escape>", self._on_escape)
        self.root.bind("<F11>", lambda e: "break")
        self.root.bind_all("<Button-1>", self._on_any_click, add="+")
        self.enforce_fullscreen()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel (Gradient Canvas)
        self.left_panel = GradientPanel(main_frame)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 10), pady=10)
        self.left_panel.bind("<Configure>", lambda e: self.root.after(10, self.sync_widget_colors), add="+")
        
        top_bar = tk.Frame(self.left_panel, bd=0)
        top_bar.pack(fill=tk.X, pady=(0, 10))
        self.left_widgets.append(top_bar)
        
        self.ui_btn = self.create_themed_button(top_bar, "UI Selector", self.toggle_ui_selector, 120)
        self.ui_btn.pack(side=tk.LEFT, padx=5)
        self.create_themed_button(top_bar, "Exit", self.exit_app, 80).pack(side=tk.RIGHT, padx=5)

        brand = tk.Frame(top_bar, bd=0)
        brand.place(relx=0.5, rely=0.5, anchor="center")
        lbl_b1 = tk.Label(brand, text="Aerowave", font=('Segoe UI', 15))
        lbl_b1.pack(side=tk.LEFT)
        lbl_b2 = tk.Label(brand, text=" Orb Creator", font=('Segoe UI', 15, 'bold italic'))
        lbl_b2.pack(side=tk.LEFT)
        self.labels.extend([lbl_b1, lbl_b2])

        # In compact mode the canvas and the controls sit side by side
        if self.compact:
            workspace = tk.Frame(self.left_panel, bd=0)
            workspace.pack(fill=tk.X)
            self.left_widgets.append(workspace)
            side = tk.Frame(self.left_panel, bd=0)
            self.left_widgets.append(side)
            canvas_host, ctl_host = workspace, side
        else:
            workspace = side = None
            canvas_host, ctl_host = self.left_panel, self.left_panel

        # Orb Drawing Canvas
        self.canvas_frame = tk.Frame(self.left_panel, bg='#1a1a1a', bd=0)
        if self.compact:
            self.canvas_frame.pack(in_=workspace, side=tk.LEFT, expand=True, padx=(0, 15), pady=5, anchor="ne")
            side.pack(in_=workspace, side=tk.LEFT, expand=True, padx=(15, 0), anchor="nw")
        else:
            self.canvas_frame.pack(pady=5)
        self.left_widgets.append(self.canvas_frame)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_size, height=self.canvas_size, 
                                bg='#1a1a1a', highlightthickness=0)
        self.canvas.pack(padx=2, pady=2)
        self.draw_checkerboard()
        
        self.snap_line_h = self.canvas.create_line(0, self.canvas_size//2, self.canvas_size, 
                                                   self.canvas_size//2, fill='red', width=1, state='hidden')
        self.snap_line_v = self.canvas.create_line(self.canvas_size//2, 0, self.canvas_size//2, 
                                                   self.canvas_size, fill='red', width=1, state='hidden')
        
        # Controls Frame
        controls_frame = tk.Frame(self.left_panel, bd=0)
        controls_frame.pack(in_=ctl_host, fill=tk.X, pady=5)
        self.left_widgets.append(controls_frame)
        controls_row = tk.Frame(controls_frame, bd=0)
        controls_row.pack()
        
        self.create_themed_button(controls_row, "Orb", self.create_orb, 80).pack(side=tk.LEFT, padx=5)
        self.create_themed_button(controls_row, "Orb Color", self.choose_color, 100).pack(side=tk.LEFT, padx=5)
        self.create_themed_button(controls_row, "Reflection", self.create_reflection, 100).pack(side=tk.LEFT, padx=5)
        self.create_themed_button(controls_row, "Glow", self.create_glow, 80).pack(side=tk.LEFT, padx=5)
        
        # Layer Properties Panel
        prop_outer = tk.Frame(self.left_panel, bd=0)
        prop_outer.pack(in_=ctl_host, fill=tk.X, pady=10, ipadx=5, ipady=5)
        self.left_widgets.append(prop_outer)
        prop_frame = tk.Frame(prop_outer, bd=0)
        prop_frame.pack()
        slider_len = 190 if self.compact else 250
        
        lbl_g_scale = tk.Label(prop_frame, text="Grad Y Scale:")
        lbl_g_scale.grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.labels.append(lbl_g_scale)
        
        self.var_grad_y_scale = tk.DoubleVar(value=1.0)
        scale_g_y = tk.Scale(prop_frame, variable=self.var_grad_y_scale, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, command=self.on_prop_change, bd=0, length=slider_len)
        scale_g_y.grid(row=0, column=1, sticky='ew', padx=5)
        self.scales.append(scale_g_y)
        
        lbl_g_pos = tk.Label(prop_frame, text="Grad Y Offset:")
        lbl_g_pos.grid(row=0, column=2, sticky='e', padx=5, pady=2)
        self.labels.append(lbl_g_pos)
        
        self.var_grad_y_pos = tk.DoubleVar(value=0)
        scale_g_pos = tk.Scale(prop_frame, variable=self.var_grad_y_pos, from_=-200, to=200, resolution=1, orient=tk.HORIZONTAL, command=self.on_prop_change, bd=0, length=slider_len)
        scale_g_pos.grid(row=0, column=3, sticky='ew', padx=5)
        self.scales.append(scale_g_pos)
        
        self.create_themed_button(prop_frame, "Custom Gradient Color", self.choose_custom_grad, 160).grid(row=1, column=0, columnspan=2, pady=5)
        self.create_themed_button(prop_frame, "Default Gradient Color", self.default_grad, 160).grid(row=1, column=2, columnspan=2, pady=5)
        
        lbl_glow_bright = tk.Label(prop_frame, text="Glow Brightness:")
        lbl_glow_bright.grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.labels.append(lbl_glow_bright)
        
        self.var_glow_opacity = tk.DoubleVar(value=220)
        scale_glow = tk.Scale(prop_frame, variable=self.var_glow_opacity, from_=0, to=255, resolution=1, orient=tk.HORIZONTAL, command=self.on_prop_change, bd=0, length=slider_len)
        scale_glow.grid(row=2, column=1, columnspan=3, sticky='ew', padx=5)
        self.scales.append(scale_glow)
        
        prop_frame.grid_columnconfigure(1, weight=1)
        prop_frame.grid_columnconfigure(3, weight=1)

        # Export Frame
        export_frame = tk.Frame(self.left_panel, bd=0)
        export_frame.pack(in_=ctl_host, fill=tk.X, pady=10)
        self.left_widgets.append(export_frame)
        export_row = tk.Frame(export_frame, bd=0)
        export_row.pack()
        
        lbl_exp = tk.Label(export_row, text="Export Res:")
        lbl_exp.pack(side=tk.LEFT, padx=5)
        self.labels.append(lbl_exp)
        
        self.resolution_var = tk.StringVar(value="1080")
        self.res_entry = tk.Entry(export_row, textvariable=self.resolution_var, width=8)
        self.res_entry.pack(side=tk.LEFT, padx=5, ipady=3)
        self.create_themed_button(export_row, "Save Orb", self.save_orb, 100).pack(side=tk.LEFT, padx=15)
        
        # Right Panel (Gradient Canvas)
        self.right_panel = GradientPanel(main_frame, width=250)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
        self.right_panel.pack_propagate(False)
        self.right_panel.bind("<Configure>", lambda e: self.root.after(10, self.sync_widget_colors), add="+")
        
        lbl_layers = tk.Label(self.right_panel, text="LAYERS", font=('Arial', 12, 'bold'))
        lbl_layers.pack(pady=10)
        self.labels.append(lbl_layers)
        self.right_widgets.append(lbl_layers)
        
        self.layers_frame = tk.Frame(self.right_panel, bd=0)
        self.layers_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.right_widgets.append(self.layers_frame)
        
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        
    def create_themed_button(self, parent, text, command, width=120, height=30):
        lbl = tk.Label(parent, text=text, cursor="hand2", font=('Arial', 9, 'bold'), compound="center", bd=0, highlightthickness=0)
        
        def on_press(e):
            lbl.config(image=self.btn_images_flipped[lbl])
        def on_release(e):
            lbl.config(image=self.btn_images[lbl])
            if 0 <= e.x <= lbl.winfo_width() and 0 <= e.y <= lbl.winfo_height():
                command()
                
        lbl.bind("<ButtonPress-1>", on_press)
        lbl.bind("<ButtonRelease-1>", on_release)
        
        self.managed_buttons.append((lbl, text, width, height))
        self.managed_button_labels.append(lbl)
        return lbl

    def get_gradient_color(self, top_hex, bot_hex, ratio):
        r1, g1, b1 = int(top_hex[1:3], 16), int(top_hex[3:5], 16), int(top_hex[5:7], 16)
        r2, g2, b2 = int(bot_hex[1:3], 16), int(bot_hex[3:5], 16), int(bot_hex[5:7], 16)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    def apply_bg_to_tree(self, widget, bg_col, t):
        if getattr(widget, 'is_layer_item', False): return
        if widget == self.canvas_frame or widget == self.canvas: return
        if isinstance(widget, tk.Entry): return          # entries get their own theme colours (style_entry)
            
        try:
            if isinstance(widget, tk.Label) and widget in self.managed_button_labels:
                widget.config(bg=bg_col, activebackground=bg_col)
            elif not isinstance(widget, ttk.Combobox):
                widget.config(bg=bg_col)
        except: pass
        
        for child in widget.winfo_children():
            self.apply_bg_to_tree(child, bg_col, t)

    def sync_widget_colors(self):
        t = THEMES[self.current_theme]
        
        h_left = self.left_panel.winfo_height()
        if h_left > 10:
            for widget in self.left_widgets:
                if not widget.winfo_exists(): continue
                wy = widget.winfo_y() + widget.winfo_height() / 2
                ratio = min(1.0, max(0.0, wy / h_left))
                bg_col = self.get_gradient_color(t["ui_top"], t["ui_bot"], ratio)
                self.apply_bg_to_tree(widget, bg_col, t)
                
        try:                                                    # decorations live only in the empty area below the widgets
            bottoms = [w.winfo_y() + w.winfo_height() for w in self.left_widgets if w.winfo_exists() and w.winfo_ismapped()]
            if bottoms:
                self.left_panel.set_decor_top(max(bottoms))
        except tk.TclError:
            pass

        h_right = self.right_panel.winfo_height()
        if h_right > 10:
            for widget in self.right_widgets:
                if not widget.winfo_exists(): continue
                wy = widget.winfo_y() + widget.winfo_height() / 2
                ratio = min(1.0, max(0.0, wy / h_right))
                bg_col = self.get_gradient_color(t["layer_top"], t["layer_bot"], ratio)
                self.apply_bg_to_tree(widget, bg_col, t)

    def apply_theme(self, theme_name):
        t = THEMES[theme_name]
        self.current_theme = theme_name
        self.root.configure(bg=t["ui_top"]) # Window background fallback
        
        self.left_panel.set_colors(t["ui_top"], t["ui_bot"], t.get("decor"))
        self.right_panel.set_colors(t["layer_top"], t["layer_bot"])
        
        for l in self.labels:
            l.configure(fg=t["fg"])
        for s in self.scales:
            s.configure(fg=t["fg"], highlightthickness=0)
            
        self.btn_images.clear()
        self.btn_images_flipped.clear()
        
        for lbl, text, w, h in self.managed_buttons:
            # Normal State Image
            img_norm = create_gradient_rect(w, h, t["btn_top"], t["btn_bot"], t["radius"], 
                                            outline_color=t.get("btn_outline"), mid_color=t.get("btn_mid"), flipped=False)
            photo_norm = ImageTk.PhotoImage(img_norm)
            self.btn_images[lbl] = photo_norm
            
            # Pressed/Flipped State Image
            img_flip = create_gradient_rect(w, h, t["btn_top"], t["btn_bot"], t["radius"], 
                                            outline_color=t.get("btn_outline"), mid_color=t.get("btn_mid"), flipped=True)
            photo_flip = ImageTk.PhotoImage(img_flip)
            self.btn_images_flipped[lbl] = photo_flip
            
            lbl.config(image=photo_norm, fg=t["btn_fg"])
                       
        self.style_entry(self.res_entry)
        self.update_layers_panel()
        self.root.after(20, self.sync_widget_colors)

    def style_entry(self, e, font=('Segoe UI', 10)):
        g = GLASS[self.current_theme]
        acc = "#%02x%02x%02x" % g["accent"]
        e.configure(bg=g["entry_bg"], fg=g["entry_fg"], insertbackground=g["entry_fg"], relief="flat", bd=0,
                    highlightthickness=1, highlightbackground=g["edge"], highlightcolor=acc,
                    selectbackground=g["list_sel"], selectforeground=g["list_sel_fg"], font=font)

    def draw_checkerboard(self):
        square_size = 20
        for i in range(0, self.canvas_size, square_size):
            for j in range(0, self.canvas_size, square_size):
                color = '#1a1a1a' if (i // square_size + j // square_size) % 2 == 0 else '#252525'
                self.canvas.create_rectangle(i, j, i + square_size, j + square_size, fill=color, outline='')

    def on_prop_change(self, *args):
        refl = next((l for l in self.layers if l.type == 'reflection'), None)
        if refl:
            refl.grad_y_scale = self.var_grad_y_scale.get()
            refl.grad_y_offset = self.var_grad_y_pos.get()
            
        glow = next((l for l in self.layers if l.type == 'glow'), None)
        if glow:
            glow.glow_opacity = int(self.var_glow_opacity.get())
            
        self.render_canvas()

    def choose_custom_grad(self):
        refl = next((l for l in self.layers if l.type == 'reflection'), None)
        if not refl:
            return
        orb = next((l for l in self.layers if l.type == 'orb'), None)
        base = orb.color if orb else (255, 255, 255)
        initial = refl.custom_grad_color or tuple(min(255, int(c + (255 - c) * 0.55)) for c in base)

        def done(rgb):
            refl.custom_grad_color = tuple(rgb)
            self.render_canvas()
        self.open_color_picker("Gradient Color", initial, done)

    def default_grad(self):
        refl = next((l for l in self.layers if l.type == 'reflection'), None)
        if refl:
            refl.custom_grad_color = None
            self.render_canvas()

    def create_orb(self):
        self.layers = [l for l in self.layers if l.type != 'orb']
        orb = OrbLayer("Orb", "orb")
        self.layers.insert(0, orb)
        self.update_layers_panel()
        self.render_canvas()

    def create_reflection(self):
        self.layers = [l for l in self.layers if l.type != 'reflection']
        ref = OrbLayer("Reflection", "reflection")
        ref.y = self.canvas_size // 2 - 40
        self.layers.append(ref)
        self.select_layer(ref)
        self.update_layers_panel()
        self.render_canvas()

    def create_glow(self):
        self.layers = [l for l in self.layers if l.type != 'glow']
        glow = OrbLayer("Glow", "glow")
        glow.glow_opacity = int(self.var_glow_opacity.get())
        glow.y = self.canvas_size // 2 + 50
        self.layers.insert(1, glow)
        self.select_layer(glow)
        self.update_layers_panel()
        self.render_canvas()

    def choose_color(self):
        orb_layer = next((l for l in self.layers if l.type == 'orb'), None)
        if not orb_layer: return

        def done(rgb):
            orb_layer.color = tuple(rgb)
            self.render_canvas()
        self.open_color_picker("Orb Color", tuple(orb_layer.color), done)

    def update_layers_panel(self):
        for widget in self.layers_frame.winfo_children():
            widget.destroy()
        for i, layer in enumerate(reversed(self.layers)):
            self.create_layer_item(layer, len(self.layers) - 1 - i)
        self.root.after(10, self.sync_widget_colors)

    def create_layer_item(self, layer, index):
        t = THEMES[self.current_theme]
        selected = (self.selected_layer == layer)
        bg_col = t["layer_sel"] if selected else t["layer_bg"]
        fg_col = "black" if self.current_theme == "Aqua" else "white"
        fg_col = t.get("layer_fg", fg_col)
        if selected:
            fg_col = t.get("layer_sel_fg", fg_col)
        
        frame = tk.Frame(self.layers_frame, bg=bg_col, relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.X, pady=2, padx=5)
        frame.is_layer_item = True
        frame.bind('<Button-1>', lambda e, l=layer: self.select_layer(l))
        
        eye = "👁️" if layer.visible else "⚫"
        eye_btn = tk.Label(frame, text=eye, bg=bg_col, fg=fg_col, cursor='hand2')
        eye_btn.pack(side=tk.RIGHT, padx=5)
        eye_btn.is_layer_item = True
        eye_btn.bind('<Button-1>', lambda e, l=layer: self.toggle_visibility(l))
        
        name_label = tk.Label(frame, text=layer.name, bg=bg_col, fg=fg_col, anchor='w')
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        name_label.is_layer_item = True
        name_label.bind('<Button-1>', lambda e, l=layer: self.select_layer(l))

    def toggle_visibility(self, layer):
        layer.visible = not layer.visible
        self.update_layers_panel()
        self.render_canvas()

    def select_layer(self, layer):
        self.selected_layer = layer
        if layer.type == 'reflection':
            self.var_grad_y_scale.set(layer.grad_y_scale)
            self.var_grad_y_pos.set(layer.grad_y_offset)
        elif layer.type == 'glow':
            self.var_glow_opacity.set(layer.glow_opacity)
            
        self.update_layers_panel()
        self.render_canvas()

    def render_composition(self, size):
        scale = size / self.canvas_size
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        if not self.layers: return img

        orb_layer = next((l for l in self.layers if l.type == 'orb'), None)
        master_mask = None

        if orb_layer and orb_layer.visible:
            master_mask = Image.new('L', (size, size), 0)
            r = int(self.orb_radius * orb_layer.scale * scale)
            x, y = int(orb_layer.x * scale), int(orb_layer.y * scale)
            ImageDraw.Draw(master_mask).ellipse([x-r, y-r, x+r, y+r], fill=255)

        for layer in self.layers:
            if not layer.visible: continue
            
            layer_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer_img)
            x, y = int(layer.x * scale), int(layer.y * scale)

            if layer.type == 'orb':
                r = int(self.orb_radius * layer.scale * scale)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=layer.color + (255,))
                img = Image.alpha_composite(img, layer_img)

            elif layer.type == 'reflection':
                w = max(1, int(self.orb_radius * 0.75 * layer.scale_x * scale))
                h = max(1, int(self.orb_radius * 0.6 * layer.scale_y * scale))
                base_col = orb_layer.color if orb_layer else (255, 255, 255)
                
                if layer.custom_grad_color:
                    lighter = layer.custom_grad_color
                else:
                    lighter = tuple(min(255, int(c + (255-c)*0.55)) for c in base_col)
                
                H = h * 2
                grad_1d = Image.new('RGBA', (1, H))
                for gy in range(H):
                    centered_y = gy - (H / 2)
                    scaled_y = centered_y / layer.grad_y_scale
                    shifted_y = scaled_y + (H / 2) - layer.grad_y_offset
                    
                    prog = shifted_y / H
                    prog = max(0.0, min(1.0, prog)) 
                    
                    cr = int(255 * (1-prog) + lighter[0] * prog)
                    cg = int(255 * (1-prog) + lighter[1] * prog)
                    cb = int(255 * (1-prog) + lighter[2] * prog)
                    ca = int(255 * (1-prog) + 30 * prog) 
                    grad_1d.putpixel((0, gy), (cr, cg, cb, ca))
                
                grad = grad_1d.resize((w*2, H))
                oval_mask = Image.new('L', (w*2, H), 0)
                ImageDraw.Draw(oval_mask).ellipse([0, 0, w*2-1, H-1], fill=255)
                grad.putalpha(ImageChops.multiply(grad.getchannel('A'), oval_mask))
                
                layer_img.paste(grad, (x-w, y-h), grad)
                
                if master_mask:
                    layer_img.putalpha(ImageChops.multiply(layer_img.getchannel('A'), master_mask))
                img = Image.alpha_composite(img, layer_img)

            elif layer.type == 'glow':
                r = int(self.orb_radius * 0.65 * layer.scale * scale)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255, int(layer.glow_opacity)))
                layer_img = layer_img.filter(ImageFilter.GaussianBlur(radius=r*0.4))
                
                if master_mask:
                    layer_img.putalpha(ImageChops.multiply(layer_img.getchannel('A'), master_mask))
                img = Image.alpha_composite(img, layer_img)

        return img

    def render_canvas(self):
        self.canvas.delete('render')
        self.canvas.delete('bbox')
        
        comp = self.render_composition(self.canvas_size)
        self.preview_photo = ImageTk.PhotoImage(comp)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_photo, tags='render')
        
        if self.selected_layer and self.selected_layer.visible:
            self.draw_bounding_box(self.selected_layer)

    def get_layer_bounds(self, layer):
        if layer.type == 'orb':
            r = self.orb_radius * layer.scale
            return (layer.x - r, layer.y - r, layer.x + r, layer.y + r)
        elif layer.type == 'reflection':
            w = self.orb_radius * 0.75 * layer.scale_x
            h = self.orb_radius * 0.6 * layer.scale_y
            return (layer.x - w, layer.y - h, layer.x + w, layer.y + h)
        elif layer.type == 'glow':
            r = self.orb_radius * 0.65 * layer.scale
            return (layer.x - r, layer.y - r, layer.x + r, layer.y + r)

    def draw_bounding_box(self, layer):
        bounds = self.get_layer_bounds(layer)
        if not bounds: return
        x1, y1, x2, y2 = bounds
        
        self.canvas.create_rectangle(x1, y1, x2, y2, outline='cyan', width=1, dash=(4, 4), tags='bbox')
        
        corners = [(x1, y1, 'corner'), (x2, y1, 'corner'), (x2, y2, 'corner'), (x1, y2, 'corner')]
        if layer.type == 'reflection':
            corners.extend([((x1+x2)/2, y1, 'top'), (x2, (y1+y2)/2, 'right'), 
                            ((x1+x2)/2, y2, 'bottom'), (x1, (y1+y2)/2, 'left')])
            
        self.scale_handles = []
        for hx, hy, htype in corners:
            h = self.canvas.create_rectangle(hx-4, hy-4, hx+4, hy+4, fill='cyan', outline='white', tags='bbox')
            self.scale_handles.append((h, htype))

    def on_canvas_click(self, event):
        if not self.selected_layer: return
        
        for handle, htype in self.scale_handles:
            coords = self.canvas.coords(handle)
            if coords and (coords[0]-5 <= event.x <= coords[2]+5) and (coords[1]-5 <= event.y <= coords[3]+5):
                self.scaling = (htype == 'corner')
                self.scaling_x = (htype in ['left', 'right'])
                self.scaling_y = (htype in ['top', 'bottom'])
                
                self.initial_scale = self.selected_layer.scale
                self.initial_scale_x = self.selected_layer.scale_x
                self.initial_scale_y = self.selected_layer.scale_y
                self.scale_start_dist = math.hypot(event.x - self.selected_layer.x, event.y - self.selected_layer.y)
                self.scale_start_x = event.x
                self.scale_start_y = event.y
                return
                
        bounds = self.get_layer_bounds(self.selected_layer)
        if bounds and (bounds[0] <= event.x <= bounds[2]) and (bounds[1] <= event.y <= bounds[3]):
            self.dragging = True
            self.drag_offset_x = event.x - self.selected_layer.x
            self.drag_offset_y = event.y - self.selected_layer.y

    def on_canvas_drag(self, event):
        if not self.selected_layer: return
        
        if self.scaling:
            dist = math.hypot(event.x - self.selected_layer.x, event.y - self.selected_layer.y)
            if self.scale_start_dist > 0:
                factor = dist / self.scale_start_dist
                if self.selected_layer.type == 'reflection':
                    self.selected_layer.scale_x = max(0.1, self.initial_scale_x * factor)
                    self.selected_layer.scale_y = max(0.1, self.initial_scale_y * factor)
                else:
                    self.selected_layer.scale = max(0.1, self.initial_scale * factor)
        
        elif self.scaling_x and self.scale_start_x != self.selected_layer.x:
            factor = abs(event.x - self.selected_layer.x) / abs(self.scale_start_x - self.selected_layer.x)
            self.selected_layer.scale_x = max(0.1, self.initial_scale_x * factor)
            
        elif self.scaling_y and self.scale_start_y != self.selected_layer.y:
            factor = abs(event.y - self.selected_layer.y) / abs(self.scale_start_y - self.selected_layer.y)
            self.selected_layer.scale_y = max(0.1, self.initial_scale_y * factor)
            
        elif self.dragging:
            nx, ny = event.x - self.drag_offset_x, event.y - self.drag_offset_y
            center = self.canvas_size // 2
            
            if abs(nx - center) < self.snap_threshold:
                nx = center
                self.canvas.itemconfig(self.snap_line_v, state='normal')
            else:
                self.canvas.itemconfig(self.snap_line_v, state='hidden')
                
            if abs(ny - center) < self.snap_threshold:
                ny = center
                self.canvas.itemconfig(self.snap_line_h, state='normal')
            else:
                self.canvas.itemconfig(self.snap_line_h, state='hidden')
                
            self.selected_layer.x, self.selected_layer.y = nx, ny
            
        self.render_canvas()

    def on_canvas_release(self, event):
        self.dragging = self.scaling = self.scaling_x = self.scaling_y = False
        self.canvas.itemconfig(self.snap_line_h, state='hidden')
        self.canvas.itemconfig(self.snap_line_v, state='hidden')

    # ==================================================================================
    #  Fullscreen / exit
    # ==================================================================================
    def enforce_fullscreen(self):
        try:
            if not self.root.attributes("-fullscreen"):
                self.root.attributes("-fullscreen", True)
        except tk.TclError:
            pass
        self.root.after(700, self.enforce_fullscreen)

    def exit_app(self):
        """Exit button / Alt+F4: play the outro animation, then quit."""
        if getattr(self, "_exiting", False):
            return
        self._exiting = True
        for fn in (lambda: self.close_ui_selector(immediate=True), lambda: self._dlg_close(immediate=True),
                   lambda: self._fsd_destroy(), lambda: self._cpk_destroy()):
            try:
                fn()
            except Exception:
                pass
        intro = getattr(self.root, "intro", None)
        if intro is not None and getattr(intro, "running", False):      # still in the intro: just leave
            self._really_exit()
            return
        try:
            AeroOutro(self.root, self._really_exit).start()
        except Exception:
            self._really_exit()

    def _really_exit(self):
        try:
            if winsound is not None:
                winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def _on_escape(self, e=None):
        if getattr(self, 'cpk', None) is not None:
            self._cpk_close(None)
        elif getattr(self, 'fsd', None) is not None:
            self._fsd_escape()
        elif self.dlg is not None:
            self._dlg_close()
        elif self.dd is not None:
            self.close_ui_selector()
        return "break"

    def _on_any_click(self, e):
        if self.dd is not None and e.widget is not self.dd["canvas"] and e.widget is not self.ui_btn:
            self.close_ui_selector()

    # ==================================================================================
    #  Screen snapshot (used for the frosted-glass look of overlays)
    # ==================================================================================
    def snapshot_root(self):
        if ImageGrab is None:
            return None
        try:
            self.root.update_idletasks()
            self.root.update()
            rx, ry = self.root.winfo_rootx(), self.root.winfo_rooty()
            rw, rh = self.root.winfo_width(), self.root.winfo_height()
            sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            shot = ImageGrab.grab().convert("RGB")
            fx, fy = shot.width / float(sw), shot.height / float(sh)
            shot = shot.crop((int(rx * fx), int(ry * fy), int((rx + rw) * fx), int((ry + rh) * fy)))
            if shot.size != (rw, rh):
                shot = shot.resize((rw, rh), Image.LANCZOS)
            return shot
        except Exception:
            return None

    def _fallback_snapshot(self, rw, rh):
        t = THEMES[self.current_theme]
        img = Image.new("RGB", (1, rh))
        c1, c2 = hex_to_rgb(t["ui_top"]), hex_to_rgb(t["ui_bot"])
        for y in range(rh):
            k = y / max(1, rh - 1)
            img.putpixel((0, y), tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3)))
        return img.resize((rw, rh))

    # ==================================================================================
    #  UI Selector drop-down
    # ==================================================================================
    DD_PW, DD_SLOT, DD_PAD, DD_ORB, DD_ORB_HOVER = 150, 104, 14, 90, 100

    def _theme_orb(self, name, size):
        key = (name, size)
        if key in self._orb_cache:
            return self._orb_cache[key]
        if name not in self._orb_src:
            src = None
            p = asset_path(THEME_ORBS[name])
            if p:
                try:
                    im = Image.open(p).convert("RGBA")
                    bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
                    src = im.crop(bb) if bb else im
                except Exception:
                    src = None
            if src is None:                                     # artwork missing: draw a simple orb
                t = THEMES[name]
                N = 400
                src = Image.new("RGBA", (N, N), (0, 0, 0, 0))
                orb = create_gradient_rect(N, N, t["btn_top"], t["btn_bot"], N // 2, outline_color=t.get("btn_outline"))
                src.alpha_composite(orb)
                ImageDraw.Draw(src).text((N // 2, N // 2), name, font=get_font(70, True), fill=(255, 255, 255, 255), anchor="mm")
            self._orb_src[name] = src
        out = self._orb_src[name].resize((size, size), Image.LANCZOS)
        self._orb_cache[key] = out
        return out

    def toggle_ui_selector(self):
        if self.dd is not None:
            self.close_ui_selector()
        else:
            self.open_ui_selector()

    def open_ui_selector(self):
        if self.dd is not None or self.dlg is not None or self.fsd is not None or self.cpk is not None:
            return
        snap = self.snapshot_root()
        rw, rh = self.root.winfo_width(), self.root.winfo_height()
        if snap is None:
            snap = self._fallback_snapshot(rw, rh)
        btn = self.ui_btn
        bx = btn.winfo_rootx() - self.root.winfo_rootx()
        by = btn.winfo_rooty() - self.root.winfo_rooty()
        PW = self.DD_PW
        PH = self.DD_PAD * 2 + self.DD_SLOT * len(THEME_ORDER) - 8
        x, y, M = bx, by + btn.winfo_height() + 8, 66
        rx0, ry0 = max(0, x - M), max(0, y - M)
        rx1, ry1 = min(rw, x + PW + M), min(rh, y + PH + M)
        backdrop = snap.crop((rx0, ry0, rx1, ry1))
        box = (x - rx0, y - ry0, x - rx0 + PW, y - ry0 + PH)
        st = GLASS[self.current_theme]
        panel = glass_panel(backdrop, box, 18, st)

        cv = tk.Canvas(self.root, width=rx1 - rx0, height=ry1 - ry0, highlightthickness=0, bd=0, cursor="hand2")
        cv.place(x=rx0, y=ry0)
        tk.Misc.tkraise(cv)
        photo = ImageTk.PhotoImage(backdrop)
        item = cv.create_image(0, 0, anchor="nw", image=photo)
        self.dd = dict(canvas=cv, photo=photo, item=item, backdrop=backdrop, panel=panel, box=box,
                       hover=None, origin=(rx0, ry0), closing=False)
        cv.bind("<Motion>", self._dd_motion)
        cv.bind("<Leave>", lambda e: self._dd_set_hover(None))
        cv.bind("<ButtonPress-1>", self._dd_click)

        final = self._dd_draw(None)
        self._dd_fade(backdrop, final, 7, opening=True)

    def _dd_slot_rect(self, i):
        x0, y0, x1, y1 = self.dd["box"]
        top = y0 + self.DD_PAD + i * self.DD_SLOT
        return (x0 + 10, top, x1 - 10, top + self.DD_SLOT - 8)

    def _dd_draw(self, hover):
        dd = self.dd
        img = dd["panel"].convert("RGBA")
        st = GLASS[self.current_theme]
        for i, name in enumerate(THEME_ORDER):
            sx0, sy0, sx1, sy1 = self._dd_slot_rect(i)
            selected = (name == self.current_theme)
            if selected or hover == i:
                S = 3
                w, h = sx1 - sx0, sy1 - sy0
                pill = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
                pd = ImageDraw.Draw(pill)
                if selected:
                    pd.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=16 * S,
                                         fill=st["accent"] + (70,), outline=st["accent"] + (230,), width=2 * S)
                else:
                    pd.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=16 * S,
                                         fill=st["pill"] + (58,), outline=st["pill"] + (120,), width=S)
                pill = pill.resize((w, h), Image.LANCZOS)
                img.alpha_composite(pill, (sx0, sy0))
            size = self.DD_ORB_HOVER if hover == i else self.DD_ORB
            orb = self._theme_orb(name, size)
            cx, cy = (sx0 + sx1) // 2, (sy0 + sy1) // 2
            if hover == i:
                glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ImageDraw.Draw(glow).ellipse([cx - size // 2 - 4, cy - size // 2 - 4, cx + size // 2 + 4, cy + size // 2 + 4],
                                             fill=st["accent"] + (110,))
                glow = glow.filter(ImageFilter.GaussianBlur(9))
                img.alpha_composite(glow)
            img.alpha_composite(orb, (cx - size // 2, cy - size // 2))
        return img.convert("RGB")

    def _dd_show(self, im):
        dd = self.dd
        if dd is None:
            return
        dd["photo"] = ImageTk.PhotoImage(im)
        dd["canvas"].itemconfig(dd["item"], image=dd["photo"])

    def _dd_fade(self, a_img, b_img, frames, opening):
        dd = self.dd
        if dd is None:
            return
        state = {"i": 0}

        def step():
            d = self.dd
            if d is None or d is not dd:
                return
            state["i"] += 1
            k = smooth(state["i"] / float(frames))
            self._dd_show(Image.blend(a_img, b_img, k if opening else 1.0 - k))
            if state["i"] < frames:
                self.root.after(14, step)
            elif not opening:
                self._dd_destroy()
        step()

    def _dd_index_at(self, x, y):
        for i in range(len(THEME_ORDER)):
            sx0, sy0, sx1, sy1 = self._dd_slot_rect(i)
            if sx0 <= x <= sx1 and sy0 <= y <= sy1:
                return i
        return None

    def _dd_motion(self, e):
        self._dd_set_hover(self._dd_index_at(e.x, e.y))

    def _dd_set_hover(self, idx):
        dd = self.dd
        if dd is None or dd["closing"] or dd["hover"] == idx:
            return
        dd["hover"] = idx
        self._dd_show(self._dd_draw(idx))

    def _dd_click(self, e):
        idx = self._dd_index_at(e.x, e.y)
        if idx is not None:
            self.close_ui_selector(immediate=True)
            self.set_theme(THEME_ORDER[idx])
        else:
            self.close_ui_selector()

    def _dd_destroy(self):
        dd, self.dd = self.dd, None
        if dd:
            try:
                dd["canvas"].destroy()
            except tk.TclError:
                pass

    def close_ui_selector(self, immediate=False):
        dd = self.dd
        if dd is None or dd["closing"]:
            return
        if immediate:
            self._dd_destroy()
            return
        dd["closing"] = True
        self._dd_fade(dd["backdrop"], self._dd_draw(dd["hover"]), 5, opening=False)

    def set_theme(self, name):
        if name not in THEMES:
            return
        self.apply_theme(name)
        self.config["theme"] = name
        save_config(self.config)

    # ==================================================================================
    #  Aero pop-up dialog (themed, frosted glass over a blurred snapshot of the editor)
    # ==================================================================================
    def show_aero_dialog(self, title, message, details=(), kind="success", thumb=None, buttons=None):
        if self.dlg is not None:
            self._dlg_close(immediate=True)
        self.close_ui_selector(immediate=True)
        snap = self.snapshot_root()
        rw, rh = self.root.winfo_width(), self.root.winfo_height()
        if snap is None:
            snap = self._fallback_snapshot(rw, rh)
        st = GLASS[self.current_theme]
        t = THEMES[self.current_theme]
        dim = make_dim(snap, st)

        PW, PH = 640, 290
        x0, y0 = (rw - PW) // 2, (rh - PH) // 2 - 10
        box = (x0, y0, x0 + PW, y0 + PH)
        scene = glass_panel(dim, box, 24, st).convert("RGBA")

        # --- artwork + text ---------------------------------------------------------
        TX = x0 + 236
        d = ImageDraw.Draw(scene)
        if thumb is not None:
            tsz = 156
            tw = thumb.copy()
            tw.thumbnail((tsz, tsz), Image.LANCZOS)
            cx, cy = x0 + 36 + tsz // 2, y0 + (PH - 54) // 2 + 8
            glow = Image.new("RGBA", scene.size, (0, 0, 0, 0))
            ImageDraw.Draw(glow).ellipse([cx - 74, cy - 70, cx + 74, cy + 78], fill=st["accent"] + (120,))
            scene.alpha_composite(glow.filter(ImageFilter.GaussianBlur(20)))
            scene.alpha_composite(tw, (cx - tw.width // 2, cy - tw.height // 2))
            badge = badge_orb(46, st["accent"] if kind == "success" else (222, 64, 56), "ok" if kind == "success" else "err")
            scene.alpha_composite(badge, (cx + tw.width // 2 - 34, cy + tw.height // 2 - 34))
        else:
            color = st["accent"] if kind == "success" else (222, 64, 56)
            big = badge_orb(110, color, "ok" if kind == "success" else "err")
            scene.alpha_composite(big, (x0 + 62, y0 + (PH - 54) // 2 - 47))

        d = ImageDraw.Draw(scene)
        f_title, f_msg, f_det = get_font(32, True), get_font(17), get_font(14)
        ty = y0 + 40
        d.text((TX, ty), title, font=f_title, fill=st["text"] + (255,))
        ty += 56
        for line in wrap_text(d, message, f_msg, PW - 236 - 36):
            d.text((TX, ty), line, font=f_msg, fill=st["text"] + (255,))
            ty += 25
        ty += 10
        for line in details:
            line = ellipsize(d, line, f_det, PW - 236 - 36)
            d.text((TX, ty), line, font=f_det, fill=st["sub"] + (255,))
            ty += 21
        final = scene.convert("RGB")

        # --- overlay canvas ---------------------------------------------------------
        cv = tk.Canvas(self.root, width=rw, height=rh, highlightthickness=0, bd=0)
        cv.place(x=0, y=0)
        tk.Misc.tkraise(cv)
        photo = ImageTk.PhotoImage(snap)
        item = cv.create_image(0, 0, anchor="nw", image=photo)
        self.dlg = dict(canvas=cv, photo=photo, item=item, snap=snap, final=final, closing=False, buttons=[], cb_close=None)

        if not buttons:
            buttons = [("OK", None)]
        self._dlg_build_buttons(buttons, box, final, t)
        self.root.bind("<Return>", lambda e: self._dlg_default())
        self.root.bind("<space>", lambda e: self._dlg_default())
        cv.focus_set()
        self._dlg_fade(snap, final, 9, opening=True)

    def _dlg_build_buttons(self, buttons, box, final, t):
        dlg = self.dlg
        bw, bh, gap = 150, 34, 14
        total = len(buttons) * bw + (len(buttons) - 1) * gap
        x = box[2] - 34 - total
        y = box[3] - 28 - bh
        dlg["plan"] = []
        for i, (label, cb) in enumerate(buttons):
            rect = (x, y, x + bw, y + bh)
            bg = final.crop(rect).convert("RGBA")
            states = {}
            norm = create_gradient_rect(bw, bh, t["btn_top"], t["btn_bot"], t["radius"], outline_color=t.get("btn_outline"), mid_color=t.get("btn_mid"))
            pressed = create_gradient_rect(bw, bh, t["btn_top"], t["btn_bot"], t["radius"], outline_color=t.get("btn_outline"), mid_color=t.get("btn_mid"), flipped=True)
            ov = Image.new("RGBA", (bw, bh), (255, 255, 255, 40))
            ov.putalpha(ImageChops.multiply(ov.getchannel("A"), norm.getchannel("A")))
            hover = Image.alpha_composite(norm, ov)
            for key, im in (("n", norm), ("h", hover), ("p", pressed)):
                comp = bg.copy()
                comp.alpha_composite(im)
                states[key] = comp.convert("RGB")
            dlg["plan"].append(dict(label=label, cb=cb, rect=rect, states=states, fg=t["btn_fg"]))
            x += bw + gap

    def _dlg_place_buttons(self):
        dlg = self.dlg
        cv = dlg["canvas"]
        for i, b in enumerate(dlg["plan"]):
            x0, y0, x1, y1 = b["rect"]
            photos = {k: ImageTk.PhotoImage(im) for k, im in b["states"].items()}
            tag = f"btn{i}"
            img_item = cv.create_image(x0, y0, anchor="nw", image=photos["n"], tags=("btn", tag))
            cv.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=b["label"], fill=b["fg"], font=("Arial", 9, "bold"), tags=("btn", tag))
            b["photos"], b["img_item"], b["down"] = photos, img_item, False
            cv.tag_bind(tag, "<Enter>", lambda e, b=b: cv.itemconfig(b["img_item"], image=b["photos"]["h"]))
            cv.tag_bind(tag, "<Leave>", lambda e, b=b: (cv.itemconfig(b["img_item"], image=b["photos"]["n"]), b.__setitem__("down", False)))
            cv.tag_bind(tag, "<ButtonPress-1>", lambda e, b=b: (cv.itemconfig(b["img_item"], image=b["photos"]["p"]), b.__setitem__("down", True)))
            cv.tag_bind(tag, "<ButtonRelease-1>", lambda e, b=b: self._dlg_release(b))
        cv.configure(cursor="arrow")

    def _dlg_release(self, b):
        was_down = b.get("down")
        cv = self.dlg["canvas"] if self.dlg else None
        if cv is None:
            return
        cv.itemconfig(b["img_item"], image=b["photos"]["h"])
        if was_down:
            cb = b["cb"]
            self._dlg_close()
            if cb:
                self.root.after(40, cb)

    def _dlg_default(self):
        if self.dlg and self.dlg.get("plan"):
            b = self.dlg["plan"][-1]
            cb = b["cb"]
            self._dlg_close()
            if cb:
                self.root.after(40, cb)

    def _dlg_show(self, im):
        dlg = self.dlg
        if dlg is None:
            return
        dlg["photo"] = ImageTk.PhotoImage(im)
        dlg["canvas"].itemconfig(dlg["item"], image=dlg["photo"])

    def _dlg_fade(self, a_img, b_img, frames, opening):
        dlg = self.dlg
        state = {"i": 0}

        def step():
            if self.dlg is not dlg or dlg is None:
                return
            state["i"] += 1
            k = smooth(state["i"] / float(frames))
            self._dlg_show(Image.blend(a_img, b_img, k if opening else 1.0 - k))
            if state["i"] < frames:
                self.root.after(14, step)
            elif opening:
                self._dlg_place_buttons()
            else:
                self._dlg_destroy()
        step()

    def _dlg_close(self, immediate=False):
        dlg = self.dlg
        if dlg is None or dlg["closing"]:
            return
        dlg["closing"] = True
        try:
            dlg["canvas"].delete("btn")
        except tk.TclError:
            pass
        for seq in ("<Return>", "<space>"):
            self.root.unbind(seq)
        if immediate:
            self._dlg_destroy()
        else:
            self._dlg_fade(dlg["snap"], dlg["final"], 6, opening=False)

    def _dlg_destroy(self):
        dlg, self.dlg = self.dlg, None
        if dlg:
            try:
                dlg["canvas"].destroy()
            except tk.TclError:
                pass

    # ==================================================================================
    #  Saving
    # ==================================================================================
    @staticmethod
    def _reveal_in_folder(path):
        try:
            path = os.path.normpath(path)
            if sys.platform.startswith("win"):
                subprocess.Popen(["explorer", "/select,", path])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", path])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(path)])
        except Exception:
            pass

    # ==================================================================================
    #  Themed colour picker (colour wheel, brightness bar, hex/RGB, 10 recent colours)
    # ==================================================================================
    CP_D, CP_PAD = 300, 8                      # wheel diameter, rim padding
    CP_BAR_W, CP_BAR_H = 240, 24

    def _recent_colors(self):
        out = []
        for hx in self.config.get("recent_colors", []):
            try:
                h = str(hx).strip().lstrip("#")
                if len(h) == 6:
                    out.append((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)))
            except ValueError:
                continue
        return out[:10]

    def _remember_color(self, rgb):
        hx = "#%02x%02x%02x" % tuple(rgb)
        old = [h for h in self.config.get("recent_colors", []) if str(h).lower() != hx]
        self.config["recent_colors"] = ([hx] + old)[:10]
        save_config(self.config)

    def open_color_picker(self, title, initial, on_pick):
        if self.cpk is not None or self.fsd is not None or self.dlg is not None:
            return
        self.close_ui_selector(immediate=True)
        snap = self.snapshot_root()
        rw, rh = self.root.winfo_width(), self.root.winfo_height()
        if snap is None:
            snap = self._fallback_snapshot(rw, rh)
        st = GLASS[self.current_theme]
        dim = make_dim(snap, st)
        PW, PH = 740, min(500, rh - 50)
        x0, y0 = (rw - PW) // 2, (rh - PH) // 2
        box = (x0, y0, x0 + PW, y0 + PH)
        scene = glass_panel(dim, box, 22, st).convert("RGBA")
        d = ImageDraw.Draw(scene)
        d.text((x0 + 30, y0 + 16), "Choose " + title, font=get_font(25, True), fill=st["text"] + (255,))

        # recent colours are baked into the panel (they don't change while the picker is open)
        recents = self._recent_colors()
        rects = []
        for i in range(10):
            cx, cy = x0 + 380 + (i % 5) * 64, y0 + 316 + (i // 5) * 42
            if i < len(recents):
                scene.alpha_composite(swatch_image(recents[i], 56, 34, 8), (cx, cy))
            else:
                scene.alpha_composite(empty_slot_image(56, 34, 8, st["text"]), (cx, cy))
            rects.append((cx, cy, cx + 56, cy + 34))
        final = scene.convert("RGB")

        cv = tk.Canvas(self.root, width=rw, height=rh, highlightthickness=0, bd=0)
        cv.place(x=0, y=0)
        tk.Misc.tkraise(cv)
        photo = ImageTk.PhotoImage(snap)
        item = cv.create_image(0, 0, anchor="nw", image=photo)
        h, s_, v = colorsys.rgb_to_hsv(*[c / 255.0 for c in initial])
        self.cpk = dict(canvas=cv, photo=photo, item=item, snap=snap, final=final, box=box, closing=False,
                        on_pick=on_pick, buttons=[], widgets=[], initial=tuple(initial), h=h, s=s_, v=v,
                        recents=recents, recent_rects=rects, drag=None, hover=None, lock=False, keep={})
        self._cpk_fade(snap, final, 9, opening=True)

    def _cpk_fade(self, a_img, b_img, frames, opening):
        cpk = self.cpk
        state = {"i": 0}

        def step():
            if self.cpk is not cpk or cpk is None:
                return
            state["i"] += 1
            k = smooth(state["i"] / float(frames))
            cpk["photo"] = ImageTk.PhotoImage(Image.blend(a_img, b_img, k if opening else 1.0 - k))
            cpk["canvas"].itemconfig(cpk["item"], image=cpk["photo"])
            if state["i"] < frames:
                self.root.after(14, step)
            elif opening:
                try:
                    self._cpk_build()
                except Exception:                             # since we don't need the software to fart befoer the user, never leave the user stuck: native chooser as a fallback 
                    init, cb = cpk["initial"], cpk["on_pick"]
                    self._cpk_destroy()
                    col = colorchooser.askcolor(color="#%02x%02x%02x" % init)
                    if col and col[0]:
                        cb(tuple(int(c) for c in col[0]))
            else:
                cb, rgb = cpk.get("after"), cpk.get("result")
                self._cpk_destroy()
                if cb and rgb:
                    self.root.after(30, lambda: cb(rgb))
        step()

    def _cpk_destroy(self):
        cpk, self.cpk = self.cpk, None
        if cpk:
            for w in cpk.get("widgets", []):
                try:
                    w.destroy()
                except tk.TclError:
                    pass
            try:
                cpk["canvas"].destroy()
            except tk.TclError:
                pass
            for seq in ("<Return>",):
                try:
                    self.root.unbind(seq)
                except tk.TclError:
                    pass

    def _cpk_rgb(self):
        c = self.cpk
        return tuple(int(round(x * 255)) for x in colorsys.hsv_to_rgb(c["h"], c["s"], c["v"]))

    def _cpk_close(self, rgb):
        cpk = self.cpk
        if cpk is None or cpk["closing"]:
            return
        cpk["closing"] = True
        cpk["result"] = rgb
        cpk["after"] = cpk["on_pick"] if rgb else None
        if rgb:
            self._remember_color(rgb)
        for w in cpk["widgets"]:
            try:
                w.destroy()
            except tk.TclError:
                pass
        cpk["widgets"] = []
        cpk["canvas"].delete("ui")
        self._cpk_fade(cpk["snap"], cpk["final"], 6, opening=False)

    def _cpk_ok(self):
        if self.cpk and not self.cpk["closing"]:
            self._cpk_close(self._cpk_rgb())

    def _cpk_build(self):
        c = self.cpk
        cv, (bx0, by0, bx1, by1) = c["canvas"], c["box"]
        PW, PH = bx1 - bx0, by1 - by0
        st = GLASS[self.current_theme]
        txt = "#%02x%02x%02x" % st["text"]
        sub = "#%02x%02x%02x" % st["sub"]
        acc = "#%02x%02x%02x" % st["accent"]
        D, pad = self.CP_D, self.CP_PAD

        # --- wheel -----------------------------------------------------------------
        c["wx"], c["wy"] = bx0 + 36, by0 + 68
        c["cx"], c["cy"] = c["wx"] + D // 2, c["wy"] + D // 2
        region = (c["wx"] - pad, c["wy"] - pad, c["wx"] + D + pad, c["wy"] + D + pad)
        bg = c["final"].crop(region).convert("RGBA")
        sh = Image.new("L", bg.size, 0)
        ImageDraw.Draw(sh).ellipse([pad + 2, pad + 7, pad + D + 2, pad + D + 7], fill=110)
        sh = sh.filter(ImageFilter.GaussianBlur(7))
        bg = Image.composite(Image.new("RGBA", bg.size, (0, 0, 0, 255)), bg, sh)
        c["wheel_bg"] = bg
        c["ring"] = wheel_ring(D, pad)
        c["wheel_item"] = cv.create_image(region[0], region[1], anchor="nw", tags="ui")

        # --- brightness bar ----------------------------------------------------------
        c["bx0"], c["by0"] = bx0 + 66, by0 + 398
        c["bar_bg"] = c["final"].crop((c["bx0"], c["by0"], c["bx0"] + self.CP_BAR_W, c["by0"] + self.CP_BAR_H)).convert("RGBA")
        c["bar_item"] = cv.create_image(c["bx0"], c["by0"], anchor="nw", tags="ui")
        mid = c["by0"] + self.CP_BAR_H // 2
        cv.create_text(bx0 + 44, mid, text="\u2212", fill=txt, font=("Arial", 18, "bold"), tags="ui")
        cv.create_text(bx0 + 330, mid, text="+", fill=txt, font=("Arial", 18, "bold"), tags="ui")
        c["handle"] = cv.create_rectangle(0, 0, 0, 0, fill="#ffffff", outline="#202020", width=2, tags="ui")

        # --- markers -------------------------------------------------------------------
        c["m_out"] = cv.create_oval(0, 0, 0, 0, outline="#000000", width=3, tags="ui")
        c["m_in"] = cv.create_oval(0, 0, 0, 0, outline="#ffffff", width=2, tags="ui")

        # --- right column: current / new, hex, rgb, recents ----------------------------
        rx = bx0 + 380
        cv.create_text(rx, by0 + 80, anchor="w", text="Current", fill=sub, font=("Segoe UI", 9), tags="ui")
        cv.create_text(rx + 170, by0 + 80, anchor="w", text="New", fill=sub, font=("Segoe UI", 9, "bold"), tags="ui")
        c["cur_rect"] = (rx, by0 + 92, rx + 150, by0 + 172)
        c["new_rect"] = (rx + 170, by0 + 92, rx + 320, by0 + 172)
        cur = c["final"].crop(c["cur_rect"]).convert("RGBA")
        cur.alpha_composite(swatch_image(c["initial"], 150, 80, 12))
        c["cur_photo"] = ImageTk.PhotoImage(cur.convert("RGB"))
        cv.create_image(c["cur_rect"][0], c["cur_rect"][1], anchor="nw", image=c["cur_photo"], tags="ui")
        c["new_bg"] = c["final"].crop(c["new_rect"]).convert("RGBA")
        c["new_item"] = cv.create_image(c["new_rect"][0], c["new_rect"][1], anchor="nw", tags="ui")

        def place(widget, x, y, w, h):
            cv.create_window(x, y, window=widget, anchor="nw", width=w, height=h, tags="ui")
            c["widgets"].append(widget)

        cv.create_text(rx, by0 + 211, anchor="w", text="Hex", fill=txt, font=("Segoe UI", 10), tags="ui")
        c["hex"] = tk.Entry(cv)
        self.style_entry(c["hex"], font=("Consolas", 10))
        place(c["hex"], rx + 44, by0 + 196, 118, 30)
        c["hex"].bind("<KeyRelease>", lambda e: self._cpk_entry("hex"))
        c["hex"].bind("<Return>", lambda e: self._cpk_ok())
        c["rgb"] = []
        for k, (lab, ox) in enumerate((("R", 0), ("G", 108), ("B", 216))):
            cv.create_text(rx + ox, by0 + 253, anchor="w", text=lab, fill=txt, font=("Segoe UI", 10), tags="ui")
            ent = tk.Entry(cv)
            self.style_entry(ent, font=("Consolas", 10))
            place(ent, rx + ox + 18, by0 + 238, 60, 30)
            ent.bind("<KeyRelease>", lambda e: self._cpk_entry("rgb"))
            ent.bind("<Return>", lambda e: self._cpk_ok())
            c["rgb"].append(ent)

        cv.create_text(rx, by0 + 298, anchor="w", text="Recent colors", fill=sub, font=("Segoe UI", 9), tags="ui")
        c["hover_item"] = cv.create_rectangle(0, 0, 0, 0, outline=acc, width=2, state="hidden", tags="ui")

        # --- buttons ---------------------------------------------------------------------
        by = by0 + PH - 50
        self._cv_button((bx1 - 30 - 130, by, bx1 - 30, by + 34), "Cancel", lambda: self._cpk_close(None), ov=c)
        self._cv_button((bx1 - 30 - 130 - 12 - 130, by, bx1 - 30 - 130 - 12, by + 34), "OK", self._cpk_ok, ov=c)

        cv.bind("<ButtonPress-1>", self._cpk_press)
        cv.bind("<B1-Motion>", self._cpk_motion)
        cv.bind("<Motion>", self._cpk_motion)
        cv.bind("<ButtonRelease-1>", lambda e: c.__setitem__("drag", None))
        self.root.bind("<Return>", lambda e: self._cpk_ok())
        self._cpk_update("init")

    # ---- rendering + state ---------------------------------------------------------
    def _cpk_update(self, src):
        c = self.cpk
        if c is None:
            return
        cv = c["canvas"]
        rgb = self._cpk_rgb()
        if src != "bar":                                       # hue / saturation changed -> bar gradient follows
            full = tuple(int(round(x * 255)) for x in colorsys.hsv_to_rgb(c["h"], c["s"], 1.0))
            img = c["bar_bg"].copy()
            img.alpha_composite(brightness_bar(self.CP_BAR_W, self.CP_BAR_H, full))
            c["bar_photo"] = ImageTk.PhotoImage(img.convert("RGB"))
            cv.itemconfig(c["bar_item"], image=c["bar_photo"])
        if src != "wheel":                                     # brightness changed -> wheel re-lit
            img = c["wheel_bg"].copy()
            img.alpha_composite(hsv_wheel(self.CP_D, c["v"]), (self.CP_PAD, self.CP_PAD))
            img.alpha_composite(c["ring"])
            c["wheel_photo"] = ImageTk.PhotoImage(img.convert("RGB"))
            cv.itemconfig(c["wheel_item"], image=c["wheel_photo"])
        sw = c["new_bg"].copy()
        sw.alpha_composite(swatch_image(rgb, 150, 80, 12))
        c["new_photo"] = ImageTk.PhotoImage(sw.convert("RGB"))
        cv.itemconfig(c["new_item"], image=c["new_photo"])

        ang = c["h"] * 2 * math.pi
        mx = c["cx"] + c["s"] * (self.CP_D / 2.0) * math.cos(ang)
        my = c["cy"] - c["s"] * (self.CP_D / 2.0) * math.sin(ang)
        cv.coords(c["m_out"], mx - 9, my - 9, mx + 9, my + 9)
        cv.coords(c["m_in"], mx - 8, my - 8, mx + 8, my + 8)
        hx = c["bx0"] + c["v"] * self.CP_BAR_W
        cv.coords(c["handle"], hx - 4, c["by0"] - 4, hx + 4, c["by0"] + self.CP_BAR_H + 4)

        c["lock"] = True                                       # keep the text boxes in sync, except the one being typed in
        if src != "entry_hex":
            c["hex"].delete(0, "end")
            c["hex"].insert(0, "#%02X%02X%02X" % rgb)
        if src != "entry_rgb":
            for ent, val in zip(c["rgb"], rgb):
                ent.delete(0, "end")
                ent.insert(0, str(val))
        c["lock"] = False

    def _cpk_set_rgb(self, rgb, src):
        c = self.cpk
        h, s_, v = colorsys.rgb_to_hsv(*[x / 255.0 for x in rgb])
        if s_ > 0.0 and v > 0.0:
            c["h"] = h
        if v > 0.0:
            c["s"] = s_
        c["v"] = v
        self._cpk_update(src)

    def _cpk_entry(self, kind):
        c = self.cpk
        if c is None or c["lock"]:
            return
        try:
            if kind == "hex":
                t = c["hex"].get().strip().lstrip("#")
                if len(t) == 3:
                    t = "".join(ch * 2 for ch in t)
                if len(t) != 6:
                    return
                rgb = (int(t[0:2], 16), int(t[2:4], 16), int(t[4:6], 16))
            else:
                rgb = tuple(max(0, min(255, int(e.get().strip()))) for e in c["rgb"])
        except ValueError:
            return
        self._cpk_set_rgb(rgb, "entry_" + kind)

    def _cpk_wheel_xy(self, x, y):
        c = self.cpk
        dx, dy = x - c["cx"], y - c["cy"]
        r = min(1.0, math.hypot(dx, dy) / (self.CP_D / 2.0))
        c["h"] = (math.atan2(-dy, dx) / (2 * math.pi)) % 1.0
        c["s"] = r
        self._cpk_update("wheel")

    def _cpk_bar_x(self, x):
        c = self.cpk
        c["v"] = max(0.0, min(1.0, (x - c["bx0"]) / float(self.CP_BAR_W)))
        self._cpk_update("bar")

    def _cpk_recent_at(self, x, y):
        for i, r in enumerate(self.cpk["recent_rects"]):
            if r[0] <= x <= r[2] and r[1] <= y <= r[3] and i < len(self.cpk["recents"]):
                return i
        return None

    def _cpk_press(self, e):
        c = self.cpk
        if c is None or c["closing"]:
            return
        if math.hypot(e.x - c["cx"], e.y - c["cy"]) <= self.CP_D / 2.0 + 6:
            c["drag"] = "wheel"
            self._cpk_wheel_xy(e.x, e.y)
        elif c["bx0"] - 10 <= e.x <= c["bx0"] + self.CP_BAR_W + 10 and c["by0"] - 8 <= e.y <= c["by0"] + self.CP_BAR_H + 8:
            c["drag"] = "bar"
            self._cpk_bar_x(e.x)
        else:
            i = self._cpk_recent_at(e.x, e.y)
            if i is not None:
                self._cpk_set_rgb(c["recents"][i], "recent")

    def _cpk_motion(self, e):
        c = self.cpk
        if c is None or c["closing"]:
            return
        if c["drag"] == "wheel":
            self._cpk_wheel_xy(e.x, e.y)
        elif c["drag"] == "bar":
            self._cpk_bar_x(e.x)
        else:
            i = self._cpk_recent_at(e.x, e.y)
            if i != c["hover"]:
                c["hover"] = i
                if i is None:
                    c["canvas"].itemconfig(c["hover_item"], state="hidden")
                else:
                    r = c["recent_rects"][i]
                    c["canvas"].coords(c["hover_item"], r[0] - 2, r[1] - 2, r[2] + 2, r[3] + 2)
                    c["canvas"].itemconfig(c["hover_item"], state="normal")

    # ==================================================================================
    #  Themed "Save As" browser (replaces the native Windows file dialog)
    # ==================================================================================
    def _start_dir(self):
        cur = self.config.get("last_dir")
        while cur and not os.path.isdir(cur):
            parent = os.path.dirname(cur)
            if parent == cur:
                cur = None
                break
            cur = parent
        if cur:
            return cur
        pics = os.path.join(os.path.expanduser("~"), "Pictures")
        return pics if os.path.isdir(pics) else os.path.expanduser("~")

    @staticmethod
    def _places():
        home = os.path.expanduser("~")
        out, seen = [], set()

        def add(label, *parts):
            for base in (home, os.path.join(home, "OneDrive")):
                p = os.path.join(base, *parts)
                if os.path.isdir(p) and p not in seen:
                    seen.add(p)
                    out.append((label, p, "folder"))
                    return
        add("Desktop", "Desktop")
        add("Documents", "Documents")
        add("Pictures", "Pictures")
        add("Downloads", "Downloads")
        out.append(("Home", home, "folder"))
        out.append(("Orb Creator folder", app_dir(), "folder"))
        if sys.platform.startswith("win"):
            import string
            for L in string.ascii_uppercase:
                p = L + ":\\"
                if os.path.exists(p):
                    out.append((p, p, "drive"))
        else:
            out.append(("/", "/", "drive"))
        return out

    @staticmethod
    def _scan_dir(path):
        """Folders + .png files of a directory, folders first. Returns (items, error)."""
        items = []
        try:
            with os.scandir(path) as it:
                for e in it:
                    if e.name.startswith("."):
                        continue
                    try:
                        st = e.stat()
                        isdir = e.is_dir()
                    except OSError:
                        continue
                    if sys.platform.startswith("win") and (getattr(st, "st_file_attributes", 0) & 0x2):
                        continue                                    # hidden on Windows
                    if isdir:
                        items.append((True, e.name, st.st_mtime, 0))
                    elif e.name.lower().endswith(".png"):
                        items.append((False, e.name, st.st_mtime, st.st_size))
        except OSError as ex:
            return None, str(ex)
        items.sort(key=lambda r: (not r[0], r[1].lower()))
        return items, None

    def open_save_browser(self, start_dir, initial_name, on_pick):
        if self.fsd is not None or self.dlg is not None or self.cpk is not None:
            return
        self.close_ui_selector(immediate=True)
        snap = self.snapshot_root()
        rw, rh = self.root.winfo_width(), self.root.winfo_height()
        if snap is None:
            snap = self._fallback_snapshot(rw, rh)
        st = GLASS[self.current_theme]
        dim = make_dim(snap, st)
        PW, PH = min(960, rw - 80), min(610, rh - 70)
        x0, y0 = (rw - PW) // 2, (rh - PH) // 2
        box = (x0, y0, x0 + PW, y0 + PH)
        scene = glass_panel(dim, box, 22, st).convert("RGBA")
        d = ImageDraw.Draw(scene)
        d.text((x0 + 30, y0 + 16), "Save Aero Orb", font=get_font(25, True), fill=st["text"] + (255,))
        final = scene.convert("RGB")

        cv = tk.Canvas(self.root, width=rw, height=rh, highlightthickness=0, bd=0)
        cv.place(x=0, y=0)
        tk.Misc.tkraise(cv)
        photo = ImageTk.PhotoImage(snap)
        item = cv.create_image(0, 0, anchor="nw", image=photo)
        self.fsd = dict(canvas=cv, photo=photo, item=item, snap=snap, final=final, box=box, closing=False,
                        on_pick=on_pick, start_dir=start_dir, initial=initial_name, buttons=[], widgets=[],
                        cwd=None, hist=[], rows={}, mode="file", confirm=None, keep=[])
        self._fsd_fade(snap, final, 9, opening=True)

    def _fsd_fade(self, a_img, b_img, frames, opening):
        fsd = self.fsd
        state = {"i": 0}

        def step():
            if self.fsd is not fsd or fsd is None:
                return
            state["i"] += 1
            k = smooth(state["i"] / float(frames))
            fsd["photo"] = ImageTk.PhotoImage(Image.blend(a_img, b_img, k if opening else 1.0 - k))
            fsd["canvas"].itemconfig(fsd["item"], image=fsd["photo"])
            if state["i"] < frames:
                self.root.after(14, step)
            elif opening:
                try:
                    self._fsd_build()
                except Exception as ex:                       # never leave the user stuck: fall back to the native dialog (mentioned the farting of the software in previous comment)
                    self._fsd_destroy()
                    self._native_save_fallback()
            else:
                cb, path = fsd.get("after"), fsd.get("result")
                self._fsd_destroy()
                if cb:
                    self.root.after(30, lambda: cb(path))
        step()

    def _fsd_destroy(self):
        fsd, self.fsd = self.fsd, None
        if fsd:
            for w in fsd.get("widgets", []):
                try:
                    w.destroy()
                except tk.TclError:
                    pass
            try:
                fsd["canvas"].destroy()
            except tk.TclError:
                pass

    def _native_save_fallback(self):
        pending = getattr(self, "_pending_export", None)
        if not pending:
            return
        filename = filedialog.asksaveasfilename(parent=self.root, title="Save Aero Orb", defaultextension=".png",
                                                initialdir=self._start_dir(), filetypes=[("PNG", "*.png")])
        if filename:
            self._export_orb(filename, pending)

    def _fsd_close(self, path=None):
        fsd = self.fsd
        if fsd is None or fsd["closing"]:
            return
        fsd["closing"] = True
        fsd["result"] = path
        fsd["after"] = fsd["on_pick"] if path else None
        for w in fsd["widgets"]:
            try:
                w.destroy()
            except tk.TclError:
                pass
        fsd["widgets"] = []
        fsd["canvas"].delete("ui")
        self._fsd_fade(fsd["snap"], fsd["final"], 6, opening=False)

    def _fsd_escape(self):
        fsd = self.fsd
        if fsd is None:
            return
        if fsd.get("mode") == "folder":
            self._fsd_set_mode("file")
        else:
            self._fsd_close(None)

    # ---- widgets ---------------------------------------------------------------------
    def _cv_button(self, rect, label, cb, font=("Arial", 9, "bold"), ov=None):
        fsd = ov or self.fsd
        cv, base, t = fsd["canvas"], fsd["final"], THEMES[self.current_theme]
        x0, y0, x1, y1 = rect
        bw, bh = x1 - x0, y1 - y0
        bg = base.crop(rect).convert("RGBA")
        kw = dict(outline_color=t.get("btn_outline"), mid_color=t.get("btn_mid"))
        norm = create_gradient_rect(bw, bh, t["btn_top"], t["btn_bot"], t["radius"], **kw)
        pressed = create_gradient_rect(bw, bh, t["btn_top"], t["btn_bot"], t["radius"], flipped=True, **kw)
        ov = Image.new("RGBA", (bw, bh), (255, 255, 255, 40))
        ov.putalpha(ImageChops.multiply(ov.getchannel("A"), norm.getchannel("A")))
        photos = {}
        for key, im in (("n", norm), ("h", Image.alpha_composite(norm, ov)), ("p", pressed)):
            comp = bg.copy()
            comp.alpha_composite(im)
            photos[key] = ImageTk.PhotoImage(comp.convert("RGB"))
        tag = "b%d" % len(fsd["buttons"])
        img = cv.create_image(x0, y0, anchor="nw", image=photos["n"], tags=("ui", tag))
        txt = cv.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=label, fill=t["btn_fg"], font=font, tags=("ui", tag))
        rec = dict(photos=photos, img=img, text=txt, down=False)

        def enter(e):
            cv.itemconfig(img, image=photos["h"])

        def leave(e):
            cv.itemconfig(img, image=photos["n"])
            rec["down"] = False

        def press(e):
            cv.itemconfig(img, image=photos["p"])
            rec["down"] = True

        def release(e):
            cv.itemconfig(img, image=photos["h"])
            if rec["down"]:
                rec["down"] = False
                cb()
        cv.tag_bind(tag, "<Enter>", enter)
        cv.tag_bind(tag, "<Leave>", leave)
        cv.tag_bind(tag, "<ButtonPress-1>", press)
        cv.tag_bind(tag, "<ButtonRelease-1>", release)
        fsd["buttons"].append(rec)
        return rec

    def _fsd_style(self):
        g = GLASS[self.current_theme]
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")                           # the only theme whose colours we can fully control
        except tk.TclError:
            pass
        nm = "Aero.Treeview"
        style.configure(nm, background=g["list_bg"], fieldbackground=g["list_bg"], foreground=g["list_fg"],
                        rowheight=26, borderwidth=0, relief="flat", font=("Segoe UI", 10))
        style.map(nm, background=[("selected", g["list_sel"])], foreground=[("selected", g["list_sel_fg"])])
        style.layout(nm, [("Treeview.treearea", {"sticky": "nswe"})])
        style.configure(nm + ".Heading", background=g["list_head"], foreground=g["list_fg"], relief="flat",
                        borderwidth=0, font=("Segoe UI", 9, "bold"))
        style.map(nm + ".Heading", background=[("active", g["list_head"])])
        style.configure("Aero.Vertical.TScrollbar", background=g["list_head"], troughcolor=g["list_bg"],
                        bordercolor=g["list_bg"], lightcolor=g["list_head"], darkcolor=g["list_head"],
                        arrowcolor=g["list_fg"], relief="flat", gripcount=0)
        style.map("Aero.Vertical.TScrollbar", background=[("active", g["edge"])])

    def _fsd_build(self):
        fsd = self.fsd
        cv, (bx0, by0, bx1, by1) = fsd["canvas"], fsd["box"]
        PW, PH = bx1 - bx0, by1 - by0
        g = GLASS[self.current_theme]
        txt_col = "#%02x%02x%02x" % g["text"]
        sub_col = "#%02x%02x%02x" % g["sub"]
        self._fsd_style()
        fsd["icons"] = {k: ImageTk.PhotoImage(make_icon(k)) for k in ("folder", "drive", "png")}

        def place(widget, x, y, w, h):
            cv.create_window(bx0 + x, by0 + y, window=widget, anchor="nw", width=w, height=h, tags="ui")
            fsd["widgets"].append(widget)

        # toolbar: back / up / path
        self._cv_button((bx0 + 30, by0 + 66, bx0 + 68, by0 + 96), "\u2190", self._fsd_back, ("Arial", 12, "bold"))
        self._cv_button((bx0 + 74, by0 + 66, bx0 + 112, by0 + 96), "\u2191", self._fsd_up, ("Arial", 12, "bold"))
        path_e = tk.Entry(cv)
        self.style_entry(path_e)
        place(path_e, 122, 66, PW - 122 - 30, 30)
        path_e.bind("<Return>", lambda e: self._fsd_go(path_e.get().strip().strip('"')) or None)
        fsd["path_entry"] = path_e

        list_top, list_bot = 108, PH - 146
        # places sidebar
        side_frame = tk.Frame(cv, bg=g["edge"], bd=0, highlightthickness=0)
        side = ttk.Treeview(side_frame, show="tree", selectmode="browse", style="Aero.Treeview")
        side.pack(fill="both", expand=True, padx=1, pady=1)
        place(side_frame, 30, list_top, 196, list_bot - list_top)
        fsd["place_map"] = {}
        for i, (label, p, kind) in enumerate(self._places()):
            iid = "p%d" % i
            side.insert("", "end", iid=iid, text="  " + label, image=fsd["icons"][kind], tags=("odd" if i % 2 else "even",))
            fsd["place_map"][iid] = p
        side.tag_configure("odd", background=g["list_alt"])
        side.tag_configure("even", background=g["list_bg"])
        side.bind("<<TreeviewSelect>>", self._fsd_on_place)
        fsd["side"] = side

        # file list + scrollbar
        file_frame = tk.Frame(cv, bg=g["edge"], bd=0, highlightthickness=0)
        inner = tk.Frame(file_frame, bg=g["list_bg"], bd=0)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        tree = ttk.Treeview(inner, columns=("modified", "size"), show="tree headings", selectmode="browse", style="Aero.Treeview")
        sb = ttk.Scrollbar(inner, orient="vertical", command=tree.yview, style="Aero.Vertical.TScrollbar")
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        tree.heading("#0", text="Name", anchor="w")
        tree.heading("modified", text="Date modified", anchor="w")
        tree.heading("size", text="Size", anchor="e")
        tree.column("#0", width=300, stretch=True)
        tree.column("modified", width=160, stretch=False, anchor="w")
        tree.column("size", width=90, stretch=False, anchor="e")
        tree.tag_configure("odd", background=g["list_alt"])
        tree.tag_configure("even", background=g["list_bg"])
        place(file_frame, 236, list_top, PW - 236 - 30, list_bot - list_top)
        tree.bind("<<TreeviewSelect>>", self._fsd_on_select)
        tree.bind("<Double-1>", self._fsd_on_double)
        tree.bind("<Return>", lambda e: self._fsd_on_enter())
        fsd["tree"] = tree

        # status + file name + type
        fsd["status"] = cv.create_text(bx0 + 30, by0 + PH - 131, anchor="w", text="", fill=sub_col, font=("Segoe UI", 9), tags="ui")
        fsd["name_label"] = cv.create_text(bx0 + 30, by0 + PH - 101, anchor="w", text="File name:", fill=txt_col, font=("Segoe UI", 10), tags="ui")
        name_e = tk.Entry(cv)
        self.style_entry(name_e)
        place(name_e, 136, PH - 116, PW - 136 - 30, 30)
        fsd["name_entry"] = name_e
        name_e.bind("<Return>", lambda e: self._fsd_primary())
        name_e.bind("<Key>", lambda e: self._fsd_reset_confirm() if e.keysym not in ("Return", "Escape") else None)
        cv.create_text(bx0 + 30, by0 + PH - 69, anchor="w", text="Save as type:", fill=txt_col, font=("Segoe UI", 10), tags="ui")
        cv.create_text(bx0 + 136, by0 + PH - 69, anchor="w", text="PNG image (*.png)", fill=sub_col, font=("Segoe UI", 10), tags="ui")

        # buttons
        by = by0 + PH - 50
        fsd["btn_new"] = self._cv_button((bx0 + 30, by, bx0 + 170, by + 34), "New Folder", lambda: self._fsd_set_mode("folder"))
        fsd["btn_cancel"] = self._cv_button((bx1 - 30 - 130, by, bx1 - 30, by + 34), "Cancel", self._fsd_escape)
        fsd["btn_primary"] = self._cv_button((bx1 - 30 - 130 - 12 - 130, by, bx1 - 30 - 130 - 12, by + 34), "Save", self._fsd_primary)

        self._fsd_go(fsd["start_dir"])
        name_e.insert(0, fsd["initial"])
        name_e.focus_set()
        stem = os.path.splitext(fsd["initial"])[0]
        name_e.selection_range(0, len(stem))
        name_e.icursor(len(stem))

    # ---- behaviour -------------------------------------------------------------------
    def _fsd_status(self, msg, kind="info"):
        fsd = self.fsd
        if fsd is None:
            return
        g = GLASS[self.current_theme]
        col = {"info": "#%02x%02x%02x" % g["sub"], "error": "#d8362a", "warn": "#d86a00" if self.current_theme != "Dark" else "#ffb066"}[kind]
        fsd["canvas"].itemconfig(fsd["status"], text=msg, fill=col)

    def _fsd_reset_confirm(self):
        fsd = self.fsd
        if fsd and fsd.get("confirm"):
            fsd["confirm"] = None
            fsd["canvas"].itemconfig(fsd["btn_primary"]["text"], text="Save" if fsd["mode"] == "file" else "Create")
            self._fsd_status("")

    def _fsd_go(self, path, push=True):
        fsd = self.fsd
        if fsd is None:
            return False
        p = os.path.abspath(os.path.expanduser(path))
        items, err = self._scan_dir(p)
        if items is None:
            self._fsd_status("Can't open that folder.", "error")
            return False
        if push and fsd["cwd"] and fsd["cwd"] != p:
            fsd["hist"].append(fsd["cwd"])
        fsd["cwd"] = p
        tree = fsd["tree"]
        tree.delete(*tree.get_children())
        fsd["rows"] = {}
        for i, (isdir, name, mt, size) in enumerate(items):
            try:
                when = time.strftime("%Y-%m-%d  %H:%M", time.localtime(mt))
            except (OSError, ValueError, OverflowError):
                when = ""
            iid = str(i)
            tree.insert("", "end", iid=iid, text=" " + name, image=fsd["icons"]["folder" if isdir else "png"],
                        values=(when, "" if isdir else human_size(size)), tags=("odd" if i % 2 else "even",))
            fsd["rows"][iid] = (isdir, name)
        pe = fsd["path_entry"]
        pe.delete(0, "end")
        pe.insert(0, p)
        nf = sum(1 for r in items if r[0])
        self._fsd_reset_confirm()
        self._fsd_status("%d folder%s, %d PNG file%s" % (nf, "" if nf == 1 else "s", len(items) - nf, "" if len(items) - nf == 1 else "s"))
        return False

    def _fsd_up(self):
        fsd = self.fsd
        if fsd and fsd["cwd"]:
            parent = os.path.dirname(fsd["cwd"].rstrip("\\/")) or fsd["cwd"]
            if parent and parent != fsd["cwd"]:
                self._fsd_go(parent)

    def _fsd_back(self):
        fsd = self.fsd
        if fsd and fsd["hist"]:
            self._fsd_go(fsd["hist"].pop(), push=False)

    def _fsd_on_place(self, e):
        fsd = self.fsd
        sel = fsd["side"].selection() if fsd else ()
        if sel:
            self._fsd_go(fsd["place_map"][sel[0]])

    def _fsd_set_name(self, name):
        e = self.fsd["name_entry"]
        e.delete(0, "end")
        e.insert(0, name)

    def _fsd_on_select(self, e):
        fsd = self.fsd
        sel = fsd["tree"].selection() if fsd else ()
        if sel and fsd["mode"] == "file":
            isdir, name = fsd["rows"][sel[0]]
            if not isdir:
                self._fsd_set_name(name)
                self._fsd_reset_confirm()

    def _fsd_on_double(self, e):
        fsd = self.fsd
        iid = fsd["tree"].identify_row(e.y)
        if not iid:
            return
        isdir, name = fsd["rows"][iid]
        if isdir:
            self._fsd_go(os.path.join(fsd["cwd"], name))
        elif fsd["mode"] == "file":
            self._fsd_set_name(name)
            self._fsd_primary()

    def _fsd_on_enter(self):
        fsd = self.fsd
        sel = fsd["tree"].selection()
        if sel:
            isdir, name = fsd["rows"][sel[0]]
            if isdir:
                self._fsd_go(os.path.join(fsd["cwd"], name))
            else:
                self._fsd_primary()

    def _fsd_set_mode(self, mode):
        fsd = self.fsd
        if fsd is None or fsd["mode"] == mode:
            return
        cv = fsd["canvas"]
        fsd["confirm"] = None
        if mode == "folder":
            fsd["file_name_backup"] = fsd["name_entry"].get()
            fsd["mode"] = "folder"
            cv.itemconfig(fsd["name_label"], text="Folder name:")
            cv.itemconfig(fsd["btn_primary"]["text"], text="Create")
            self._fsd_set_name("New folder")
            fsd["name_entry"].focus_set()
            fsd["name_entry"].selection_range(0, "end")
            self._fsd_status("Type a name and press Create to make a new folder here.")
        else:
            fsd["mode"] = "file"
            cv.itemconfig(fsd["name_label"], text="File name:")
            cv.itemconfig(fsd["btn_primary"]["text"], text="Save")
            self._fsd_set_name(fsd.get("file_name_backup", fsd["initial"]))
            fsd["name_entry"].focus_set()
            self._fsd_status("")

    @staticmethod
    def _bad_name(name):
        return (not name) or any(c in name for c in '<>:"/\\|?*') or name in (".", "..")

    def _fsd_primary(self):
        fsd = self.fsd
        if fsd is None or fsd["closing"]:
            return
        name = fsd["name_entry"].get().strip()
        if fsd["mode"] == "folder":
            if self._bad_name(name):
                self._fsd_status("A folder name can't be empty or contain  < > : \" / \\ | ? *", "error")
                return
            target = os.path.join(fsd["cwd"], name)
            try:
                os.mkdir(target)
            except OSError as ex:
                self._fsd_status("Couldn't create the folder: %s" % (ex.strerror or ex), "error")
                return
            self._fsd_set_mode("file")
            self._fsd_go(target)
            return
        if not name:
            self._fsd_status("Enter a file name.", "error")
            return
        if not name.lower().endswith(".png"):
            name += ".png"
        path = name if os.path.isabs(name) else os.path.join(fsd["cwd"], name)
        if self._bad_name(os.path.basename(path)):
            self._fsd_status("A file name can't contain  < > : \" / \\ | ? *", "error")
            return
        if not os.path.isdir(os.path.dirname(path)):
            self._fsd_status("That folder doesn't exist.", "error")
            return
        if os.path.isdir(path):
            self._fsd_go(path)
            return
        if os.path.exists(path) and fsd.get("confirm") != path:
            fsd["confirm"] = path
            fsd["canvas"].itemconfig(fsd["btn_primary"]["text"], text="Replace")
            self._fsd_status("\u201c%s\u201d already exists. Press Replace to overwrite it." % os.path.basename(path), "warn")
            return
        self._fsd_close(path)

    # ==================================================================================
    #  Saving
    # ==================================================================================
    def save_orb(self):
        try:
            res = int(self.resolution_var.get())
            if not (100 <= res <= 10000): raise ValueError
        except ValueError:
            self.show_aero_dialog("Invalid Resolution", "Resolution must be a whole number between 100 and 10000.", kind="error")
            return
        self._pending_export = res
        try:
            self.open_save_browser(self._start_dir(), "orb.png", lambda p: self._export_orb(p, res))
        except Exception:
            self._fsd_destroy()
            self._native_save_fallback()

    def _export_orb(self, filename, res):
        try:
            final_img = self.render_composition(res)
            final_img.save(filename, 'PNG')
        except Exception as ex:
            self.show_aero_dialog("Couldn't Save", "The orb could not be exported.", details=[str(ex)], kind="error")
            return

        # remember the folder for next time
        self.config["last_dir"] = os.path.dirname(os.path.abspath(filename))
        save_config(self.config)

        # small preview of what was just exported
        thumb = self.render_composition(320)
        bb = thumb.getchannel("A").point(lambda v: 255 if v > 4 else 0).getbbox()
        if bb:
            pad = 6
            thumb = thumb.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), min(320, bb[2] + pad), min(320, bb[3] + pad)))
        else:
            thumb = None

        Sound.play(asset_path("saved.wav"))
        self.show_aero_dialog(
            "Orb Saved!", "Aero Orb Exported Successfully!",
            details=[os.path.basename(filename), f"{res} \u00d7 {res} px  \u2022  PNG"],
            kind="success", thumb=thumb,
            buttons=[("Show in Folder", lambda p=filename: self._reveal_in_folder(p)), ("OK", None)])


def main():
    root = tk.Tk()
    root.withdraw()
    root.title(APP_NAME)
    try:
        ip = asset_path("Orangeorb.png")
        if ip:
            ico = Image.open(ip).convert("RGBA")
            ico = ico.crop(ico.getchannel("A").getbbox()).resize((64, 64), Image.LANCZOS)
            root._icon = ImageTk.PhotoImage(ico)
            root.iconphoto(True, root._icon)
    except Exception:
        pass

    intro = AeroIntro(root)                  # black fullscreen cover appears instantly
    root.intro = intro
    try:
        root.attributes("-fullscreen", True)
    except tk.TclError:
        pass
    app = OrbCreator(root)                   # build the editor behind the intro
    root.deiconify()
    try:
        root.attributes("-fullscreen", True)
    except tk.TclError:
        pass
    root.update()
    root.app = app

    def intro_done():
        try:
            root.focus_force()
        except tk.TclError:
            pass

    intro.start(on_done=intro_done)
    root.mainloop()


if __name__ == "__main__":
    main()

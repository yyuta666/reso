#!/usr/bin/env python3
"""Генератор векторного чертежа футуристической башни (4 вида, CAD-стиль)."""

from __future__ import annotations

import math
from pathlib import Path

import cairosvg

# Размер холста и отступы (большой холст = чёткие линии при печати/зуме)
W, H = 4096, 4096
MARGIN = 64
GAP = 36
PANEL_W = (W - 2 * MARGIN - GAP) / 2
PANEL_H = (H - 2 * MARGIN - GAP) / 2

# Цвета blueprint
BG = "#061428"
GRID = "#0d2a4a"
LINE = "#9fd4ff"
LINE_DIM = "#6aa8d8"
ACCENT = "#e8f6ff"
CORE = "#7ecbff"
TITLE = "#d7ecff"


def esc(text: str) -> str:
    """Экранирует XML-текст."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def panel_origin(col: int, row: int) -> tuple[float, float]:
    """Возвращает левый верхний угол панели."""
    x = MARGIN + col * (PANEL_W + GAP)
    y = MARGIN + row * (PANEL_H + GAP)
    return x, y


def svg_header() -> str:
    """Шапка SVG с defs (сетка, стили)."""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{GRID}" stroke-width="1"/>
    </pattern>
    <pattern id="grid-fine" width="10" height="10" patternUnits="userSpaceOnUse">
      <path d="M 10 0 L 0 0 0 10" fill="none" stroke="{GRID}" stroke-width="0.4" opacity="0.55"/>
    </pattern>
    <style>
      .title {{ fill: {TITLE}; font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
               font-size: 36px; font-weight: 700; letter-spacing: 1.5px; }}
      .label {{ fill: {LINE_DIM}; font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
               font-size: 22px; font-weight: 500; }}
      .dim {{ fill: {LINE}; font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
             font-size: 21px; font-weight: 600; }}
      .thin {{ stroke: {LINE}; stroke-width: 1.4; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
      .med {{ stroke: {LINE}; stroke-width: 2.4; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
      .thick {{ stroke: {ACCENT}; stroke-width: 3.2; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
      .dimline {{ stroke: {LINE_DIM}; stroke-width: 1.3; fill: none; }}
      .core {{ stroke: {CORE}; stroke-width: 2.6; fill: none; }}
      .fill-soft {{ fill: {CORE}; fill-opacity: 0.08; stroke: none; }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="{H}" fill="url(#grid-fine)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
'''


def panel_frame(x: float, y: float, title: str) -> str:
    """Рамка панели и заголовок."""
    return f'''
  <g>
    <rect x="{x}" y="{y}" width="{PANEL_W}" height="{PANEL_H}"
          fill="none" stroke="{LINE_DIM}" stroke-width="1.5" opacity="0.85"/>
    <text class="title" x="{x + 24}" y="{y + 40}">{esc(title)}</text>
  </g>
'''


def elevation_silhouette(cx: float, base_y: float, scale_h: float, scale_w: float) -> list[str]:
    """Контур фасада башни в ортогональной проекции (симметрично относительно cx)."""
    # Высоты уровней (м) и полуширины профиля (м) — готик-футуристский силуэт
    profile = [
        (0, 600),
        (40, 595),
        (120, 560),
        (220, 500),
        (320, 455),
        (420, 420),
        (520, 400),
        (600, 510),  # промежуточный пояс
        (640, 470),
        (720, 390),
        (850, 340),
        (1000, 310),
        (1120, 295),
        (1200, 430),  # жилой/офисный пояс
        (1260, 380),
        (1380, 280),
        (1500, 230),
        (1650, 190),
        (1800, 160),
        (1920, 145),
        (2000, 210),  # тех. уровень
        (2060, 170),
        (2150, 120),
        (2250, 95),
        (2350, 80),
        (2400, 95),  # антенный слой
        (2480, 60),
        (2580, 38),
        (2680, 22),
        (2800, 6),
    ]
    pts_r = []
    pts_l = []
    for h_m, half_w in profile:
        x = cx + half_w * scale_w
        y = base_y - h_m * scale_h
        pts_r.append((x, y))
        pts_l.append((cx - half_w * scale_w, y))
    pts = pts_l[::-1] + pts_r
    d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"
    parts = [f'<path class="thick" d="{d}"/>', f'<path class="fill-soft" d="{d}"/>']

    # Внутренние этажные линии
    for h_m in range(40, 2800, 40):
        # интерполяция полуширины
        half = _interp_half(profile, h_m) * scale_w * 0.92
        y = base_y - h_m * scale_h
        opacity = 0.35 if h_m % 200 else 0.7
        sw = 0.7 if h_m % 200 else 1.3
        parts.append(
            f'<line x1="{cx - half:.2f}" y1="{y:.2f}" x2="{cx + half:.2f}" y2="{y:.2f}" '
            f'stroke="{LINE}" stroke-width="{sw}" opacity="{opacity}"/>'
        )

    # Вертикальные стойки / рёбра
    for t in (-0.85, -0.55, -0.25, 0.25, 0.55, 0.85):
        path_pts = []
        for h_m, half_w in profile:
            if h_m > 2550:
                break
            x = cx + half_w * scale_w * t
            y = base_y - h_m * scale_h
            path_pts.append(f"{x:.2f},{y:.2f}")
        parts.append(
            f'<polyline class="thin" points="{" ".join(path_pts)}" opacity="0.55"/>'
        )

    # Пояса-платформы
    for h_m, out_extra in ((600, 40), (1200, 50), (2000, 30), (2400, 18)):
        half = _interp_half(profile, h_m) * scale_w + out_extra * scale_w
        y = base_y - h_m * scale_h
        th = 10 * scale_h
        parts.append(
            f'<rect x="{cx - half:.2f}" y="{y - th:.2f}" width="{2 * half:.2f}" height="{th:.2f}" '
            f'class="med" fill="{CORE}" fill-opacity="0.12"/>'
        )
        # зубцы платформы
        n = 14
        for i in range(n + 1):
            px = cx - half + (2 * half) * i / n
            parts.append(
                f'<line x1="{px:.2f}" y1="{y - th:.2f}" x2="{px:.2f}" y2="{y + 4:.2f}" '
                f'class="thin" opacity="0.7"/>'
            )

    # Центральный ствол
    core_w = 28 * scale_w
    parts.append(
        f'<rect x="{cx - core_w:.2f}" y="{base_y - 2700 * scale_h:.2f}" '
        f'width="{2 * core_w:.2f}" height="{2700 * scale_h:.2f}" class="core" '
        f'fill="{CORE}" fill-opacity="0.15"/>'
    )

    # Треугольная эмблема
    ey = base_y - 2100 * scale_h
    ew = 55 * scale_w
    eh = 70 * scale_h
    parts.append(
        f'<polygon points="{cx:.2f},{ey - eh:.2f} {cx - ew:.2f},{ey + eh * 0.5:.2f} '
        f'{cx + ew:.2f},{ey + eh * 0.5:.2f}" class="thick" fill="{CORE}" fill-opacity="0.25"/>'
    )

    # Антенный слой — плотный «лес» шпилей
    antennas = [
        (-110, 2650), (-95, 2720), (-80, 2780), (-65, 2840), (-50, 2880),
        (-35, 2910), (-20, 2940), (-8, 2970), (0, 3020), (8, 2970),
        (20, 2940), (35, 2910), (50, 2880), (65, 2840), (80, 2780),
        (95, 2720), (110, 2650), (-42, 2760), (42, 2760), (-28, 2820), (28, 2820),
    ]
    for dx, h_top in antennas:
        x = cx + dx * scale_w
        y0 = base_y - 2400 * scale_h
        y1 = base_y - h_top * scale_h
        parts.append(f'<line x1="{x:.2f}" y1="{y0:.2f}" x2="{x:.2f}" y2="{y1:.2f}" class="med"/>')
        parts.append(
            f'<circle cx="{x:.2f}" cy="{y1:.2f}" r="2.0" fill="{ACCENT}" stroke="none"/>'
        )
        # короткие поперечины
        if abs(dx) < 60:
            parts.append(
                f'<line x1="{x - 6:.2f}" y1="{(y0 + y1) / 2:.2f}" x2="{x + 6:.2f}" '
                f'y2="{(y0 + y1) / 2:.2f}" class="thin" opacity="0.8"/>'
            )

    # Основание с контрфорсами
    base_half = 600 * scale_w
    parts.append(
        f'<rect x="{cx - base_half:.2f}" y="{base_y - 8:.2f}" width="{2 * base_half:.2f}" '
        f'height="16" class="thick"/>'
    )
    for dx in (-520, -360, -200, 200, 360, 520):
        x = cx + dx * scale_w
        parts.append(
            f'<path class="med" d="M {x:.2f},{base_y:.2f} L {x:.2f},{base_y - 180 * scale_h:.2f} '
            f'L {cx + dx * 0.6 * scale_w:.2f},{base_y - 320 * scale_h:.2f}"/>'
        )

    # Окна / панели на поясах
    for h_m in (650, 800, 1000, 1250, 1400, 1600):
        half = _interp_half(profile, h_m) * scale_w * 0.88
        y = base_y - h_m * scale_h
        n = 18
        for i in range(n):
            x0 = cx - half + (2 * half) * i / n
            x1 = cx - half + (2 * half) * (i + 0.7) / n
            parts.append(
                f'<rect x="{x0:.2f}" y="{y - 10:.2f}" width="{max(2, x1 - x0):.2f}" height="8" '
                f'fill="{ACCENT}" fill-opacity="0.35" stroke="none"/>'
            )

    return parts


def _interp_half(profile: list[tuple[float, float]], h: float) -> float:
    """Линейная интерполяция полуширины по высоте."""
    if h <= profile[0][0]:
        return profile[0][1]
    if h >= profile[-1][0]:
        return profile[-1][1]
    for (h0, w0), (h1, w1) in zip(profile, profile[1:]):
        if h0 <= h <= h1:
            t = (h - h0) / (h1 - h0) if h1 != h0 else 0
            return w0 + (w1 - w0) * t
    return profile[-1][1]


def draw_elevation_panel(col: int, row: int, title: str, mirror_labels_side: str = "left") -> str:
    """Ортогональный вид спереди/сбоку с размерными линиями."""
    px, py = panel_origin(col, row)
    parts = [panel_frame(px, py, title)]

    # Рабочая область
    left_pad = 280 if mirror_labels_side == "left" else 100
    right_pad = 100 if mirror_labels_side == "left" else 280
    bottom_pad = 100
    top_pad = 80
    draw_w = PANEL_W - left_pad - right_pad
    draw_h = PANEL_H - top_pad - bottom_pad
    cx = px + left_pad + draw_w / 2
    base_y = py + top_pad + draw_h
    scale_h = draw_h / 3050  # запас под антенны выше 2800
    scale_w = draw_w / 1550

    parts.extend(elevation_silhouette(cx, base_y, scale_h, scale_w))

    # Размеры по высоте
    labels = [
        (2800, "Высота шпиля"),
        (2400, "Верхний уровень (антенный слой)"),
        (2000, "Технический уровень"),
        (1200, "Жилой/офисные этажи"),
        (600, "Промежуточный пояс"),
        (0, "Основание"),
    ]
    if mirror_labels_side == "left":
        lx = px + 20
        tick_x = cx - 600 * scale_w - 20
        text_anchor = "start"
        label_x = lx
    else:
        lx = px + PANEL_W - 20
        tick_x = cx + 600 * scale_w + 20
        text_anchor = "end"
        label_x = lx

    # Вертикальная размерная линия
    dim_x = tick_x + (12 if mirror_labels_side == "left" else -12)
    y0 = base_y
    y1 = base_y - 2800 * scale_h
    parts.append(f'<line class="dimline" x1="{dim_x:.2f}" y1="{y0:.2f}" x2="{dim_x:.2f}" y2="{y1:.2f}"/>')
    parts.append(
        f'<text class="dim" text-anchor="middle" transform="translate({dim_x + (18 if mirror_labels_side == "left" else -18):.2f},'
        f'{(y0 + y1) / 2:.2f}) rotate(-90)">2800 м</text>'
    )

    for h_m, name in labels:
        y = base_y - h_m * scale_h
        parts.append(
            f'<line class="dimline" x1="{tick_x:.2f}" y1="{y:.2f}" '
            f'x2="{cx + (600 if mirror_labels_side == "right" else -600) * scale_w:.2f}" y2="{y:.2f}" '
            f'stroke-dasharray="4 4" opacity="0.75"/>'
        )
        parts.append(
            f'<text class="label" text-anchor="{text_anchor}" x="{label_x:.2f}" y="{y - 4:.2f}">'
            f'{esc(name)}</text>'
        )
        parts.append(
            f'<text class="dim" text-anchor="{text_anchor}" x="{label_x:.2f}" y="{y + 16:.2f}">'
            f'{h_m} м</text>'
        )

    # Ширина основания
    x_l = cx - 600 * scale_w
    x_r = cx + 600 * scale_w
    y_d = base_y + 36
    parts.append(f'<line class="dimline" x1="{x_l:.2f}" y1="{y_d:.2f}" x2="{x_r:.2f}" y2="{y_d:.2f}"/>')
    parts.append(f'<line class="dimline" x1="{x_l:.2f}" y1="{y_d - 8:.2f}" x2="{x_l:.2f}" y2="{y_d + 8:.2f}"/>')
    parts.append(f'<line class="dimline" x1="{x_r:.2f}" y1="{y_d - 8:.2f}" x2="{x_r:.2f}" y2="{y_d + 8:.2f}"/>')
    parts.append(
        f'<text class="dim" text-anchor="middle" x="{cx:.2f}" y="{y_d + 22:.2f}">1200 м</text>'
    )

    return "\n".join(parts)


def draw_top_view() -> str:
    """Вид сверху: крестообразный план с кольцами."""
    px, py = panel_origin(0, 1)
    parts = [panel_frame(px, py, "ВИД СВЕРХУ")]

    cx = px + PANEL_W / 2
    cy = py + PANEL_H / 2 + 10
    scale = (min(PANEL_W, PANEL_H) - 180) / 1200

    # Внешний квадрат габарита
    half = 600 * scale
    parts.append(
        f'<rect x="{cx - half:.2f}" y="{cy - half:.2f}" width="{2 * half:.2f}" height="{2 * half:.2f}" '
        f'class="dimline" stroke-dasharray="6 4"/>'
    )

    # Концентрические кольца
    for r_m, sw in ((580, 2.2), (480, 1.4), (360, 1.4), (240, 1.6), (140, 2), (70, 2.4)):
        r = r_m * scale
        parts.append(
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" class="med" stroke-width="{sw}"/>'
        )

    # Крестообразные «рукава»
    arm_w = 160 * scale
    arm_len = 600 * scale
    for ang in (0, 90, 180, 270):
        rad = math.radians(ang)
        # прямоугольник от центра наружу
        ux, uy = math.cos(rad), math.sin(rad)
        px0 = cx - uy * arm_w / 2
        py0 = cy - ux * arm_w / 2
        # четыре угла рукава
        c1 = (cx - uy * arm_w / 2, cy + ux * arm_w / 2)
        c2 = (cx + uy * arm_w / 2, cy - ux * arm_w / 2)
        tip1 = (cx + ux * arm_len - uy * arm_w / 2, cy + uy * arm_len + ux * arm_w / 2)
        tip2 = (cx + ux * arm_len + uy * arm_w / 2, cy + uy * arm_len - ux * arm_w / 2)
        d = f"M {c1[0]:.2f},{c1[1]:.2f} L {tip1[0]:.2f},{tip1[1]:.2f} L {tip2[0]:.2f},{tip2[1]:.2f} L {c2[0]:.2f},{c2[1]:.2f}"
        parts.append(f'<path class="thick" d="{d}"/>')

        # внутренние направляющие рукава
        for t in (-0.35, 0.35):
            x1 = cx - uy * arm_w * t
            y1 = cy + ux * arm_w * t
            x2 = cx + ux * arm_len * 0.95 - uy * arm_w * t
            y2 = cy + uy * arm_len * 0.95 + ux * arm_w * t
            parts.append(
                f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="thin" opacity="0.6"/>'
            )

    # Радиальные балки
    for ang in range(0, 360, 15):
        rad = math.radians(ang)
        r0, r1 = 70 * scale, 480 * scale
        parts.append(
            f'<line x1="{cx + r0 * math.cos(rad):.2f}" y1="{cy + r0 * math.sin(rad):.2f}" '
            f'x2="{cx + r1 * math.cos(rad):.2f}" y2="{cy + r1 * math.sin(rad):.2f}" '
            f'class="thin" opacity="0.45"/>'
        )

    # Колонны по кольцу
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        r = 360 * scale
        parts.append(
            f'<rect x="{cx + r * math.cos(rad) - 4:.2f}" y="{cy + r * math.sin(rad) - 4:.2f}" '
            f'width="8" height="8" fill="{ACCENT}" stroke="{LINE}" stroke-width="1"/>'
        )

    # Ядро
    parts.append(
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{40 * scale:.2f}" class="core" '
        f'fill="{CORE}" fill-opacity="0.2"/>'
    )
    parts.append(
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{18 * scale:.2f}" class="thick"/>'
    )

    # Размеры 1200×1200
    y_dim = cy + half + 28
    parts.append(f'<line class="dimline" x1="{cx - half:.2f}" y1="{y_dim:.2f}" x2="{cx + half:.2f}" y2="{y_dim:.2f}"/>')
    parts.append(f'<text class="dim" text-anchor="middle" x="{cx:.2f}" y="{y_dim + 22:.2f}">1200 м</text>')
    x_dim = cx + half + 28
    parts.append(f'<line class="dimline" x1="{x_dim:.2f}" y1="{cy - half:.2f}" x2="{x_dim:.2f}" y2="{cy + half:.2f}"/>')
    parts.append(
        f'<text class="dim" text-anchor="middle" transform="translate({x_dim + 18:.2f},{cy:.2f}) rotate(-90)">1200 м</text>'
    )

    # Компас
    compass_x = px + PANEL_W - 110
    compass_y = py + 110
    r = 36
    parts.append(f'<circle cx="{compass_x}" cy="{compass_y}" r="{r}" class="med"/>')
    parts.append(f'<circle cx="{compass_x}" cy="{compass_y}" r="{r - 10}" class="thin"/>')
    parts.append(
        f'<polygon points="{compass_x},{compass_y - r + 4} {compass_x - 7},{compass_y + 4} '
        f'{compass_x},{compass_y - 6} {compass_x + 7},{compass_y + 4}" fill="{ACCENT}" stroke="{LINE}" stroke-width="1"/>'
    )
    parts.append(f'<text class="dim" text-anchor="middle" x="{compass_x}" y="{compass_y - r - 8}">N</text>')
    parts.append(f'<text class="label" text-anchor="middle" x="{compass_x}" y="{compass_y + r + 18}">S</text>')
    parts.append(f'<text class="label" text-anchor="start" x="{compass_x + r + 6}" y="{compass_y + 5}">E</text>')
    parts.append(f'<text class="label" text-anchor="end" x="{compass_x - r - 6}" y="{compass_y + 5}">W</text>')

    return "\n".join(parts)


def draw_iso_view() -> str:
    """Изометрический общий вид с деталями каркаса."""
    px, py = panel_origin(0, 0)
    parts = [panel_frame(px, py, "3D ВИД (ОБЩИЙ ВИД)")]

    # Изометрия: x' = (x - y) * cos30, y' = (x + y) * sin30 - z
    ox = px + PANEL_W * 0.52
    oy = py + PANEL_H * 0.82
    s = 0.42  # масштаб метров -> px

    def iso(x: float, y: float, z: float) -> tuple[float, float]:
        xx = (x - y) * math.cos(math.radians(30)) * s
        yy = (x + y) * math.sin(math.radians(30)) * s - z * s
        return ox + xx, oy + yy

    # Плита-сетка земли
    for i in range(-5, 6):
        a = iso(-650, i * 120, 0)
        b = iso(650, i * 120, 0)
        parts.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" class="thin" opacity="0.35"/>')
        a = iso(i * 120, -650, 0)
        b = iso(i * 120, 650, 0)
        parts.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" class="thin" opacity="0.35"/>')

    profile = [
        (0, 580),
        (150, 520),
        (300, 460),
        (450, 410),
        (600, 510),
        (750, 370),
        (950, 320),
        (1200, 430),
        (1400, 280),
        (1650, 210),
        (1850, 165),
        (2000, 205),
        (2200, 110),
        (2400, 95),
        (2600, 40),
        (2800, 10),
    ]

    # Горизонтальные контуры (эллипсы в изометрии ≈ параллелограммы/ромбы)
    for h_m, half in profile:
        pts = []
        for ang in range(0, 360, 10):
            rad = math.radians(ang)
            # крестообразное утолщение на основных осях
            bump = 1.0 + (0.18 if abs(math.cos(2 * rad)) > 0.85 else 0.0)
            if h_m in (600, 1200, 2000):
                bump += 0.12
            x = half * bump * math.cos(rad)
            y = half * bump * math.sin(rad)
            pts.append(iso(x, y, h_m))
        d = "M " + " L ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in pts) + " Z"
        parts.append(f'<path class="med" d="{d}" opacity="0.95"/>')
        if h_m in (0, 600, 1200, 2000, 2400):
            parts.append(f'<path class="fill-soft" d="{d}"/>')

    # Вертикальные рёбра — густой каркас
    for ang in range(0, 360, 12):
        rad = math.radians(ang)
        path = []
        for h_m, half in profile:
            bump = 1.0 + (0.2 if abs(math.cos(2 * rad)) > 0.8 else 0.0)
            if h_m in (600, 1200, 2000, 2400):
                bump += 0.14
            x = half * bump * math.cos(rad)
            y = half * bump * math.sin(rad)
            path.append(iso(x, y, h_m))
        opacity = 0.85 if ang % 36 == 0 else 0.55
        parts.append(
            f'<polyline class="thin" points="{" ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in path)}" opacity="{opacity}"/>'
        )

    # Диагональные раскосы на поясах
    for h_m, half in ((400, 430), (900, 330), (1500, 250), (2200, 110)):
        for ang in range(0, 360, 45):
            rad0 = math.radians(ang)
            rad1 = math.radians(ang + 22.5)
            a = iso(half * math.cos(rad0), half * math.sin(rad0), h_m)
            b = iso(half * 0.75 * math.cos(rad1), half * 0.75 * math.sin(rad1), h_m + 120)
            parts.append(
                f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" '
                f'class="thin" opacity="0.5"/>'
            )

    # Центральный ствол
    core_pts_bot = [iso(25, 25, 0), iso(-25, 25, 0), iso(-25, -25, 0), iso(25, -25, 0)]
    core_pts_top = [iso(12, 12, 2700), iso(-12, 12, 2700), iso(-12, -12, 2700), iso(12, -12, 2700)]
    for i in range(4):
        a, b = core_pts_bot[i], core_pts_top[i]
        parts.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" class="core"/>')
    d = "M " + " L ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in core_pts_top) + " Z"
    parts.append(f'<path class="core" d="{d}" fill="{CORE}" fill-opacity="0.25"/>')

    # Эмблема
    e1 = iso(0, 0, 2150)
    e2 = iso(-60, 0, 2000)
    e3 = iso(60, 0, 2000)
    parts.append(
        f'<polygon points="{e1[0]:.2f},{e1[1]:.2f} {e2[0]:.2f},{e2[1]:.2f} {e3[0]:.2f},{e3[1]:.2f}" '
        f'class="thick" fill="{CORE}" fill-opacity="0.35"/>'
    )

    # Антенны — плотный пучок
    for dx, dy, h_top in [
        (0, 0, 3020), (-25, 8, 2960), (25, -8, 2960), (-12, -22, 2920),
        (18, 28, 2930), (-45, -15, 2860), (48, 12, 2860), (0, 40, 2890),
        (0, -42, 2890), (-60, 25, 2780), (62, -20, 2780), (35, 45, 2820),
        (-38, -40, 2820), (15, -5, 2985), (-8, 15, 2995),
    ]:
        a = iso(dx, dy, 2400)
        b = iso(dx * 0.25, dy * 0.25, h_top)
        parts.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" class="med"/>')
        parts.append(f'<circle cx="{b[0]:.2f}" cy="{b[1]:.2f}" r="2.2" fill="{ACCENT}" stroke="none"/>')

    # Контрфорсы основания
    for ang in (0, 90, 180, 270):
        rad = math.radians(ang)
        x, y = 520 * math.cos(rad), 520 * math.sin(rad)
        a = iso(x, y, 0)
        b = iso(x * 0.55, y * 0.55, 350)
        c = iso(x * 0.35, y * 0.35, 600)
        parts.append(
            f'<polyline class="med" points="{a[0]:.2f},{a[1]:.2f} {b[0]:.2f},{b[1]:.2f} {c[0]:.2f},{c[1]:.2f}"/>'
        )

    # Точки «огни»
    for h_m in (600, 1200, 2000, 2400):
        for ang in range(0, 360, 30):
            rad = math.radians(ang)
            half = _interp_half([(p[0], p[1]) for p in profile], h_m)
            p = iso(half * math.cos(rad), half * math.sin(rad), h_m)
            parts.append(f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="1.8" fill="{ACCENT}" stroke="none"/>')

    return "\n".join(parts)


def build_svg() -> str:
    """Собирает полный SVG-чертёж."""
    chunks = [
        svg_header(),
        draw_iso_view(),
        draw_elevation_panel(1, 0, "ВИД СПЕРЕДИ (СЕВЕРНАЯ СТОРОНА)", "left"),
        draw_top_view(),
        draw_elevation_panel(1, 1, "ВИД СБОКУ (ВОСТОЧНАЯ СТОРОНА)", "left"),
        # Общий заголовок листа
        f'<text class="title" x="{W / 2}" y="36" text-anchor="middle" font-size="22">ЧЕРТЁЖ МЕГАСТРУКТУРЫ — МАСШТАБ 1:10000</text>',
        "</svg>\n",
    ]
    return "\n".join(chunks)


def main() -> None:
    """Пишет SVG и растеризует в HD PNG."""
    out_dir = Path("/workspace/artifacts/blueprint")
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = out_dir / "bashnya-chertezh.svg"
    png_path = out_dir / "bashnya-chertezh-hd.png"
    root_png = Path("/workspace/bashnya-chertezh-hd.png")
    artifacts_png = Path("/opt/cursor/artifacts/bashnya-chertezh-hd.png")

    svg = build_svg()
    svg_path.write_text(svg, encoding="utf-8")
    print(f"SVG: {svg_path} ({len(svg)} bytes)")

    # 3200px — чёткие линии без glow
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(png_path), output_width=W, output_height=H)
    root_png.write_bytes(png_path.read_bytes())
    artifacts_png.parent.mkdir(parents=True, exist_ok=True)
    artifacts_png.write_bytes(png_path.read_bytes())
    print(f"PNG: {png_path} ({png_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

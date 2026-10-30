# -*- coding: utf-8 -*-
"""Gera os 4 clipes da seção "Como funciona" (creators) a partir das ilustrações 2D originais.

Uso: python3 make_comofunciona.py PASTA_COM_cena1.png..cena4.png
Saída: assets/como-funciona/cenaN.mp4 (720×720, 4 s, 30 fps, sem áudio, loop exato) e cenaN.webp (quadro parado).

Técnica: nada é redesenhado. Cada quadro é a própria ilustração deformada por campos de deslocamento
pequenos e suaves (máscaras com borda desfocada), então traços, cores, textos e interface continuam os
originais. Todos os movimentos são periódicos em 4 s: o quadro 0 e o quadro 120 são iguais.
"""
import os, sys, math, subprocess
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets', 'como-funciona')
N, FPS, SIDE, SRC = 120, 30, 720, 1254
W = 2 * math.pi / 4.0  # uma volta a cada 4 s

def D(pts):  # pontos medidos na grade de 1000 px -> px da ilustração (1254)
    return np.array([[x * 1.254, y * 1.254] for x, y in pts], np.float32)

def mask_poly(pts, sigma):
    m = np.zeros((SRC, SRC), np.float32)
    cv2.fillPoly(m, [pts.astype(np.int32)], 1.0)
    return cv2.GaussianBlur(m, (0, 0), sigma) if sigma else m

def mask_rect(x0, y0, x1, y1, sigma):
    return mask_poly(D([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), sigma)

def mask_circle(cx, cy, r, sigma):
    m = np.zeros((SRC, SRC), np.float32)
    cv2.circle(m, (int(cx * 1.254), int(cy * 1.254)), int(r * 1.254), 1.0, -1)
    return cv2.GaussianBlur(m, (0, 0), sigma)

YY, XX = np.mgrid[0:SRC, 0:SRC].astype(np.float32)

def rigid(cx, cy, ang_deg=0.0, tx=0.0, ty=0.0, s=1.0):
    """Mapa inverso de um movimento rígido (gira/escala em torno de c, depois desloca): retorna (qx, qy) - (x, y)."""
    a = math.radians(ang_deg); ca, sa = math.cos(a), math.sin(a)
    px, py = XX - cx - tx, YY - cy - ty
    qx = cx + (ca * px + sa * py) / s
    qy = cy + (-sa * px + ca * py) / s
    return qx - XX, qy - YY

def bump(t, t0, w):
    """Pulso suave entre t0 e t0+w (0 fora), periódico em 4 s."""
    u = ((t - t0) % 4.0) / w
    return 0.5 - 0.5 * math.cos(2 * math.pi * u) if u < 1 else 0.0

def wave(mask, amp, lam, t, phase=0.0):
    """Ondulação vertical que viaja na horizontal (para a faixa roxa)."""
    return np.zeros_like(XX), mask * amp * np.sin(2 * math.pi * XX / lam - W * t + phase)

def render(img, fields):
    dx = np.zeros_like(XX); dy = np.zeros_like(XX)
    for fx, fy in fields:
        dx += fx; dy += fy
    return cv2.remap(img, XX + dx, YY + dy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

def lerp_mask(img, mask, color, alpha):
    """Esmaece pixels da máscara em direção à cor do fundo (alpha 1 = original, 0 = some)."""
    k = (mask * (1 - alpha))[..., None]
    return (img * (1 - k) + np.array(color, np.float32) * k).astype(np.uint8)

# ---------- Cena 1 · Perfil ----------
def scene1(img):
    body = mask_poly(D([(185, 80), (440, 80), (485, 175), (475, 285), (580, 232), (650, 250), (655, 335), (630, 385),
                        (800, 465), (870, 412), (935, 428), (905, 505), (880, 565), (805, 552), (835, 690), (875, 790),
                        (875, 885), (780, 895), (640, 865), (630, 790), (440, 790), (410, 800), (330, 905), (265, 885),
                        (165, 805), (55, 650), (55, 590), (190, 540), (300, 600), (330, 555), (420, 485), (400, 405),
                        (240, 362), (165, 342), (125, 280), (140, 170)]), 22)
    card = mask_rect(615, 100, 940, 340, 14)
    shoe_r = mask_poly(D([(635, 790), (790, 760), (880, 800), (875, 890), (780, 900), (640, 865)]), 12)
    band = mask_rect(0, 320, 250, 560, 30) + mask_rect(850, 470, 1000, 860, 30)
    def frame(t):
        s = math.sin(W * t)
        f = [(body * fx, body * fy) for fx, fy in [rigid(560, 560, 0.0, 1.2 * math.sin(W * t + 1.2), -5.5 * s)]]
        f += [(shoe_r * a, shoe_r * b) for a, b in [rigid(830, 1050, 1.2 * math.sin(W * t + 0.8), 0, -2.0 * math.sin(W * t + 1.6))]]
        f += [(card * a, card * b) for a, b in [rigid(975, 276, 1.1 * math.sin(W * t + 0.6), 0, -3.0 * math.sin(W * t + 2.0))]]
        f.append(wave(band, 5.0, 520, t))
        return render(img, f)
    return frame

# ---------- Cena 2 · Campanhas ----------
PHONE2 = [(440, 45), (850, 85), (895, 130), (893, 205), (722, 975), (690, 1002), (640, 995), (180, 880), (148, 840), (152, 790), (395, 75)]
def scene2(img):
    phone = mask_poly(D(PHONE2), 10)
    band = mask_rect(0, 300, 230, 600, 28) + mask_rect(840, 440, 1000, 800, 28)
    bg = img[60, 60].astype(np.float32)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    purple = ((lab[..., 1] > 90) & (lab[..., 2] > 120)).astype(np.float32)
    strokes = []
    for box in [(250, 105, 315, 210), (155, 185, 275, 255), (175, 265, 270, 315)]:
        m = np.zeros_like(XX); x0, y0, x1, y1 = [int(v * 1.254) for v in box]
        m[y0:y1, x0:x1] = purple[y0:y1, x0:x1]
        strokes.append(cv2.GaussianBlur(cv2.dilate(m, np.ones((5, 5))), (0, 0), 1.5))
    def frame(t):
        f = [(phone * a, phone * b) for a, b in [rigid(650, 660, 1.0 * math.sin(W * t + 0.5), 0, -6.0 * math.sin(W * t))]]
        f.append(wave(band, 6.0, 560, t))
        out = render(img, f)
        for i, m in enumerate(strokes):
            alpha = 0.55 + 0.45 * math.cos(W * t - i * 0.9)
            out = lerp_mask(out.astype(np.float32), m, bg, alpha)
        return out
    return frame

# ---------- Cena 3 · Entregas ----------
def scene3(img):
    hand = mask_poly(D([(120, 345), (300, 325), (420, 410), (480, 515), (505, 615), (522, 680), (532, 742), (505, 760),
                        (462, 757), (440, 705), (330, 672), (210, 672), (105, 560), (98, 450)]), 5)
    badge = mask_circle(826, 121, 78, 6)
    band = mask_rect(0, 110, 250, 260, 26) + mask_rect(880, 400, 1000, 560, 26)
    def frame(t):
        tap = bump(t, 0.7, 0.55)  # toque curto: desce e volta
        pulse = bump(t, 1.15, 0.6)
        f = [(hand * a, hand * b) for a, b in [rigid(400, 600, 0, 0, 12.0 * tap)]]
        f += [(badge * a, badge * b) for a, b in [rigid(826 * 1.254, 121 * 1.254, 0, 0, 0, 1 + 0.12 * pulse)]]
        f.append(wave(band, 4.0, 520, t))
        return render(img, f)
    return frame

# ---------- Cena 4 · Carteira ----------
PHONE4 = [(430, 50), (860, 88), (915, 140), (908, 230), (748, 975), (702, 1002), (655, 995), (172, 862), (158, 828), (398, 85)]
def scene4(img):
    phone = mask_poly(D(PHONE4), 10)
    pix = mask_circle(380, 530, 62, 5)
    band = mask_rect(0, 320, 240, 600, 28) + mask_rect(840, 430, 1000, 800, 28)
    def frame(t):
        ty = -6.0 * math.sin(W * t); ang = 1.0 * math.sin(W * t + 0.5)
        pulse = bump(t, 1.4, 0.9)
        f = [(phone * a, phone * b) for a, b in [rigid(660, 660, ang, 0, ty)]]
        # destaque do PIX: pulso de escala pequeno, acompanhando o celular
        a = math.radians(ang); cx0, cy0 = 380 * 1.254 - 660, 530 * 1.254 - 660
        cx = 660 + math.cos(a) * cx0 - math.sin(a) * cy0; cy = 660 + ty + math.sin(a) * cx0 + math.cos(a) * cy0
        f += [(pix * a2, pix * b2) for a2, b2 in [rigid(cx, cy, 0, 0, 0, 1 + 0.08 * pulse)]]
        f.append(wave(band, 6.0, 560, t))
        return render(img, f)
    return frame

SCENES = [scene1, scene2, scene3, scene4]

def encode(frames_fn, path):
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{SIDE}x{SIDE}', '-r', str(FPS), '-i', '-',
                          '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path], stdin=subprocess.PIPE)
    for i in range(N):
        fr = frames_fn(i / FPS)
        p.stdin.write(cv2.resize(fr, (SIDE, SIDE), interpolation=cv2.INTER_AREA).tobytes())
    p.stdin.close(); p.wait()

def main(src_dir):
    os.makedirs(OUT, exist_ok=True)
    for i, sc in enumerate(SCENES, 1):
        img = cv2.imread(os.path.join(src_dir, f'cena{i}.png'), cv2.IMREAD_COLOR)
        assert img.shape[:2] == (SRC, SRC), img.shape
        fn = sc(img)
        f0, f4 = fn(0.0), fn(4.0)
        assert np.abs(f0.astype(int) - f4.astype(int)).max() <= 1, 'loop não fecha'
        encode(fn, os.path.join(OUT, f'cena{i}.mp4'))
        cv2.imwrite(os.path.join(OUT, f'cena{i}.webp'), cv2.resize(img, (SIDE, SIDE), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_WEBP_QUALITY, 86])
        print('ok cena', i)

if __name__ == '__main__':
    main(sys.argv[1])

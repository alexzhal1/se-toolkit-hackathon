import os
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ── Constants ──────────────────────────────────────────────
BG_DARK    = "#1A1A2E"
ACCENT     = "#4285F4"
WHITE      = "#FFFFFF"
GRAY       = "#CCCCCC"
LIGHT_GRAY = "#9999AA"
CARD_BG    = "#22223A"
GREEN      = "#34D39A"

NAME   = "Aleksandr Martiushev"
EMAIL  = "a.martiushev@innopolis.university"
GROUP  = "CSE-03"
GITHUB = "https://github.com/alexzhal1/se-toolkit-hackathon"
URL    = "http://10.93.26.98/"

OUTPUT = os.path.join(os.path.dirname(__file__), "StudyBot_Presentation.pdf")

# landscape A4: 841.89 x 595.27 points
PAGE_W = 841.89
PAGE_H = 595.27

# ── QR Codes ───────────────────────────────────────────────
qr_dir = os.path.join(os.path.dirname(__file__), "qr_temp")
os.makedirs(qr_dir, exist_ok=True)
qr_gh = os.path.join(qr_dir, "qr_github.png")
qr_pr = os.path.join(qr_dir, "qr_product.png")
qrcode.make(GITHUB, border=1).save(qr_gh)
qrcode.make(URL, border=1).save(qr_pr)

# ── Helpers ────────────────────────────────────────────────

def draw_bg(c, color=BG_DARK):
    c.setFillColor(HexColor(color))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

def draw_rounded_rect(c, x, y, w, h, fill_color, radius=10):
    c.setFillColor(HexColor(fill_color))
    c.setStrokeColor(HexColor(fill_color))
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)

def draw_accent_line(c, x, y, w):
    c.setFillColor(HexColor(ACCENT))
    c.rect(x, y, w, 3, fill=1, stroke=0)

def draw_text(c, x, y, text, size=14, color=WHITE, bold=False, font="Helvetica"):
    fn = font + "-Bold" if bold else font
    c.setFont(fn, size)
    c.setFillColor(HexColor(color))
    c.drawString(x, y, text)

def draw_centered_text(c, cx, y, text, size=14, color=WHITE, bold=False, font="Helvetica"):
    fn = font + "-Bold" if bold else font
    c.setFont(fn, size)
    c.setFillColor(HexColor(color))
    tw = c.stringWidth(text, fn, size)
    c.drawString(cx - tw / 2, y, text)

def draw_wrapped_text(c, x, y, w, text, size=14, color=WHITE, leading=18, font="Helvetica"):
    fn = font
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test = current_line + (" " if current_line else "") + word
        if c.stringWidth(test, fn, size) < w:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    c.setFont(fn, size)
    c.setFillColor(HexColor(color))
    textobj = c.beginText(x, y)
    for line in lines:
        textobj.textLine(line)
    c.drawText(textobj)
    return y - len(lines) * leading

def draw_circle(c, cx, cy, r, fill_color):
    c.setFillColor(HexColor(fill_color))
    c.setStrokeColor(HexColor(fill_color))
    c.circle(cx, cy, r, fill=1, stroke=1)

c = canvas.Canvas(OUTPUT, pagesize=(PAGE_W, PAGE_H))

# ═══════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ═══════════════════════════════════════════════════════════
draw_bg(c)
draw_accent_line(c, 60, 440, 100)
draw_text(c, 60, 370, "StudyBot", size=48, color=WHITE, bold=True)
draw_text(c, 60, 330, "AI-Powered Study Assistant", size=24, color=ACCENT)
draw_text(c, 60, 260, NAME, size=18, color=GRAY)
draw_text(c, 60, 232, f"{EMAIL}   |   {GROUP}", size=15, color=LIGHT_GRAY)
c.showPage()

# ═══════════════════════════════════════════════════════════
# SLIDE 2 — Context
# ═══════════════════════════════════════════════════════════
draw_bg(c)
draw_text(c, 40, 540, "Context", size=34, color=WHITE, bold=True)
draw_accent_line(c, 40, 522, 70)

# End-user card
draw_rounded_rect(c, 40, 370, 370, 130, CARD_BG)
draw_text(c, 55, 482, "End-user", size=18, color=ACCENT, bold=True)
draw_wrapped_text(c, 55, 468, 340,
    "University students who want to efficiently understand study material and retain it long-term.",
    size=14, color=GRAY, leading=18)

# Problem card
draw_rounded_rect(c, 430, 370, 370, 130, CARD_BG)
draw_text(c, 445, 482, "Problem", size=18, color=ACCENT, bold=True)
draw_wrapped_text(c, 445, 468, 340,
    "Students spend hours on lecture notes and textbooks without a tool to explain concepts, generate flashcards, or create self-assessment quizzes.",
    size=14, color=GRAY, leading=18)

# Product idea card
draw_rounded_rect(c, 40, 160, 760, 190, CARD_BG)
draw_text(c, 55, 330, "Product idea", size=18, color=ACCENT, bold=True)
draw_wrapped_text(c, 55, 312, 720,
    "StudyBot is an AI assistant that takes study material (text, PDF, DOCX), explains it in simple terms, creates flashcards with spaced repetition, and generates multiple-choice quizzes for self-testing.",
    size=15, color=WHITE, leading=19)

c.showPage()

# ═══════════════════════════════════════════════════════════
# SLIDE 3 — Implementation
# ═══════════════════════════════════════════════════════════
draw_bg(c)
draw_text(c, 40, 540, "Implementation", size=34, color=WHITE, bold=True)
draw_accent_line(c, 40, 522, 70)

# Tech Stack card
draw_text(c, 40, 488, "Tech Stack", size=20, color=ACCENT, bold=True)
stack_items = [
    ("Backend", "Python 3.12 + FastAPI"),
    ("Database", "PostgreSQL + SQLAlchemy (async) + Alembic"),
    ("AI", "DeepSeek API (OpenAI-compatible)"),
    ("Auth", "JWT (bcrypt + PyJWT)"),
    ("Web Client", "React + Vite + TypeScript"),
    ("Deployment", "Docker Compose + Nginx + VM"),
]
stack_card_h = 155
draw_rounded_rect(c, 40, 318, 370, stack_card_h, CARD_BG)
for i, (layer, tech) in enumerate(stack_items):
    y = 458 - i * 22
    draw_text(c, 55, y, f"{layer}:", size=13, color=WHITE, bold=True)
    draw_text(c, 145, y, tech, size=13, color=GRAY)

# V1 card (left, below stack)
draw_rounded_rect(c, 40, 155, 370, 148, CARD_BG)
draw_text(c, 55, 285, "Version 1", size=18, color=GREEN, bold=True)
draw_wrapped_text(c, 55, 268, 340,
    "Upload study text -> AI explanation -> Generate flashcards.\nWeb interface with JWT authentication.",
    size=14, color=GRAY, leading=18)

# V2 card (right, tall)
draw_rounded_rect(c, 430, 155, 370, 360, CARD_BG)
draw_text(c, 445, 495, "Version 2 - New Features", size=18, color=ACCENT, bold=True)
v2_items = [
    "Quiz generation (10 MCQs, single & multi-select)",
    "Interactive quiz UI with score & explanations",
    "Spaced repetition (SM-2 algorithm)",
    "Review page for due flashcards (quality 0-5)",
    "Statistics page (progress tracking)",
    "File upload (.pdf, .docx with text extraction)",
    "Public deployment on VM with Nginx",
]
for i, item in enumerate(v2_items):
    draw_text(c, 450, 470 - i * 24, f">  {item}", size=13, color=GRAY)

c.showPage()

# ═══════════════════════════════════════════════════════════
# SLIDE 4 — Demo
# ═══════════════════════════════════════════════════════════
draw_bg(c)
draw_text(c, 40, 540, "Demo", size=34, color=WHITE, bold=True)
draw_accent_line(c, 40, 522, 70)

draw_text(c, 40, 495, "Pre-recorded video of Version 2 (<= 2 min with voice-over):",
          size=15, color=GRAY)

steps = [
    "Open the web app -> home page showing uploaded materials",
    "Upload a PDF file -> material is created automatically",
    'Click "Explain" -> AI generates a clear explanation as Markdown',
    'Click "Flashcards" -> interactive flip cards appear',
    'Open "Review" -> start a spaced repetition session (SM-2)',
    'Click "Generate Quiz" -> take a quiz, see score, review mistakes',
]

for i, step in enumerate(steps):
    y = 460 - i * 48
    num = str(i + 1)
    draw_circle(c, 62, y, 15, ACCENT)
    draw_centered_text(c, 62, y - 5, num, size=14, color=WHITE, bold=True)
    draw_wrapped_text(c, 90, y + 5, 400, step, size=14, color=GRAY, leading=18)

# Video placeholder box
draw_rounded_rect(c, 620, 300, 180, 220, CARD_BG)
draw_text(c, 640, 500, "Demo Video", size=16, color=LIGHT_GRAY, bold=True)
draw_wrapped_text(c, 640, 480, 140, "[Insert pre-recorded\ndemo video here]",
                  size=13, color=LIGHT_GRAY, leading=17)

c.showPage()

# ═══════════════════════════════════════════════════════════
# SLIDE 5 — Links
# ═══════════════════════════════════════════════════════════
draw_bg(c)
draw_text(c, 40, 540, "Links", size=34, color=WHITE, bold=True)
draw_accent_line(c, 40, 522, 70)

# GitHub card
draw_rounded_rect(c, 40, 290, 370, 210, CARD_BG)
draw_text(c, 55, 480, "GitHub Repository", size=20, color=ACCENT, bold=True)
draw_wrapped_text(c, 55, 458, 250, GITHUB, size=13, color=GRAY, leading=17)
if os.path.exists(qr_gh):
    img = ImageReader(qr_gh)
    c.drawImage(img, 320, 320, width=70, height=70)

# Product card
draw_rounded_rect(c, 430, 290, 370, 210, CARD_BG)
draw_text(c, 445, 480, "Deployed Product (V2)", size=20, color=GREEN, bold=True)
draw_wrapped_text(c, 445, 458, 250, URL, size=13, color=GRAY, leading=17)
if os.path.exists(qr_pr):
    img = ImageReader(qr_pr)
    c.drawImage(img, 710, 320, width=70, height=70)

c.showPage()

# ── Save ───────────────────────────────────────────────────
c.save()
print(f"Saved -> {OUTPUT}")

# cleanup
import shutil
shutil.rmtree(qr_dir)

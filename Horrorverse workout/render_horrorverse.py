# render_horrorverse.py
# Renders: HorrorVerse_20_Week_Cut_Guide.pdf (A4, portrait, solid black)
# Requirements: pip install reportlab
# Optional: place Creepster-Regular.ttf in the same folder for gothic headings.
# Place your logo as horrorverse_logo.png in the same folder.

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Flowable,
                                Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
import os

OUTPUT = "HorrorVerse_20_Week_Cut_Guide.pdf"
LOGO = "horrorverse_logo.png"          # <-- put your logo file here
CREEPSTER = "Creepster-Regular.ttf"    # <-- optional gothic font (falls back if missing)
DRIP_IMG = "blood_drip.png"
PAGE_W, PAGE_H = A4

# ---------- Font setup ----------
HAS_CREEP = False
if os.path.exists(CREEPSTER):
    try:
        pdfmetrics.registerFont(TTFont("Creepster", CREEPSTER))
        HAS_CREEP = True
    except:
        HAS_CREEP = False

# ---------- Colors ----------
BLOOD = colors.Color(1, 0, 0)                   # pure red
BLOOD_DARK = colors.Color(0.6, 0, 0)            # dark red for "glow" underlay
ASH = colors.Color(0.8, 0.8, 0.85)              # light gray for body text
BLACK = colors.black

# ---------- Background painter ----------
def paint_black_bg(canv, doc):
    canv.saveState()
    canv.setFillColor(BLACK)
    canv.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canv.restoreState()

# ---------- Utility: "glow" text (fake glow by stacked draws) ----------
def draw_glow_text(canv, txt, x, y, font_name, size):
    # Underlay darker red outlines
    canv.saveState()
    canv.setFillColor(BLOOD_DARK)
    canv.setFont(font_name, size)
    offsets = [(-0.5,0), (0.5,0), (0,-0.5), (0,0.5)]
    for dx, dy in offsets:
        canv.drawString(x+dx, y+dy, txt)
    # Foreground bright red
    canv.setFillColor(BLOOD)
    canv.drawString(x, y, txt)
    canv.restoreState()


# ---------- Styles ----------
styles = getSampleStyleSheet()

# Headline style (Creepster or fallback)
head_font = "Creepster" if HAS_CREEP else "Helvetica-Bold"
title_style = ParagraphStyle(
    "title_style",
    fontName=head_font,
    fontSize=28,
    leading=32,
    textColor=BLOOD,
    alignment=1, # center
    spaceAfter=12
)

sub_style = ParagraphStyle(
    "sub_style",
    fontName=head_font,
    fontSize=16,
    leading=20,
    textColor=BLOOD,
    alignment=1,
    spaceAfter=10
)

quote_style = ParagraphStyle(
    "quote_style",
    fontName=head_font if HAS_CREEP else "Helvetica-Oblique",
    fontSize=14,
    leading=18,
    textColor=BLOOD,
    alignment=1,
    spaceBefore=6,
    spaceAfter=6,
)

h2_style = ParagraphStyle(
    "h2_style",
    fontName=head_font,
    fontSize=20,
    leading=24,
    textColor=BLOOD,
    spaceBefore=10,
    spaceAfter=8
)

h3_style = ParagraphStyle(
    "h3_style",
    fontName=head_font,
    fontSize=16,
    leading=20,
    textColor=BLOOD,
    spaceBefore=10,
    spaceAfter=6
)

body_style = ParagraphStyle(
    "body_style",
    fontName="Helvetica",
    fontSize=10.5,
    leading=15,
    textColor=ASH,
    spaceAfter=6
)

mini_style = ParagraphStyle(
    "mini_style",
    fontName="Helvetica-Oblique",
    fontSize=9,
    leading=12,
    textColor=ASH,
    alignment=1,
    spaceBefore=8
)

table_wrap_style = ParagraphStyle(
    "table_wrap_style",
    fontName = "Helvetica",
    fontSize = 9.5,
    leading = 12,
    textColor = ASH,
    wordWrap = "CJK",
)

def para(txt):
    if txt is None:
        txt = ""
    return Paragraph(str(txt).replace("&", "&amp;"), table_wrap_style)

# ---------- Tables ----------
def horror_table(header_cols, rows, col_widths=None):
    wrapped_rows = []
    for r in rows:
        r = list(r)
        if len(r) > 0 and isinstance(r[0], str):
            r[0] = para(r[0])
        if len(r) > 3 and isinstance(r[3], str):
            r[3] = para(r[3])
        wrapped_rows.append(r)
    data = [header_cols] + wrapped_rows
    t = Table(data, colWidths=col_widths, repeatRows = 1)
    
    t.setStyle(TableStyle([
        # Header
        ("BACKGROUND", (0,0), (-1,0), BLACK),
        ("TEXTCOLOR", (0,0), (-1,0), BLOOD),
        ("LINEBELOW", (0,0), (-1,0), 0.5, BLOOD),
        ("FONT", (0,0), (-1,0), head_font, 11),
        # Body
        ("TEXTCOLOR", (0,1), (-1,-1), ASH),
        ("FONT", (0,1), (-1,-1), "Helvetica", 9.5),
        ("GRID", (0,0), (-1,-1), 0.25, colors.Color(0.2,0,0)),
        ("BACKGROUND", (0,1), (-1,-1), colors.Color(0.05,0,0)),  # very dark red-black
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),

        ("ALIGN",      (0,1), (0,-1), "LEFT"),   # Exercise
        ("ALIGN",      (3,1), (3,-1), "LEFT"),   # Form Scheme
        ("RIGHTPADDING",(3,1),(3,-1), 8),
    ]))
    return t

# ---------- Chapter divider block ----------
def chapter_divider(title_text, one_liner, icon=""):
    blk = []
    blk.append(Paragraph(f"{icon} {title_text}", h2_style))
    if one_liner:
        blk.append(Paragraph(f"<i>{one_liner}</i>", quote_style))
    blk.append(Spacer(1, 6))
    return blk

# ---------- Content data (condensed from our plan) ----------
# Each day: [ [Exercise, Sets, Reps, Form/Scheme, Tempo, Rest], ... ]
CHEST_CALVES = [
    ["Incline Bench (DB/BB/Smith)", "5", "15-8", "Slight arch, scapula set", "2–0–1–1", "60s"],
    ["Bench Press (DB/BB/Machine)", "5", "15-8", "Elbows ~45°, full ROM", "2–0–1–1", "60s"],
    ["HS Incline Press", "5", "15-8", "Controlled eccentric, chest lead", "2–0–1–2", "45s"],
    ["DB Pull Over", "5", "15-8", "Grip the DB palms up, sit back on edge of bench", "2–0–1–1", "45s"],
    ["Incline Cable Fly", "6", "20-8", "Big stretch, soft elbows", "3–1–1–2", "60s"],
    ["Decline Cable Fly", "6", "20-8", "Stretch & squeeze", "3–1–1–2", "60s"],
    ["Pec Dec", "6", "20-8 + DropSet", "2s peak squeeze. Flex chest on rest", "2–1–1–2", "45s"],
    ["Leg Press Calf Raise", "4", "10–15", "Full stretch → squeeze", "2–1–1–2", "45–60s"],
    ["Standing Calf Raise", "4", "15–20", "Slow control, long squeeze", "2–1–1–2", "45–60s"],
    [
        Paragraph("<b><font color='red'>The Heart-Ripper Drop Set</font></b>", body_style),
        "1", "12 (Dropsets)",
        "A final offering to the iron gods. Three drops. No breath. No hope.",
        "3-1-1-1", "90s after all 3 drops"
    ]
]

BACK_ABS = [
    ["Low cable row", "4", "10–15", "Use Wide grip bar, keep elbows tucked and bring bar up at an angle, squeeze at top for 2 seconds", "2–2–1–1", "75s"],
    ["Lat Pulldown", "4", "10–15", "Elbows down/in", "2–1–1–1", "75s"],
    ["Reverse Grip Pulldown", "4", "10–15", "Underhand, squeeze low lats", "2–1–1–1", "75s"],
    ["Single Arm Cable Row", "4", "10–15", "Isolate side, slight twist", "2–1–1–1", "60s"],
    ["Dumbbell Chest-Supported High Row", "4", "12-15", "Upper lat stretch → squeeze", "2–1–1–2", "75s"],
    ["Straight Arm Pulldown", "4", "12–15", "Long stretch, brace ribs", "3–1–1–2", "60s"],
    ["Lat Pull-In", "4", "12–15", "Elbow close to ribs", "3–1–1–1", "60s"],
    [
        Paragraph("<b><font color='red'>The Doom Lift</font></b>", body_style),
        "3", "6–10",
        "Short, violent, and straight to the point.",
        "2–0–1–1", "120s"
    ],
]


LEGS_TORTURE = [
    ["Leg Extension Warm Up", "2", "20", "Light, controlled; full squeeze, 2-sec hold at top", "2-2-1-1", "45s"],
    ["Barbell Back Squat", "5", "12-6", "Sit deep, drive through heels, core tight, no bounce", "3-1-1-1", "90s"],
    ["Leg Press (Feet Low & Shoulder-Width)", "4", "12-10", "Drive through heels, no lockout, deep range", "3-1-1-1", "75-90s"],
    ["Hack Squat", "4", "10-12", "Knees forward, back glued to the pad, sink deep without hip roll, drive up through mid-foot, and never fully lock out.", "3-1-1-1", "90s"],
    ["Seated Leg Curl", "4", "12-10", "Full stretch, 2-sec squeeze at bottom", "2-2-1-1", "60s"],
    ["RDL (Dumbbell or Barbell)", "4", "10", "Hips back, slight knee bend, glute drive at top", "3-1-1-1", "75s"],
    ["Leg Extensions", "4", "15-20", "Constant tension; last set drop to failure", "2-1-1-2", "60s"],
    [
        Paragraph("<b><font color='red'>The Knee-Reaper Ladder</font></b>", body_style),
        "2", "Ladder",
        "That top hold is where normal men break… but monsters keep going.",
        "2-1-1-2", "60s"
    ],
    [
        Paragraph("<b><font color='red'>The Crimson Coil</font></b>", body_style),
        "2", "Ladder",
        "Slow, squeezing contractions that feel like your hamstrings are winding up like ancient chains.",
        "3-1-1-2", "75s"
    ]
]

SHOULDERS_TRAPS = [
    ["BB Push Press", "4", "8–10", "Explosive power through lockout; control the drop", "2–0–1–0", "90s"],
    ["DB Lat Raise", "10", "12–15", "Go for blood-volume, slow negatives", "2–1–1–2", "45-60s"],
    ["Cable Lat Raise", "4", "12-15", "lead with elbow, pause 1s at top, slow negative", "2-1-1-2", "60s"],
    ["Reverse Pec Deck", "4", "12–15", "Rear-delt squeeze, control the eccentric", "2–1–1–2", "60s"],
    ["Reverse Cable Fly", "4", "12–15", "Keep constant tenstion", "3–1–1–2", "60s"],
    ["Face Pulls (Rope, Cable at Eye Height)", "4", "15-20", "Elbows High, rear-delt peak squeeze", "2–1–1–2", "60s"],
    ["Barbell Shrug", "4", "12-15", "2-second squeeze at peak, slow 3-second descent.", "2–2–1–2", "75s"],
    ["High Pulls", "4", "15", "Explode up (quick) → Squeeze at the top → Lower slow (2–3 seconds)", "1–2–2–1", "60s"],
    [
        Paragraph("<b><font color='red'>The Hangman's Halo</font></b>", body_style),
        "2", "Sequence",
        "Three angles, zero survivors. Your shoulders glow like a cursed halo when this one ends.",
        "2-1-1-2", "60s"
    ]
]

CHEST_BACK = [
    ["HS Incline Press", "4", "8–12", "Upper chest, control negative", "2–0–1–1", "90s"],
    ["Machine Chest Press", "4", "8–12", "Scaps set, mid-pec line", "2–0–1–1", "90s"],
    ["HS Pullover", "4", "10–15", "Elbows soft, deep stretch", "3–1–1–2", "75s"],
    ["Pec Dec", "4", "12–15", "2s squeeze", "2–1–1–2", "60s"],
    ["Machine Lat Pulldown", "4", "10–15", "Drive elbows down", "2–1–1–1", "75s"],
    ["HS Row", "4", "8–12", "Scap retraction focus", "2–0–1–2", "90s"],
    ["Lat Pull-In", "4", "12–15", "Elbow tucked path", "3–1–1–1", "60s"],
    ["Single-Arm HS High Row", "4", "10–15", "Full stretch → squeeze", "2–1–1–2", "75s"],
    ["Leg Press Calf Raise", "4", "10–15", "Full stretch → squeeze", "2–1–1–2", "45–60s"],
    ["Seated Calf Raise", "4", "15–20", "Slow control, long squeeze", "2–1–1–2", "45–60s"],
    [
        Paragraph("<b><font color='red'>The Tormented Twin Peaks</font></b>", body_style),
        "2", "Superset",
        "Chest collapses, back ignites — both halves of the upper body screaming in one ritual.",
        "2-1-1-2", "60s"
    ]
]

ARMS_ABS = [
    ["Tricep Pushdown (V/Rope)", "4", "10–15", "Elbows locked, full ext", "2–1–1–2", "60s"],
    ["EZ Skull Crushers", "4", "8–12", "Slow negative to forehead", "3–1–1–1", "75s"],
    ["Single-Arm Tricep Ext", "4", "12–15", "Elbow tucked", "2–1–1–2", "60s"],
    ["Dip Machine", "4", "8–12", "Chest fwd, tricep squeeze", "2–0–1–1", "75s"],
    ["EZ Bar Curl", "4", "8–12", "Strict elbows", "2–0–1–1", "75s"],
    ["Single-Arm Cable Curl", "4", "12–15", "Slow eccentric, peak", "2–1–1–2", "60s"],
    ["Machine Curl", "4", "10–15", "Constant tension", "2–1–1–2", "60s"],
    ["Hammer Curl", "4", "10–12", "Neutral grip, control", "2–0–1–1", "75s"],
    [
        Paragraph("<b><font color='red'>The Soul Siphon 21s</font></b>", body_style),
        "1", "Sequence",
        "One long ritual to drain every last ounce of strength from biceps and triceps.",
        "2-1-1-2", "75s"
    ]
]

# Conditioning / Cardio / Morning Rituals
HOW_TO = [
    "“Discipline is the ritual. Consistency is the curse that brings transformation.”",
    "1) Morning Rituals of the Undead — do vacuums & contractions upon waking.",
    "2) Nutrition of the Damned — 6 meals/day, track macros relentlessly.",
    "3) Training the Monster — execute your day’s plan with precision.",
    "4) Cardio Inferno — stair-climber HIIT (post-workout or AM fasted).",
    "5) Record the Blood Price — track weight, strength, macros weekly.",
    "Refeeds: every 6–8 weeks for 2–3 days (carb-focused) to refuel the beast.",
    "Tempo is (eccentric–pause–concentric–pause). Example 3–1–1–2.",
    "Progress only when all sets hit the top of the rep range cleanly.",
    "AMRAP = As Many Reps As Possible"
    "Perform all of the reps and sets of the pyramid"
]

RULES = [
    "Thou Shalt Not Skip Leg Day — The Torture Chamber awaits.",
    "The Pump Is the Offering — Each rep is a ritual; bleed for progress.",
    "Thy Tempo Is Thy Faith — Control is the creed of beasts.",
    "Macros Are Law — Track thy fuel; the body keeps no secrets.",
    "Rest Only in the Coffin — Sleep is the recovery of the dead.",
    "Hydration Is The Blood Of The Beast - Deny it, And The Monster Dies.",
]

Finishers = {
    "The Heart-Ripper Drop Set - Machine Chest Press Drop Set": [
        "12 Reps Heavy",
        "Drop Weight 20-30%",
        "12 Reps",
        "Drop Again",
        "15-20 slow reps (full stretch, 2-sec squeeze)"
    ],
    "The Doom Lift - Rack Pulls": [],
    "The Knee-Reaper Ladder - Leg Extensions (Quad Dominant)": [
        "Set Weight: something you can do 15 reps with",
        "Do 15 reps - hold the top squeeze for 10s",
        "Do 10 reps - hold the top for 10s",
        "Do 8 reps - hold 10s"
    ],
    "The Crimson Coil - Leg Curl Drop Set (Hamstring Dominant)": [
        "Heavy: 10 reps slow",
        "Drop Weight 20%: 10 reps",
        "Drop another 20%: 10 reps with 2-second squeeze"
    ], 
    "The Hangman's Halo": [
        "Standing Y-raise - 12 reps, Tempo: 2-1-1-2",
        "Immediately bent-over rear delt cable raise - 12 reps, Tempo: 3-1-1-1",
        "Immediately lateral raise from the cable - 12 reps Tempo: 2-1-1-2"
    ],
    "The Tormented Twin Peaks": [
        "Push-ups to failure, Tempo: 2-1-1-0",
        "Immediately into Straight-arm Cable Pulldown - 15 reps, Tempo: 3-1-1-1",
        "2 rounds 45 seconds rest"
    ],
    "The Soul Siphon 21s": [
        "EZ bar curl - 7 bottom half reps, 7 top half reps, 7 full reps",
        "Immediately Rope pushdown - 21 reps nonstop",
        "1 round but if you can do 2 you're not human"
    ],
    "Every Other Day - The Torso Torture Rack": [
        "Cable Crunch - Hanging Leg Raise Superset",
        "Cable Crunch - 15-20 reps",
        "Hanging Leg Raise - AMRAP",
        "Rest 45s, repeat 2-3 times"
    ],
}


MORNING_RITUALS = [
    "Stomach Vacuums — 3–5 sets × 15–30 sec (fasted on waking).",
    "Standing/Seated Ab Contractions — 3 sets × 20 reps or 10-sec squeezes.",
]

CARDIO = [
    "Stair Climber HIIT (8–10 rounds):",
    "Warm-up: 3 min (Level 3–4)",
    "Work: 30 sec (Level 8–10)",
    "Recover: 1 min (Level 5)",
    "Repeat: 8–10 total (~15 min). Cooldown: 2 min (Level 3).",
    "Use 4–6 days/week; post-workout or AM fasted."
]

# Nutrition overview (phases + macros)
NUTRITION_ROWS = [
    ["1", "Weeks 1–5",  "1950", "200–210g", "100–120g", "55–65g",  "Strength + Fat Loss"],
    ["2", "Weeks 6–10", "1875", "200–210g", "90–100g",  "50–60g",  "Definition + Performance"],
    ["3", "Weeks 11–15","1800", "200–210g", "80–90g",   "45–55g",  "Tightening + Detail"],
    ["4", "Weeks 16–20","2200–2300 (2 days/week)", "200g", "150–170g", "60–65g", "Refeed Metabolism & Peak"],
]

# ---------- Build document ----------
class HorrorDoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        BaseDocTemplate.__init__(self, filename, pagesize=A4, **kw)
        frame = Frame(1.3*cm, 1.3*cm, PAGE_W-2.6*cm, PAGE_H-2.6*cm, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        template = PageTemplate(id="black", frames=[frame], onPage=paint_black_bg)
        self.addPageTemplates([template])

class BloodDripDivider(Flowable):
    """
    A blood-drip divider bar that draws inside the text frame.
    Draws a dark red underlayer + bright red bar + several drips.
    """
    def __init__(self, width=None, thickness=10, drip_count=7, max_drip=28, gap=8):
        super().__init__()
        # If width not provided, match your frame width (A4 minus 2.6cm margins)
        self.width = width if width else (PAGE_W - 2.6*cm)
        self.thickness = thickness
        self.drip_count = drip_count
        self.max_drip = max_drip
        self.gap = gap
        # Height the flowable occupies (bar thickness + max drip + some gap below)
        self._height = thickness + max_drip + gap

    def wrap(self, availWidth, availHeight):
        # Respect frame width automatically
        self.width = min(self.width, availWidth)
        return self.width, self._height

    def draw(self):
        c = self.canv
        w = self.width
        t = self.thickness
        maxd = self.max_drip

        # 1) Underlayer dark bar (fake “shadow”)
        c.saveState()
        c.setFillColor(BLOOD_DARK)
        c.rect(0, self._height - t, w, t, stroke=0, fill=1)

        # 2) Foreground bright bar (slightly thinner so shadow peeks)
        c.setFillColor(BLOOD)
        c.rect(0, self._height - (t*0.9), w, (t*0.8), stroke=0, fill=1)

        # 3) Drips (simple teardrops with small bezier/ovals)
        step = w / (self.drip_count + 1)
        x = step
        for i in range(self.drip_count):
            # Vary drip length a bit
            length = maxd * (0.55 + 0.45 * ((i % 3) / 2))  # mild variation without randomness
            top_y = self._height - (t*0.9)
            bottom_y = top_y - length

            # Dark red backdrop “shadow”
            c.setFillColor(BLOOD_DARK)
            path = c.beginPath()
            path.moveTo(x-2, top_y)
            path.curveTo(x-6, top_y - length*0.35, x-3, top_y - length*0.75, x-2, bottom_y)
            path.curveTo(x, bottom_y-1, x+2, top_y - length*0.75, x+2, top_y)
            c.drawPath(path, fill=1, stroke=0)

            # Bright red foreground drip
            c.setFillColor(BLOOD)
            path2 = c.beginPath()
            path2.moveTo(x-1.4, top_y)
            path2.curveTo(x-4, top_y - length*0.34, x-2, top_y - length*0.72, x-1.1, bottom_y+1.2)
            path2.curveTo(x, bottom_y, x+1.4, top_y - length*0.70, x+1.4, top_y)
            c.drawPath(path2, fill=1, stroke=0)

            x += step

        c.restoreState()


def cover_story():
    flow = []
    # Logo with glow simulation (draw directly on canvas in onPage? Simpler: just Image centered; glow we emulate via title glow)
    if os.path.exists(LOGO):
        im = Image(LOGO, width=7*cm, height=7*cm)
        im.hAlign = "CENTER"
        flow.append(Spacer(1, 1.5*cm))
        flow.append(im)
        flow.append(Spacer(1, 0.6*cm))
    # Title + subtitle + quote
    flow.append(Paragraph("Shaun White’s HorrorVerse 20-Week Cut Guide", title_style))
    flow.append(Paragraph("<i>A 20-Week Transformation from Flesh to Fury</i>", sub_style))
    flow.append(Paragraph("“Become the monster that burns the fat.”", quote_style))
    # Footer + dedication (cover only)
    flow.append(Paragraph("© HorrorVerse Studios", mini_style))
    flow.append(Paragraph("<i>Dedicated to the HorrorVerse Family — Forged in the Shadows of Discipline</i>", mini_style))
    flow.append(PageBreak())
    return flow

def bullets_block(title, bullets):
    blk = [Paragraph(title, h2_style)]
    for b in bullets:
        blk.append(Paragraph("• " + b, body_style))
    blk.append(Spacer(1, 6))
    return blk

def finishers_block(title, finishers_dict):
    blk = [Paragraph(title, h2_style)]
    
    for name, steps in finishers_dict.items():
        # Finisher name as subheading
        blk.append(Paragraph(f"<b>{name}</b>", h3_style))
        
        # Each step as a bullet point
        for step in steps:
            blk.append(Paragraph("• " + step, body_style))
        
        blk.append(Spacer(1, 6))  # space between finishers
    
    return blk

def workout_block(title, one_liner, rows, colw=None):
    flow = []
    flow += chapter_divider(title, one_liner, icon="")
    header = ["Exercise", "Sets", "Reps", "Form Scheme", "Tempo", "Rest"]
    default_colw = [185, 55, 65, 150, 70, 45]
    flow.append(horror_table(header, rows, colw or default_colw))
    flow.append(Spacer(1, 10))
    return flow

def run():
    doc = HorrorDoc(OUTPUT)
    story = []

    # COVER
    story += cover_story()

    # HOW TO + RULES + Finishers
    story += bullets_block("🧠 How to Use This Guide", HOW_TO)
    story += bullets_block("⚔️ Rules of the HorrorVerse", RULES)
    story.append(PageBreak())

    #FINISHERS
    story += finishers_block("🩸 Finishers For The Psychos", Finishers)
    story.append(PageBreak())

    # WORKOUT CHAPTERS (with one-liners)
    story += workout_block("⚰️ CHEST + CALVES OF THE DAMNED", "The heart still beats… but not for long.", CHEST_CALVES)
    story += workout_block("👁 BACK FROM THE ABYSS", "Pull your strength from the shadows.", BACK_ABS)
    story.append(PageBreak())
    legs_colw = [175, 60, 60, 160, 70, 50]
    story += workout_block("🩸 THE TORTURE CHAMBER — LEG DAY", "Abandon mercy. Embrace the pain.", LEGS_TORTURE,
                           colw=legs_colw)
    story += workout_block("🔥 SHOULDERS + TRAPS OF THE HEADLESS HORDE", "Carry the weight of the damned.", SHOULDERS_TRAPS)
    story.append(PageBreak())
    story += workout_block("⚰️ CHEST + BACK OF THE FALLEN", "Where strength and sorrow intertwine.", CHEST_BACK)
    story += workout_block("💀 ARMS OF THE REAPER", "Each rep reaps another weakness.", ARMS_ABS)
    story.append(PageBreak())

    # MORNING RITUALS & CARDIO
    story += bullets_block("🧠 Morning Rituals of the Undead", MORNING_RITUALS)
    story += bullets_block("🔥 Cardio Inferno", CARDIO)
    story.append(PageBreak())

    # NUTRITION OVERVIEW
    story.append(Paragraph("🍽️ 20-Week Nutrition & Macro Overview", h2_style))
    header = ["Phase", "Weeks", "Calories", "Protein", "Carbs", "Fats", "Focus"]
    colw = [45, 75, 110, 85, 75, 65, 150]
    story.append(horror_table(header, NUTRITION_ROWS, colw))
    story.append(PageBreak())

    # FINAL QUOTE PAGE
    story.append(Spacer(1, 6*cm))
    story.append(Paragraph("“The flesh is temporary. The grind is eternal.”", quote_style))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("— Shaun White", quote_style))
    story.append(Paragraph("<i>It’s not just a program — it’s a ritual.</i>", quote_style))

    # Build
    doc.build(story)


    # Post note
    print(f"Done! Wrote {OUTPUT}")

if __name__ == "__main__":
    run()

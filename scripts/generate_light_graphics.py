"""
Script to generate ultra-crisp, high-resolution light-theme PNG and SVG visual graphics
for NEXUS Flow AI README and LinkedIn showcase.
"""

import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
os.makedirs(ASSETS_DIR, exist_ok=True)

FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf" if os.path.exists("C:/Windows/Fonts/segoeui.ttf") else "C:/Windows/Fonts/arial.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf" if os.path.exists("C:/Windows/Fonts/segoeuib.ttf") else "C:/Windows/Fonts/arialbd.ttf"
FONT_SEMI = "C:/Windows/Fonts/seguisb.ttf" if os.path.exists("C:/Windows/Fonts/seguisb.ttf") else FONT_BOLD

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def draw_rounded_card(draw, xy, radius=16, fill=(255, 255, 255), outline=(226, 232, 240), outline_width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=outline_width)

def draw_pill(draw, xy, text, font, text_color=(15, 23, 42), bg_color=(241, 245, 249), border_color=(203, 213, 225)):
    draw.rounded_rectangle(xy, radius=12, fill=bg_color, outline=border_color, width=1)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    cx = (xy[0] + xy[2] - tw) // 2
    cy = (xy[1] + xy[3] - th) // 2
    draw.text((cx, cy), text, font=font, fill=text_color)

def generate_hero_banner():
    width, height = 1600, 640
    img = Image.new("RGBA", (width, height), (248, 250, 252, 255))
    draw = ImageDraw.Draw(img)

    # Subtle background dot grid pattern
    for x in range(0, width, 32):
        for y in range(0, height, 32):
            draw.ellipse((x, y, x + 2, y + 2), fill=(226, 232, 240, 180))

    # Top gradient soft glow
    draw.ellipse((-100, -100, 600, 400), fill=(238, 242, 255, 120))
    draw.ellipse((width - 500, -100, width + 200, 400), fill=(236, 253, 245, 120))

    # Header Top Pill Badge
    pill_font = get_font(FONT_BOLD, 14)
    draw_pill(draw, (width // 2 - 190, 45, width // 2 + 190, 75), "⚡ AUTONOMOUS AI BUSINESS PLATFORM • RISK V2", pill_font, text_color=(14, 116, 144), bg_color=(240, 249, 255), border_color=(186, 230, 253))

    # Title
    title_font = get_font(FONT_BOLD, 52)
    title = "NEXUS FLOW AI"
    draw.text((width // 2 - 210, 95), title, font=title_font, fill=(15, 23, 42))

    # Subtitle
    sub_font = get_font(FONT_REGULAR, 22)
    sub = "Intelligent Operations Hub • 4 Independent AI Engines • Unified Mission Control"
    draw.text((width // 2 - 380, 165), sub, font=sub_font, fill=(71, 85, 105))

    # 4 Floating Feature Cards
    card_width = 330
    card_height = 270
    spacing = 30
    start_x = (width - (4 * card_width + 3 * spacing)) // 2
    card_y = 230

    cards = [
        {
            "icon": "🎯",
            "title": "Lead Intelligence",
            "tag": "CUSTOMER INTAKE",
            "tag_bg": (238, 242, 255),
            "tag_fg": (79, 70, 229),
            "lines": [
                "• Ingestion from Forms & Webhooks",
                "• 0–100 Scoring & Priority Tiers",
                "• AI Summaries & Talking Points",
                "• Airtable & Slack Auto-Routing",
                "• Sub-10s Execution (0.048s)",
            ]
        },
        {
            "icon": "🛡️",
            "title": "Support Intelligence",
            "tag": "EMAIL TRIAGE",
            "tag_bg": (236, 253, 245),
            "tag_fg": (5, 150, 105),
            "lines": [
                "• 8 Intent Categories (Billing, Bug...)",
                "• Decoupled Urgency & Sentiment",
                "• Grounded KB Policy Retrieval",
                "• Strict Draft-Only Enforcement",
                "• Prompt-Injection Sanitization",
            ]
        },
        {
            "icon": "📑",
            "title": "Invoice Intelligence",
            "tag": "DOCUMENT AUDIT",
            "tag_bg": (254, 243, 199),
            "tag_fg": (217, 119, 6),
            "lines": [
                "• PDF Parse & Line-Item Extraction",
                "• ±$0.01 Arithmetic Reconciliation",
                "• Discrepancy & Duplicate Flags",
                "• OWASP Formula-Injection Guard",
                "• Google Sheets Batch Export",
            ]
        },
        {
            "icon": "⚙️",
            "title": "Enterprise Orchestration",
            "tag": "BUSINESS DELIVERY",
            "tag_bg": (245, 243, 255),
            "tag_fg": (147, 51, 234),
            "lines": [
                "• PRJ-YYYYMM-XXXX Code Generation",
                "• MSA Legal Template Protection",
                "• Stripe HMAC-SHA256 Signature",
                "• Slack Project Channel Provisioning",
                "• Weekly Executive Digest AI",
            ]
        }
    ]

    card_title_font = get_font(FONT_BOLD, 18)
    card_tag_font = get_font(FONT_BOLD, 11)
    card_text_font = get_font(FONT_REGULAR, 14)

    for i, c in enumerate(cards):
        cx = start_x + i * (card_width + spacing)
        # Card background & shadow simulation
        draw_rounded_card(draw, (cx + 2, card_y + 4, cx + card_width + 2, card_y + card_height + 4), radius=16, fill=(241, 245, 249, 100), outline=(226, 232, 240, 0))
        draw_rounded_card(draw, (cx, card_y, cx + card_width, card_y + card_height), radius=16, fill=(255, 255, 255), outline=(226, 232, 240), outline_width=2)

        # Header tag pill
        draw_pill(draw, (cx + 18, card_y + 18, cx + 160, card_y + 42), c["tag"], card_tag_font, text_color=c["tag_fg"], bg_color=c["tag_bg"], border_color=c["tag_bg"])

        # Title
        draw.text((cx + 18, card_y + 55), f"{c['icon']} {c['title']}", font=card_title_font, fill=(15, 23, 42))

        # Bullet points
        for idx, line in enumerate(c["lines"]):
            draw.text((cx + 18, card_y + 95 + idx * 30), line, font=card_text_font, fill=(51, 65, 85))

    # Bottom Trust Badges
    badge_y = 535
    badges = [
        "✓ 27/27 Tests Passed (100%)",
        "🔒 Stripe HMAC-SHA256 Verified",
        "🛡️ Zero Formula/Prompt Injection",
        "⏱️ Sub-100ms Heuristic Engine",
        "👤 Human-in-the-Loop Gateway",
    ]
    badge_font = get_font(FONT_SEMI, 13)
    bw = 250
    b_start = (width - (5 * 260)) // 2
    for i, b in enumerate(badges):
        bx = b_start + i * 260
        draw_pill(draw, (bx, badge_y, bx + 245, badge_y + 36), b, badge_font, text_color=(15, 23, 42), bg_color=(255, 255, 255), border_color=(203, 213, 225))

    out_path = os.path.join(ASSETS_DIR, "hero_banner_light.png")
    img.save(out_path, "PNG")
    print(f"Generated: {out_path}")

def generate_architecture_light():
    width, height = 1600, 840
    img = Image.new("RGBA", (width, height), (248, 250, 252, 255))
    draw = ImageDraw.Draw(img)

    # Dot grid
    for x in range(0, width, 32):
        for y in range(0, height, 32):
            draw.ellipse((x, y, x + 2, y + 2), fill=(226, 232, 240, 180))

    # Header
    title_font = get_font(FONT_BOLD, 36)
    sub_font = get_font(FONT_REGULAR, 18)
    draw.text((width // 2 - 320, 35), "NEXUS FLOW AI — 5-TIER ARCHITECTURE", font=title_font, fill=(15, 23, 42))
    draw.text((width // 2 - 350, 85), "Event-Driven Autonomous Business Architecture with Strict Isolation & Fallbacks", font=sub_font, fill=(100, 116, 139))

    # 5 Architecture Tiers as horizontal stacked bands
    tier_font_title = get_font(FONT_BOLD, 17)
    tier_font_body = get_font(FONT_REGULAR, 14)

    tiers = [
        {
            "tier": "TIER 1: Ingestion Channels & External Triggers",
            "items": ["Web Forms (JSON/REST)", "Email Inbound (IMAP/Graph API)", "Invoice PDF Uploads (OCR/Vision)", "Stripe Webhooks (HMAC-SHA256)"],
            "color": (240, 249, 255),
            "border": (186, 230, 253),
            "title_color": (3, 105, 161)
        },
        {
            "tier": "TIER 2: API Gateway & Security Governance",
            "items": ["FastAPI Async Router", "Pydantic V2 Contract Validation", "Prompt-Injection Sanitizer", "Formula Injection Escaping", "Rate Limiter & Audit Logger"],
            "color": (245, 243, 255),
            "border": (221, 214, 254),
            "title_color": (109, 40, 217)
        },
        {
            "tier": "TIER 3: Four Autonomous Intelligence Micro-Engines",
            "items": [
                "1. Lead Intelligence Engine\n(Suitability Rules, Scoring, Talking Points)",
                "2. Support Intelligence Engine\n(8-Way Triage, KB Retrieval, Draft Invariant)",
                "3. Invoice Intelligence Engine\n(Line Items, ±$0.01 Arithmetic Check)",
                "4. Enterprise Orchestration\n(Intake, Contracts, Stripe Ledger, Exec Digest)"
            ],
            "color": (255, 255, 255),
            "border": (148, 163, 184),
            "title_color": (15, 23, 42),
            "large": True
        },
        {
            "tier": "TIER 4: Cognition & Fallback Intelligence",
            "items": ["OpenAI gpt-4o Client (Structured Outputs)", "Grounded Enterprise Knowledge Base", "Deterministic Heuristic Fallbacks (0ms Downtime)"],
            "color": (236, 253, 245),
            "border": (167, 243, 208),
            "title_color": (4, 120, 87)
        },
        {
            "tier": "TIER 5: Persistence & External Integration Adapters",
            "items": ["SQLAlchemy 2.0 (SQLite / PostgreSQL)", "Airtable CRM Adapter", "Slack Channels & Webhooks", "Google Sheets Ledger", "Email Draft Store"],
            "color": (254, 243, 199),
            "border": (253, 230, 138),
            "title_color": (180, 83, 9)
        }
    ]

    cur_y = 135
    for t in tiers:
        is_large = t.get("large", False)
        block_h = 160 if is_large else 100
        draw_rounded_card(draw, (80, cur_y, width - 80, cur_y + block_h), radius=14, fill=t["color"], outline=t["border"], outline_width=2)
        draw.text((105, cur_y + 14), t["tier"], font=tier_font_title, fill=t["title_color"])

        items = t["items"]
        item_w = (width - 240) // len(items)
        for idx, itm in enumerate(items):
            ix = 105 + idx * (item_w + 15)
            iy = cur_y + 45
            draw_rounded_card(draw, (ix, iy, ix + item_w, iy + (block_h - 60)), radius=10, fill=(255, 255, 255), outline=t["border"], outline_width=1)
            # Text multiline
            lines = itm.split("\n")
            for l_idx, l in enumerate(lines):
                fw = tier_font_title if l_idx == 0 and is_large else tier_font_body
                draw.text((ix + 12, iy + 10 + l_idx * 22), l, font=fw, fill=(30, 41, 59))

        cur_y += block_h + 20

    out_path = os.path.join(ASSETS_DIR, "architecture_light.png")
    img.save(out_path, "PNG")
    print(f"Generated: {out_path}")

def generate_engines_showcase():
    width, height = 1600, 920
    img = Image.new("RGBA", (width, height), (248, 250, 252, 255))
    draw = ImageDraw.Draw(img)

    for x in range(0, width, 32):
        for y in range(0, height, 32):
            draw.ellipse((x, y, x + 2, y + 2), fill=(226, 232, 240, 180))

    title_font = get_font(FONT_BOLD, 36)
    sub_font = get_font(FONT_REGULAR, 18)
    draw.text((width // 2 - 340, 35), "FOUR INDEPENDENT INTELLIGENCE ENGINES", font=title_font, fill=(15, 23, 42))
    draw.text((width // 2 - 330, 85), "Modular Architecture: Each engine functions independently or unified in Mission Control", font=sub_font, fill=(100, 116, 139))

    # Bento 2x2 Grid + Command Center Bottom Span
    grid_w = 690
    grid_h = 320
    col1_x = 90
    col2_x = 820
    row1_y = 135
    row2_y = 480

    engine_blocks = [
        (col1_x, row1_y, "1. LEAD INTELLIGENCE ENGINE", "Target: Under 10s • Measured: 0.048s", (238, 242, 255), (79, 70, 229), [
            "• Webhooks & Forms Multi-Source Ingestion",
            "• Automated Deduplication & Consent Validation",
            "• Configurable Suitability Decision Rules",
            "• 0–100 Scoring (High, Medium, Low Tiers)",
            "• AI-Generated Prospect Summary & Sales Talking Points",
            "• Bidirectional Airtable Sync & Slack Pipeline Alerts"
        ]),
        (col2_x, row1_y, "2. SUPPORT INTELLIGENCE ENGINE", "Strict Invariant: 100% Draft-Only Mode", (236, 253, 245), (5, 150, 105), [
            "• 8 Intent Categories (Billing, Incidents, Spam...)",
            "• Independent Urgency & Sentiment Scoring",
            "• Grounded Knowledge Base Retrieval (10+ Policies)",
            "• Policy-Anchored Context-Aware Draft Generation",
            "• Prompt-Injection Sanitization Defense Filter",
            "• Tier-2 Human Escalation Queue Integration"
        ]),
        (col1_x, row2_y, "3. INVOICE INTELLIGENCE ENGINE", "Strict Invariant: ±$0.01 Arithmetic Match", (254, 243, 199), (217, 119, 6), [
            "• PDF Document Ingestion & Structured Text Extraction",
            "• Header Parsing: Vendor, Number, Date, Currency",
            "• Line-Item Parser: Qty, Unit Price, Line Total",
            "• Arithmetic Check: Subtotal - Discount + Tax == Total",
            "• Discrepancy Flagging & Duplicate Invoice Detection",
            "• OWASP Formula-Sanitized Export to Google Sheets"
        ]),
        (col2_x, row2_y, "4. ENTERPRISE ORCHESTRATION", "Security Invariant: Stripe HMAC-SHA256", (245, 243, 255), (147, 51, 234), [
            "• Standardized Project Code Generation (PRJ-YYYYMM-XXXX)",
            "• MSA Contract Template Population & Clause Protection",
            "• Cryptographic Stripe Webhook Signature Verification",
            "• Replay Attack Prevention via Idempotency Ledger",
            "• Automated Project Slack Channel Provisioning",
            "• Weekly Executive Intelligence Digest Generator"
        ])
    ]

    h_font = get_font(FONT_BOLD, 19)
    sub_tag_font = get_font(FONT_BOLD, 12)
    li_font = get_font(FONT_REGULAR, 15)

    for x, y, title, tag, bg, fg, items in engine_blocks:
        draw_rounded_card(draw, (x, y, x + grid_w, y + grid_h), radius=16, fill=(255, 255, 255), outline=(226, 232, 240), outline_width=2)
        draw_pill(draw, (x + 20, y + 20, x + 340, y + 46), tag, sub_tag_font, text_color=fg, bg_color=bg, border_color=bg)
        draw.text((x + 20, y + 60), title, font=h_font, fill=(15, 23, 42))

        for idx, itm in enumerate(items):
            draw.text((x + 20, y + 100 + idx * 32), itm, font=li_font, fill=(51, 65, 85))

    # Bottom Banner for Unified Command Center
    bottom_y = 820
    draw_rounded_card(draw, (col1_x, bottom_y, col2_x + grid_w, bottom_y + 70), radius=14, fill=(240, 249, 255), outline=(186, 230, 253), outline_width=2)
    b_font = get_font(FONT_BOLD, 16)
    draw.text((col1_x + 30, bottom_y + 24), "🌟 UNIFIED MISSION CONTROL COMMAND CENTER", font=b_font, fill=(3, 105, 161))
    sub_b_font = get_font(FONT_REGULAR, 14)
    draw.text((col1_x + 480, bottom_y + 26), "Real-time Telemetry • Approval Center • Execution Feed • Latency Monitor • Live/Demo Switch", font=sub_b_font, fill=(71, 85, 105))

    out_path = os.path.join(ASSETS_DIR, "engines_overview_light.png")
    img.save(out_path, "PNG")
    print(f"Generated: {out_path}")

def generate_linkedin_showcase():
    width, height = 1200, 1200
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Dot grid
    for x in range(0, width, 30):
        for y in range(0, height, 30):
            draw.ellipse((x, y, x + 2, y + 2), fill=(241, 245, 249, 255))

    # Top Brand Bar
    draw_pill(draw, (width // 2 - 220, 60, width // 2 + 220, 95), "🚀 OPEN-SOURCE ENTERPRISE PLATFORM LAUNCH", get_font(FONT_BOLD, 13), text_color=(14, 116, 144), bg_color=(240, 249, 255), border_color=(186, 230, 253))

    # Hero Title
    draw.text((width // 2 - 270, 125), "NEXUS FLOW AI", font=get_font(FONT_BOLD, 54), fill=(15, 23, 42))
    draw.text((width // 2 - 320, 200), "Autonomous AI Business Automation Platform", font=get_font(FONT_SEMI, 24), fill=(71, 85, 105))

    # 4 Engines 2x2 Grid in LinkedIn post
    card_w = 490
    card_h = 240
    c1_x = 90
    c2_x = 620
    r1_y = 265
    r2_y = 530

    engines = [
        (c1_x, r1_y, "🎯 Lead Intelligence", "• 0-100 Suitability Scoring\n• AI Sales Talking Points\n• Airtable & Slack Sync\n• <10s Latency (0.048s actual)", (238, 242, 255), (79, 70, 229)),
        (c2_x, r1_y, "🛡️ Support Intelligence", "• 8 Intent Categories Triage\n• Grounded Knowledge Base\n• Draft-Only Safe Enforcement\n• Prompt-Injection Defense", (236, 253, 245), (5, 150, 105)),
        (c1_x, r2_y, "📑 Invoice Intelligence", "• PDF OCR & Line Item Parse\n• ±$0.01 Arithmetic Check\n• Discrepancy Auto-Flagging\n• OWASP Formula-Safe Sheets", (254, 243, 199), (217, 119, 6)),
        (c2_x, r2_y, "⚙️ Enterprise Orchestration", "• PRJ-YYYYMM-XXXX ID Engine\n• MSA Contract Drafter\n• Stripe HMAC-SHA256 Check\n• Weekly Executive Digest AI", (245, 243, 255), (147, 51, 234))
    ]

    for x, y, title, text, bg, fg in engines:
        draw_rounded_card(draw, (x, y, x + card_w, y + card_h), radius=16, fill=(255, 255, 255), outline=(226, 232, 240), outline_width=2)
        draw_rounded_card(draw, (x + 20, y + 20, x + card_w - 20, y + 60), radius=8, fill=bg, outline=bg)
        draw.text((x + 35, y + 28), title, font=get_font(FONT_BOLD, 18), fill=fg)
        lines = text.split("\n")
        for idx, line in enumerate(lines):
            draw.text((x + 25, y + 80 + idx * 34), line, font=get_font(FONT_REGULAR, 16), fill=(51, 65, 85))

    # Metric Banner
    draw_rounded_card(draw, (c1_x, 800, c2_x + card_w, 940), radius=18, fill=(240, 249, 255), outline=(186, 230, 253), outline_width=2)
    stats = [
        ("27 / 27", "Tests Passed (100%)"),
        ("0.048s", "Lead Pipeline Latency"),
        ("HMAC-SHA256", "Payment Verification"),
        ("Draft-Only", "Email Safe Invariant")
    ]
    sw = (c2_x + card_w - c1_x) // 4
    for idx, (val, lbl) in enumerate(stats):
        sx = c1_x + idx * sw
        draw.text((sx + 35, 825), val, font=get_font(FONT_BOLD, 28), fill=(3, 105, 161))
        draw.text((sx + 20, 885), lbl, font=get_font(FONT_REGULAR, 14), fill=(71, 85, 105))

    # Tech Stack & GitHub Bar
    draw_rounded_card(draw, (c1_x, 970, c2_x + card_w, 1120), radius=18, fill=(248, 250, 252), outline=(226, 232, 240), outline_width=1)
    draw.text((c1_x + 30, 995), "STACK: Python 3.12 • FastAPI • SQLAlchemy 2.0 • Pydantic V2 • Stripe • Airtable • Slack • Sheets", font=get_font(FONT_BOLD, 15), fill=(15, 23, 42))
    draw.text((c1_x + 30, 1040), "GITHUB: github.com/maheswari9080/Datheon_AI_Automation_-_Agent_Building", font=get_font(FONT_SEMI, 16), fill=(14, 116, 144))
    draw.text((c1_x + 30, 1075), "⚡ 30 Commits Delivered • Production-Grade Security • Full Enterprise Docs", font=get_font(FONT_REGULAR, 14), fill=(100, 116, 139))

    out_path = os.path.join(ASSETS_DIR, "linkedin_showcase.png")
    img.save(out_path, "PNG")
    print(f"Generated: {out_path}")

def generate_svg_linkedin_card():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F8FAFC"/>
      <stop offset="50%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#EFF6FF"/>
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.06"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bg)"/>

  <!-- Top Pill -->
  <rect x="420" y="35" width="360" height="32" rx="16" fill="#F0F9FF" stroke="#BAE6FD" stroke-width="1.5"/>
  <text x="600" y="56" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#0284C7" text-anchor="middle">⚡ AUTONOMOUS AI BUSINESS AUTOMATION • RISK V2</text>

  <!-- Title -->
  <text x="600" y="115" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="46" font-weight="800" fill="#0F172A" text-anchor="middle">NEXUS FLOW AI</text>
  <text x="600" y="150" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="18" font-weight="500" fill="#64748B" text-anchor="middle">Four Autonomous Micro-Engines + Unified Mission Control Command Center</text>

  <!-- 4 Engine Cards Grid -->
  <g transform="translate(60, 180)">
    <!-- Engine 1 -->
    <rect x="0" y="0" width="255" height="230" rx="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5" filter="url(#shadow)"/>
    <rect x="15" y="15" width="225" height="34" rx="8" fill="#EEF2FF"/>
    <text x="127" y="37" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#4F46E5" text-anchor="middle">🎯 Lead Intelligence</text>
    <text x="20" y="75" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• Forms &amp; Webhook Ingest</text>
    <text x="20" y="100" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• 0-100 Score Matrix</text>
    <text x="20" y="125" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• AI Sales Talking Points</text>
    <text x="20" y="150" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• Airtable &amp; Slack Routing</text>
    <text x="20" y="180" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#059669">⚡ Measured: 0.048s SLA</text>

    <!-- Engine 2 -->
    <rect x="275" y="0" width="255" height="230" rx="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5" filter="url(#shadow)"/>
    <rect x="290" y="15" width="225" height="34" rx="8" fill="#ECFDF5"/>
    <text x="402" y="37" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#059669" text-anchor="middle">🛡️ Support Intelligence</text>
    <text x="295" y="75" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• 8 Intent Categories Triage</text>
    <text x="295" y="100" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• Decoupled Urgency Scoring</text>
    <text x="295" y="125" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• Grounded Policy Retrieval</text>
    <text x="295" y="150" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• Prompt-Injection Filter</text>
    <text x="295" y="180" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#D97706">🔒 Invariant: Draft-Only</text>

    <!-- Engine 3 -->
    <rect x="550" y="0" width="255" height="230" rx="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5" filter="url(#shadow)"/>
    <rect x="565" y="15" width="225" height="34" rx="8" fill="#FFFBEB"/>
    <text x="677" y="37" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#D97706" text-anchor="middle">📑 Invoice Intelligence</text>
    <text x="570" y="75" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• PDF Parser &amp; Line Items</text>
    <text x="570" y="100" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• ±$0.01 Arithmetic Match</text>
    <text x="570" y="125" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• Discrepancy Auto-Flags</text>
    <text x="570" y="150" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• OWASP Formula Defense</text>
    <text x="570" y="180" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#0284C7">📊 Google Sheets Sync</text>

    <!-- Engine 4 -->
    <rect x="825" y="0" width="255" height="230" rx="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5" filter="url(#shadow)"/>
    <rect x="840" y="15" width="225" height="34" rx="8" fill="#F5F3FF"/>
    <text x="952" y="37" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#7C3AED" text-anchor="middle">⚙️ Orchestration Engine</text>
    <text x="845" y="75" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• PRJ-YYYYMM-XXXX Codes</text>
    <text x="845" y="100" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• MSA Legal Contract Drafts</text>
    <text x="845" y="125" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• Stripe HMAC-SHA256</text>
    <text x="845" y="150" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#334155">• Slack Channel Provision</text>
    <text x="845" y="180" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#4F46E5">📈 Weekly Executive Digest</text>
  </g>

  <!-- Metrics Bar -->
  <rect x="60" y="440" width="1080" height="90" rx="14" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" filter="url(#shadow)"/>
  <g transform="translate(60, 440)">
    <text x="135" y="40" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="24" font-weight="800" fill="#0284C7" text-anchor="middle">27 / 27</text>
    <text x="135" y="65" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Tests Passed (100%)</text>

    <text x="405" y="40" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="24" font-weight="800" fill="#059669" text-anchor="middle">0.048s</text>
    <text x="405" y="65" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Pipeline Latency (&lt;10s)</text>

    <text x="675" y="40" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="24" font-weight="800" fill="#7C3AED" text-anchor="middle">HMAC-SHA256</text>
    <text x="675" y="65" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Stripe Signature Check</text>

    <text x="945" y="40" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="24" font-weight="800" fill="#D97706" text-anchor="middle">100% Invariant</text>
    <text x="945" y="65" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Draft-Only Human Gate</text>
  </g>

  <!-- Footer -->
  <text x="600" y="585" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="600" fill="#334155" text-anchor="middle">Python 3.12 • FastAPI • SQLAlchemy 2.0 • Pydantic V2 • Airtable • Slack • Stripe • Google Sheets</text>
  <text x="600" y="610" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle">github.com/maheswari9080/Datheon_AI_Automation_-_Agent_Building</text>
</svg>
"""
    out_path = os.path.join(ASSETS_DIR, "linkedin_card.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content.strip())
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    generate_hero_banner()
    generate_architecture_light()
    generate_engines_showcase()
    generate_linkedin_showcase()
    generate_svg_linkedin_card()

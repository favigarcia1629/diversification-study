"""
Generates a professional PDF report + LinkedIn post draft.
Usage: python generate_pdf.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import date

OUTPUT = Path(__file__).parent / "exports" / "Diversification_vs_Concentration_Report.pdf"

# ── Palette ──────────────────────────────────────────────────────────────────
ORANGE  = colors.HexColor("#FF6B35")
BLUE    = colors.HexColor("#2196F3")
GRAY    = colors.HexColor("#9E9E9E")
DARK    = colors.HexColor("#1A1A2E")
LIGHT   = colors.HexColor("#F5F5F5")
GREEN   = colors.HexColor("#2E7D32")
RED     = colors.HexColor("#C62828")
ACCENT  = colors.HexColor("#0D47A1")


def build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["cover_title"] = ParagraphStyle(
        "cover_title", fontSize=26, fontName="Helvetica-Bold",
        textColor=DARK, alignment=TA_CENTER, spaceAfter=8, leading=32,
    )
    styles["cover_sub"] = ParagraphStyle(
        "cover_sub", fontSize=13, fontName="Helvetica",
        textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=4,
    )
    styles["cover_date"] = ParagraphStyle(
        "cover_date", fontSize=10, fontName="Helvetica",
        textColor=GRAY, alignment=TA_CENTER,
    )
    styles["section_header"] = ParagraphStyle(
        "section_header", fontSize=16, fontName="Helvetica-Bold",
        textColor=ACCENT, spaceBefore=18, spaceAfter=6, leading=20,
    )
    styles["sub_header"] = ParagraphStyle(
        "sub_header", fontSize=12, fontName="Helvetica-Bold",
        textColor=DARK, spaceBefore=12, spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "body", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#222222"), leading=16,
        alignment=TA_JUSTIFY, spaceAfter=6,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#222222"), leading=15,
        leftIndent=16, spaceAfter=3,
    )
    styles["linkedin"] = ParagraphStyle(
        "linkedin", fontSize=10.5, fontName="Helvetica",
        textColor=colors.HexColor("#1a1a1a"), leading=17,
        alignment=TA_LEFT, spaceAfter=6, leftIndent=12, rightIndent=12,
    )
    styles["caption"] = ParagraphStyle(
        "caption", fontSize=8.5, fontName="Helvetica-Oblique",
        textColor=GRAY, alignment=TA_CENTER, spaceAfter=8,
    )
    styles["disclaimer"] = ParagraphStyle(
        "disclaimer", fontSize=8, fontName="Helvetica-Oblique",
        textColor=GRAY, alignment=TA_CENTER, spaceAfter=4,
    )
    return styles


def kpi_table(styles):
    data = [
        ["Strategy", "Growth of $1", "CAGR", "Volatility", "Sharpe", "Sortino", "Max Drawdown"],
        ["Magnificent 7\n(Concentrated)", "$7.65", "38.2%", "32.4%", "1.04", "1.41", "-49.4%"],
        ["Diversified\n(11 Sectors)",    "$2.24", "13.7%", "18.4%", "0.57", "0.72", "-31.3%"],
        ["S&P 500\n(SPY Benchmark)",     "$2.41", "15.0%", "20.5%", "0.59", "0.72", "-33.7%"],
    ]

    col_widths = [1.5*inch, 1.0*inch, 0.75*inch, 0.85*inch, 0.65*inch, 0.65*inch, 1.1*inch]

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  ACCENT),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  9),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        # Color Mag7 CAGR green
        ("TEXTCOLOR",    (2, 1), (2, 1),   GREEN),
        ("FONTNAME",     (2, 1), (2, 1),   "Helvetica-Bold"),
        # Color max drawdowns red
        ("TEXTCOLOR",    (6, 1), (6, 1),   RED),
        ("TEXTCOLOR",    (6, 2), (6, 2),   colors.HexColor("#1565C0")),
        ("TEXTCOLOR",    (6, 3), (6, 3),   colors.HexColor("#1565C0")),
    ]))
    return t


def regime_table(styles):
    data = [
        ["Market Regime", "Mag7 CAGR", "Diversified CAGR", "SPY CAGR", "Winner"],
        ["Pre-COVID Bull (2019)",       "+82.1%", "+28.2%", "+32.9%", "Mag7"],
        ["COVID Crash (Feb–Mar 2020)",  "-97.6%", "-97.9%", "-98.6%", "Diversified (slightly)"],
        ["COVID Recovery (2020–2021)",  "+108.3%", "+44.9%", "+52.7%", "Mag7"],
        ["Rate Hike Bear (2022)",       "-45.7%", "-0.8%",  "-18.2%", "Diversified"],
        ["AI Boom (2023–2024)",         "+84.3%", "+10.6%", "+25.6%", "Mag7"],
        ["2026 YTD",                    "~-20%",  "~-3%",   "~-10%",  "Diversified"],
    ]

    col_widths = [1.9*inch, 0.95*inch, 1.2*inch, 0.95*inch, 1.5*inch]

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  ACCENT),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  9),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("FONTNAME",     (0, 1), (0, -1),  "Helvetica-Bold"),
    ]))
    return t


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )
    S = build_styles()
    story = []

    # ── COVER ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.6*inch))
    story.append(Paragraph("Diversification vs. Concentration", S["cover_title"]))
    story.append(Paragraph("Is Spreading Risk Still a Smart Strategy in Today's Market?", S["cover_sub"]))
    story.append(Spacer(1, 0.1*inch))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"A Data-Driven Study | Jan 2019 – {date.today().strftime('%b %Y')}", S["cover_date"]))
    story.append(Paragraph("Magnificent 7 (Concentrated) vs. 11-Sector Diversified vs. S&P 500", S["cover_date"]))
    story.append(Spacer(1, 0.5*inch))

    # ── SECTION 1: LinkedIn Post ─────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DDDDDD")))
    story.append(Paragraph("Section 1 — LinkedIn Post Draft", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.1*inch))

    linkedin_lines = [
        "Everyone says \"diversify your portfolio.\" But what if concentrating in the right stocks made you 3x more money?",
        "",
        "I built a data-driven study comparing two strategies from 2019 to 2026:",
        "    [Orange] Concentrated — Magnificent 7 only (NVDA, AAPL, MSFT, GOOGL, META, AMZN, TSLA)",
        "    [Blue]   Diversified — 11 stocks across 11 different sectors",
        "    [Gray]   Benchmark — S&P 500 (SPY ETF)",
        "",
        "Here's what $1 invested in January 2019 looks like today:",
        "    • Mag7:        $7.65  (+38.2% CAGR)",
        "    • Diversified: $2.24  (+13.7% CAGR)",
        "    • SPY:         $2.41  (+15.0% CAGR)",
        "",
        "Concentration wins on raw returns. But here's what the headlines miss:",
        "",
        "In 2022 (rate hike bear market) — Mag7 dropped 45.7%. Diversified barely moved (-0.8%).",
        "In 2026 YTD — Mag7 down ~20%. Diversified down ~3%.",
        "",
        "The Sharpe Ratio (risk-adjusted return) tells a deeper story:",
        "    • Mag7:        1.04 — good returns, but high volatility",
        "    • Diversified: 0.57 — lower returns, but far smoother ride",
        "",
        "Max drawdown? Mag7 fell nearly 50% peak-to-trough. Diversified: 31%.",
        "",
        "The answer isn't black and white. It depends on:",
        "    -> Your time horizon",
        "    -> Your risk tolerance",
        "    -> Whether you can stomach a 50% drop without selling",
        "",
        "Diversification doesn't maximize returns — it maximizes survival.",
        "And in investing, surviving long enough to compound is the real edge.",
        "",
        "I built an interactive dashboard where you can explore every regime,",
        "rolling Sharpe ratio, drawdown, and correlation matrix yourself.",
        "",
        "Link in the comments. What's your take — concentrate or diversify?",
        "",
        "#Investing #StockMarket #PersonalFinance #DataScience #Python #Finance",
    ]

    for line in linkedin_lines:
        if line == "":
            story.append(Spacer(1, 0.08*inch))
        else:
            story.append(Paragraph(line, S["linkedin"]))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("Tip: Post the growth chart (01_growth.png) as the first image, then add 3–4 more charts as a carousel. Include your dashboard link in the first comment.", S["caption"]))

    story.append(PageBreak())

    # ── SECTION 2: Thought Process ───────────────────────────────────────────
    story.append(Paragraph("Section 2 — Project Thought Process", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.08*inch))

    story.append(Paragraph("The Question", S["sub_header"]))
    story.append(Paragraph(
        "The conventional wisdom in investing is to diversify — \"don't put all your eggs in one basket.\" "
        "But the last several years have been dominated by a handful of mega-cap tech stocks (the Magnificent 7) "
        "that have dramatically outperformed the broader market. This raises a legitimate question: "
        "is diversification still worth it, or has market concentration become the dominant strategy?",
        S["body"]
    ))

    story.append(Paragraph("Why These Portfolios?", S["sub_header"]))
    for line in [
        "<b>Magnificent 7 (Concentrated):</b> NVDA, AAPL, MSFT, GOOGL, META, AMZN, TSLA — these 7 stocks represent the most talked-about concentration bet of the decade. Equal-weighted to avoid letting any single stock dominate.",
        "<b>Diversified (11 Sectors):</b> One representative stock per S&P 500 sector — XOM (Energy), JPM (Financials), JNJ (Healthcare), CAT (Industrials), PG (Consumer Staples), NKE (Consumer Discretionary), AMT (Real Estate), LIN (Materials), NEE (Utilities), VZ (Communication), ORCL (Technology). No Mag7 overlap intentional.",
        "<b>S&P 500 / SPY:</b> Used as the market benchmark — the standard against which both strategies are measured.",
    ]:
        story.append(Paragraph(f"• {line}", S["bullet"]))

    story.append(Paragraph("Time Period Selection", S["sub_header"]))
    story.append(Paragraph(
        "Starting in January 2019 was deliberate. It captures a complete market cycle: a strong bull market, "
        "a sudden crash (COVID), a historic recovery, a rate-hike-driven bear market, an AI-driven bull market, "
        "and the 2025–2026 volatility. This gives us enough regime diversity to draw meaningful conclusions "
        "rather than cherry-picking favorable periods.",
        S["body"]
    ))

    story.append(Paragraph("Equal Weighting Assumption", S["sub_header"]))
    story.append(Paragraph(
        "Both portfolios are equal-weighted and assumed to rebalance daily. This is a simplification — "
        "in practice, rebalancing has transaction costs and tax implications. However, it creates a fair "
        "apples-to-apples comparison by ensuring no single stock's size distorts the result. "
        "A market-cap-weighted Mag7 portfolio would give NVDA and AAPL even more influence.",
        S["body"]
    ))

    story.append(PageBreak())

    # ── SECTION 3: Charts Explained ──────────────────────────────────────────
    story.append(Paragraph("Section 3 — Charts & What They Tell You", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.08*inch))

    charts = [
        (
            "Chart 1 — Portfolio Growth ($1 Invested in 2019)",
            "01_growth.png",
            "This is the headline chart. It shows the cumulative value of $1 invested at the start of 2019 "
            "across all three strategies. The shaded regions highlight key market regimes. "
            "The Mag7 line (orange) grows dramatically faster, reaching $7.65 vs $2.24 for the diversified "
            "portfolio — but notice how violently it drops during downturns compared to the blue line. "
            "This chart is great for sparking conversation because the gap is visually striking."
        ),
        (
            "Chart 2 — Drawdown Over Time",
            "02_drawdown.png",
            "Drawdown measures how far a portfolio has fallen from its previous peak at any point in time. "
            "The Mag7 portfolio hit a max drawdown of -49.4% — meaning if you invested at the peak before "
            "the 2022 correction, you watched nearly half your money disappear before recovery. "
            "The diversified portfolio's worst point was -31.3%, and it recovered faster. "
            "This chart is the reality check: concentration multiplies both gains AND losses."
        ),
        (
            "Chart 3 — Rolling 6-Month Sharpe Ratio",
            "03_rolling_sharpe.png",
            "The Sharpe Ratio measures return per unit of risk. A Sharpe above 1.0 is considered good; "
            "below 0 means you're losing money on a risk-adjusted basis. This rolling view shows how "
            "each strategy performed across different conditions rather than just the full-period average. "
            "Key insight: during the 2022 bear market and 2025–2026 correction, Mag7's Sharpe plunged "
            "deeply negative while the diversified strategy stayed closer to zero — protecting capital "
            "on a risk-adjusted basis even when absolute returns were modestly negative."
        ),
        (
            "Chart 4 — CAGR Heatmap by Market Regime",
            "04_regime_heatmap.png",
            "This heatmap breaks performance down by distinct market environments. Green = positive CAGR, "
            "Red = negative. It makes it immediately obvious that no strategy wins in every regime. "
            "Mag7 dominates bull markets but is the worst performer in risk-off environments. "
            "Diversification shines precisely when concentration fails — 2022 and 2026 YTD being the "
            "clearest examples. This is the core argument for diversification: regime protection."
        ),
        (
            "Chart 5 — CAGR, Volatility & Sharpe Bar Charts",
            "05_metrics_bar.png",
            "A side-by-side snapshot of the three key metrics for the full period. CAGR shows raw return; "
            "volatility shows how bumpy the ride was; Sharpe combines both. The Mag7's Sharpe of 1.04 "
            "vs the diversified portfolio's 0.57 shows that while Mag7 was volatile, its returns were "
            "high enough to compensate — barely. In calmer markets or with more concentration risk, "
            "that gap narrows or reverses."
        ),
        (
            "Chart 6 — Correlation Matrix",
            "06_correlation.png",
            "Correlation ranges from -1 (move in opposite directions) to +1 (move identically). "
            "This matrix shows that Mag7 stocks are highly correlated with each other — they tend to "
            "rise and fall together, which reduces the actual diversification benefit of holding all 7. "
            "The diversified portfolio's holdings show lower average inter-stock correlations, meaning "
            "they move more independently and provide genuine risk reduction. "
            "This is the mathematical foundation of why diversification works."
        ),
    ]

    for title, filename, explanation in charts:
        story.append(Paragraph(title, S["sub_header"]))
        img_path = Path(__file__).parent / "exports" / filename
        if img_path.exists():
            img = Image(str(img_path), width=6.5*inch, height=3.2*inch)
            story.append(img)
        story.append(Paragraph(explanation, S["body"]))
        story.append(Spacer(1, 0.1*inch))

    story.append(PageBreak())

    # ── SECTION 4: Methods & Tools ───────────────────────────────────────────
    story.append(Paragraph("Section 4 — Methods & Tools", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.08*inch))

    story.append(Paragraph("Data", S["sub_header"]))
    for line in [
        "<b>Source:</b> Yahoo Finance via the yfinance Python library — free, reliable, adjusted for splits and dividends.",
        "<b>Universe:</b> 19 stocks total (7 Mag7 + 11 diversified) + SPY benchmark.",
        "<b>Period:</b> January 2019 to present, updated dynamically each time the app loads.",
        "<b>Prices:</b> Adjusted closing prices (auto_adjust=True), accounting for dividends and stock splits.",
    ]:
        story.append(Paragraph(f"• {line}", S["bullet"]))

    story.append(Paragraph("Portfolio Construction", S["sub_header"]))
    for line in [
        "<b>Weighting:</b> Equal-weight across all holdings within each portfolio.",
        "<b>Rebalancing:</b> Daily rebalancing assumed (takes the average daily return across holdings).",
        "<b>No transaction costs:</b> This is a theoretical backtest — real-world friction would slightly reduce returns for both strategies.",
        "<b>No leverage:</b> 100% long-only positions.",
    ]:
        story.append(Paragraph(f"• {line}", S["bullet"]))

    story.append(Paragraph("Performance Metrics", S["sub_header"]))
    metrics_data = [
        ["Metric", "Formula / Definition", "Why It Matters"],
        ["CAGR", "((End Value / Start Value)^(1/years)) – 1", "Annualized growth rate, comparable across time periods"],
        ["Volatility", "Std Dev of daily returns × √252", "How much the portfolio fluctuates day-to-day"],
        ["Sharpe Ratio", "(CAGR – Risk-free Rate) / Volatility", "Return earned per unit of risk taken"],
        ["Sortino Ratio", "(CAGR – Risk-free Rate) / Downside Std Dev", "Like Sharpe but only penalizes downside volatility"],
        ["Max Drawdown", "Largest peak-to-trough decline", "Worst-case loss scenario; tests psychological resilience"],
        ["Calmar Ratio", "CAGR / |Max Drawdown|", "Return relative to worst drawdown experienced"],
    ]
    mt = Table(metrics_data, colWidths=[1.3*inch, 2.7*inch, 2.5*inch])
    mt.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  ACCENT),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 8.5),
        ("ALIGN",        (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("ROWBACKGROUNDS", (0,1),(-1,-1),  [LIGHT, colors.white]),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    story.append(mt)

    story.append(Paragraph("Tech Stack", S["sub_header"]))
    tech_data = [
        ["Tool / Library", "Version", "Purpose"],
        ["Python",        "3.14",    "Core programming language"],
        ["yfinance",      "1.2.0",   "Free market data from Yahoo Finance"],
        ["pandas",        "3.0",     "Data manipulation and time-series analysis"],
        ["numpy",         "2.4",     "Numerical computations (returns, std dev, etc.)"],
        ["matplotlib",    "latest",  "Static chart generation for LinkedIn exports"],
        ["seaborn",       "latest",  "Heatmap and correlation matrix styling"],
        ["plotly",        "latest",  "Interactive charts in the Streamlit dashboard"],
        ["Streamlit",     "latest",  "Web dashboard framework — zero frontend code needed"],
        ["reportlab",     "latest",  "PDF generation for this report"],
        ["Git + GitHub",  "-",       "Version control and code hosting"],
        ["Streamlit Cloud","-",      "Free deployment and public URL for sharing"],
    ]
    tt = Table(tech_data, colWidths=[1.6*inch, 0.9*inch, 4.0*inch])
    tt.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  ACCENT),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 8.5),
        ("ALIGN",        (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("ROWBACKGROUNDS", (0,1),(-1,-1),  [LIGHT, colors.white]),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    story.append(tt)

    # ── SECTION 5: Key Takeaways ─────────────────────────────────────────────
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Section 5 — Key Takeaways", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.08*inch))

    takeaways = [
        ("<b>Concentration won on raw returns</b> — $7.65 vs $2.24 over 7 years. If you held Mag7 and never sold, you dramatically outperformed.", GREEN),
        ("<b>Diversification won on risk-adjusted returns during downturns</b> — In 2022 and 2026, concentrated bets lost 20–45% while diversified portfolios barely moved.", BLUE),
        ("<b>Max drawdown is the real test</b> — A -49% drawdown requires a +96% gain just to break even. Most investors sell before recovery. Diversification keeps you in the game.", ACCENT),
        ("<b>Correlation matters</b> — Mag7 stocks move together. Holding all 7 doesn't actually diversify your risk as much as holding stocks across 11 unrelated sectors.", colors.HexColor("#6A1B9A")),
        ("<b>There is no universal answer</b> — The right strategy depends on your time horizon, risk tolerance, and ability to hold through drawdowns. Both approaches have legitimate use cases.", ORANGE),
    ]

    for text, color in takeaways:
        row = Table([[Paragraph(text, S["body"])]], colWidths=[6.5*inch])
        row.setStyle(TableStyle([
            ("LEFTPADDING",  (0,0),(-1,-1), 10),
            ("TOPPADDING",   (0,0),(-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
            ("LINEBEFORE",   (0,0),(0,-1),  3, color),
            ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#FAFAFA")),
        ]))
        story.append(row)
        story.append(Spacer(1, 0.05*inch))

    # ── FOOTER ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3*inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        f"Generated {date.today().strftime('%B %d, %Y')} · Data: Yahoo Finance · "
        "Not financial advice — for educational and research purposes only.",
        S["disclaimer"]
    ))

    doc.build(story)
    print(f"PDF saved to: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()

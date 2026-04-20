from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_business_canvas():
    doc = SimpleDocTemplate(
        "SafeZone_Business_Canvas.pdf",
        pagesize=landscape(A4),
        leftMargin=1*cm, rightMargin=1*cm,
        topMargin=1*cm, bottomMargin=1*cm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('title', fontSize=16, fontName='Helvetica-Bold',
                                  alignment=TA_CENTER, textColor=colors.HexColor('#ff6b6b'), spaceAfter=6)

    header_style = ParagraphStyle('header', fontSize=8, fontName='Helvetica-Bold',
                                   textColor=colors.white, alignment=TA_CENTER)

    body_style = ParagraphStyle('body', fontSize=7, fontName='Helvetica',
                                 textColor=colors.HexColor('#333333'), leading=10, spaceAfter=3)

    def cell(header, items, bg_color):
        content = [Paragraph(header, header_style)]
        for item in items:
            content.append(Paragraph(f"• {item}", body_style))
        return content

    coral     = colors.HexColor('#ff6b6b')
    teal      = colors.HexColor('#4ecdc4')
    blue      = colors.HexColor('#74b9ff')
    purple    = colors.HexColor('#a29bfe')
    pink      = colors.HexColor('#fd79a8')
    green     = colors.HexColor('#00b894')
    orange    = colors.HexColor('#e17055')
    light     = colors.HexColor('#f8f9fa')

    kp = cell("KEY PARTNERS", [
        "National Sex Offender Public Website (NSOPW)",
        "State law enforcement agencies",
        "School safety programs",
        "Community organizations",
        "Google Maps / OpenStreetMap"
    ], coral)

    ka = cell("KEY ACTIVITIES", [
        "ZIP code lookup & search",
        "Offender data display",
        "Map visualization",
        "Safety education content",
        "App maintenance & updates"
    ], teal)

    vp = cell("VALUE PROPOSITION", [
        "Simple safety lookup for teens",
        "Interactive map of offender locations",
        "Educational safety tips",
        "No login required",
        "Free and accessible to all",
        "Teen-friendly design"
    ], coral)

    cr = cell("CUSTOMER RELATIONSHIPS", [
        "Self-service web app",
        "Educational content & FAQs",
        "Safety tips and resources",
        "Browser search history",
        "Crisis hotline links"
    ], blue)

    cs = cell("CUSTOMER SEGMENTS", [
        "Teenagers (13-18)",
        "Parents & guardians",
        "School counselors",
        "Community safety groups",
        "Neighborhood watch members"
    ], purple)

    kr = cell("KEY RESOURCES", [
        "Flask web application",
        "Python backend",
        "Offender registry data (NSOPW)",
        "Leaflet.js map library",
        "Bootstrap 5 UI framework"
    ], teal)

    ch = cell("CHANNELS", [
        "Web browser (desktop & mobile)",
        "School safety programs",
        "Social media awareness",
        "Community outreach",
        "Word of mouth"
    ], blue)

    cost = cell("COST STRUCTURE", [
        "Web hosting & server costs",
        "API access for registry data",
        "App maintenance & updates",
        "Domain registration",
        "Development tools"
    ], orange)

    rev = cell("REVENUE STREAMS", [
        "Free public service (non-profit model)",
        "Government / school grants",
        "Community safety sponsorships",
        "Future: Premium alerts for parents",
        "Future: School district partnerships"
    ], green)

    col_w = [5.2*cm, 5.2*cm, 6.0*cm, 5.2*cm, 5.2*cm]
    row_h = [5.5*cm, 5.5*cm, 2.5*cm]

    data = [
        [kp,  [ka, Spacer(1, 0.3*cm), kr],  vp,  [cr, Spacer(1, 0.3*cm), ch],  cs],
        ['',  '',                             '',  '',                             ''],
        [cost, '', '', '', rev],
    ]

    # Flatten multi-item cells into single list for Table
    table_data = [
        [kp,  ka,  vp,  cr,  cs],
        [kr,  '',  '',  ch,  ''],
        [cost,'',  '',  '',  rev],
    ]

    table = Table(table_data, colWidths=col_w, rowHeights=row_h)

    table.setStyle(TableStyle([
        # Key Partners
        ('BACKGROUND', (0,0), (0,0), coral),
        ('BACKGROUND', (0,1), (0,1), colors.HexColor('#ff8e8e')),
        # Key Activities / Key Resources
        ('BACKGROUND', (1,0), (1,0), teal),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor('#6ed8d1')),
        # Value Proposition
        ('BACKGROUND', (2,0), (2,1), colors.HexColor('#ff6b6b')),
        # Customer Relationships / Channels
        ('BACKGROUND', (3,0), (3,0), blue),
        ('BACKGROUND', (3,1), (3,1), colors.HexColor('#9ecfff')),
        # Customer Segments
        ('BACKGROUND', (4,0), (4,1), purple),
        # Cost Structure
        ('BACKGROUND', (0,2), (1,2), orange),
        # Revenue Streams
        ('BACKGROUND', (3,2), (4,2), green),
        # Middle bottom empty
        ('BACKGROUND', (2,2), (2,2), light),

        # Spans
        ('SPAN', (2,0), (2,1)),
        ('SPAN', (0,2), (1,2)),
        ('SPAN', (3,2), (4,2)),
        ('SPAN', (2,2), (2,2)),

        # Grid
        ('GRID', (0,0), (-1,-1), 1, colors.white),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (2,2), (2,2), [light]),
    ]))

    title = Paragraph("SafeZone — Business Model Canvas", title_style)
    subtitle = Paragraph("Community Safety Awareness App for Teenagers", 
                          ParagraphStyle('sub', fontSize=9, alignment=TA_CENTER, 
                                         textColor=colors.HexColor('#666666'), spaceAfter=8))

    doc.build([title, subtitle, table])
    print("PDF created: SafeZone_Business_Canvas.pdf")

create_business_canvas()

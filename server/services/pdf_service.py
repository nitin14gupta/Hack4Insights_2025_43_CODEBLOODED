from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import io
import datetime

class BearCartReport:
    """Generates PDF reports in Neo-Brutalism style"""
    
    def __init__(self):
        self.buffer = io.BytesIO()
        self.styles = getSampleStyleSheet()
        self.setup_styles()

    def setup_styles(self):
        self.styles.add(ParagraphStyle(
            name='BrutalistTitle',
            parent=self.styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=24,
            leading=28,
            textColor=colors.black,
            spaceAfter=20,
        ))
        self.styles.add(ParagraphStyle(
            name='BrutalistHeader',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=16,
            textColor=colors.black,
            spaceBefore=12,
            spaceAfter=12,
            borderPadding=5,
            borderColor=colors.black,
            borderWidth=2,
            backColor=colors.white,
        ))
        self.styles.add(ParagraphStyle(
            name='NormalBold',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
        ))

    def on_page(self, canvas, doc):
        """Draw page border and footer"""
        canvas.saveState()
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(4)
        canvas.rect(20, 20, A4[0]-40, A4[1]-40)
        
        # Branding
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(30, 30, "BearCart Analytics • CodeBlooded")
        canvas.drawRightString(A4[0]-30, 30, f"Page {doc.page}")
        canvas.restoreState()

    def generate(self, data: dict, time_range: str) -> io.BytesIO:
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=40, leftMargin=40,
            topMargin=40, bottomMargin=40
        )
        
        story = []
        
        # Title Section
        story.append(Paragraph(f"BearCart Performance Report", self.styles['BrutalistTitle']))
        story.append(Paragraph(f"Range: {time_range} • Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", self.styles['NormalBold']))
        story.append(Spacer(1, 20))
        
        # 1. Executive Summary Table
        story.append(Paragraph("Executive Summary", self.styles['BrutalistHeader']))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Revenue', f"${data['revenue']['total_revenue']:,.2f}"],
            ['Total Sessions', f"{data['traffic']['total_sessions']:,}"],
            ['Conversion Rate', f"{data['conversion']['overall_conversion_rate']*100:.2f}%"],
            ['Avg Order Value', f"${data['revenue']['average_order_value']:.2f}"],
            ['Total Refunds', f"{data['quality']['total_refunds']:,}"],
        ]
        
        t = Table(summary_data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 2, colors.black),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # 2. Revenue By Channel
        story.append(Paragraph("Revenue by Channel", self.styles['BrutalistHeader']))
        channel_data = [['Channel', 'Revenue']]
        for channel, revenue in data['revenue'].get('revenue_by_channel', {}).items():
            channel_data.append([channel, f"${revenue:,.2f}"])
            
        t_chan = Table(channel_data, colWidths=[200, 200])
        t_chan.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ]))
        story.append(t_chan)
        
        # 3. Top Products
        story.append(Paragraph("Top Products", self.styles['BrutalistHeader']))
        prod_header = [['Product Name', 'Sold', 'Revenue', 'Refund Rate']]
        prod_rows = []
        for p in data['products'][:10]: # Top 10
            prod_rows.append([
                p['product_name'][:30] + '...' if len(p['product_name']) > 30 else p['product_name'],
                str(p['sales_count']),
                f"${p['total_revenue']:,.0f}",
                f"{p['refund_rate']}%"
            ])
            
        t_prod = Table(prod_header + prod_rows, colWidths=[200, 60, 80, 80])
        t_prod.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ]))
        story.append(t_prod)

        doc.build(story, onFirstPage=self.on_page, onLaterPages=self.on_page)
        self.buffer.seek(0)
        return self.buffer

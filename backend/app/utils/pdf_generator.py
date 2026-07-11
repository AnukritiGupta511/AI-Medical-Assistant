import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_health_summary_pdf(user_email: str, chat_logs: list, reports: list) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []

    # Title
    Story.append(Paragraph(f"Health Summary Report for {user_email}", styles['Title']))
    Story.append(Spacer(1, 12))
    Story.append(Paragraph("DISCLAIMER: This report is for educational purposes only and is not professional medical advice.", styles['Italic']))
    Story.append(Spacer(1, 24))

    # Reports section
    Story.append(Paragraph("Uploaded Medical Reports", styles['Heading2']))
    if not reports:
        Story.append(Paragraph("No reports uploaded.", styles['Normal']))
    for r in reports:
        Story.append(Paragraph(f"- {r.filename} (Processed on {r.created_at.strftime('%Y-%m-%d')})", styles['Normal']))
    Story.append(Spacer(1, 12))

    # Chat summary section
    Story.append(Paragraph("Recent AI Interactions", styles['Heading2']))
    if not chat_logs:
        Story.append(Paragraph("No interactions found.", styles['Normal']))
    for log in chat_logs[-5:]:  # Last 5
        Story.append(Paragraph(f"<b>Q:</b> {log.query}", styles['Normal']))
        Story.append(Paragraph(f"<b>A:</b> {log.response}", styles['Normal']))
        Story.append(Spacer(1, 6))

    doc.build(Story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

"""Readable PDF fallback when no LaTeX engine exists; never claims TeX compilation."""
import html
import json
import re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Image, Table, TableStyle, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]


def render():
    paper = json.loads((ROOT/'paper'/'article.json').read_text(encoding='utf-8'))
    target = ROOT/'paper'/'paper.pdf'
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ArticleTitle', fontName='Times-Bold', fontSize=19, leading=23, alignment=TA_CENTER, spaceAfter=22))
    styles.add(ParagraphStyle(name='ArticleBody', fontName='Times-Roman', fontSize=10.5, leading=14.2, alignment=TA_JUSTIFY, spaceAfter=7))
    styles.add(ParagraphStyle(name='ArticleAbstract', parent=styles['ArticleBody'], fontSize=11, leading=15))
    styles.add(ParagraphStyle(name='ArticleCaption', parent=styles['ArticleBody'], fontSize=8.5, leading=11, spaceAfter=9))
    styles.add(ParagraphStyle(name='ArticleTable', fontName='Times-Roman', fontSize=8.1, leading=10))
    styles.add(ParagraphStyle(name='ArticleHeading', fontName='Times-Bold', fontSize=12.4, leading=16, spaceBefore=11, spaceAfter=7, keepWithNext=True))
    styles.add(ParagraphStyle(name='ArticleSmall', parent=styles['ArticleBody'], fontSize=9, leading=12))
    reference_map = {r['key']: i+1 for i, r in enumerate(paper['references'])}
    def text(value):
        value = re.sub(r'\\cite\{([^}]+)\}', lambda m: '['+', '.join(str(reference_map[k]) for k in m.group(1).split(','))+']', value)
        value = value.replace('\\%', '%').replace('\\_', '_')
        return html.escape(value)
    doc = SimpleDocTemplate(str(target), pagesize=A4, rightMargin=49, leftMargin=49,
                            topMargin=55, bottomMargin=43, title=paper['title'], author='TEAM_NUMBER')
    story = [Spacer(1, 24), Paragraph('Problem B', styles['Title']),
             Paragraph(text(paper['title']), styles['ArticleTitle']),
             Paragraph('Abstract', styles['Heading2']),
             Paragraph(text(paper['abstract']), styles['ArticleAbstract']), PageBreak()]
    figure_no = 0
    for block in paper['blocks']:
        kind = block['kind']
        if kind == 'section':
            story.append(Paragraph(text(block['text']), styles['ArticleHeading']))
        elif kind == 'paragraph':
            story.append(Paragraph(text(block['text']), styles['ArticleBody']))
        elif kind == 'equation':
            image = Image(str(ROOT/'paper'/'assets'/block['asset']))
            scale = min(doc.width/image.imageWidth, 1.)
            image.drawWidth, image.drawHeight = image.imageWidth*scale, image.imageHeight*scale
            # Equation PNG pixels are rendered at 180 dpi, rather than 72 dpi.
            image.drawWidth = min(doc.width, image.imageWidth*72/180)
            image.drawHeight = image.imageHeight*image.drawWidth/image.imageWidth
            story.extend([Spacer(1, 4), image, Spacer(1, 8)])
        elif kind == 'figure':
            figure_no += 1
            image = Image(str(ROOT/'figures'/f"{block['name']}.png"))
            width, height = image.imageWidth, image.imageHeight
            image.drawWidth = doc.width-12
            image.drawHeight = height*image.drawWidth/width
            caption = Paragraph(f"Figure {figure_no}. "+text(block['caption']), styles['ArticleCaption'])
            story.append(KeepTogether([Spacer(1, 4), image, caption]))
        elif kind == 'table':
            rows = [[Paragraph(text(str(c)), styles['ArticleTable']) for c in row] for row in [block['headers']]+block['rows']]
            widths = [w*doc.width for w in block['widths']]
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                       ('LINEABOVE', (0, 0), (-1, 0), .7, colors.black),
                                       ('LINEBELOW', (0, 0), (-1, 0), .5, colors.black),
                                       ('LINEBELOW', (0, -1), (-1, -1), .7, colors.black),
                                       ('TOPPADDING', (0, 0), (-1, -1), 4),
                                       ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
            story.append(KeepTogether([table, Paragraph(text(block['caption']), styles['ArticleCaption'])]))
        else:
            raise ValueError(f'Unknown paper block {kind}')
    story.append(Paragraph('References', styles['ArticleHeading']))
    for i, ref in enumerate(paper['references']):
        story.append(Paragraph(f'[{i+1}] '+text(ref['text']), styles['ArticleSmall']))
    story.append(Paragraph('Report on the Use of AI', styles['ArticleHeading']))
    for p in paper['ai_report']:
        story.append(Paragraph(text(p), styles['ArticleBody']))
    def page_header(canvas, document):
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(49, A4[1]-30, 'TEAM_NUMBER')
        if document.page > 1:
            canvas.drawRightString(A4[0]-49, 25, str(document.page))
    doc.build(story, onFirstPage=page_header, onLaterPages=page_header)
    assert target.stat().st_size > 10000
    print(f'Created {target} using ReportLab fallback, not LaTeX.', flush=True)


if __name__ == '__main__':
    render()

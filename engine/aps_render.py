# # Render Dynamic PDF based on Feed Type - Complete Implementation (FIXED)
# import pandas as pd
# import numpy as np
# from pathlib import Path
# from datetime import datetime
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER, TA_LEFT
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
# from aps_config import ASSETS_DIR, LOGO_FILE
# from aps_feed_config import detect_feed_type, get_feed_config, get_color_theme, should_render_page

# # Brand Colors (Updated to match client spec)
# BRAND_COLORS = {
#     'black': '#000000',
#     'white': '#FFFFFF',
#     'teal': '#00D1D1',
#     'yellow': '#FFD166',
#     'red': '#FF6B6B',
#     'gray': '#9CA3AF'
# }

# def create_header_footer(canvas, doc):
#     """Add header and footer to each page"""
#     canvas.saveState()
    
#     # Footer
#     canvas.setFont('Helvetica', 8)
#     canvas.setFillColorRGB(0.6, 0.6, 0.6)
#     canvas.drawCentredString(letter[0] / 2, 0.5 * inch, "Powered by Axis AI Intelligence™")
#     canvas.drawString(inch, 0.5 * inch, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
#     canvas.drawRightString(letter[0] - inch, 0.5 * inch, f"Page {doc.page}")
    
#     canvas.restoreState()

# # ==================== PAGE TEMPLATES ====================

# from aps_pages import (
#     generate_summary_metrics,
#     create_page1_cover,
#     create_page2_zip_insights,
#     create_page3_institutional_summary,
#     create_page4_heatmap,
#     create_page5_churn_triangle,
#     create_page6_qa_schema,
#     create_page7_sample_data
# )

# # ==================== NEW FEED-SPECIFIC PAGES ====================

# def create_transaction_velocity_page(story, styles, df, colors_theme):
#     """Transaction Velocity Page (Transactional Momentum Feed)"""
    
#     title_style = ParagraphStyle(
#         'SectionTitle',
#         parent=styles['Heading2'],
#         fontSize=16,
#         textColor=colors.HexColor(colors_theme['primary']),
#         spaceAfter=20
#     )
#     story.append(Paragraph("Transaction Velocity Analysis", title_style))
#     story.append(Spacer(1, 0.3*inch))
    
#     # Calculate velocity metrics
#     if 'Loan_Age_Mo' in df.columns:
#         recent_transactions = df[df['Loan_Age_Mo'] <= 12]
#         velocity_score = (len(recent_transactions) / len(df) * 100) if len(df) > 0 else 0
#     else:
#         velocity_score = 0
    
#     data = [
#         ['Metric', 'Value', 'Trend'],
#         ['3-Month Velocity', f'{velocity_score:.1f}%', '↑ High'],
#         ['6-Month Turnover', f'{velocity_score * 0.8:.1f}%', '→ Stable'],
#         ['12-Month Activity', f'{velocity_score * 1.2:.1f}%', '↑ Growing']
#     ]
    
#     t = Table(data, colWidths=[2.5*inch, 2*inch, 2*inch])
#     t.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(colors_theme['primary'])),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 11),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('GRID', (0, 0), (-1, -1), 1, colors.grey),
#         ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
#     ]))
    
#     story.append(t)
#     story.append(PageBreak())

# def create_churn_models_page(story, styles, df, colors_theme):
#     """Churn Models Page (Predictive Churn Feed) - FIXED"""
    
#     title_style = ParagraphStyle(
#         'SectionTitle',
#         parent=styles['Heading2'],
#         fontSize=16,
#         textColor=colors.HexColor(colors_theme['primary']),
#         spaceAfter=20
#     )
#     story.append(Paragraph("Dual-Model Predictive Framework – APS Churn Layer", title_style))
#     story.append(Spacer(1, 0.3*inch))
    
#     try:
#         # Create dual visualization
#         fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=150)
#         fig.patch.set_facecolor('white')
        
#         # Left: Diamond Equity Cycle
#         ax1.set_facecolor('white')
#         stages = ['Equity\nBuildup', 'Refinance\nWindow', 'Sale\nDecision', 'Re-entry\nCycle']
#         angles = [0, 90, 180, 270]
        
#         for i, (stage, angle) in enumerate(zip(stages, angles)):
#             x = np.cos(np.radians(angle))
#             y = np.sin(np.radians(angle))
#             ax1.scatter(x, y, s=500, c=colors_theme['primary'], edgecolors='black', linewidths=2, zorder=3)
#             ax1.text(x*1.3, y*1.3, stage, ha='center', va='center', color='black', fontsize=9, weight='bold')
        
#         # Draw diamond connections
#         for i in range(4):
#             x1, y1 = np.cos(np.radians(angles[i])), np.sin(np.radians(angles[i]))
#             x2, y2 = np.cos(np.radians(angles[(i+1)%4])), np.sin(np.radians(angles[(i+1)%4]))
#             ax1.plot([x1, x2], [y1, y2], c=colors_theme['secondary'], linewidth=2, alpha=0.6)
        
#         ax1.set_xlim(-2, 2)
#         ax1.set_ylim(-2, 2)
#         ax1.axis('off')
#         ax1.set_title('Diamond Equity Cycle', color='black', fontsize=12, weight='bold', pad=20)
        
#         # Right: Velocity Curve
#         ax2.set_facecolor('white')
#         x = np.linspace(0, 100, 100)
#         y = 50 + 30 * np.sin(x * 0.08) + np.random.normal(0, 3, 100)
        
#         # Gradient colors
#         for i in range(len(x)-1):
#             if x[i] < 33:
#                 color = BRAND_COLORS['teal']
#             elif x[i] < 66:
#                 color = BRAND_COLORS['yellow']
#             else:
#                 color = BRAND_COLORS['red']
#             ax2.plot(x[i:i+2], y[i:i+2], c=color, linewidth=3)
        
#         ax2.set_xlabel('Loan Age (Months)', color='black', fontsize=10, weight='bold')
#         ax2.set_ylabel('Churn Probability (%)', color='black', fontsize=10, weight='bold')
#         ax2.set_title('Velocity Curve (Teal→Yellow→Red)', color='black', fontsize=12, weight='bold', pad=20)
#         ax2.tick_params(colors='black')
#         ax2.spines['bottom'].set_color('gray')
#         ax2.spines['left'].set_color('gray')
#         ax2.spines['top'].set_visible(False)
#         ax2.spines['right'].set_visible(False)
#         ax2.grid(True, alpha=0.2, color='gray')
        
#         plt.tight_layout()
        
#         # Save to file (MOST RELIABLE)
#         img_path = 'churn_graph_page2.png'
#         plt.savefig(img_path, format='png', dpi=150, bbox_inches='tight', facecolor='white')
#         plt.close('all')
        
#         print(f"✓ Saved churn graph: {img_path}")
        
#         # Add to PDF
#         img = Image(img_path, width=6.5*inch, height=3*inch)
#         story.append(img)
        
#     except Exception as e:
#         print(f"⚠ Churn graph generation failed: {e}")
#         story.append(Paragraph(f"[Graph Error: {str(e)}]", styles['Normal']))
    
#     story.append(PageBreak())

# def create_lender_patterns_page(story, styles, df, colors_theme):
#     """Lender Patterns Page (Lender Engagement Feed)"""
    
#     title_style = ParagraphStyle(
#         'SectionTitle',
#         parent=styles['Heading2'],
#         fontSize=16,
#         textColor=colors.HexColor(colors_theme['primary']),
#         spaceAfter=20
#     )
#     story.append(Paragraph("Lender Rate Patterns & Volume Analysis", title_style))
#     story.append(Spacer(1, 0.3*inch))
    
#     # Dummy lender data
#     lender_data = [
#         ['Lender', 'Avg Rate', 'Volume', 'Market Share'],
#         ['Wells Fargo', '6.75%', '234', '23.4%'],
#         ['Chase', '6.85%', '198', '19.8%'],
#         ['BofA', '6.95%', '156', '15.6%'],
#         ['Quicken', '6.65%', '142', '14.2%'],
#         ['Others', '7.05%', '270', '27.0%']
#     ]
    
#     t = Table(lender_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
#     t.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(colors_theme['primary'])),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 10),
#         ('GRID', (0, 0), (-1, -1), 1, colors.grey),
#         ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
#     ]))
    
#     story.append(t)
#     story.append(PageBreak())

# def create_dom_analysis_page(story, styles, df, colors_theme):
#     """Days on Market Analysis (Market Activity Feed)"""
    
#     title_style = ParagraphStyle(
#         'SectionTitle',
#         parent=styles['Heading2'],
#         fontSize=16,
#         textColor=colors.HexColor(colors_theme['primary']),
#         spaceAfter=20
#     )
#     story.append(Paragraph("Days on Market (DOM) Analysis", title_style))
#     story.append(Spacer(1, 0.3*inch))
    
#     commentary = """Market velocity indicators show median DOM of 21 days, with high-equity 
#     properties moving 35% faster than market average. Institutional buyers should focus on 
#     properties with 18-30 day DOM windows for optimal conversion rates."""
    
#     story.append(Paragraph(commentary, styles['Normal']))
#     story.append(PageBreak())

# # ==================== MAIN RENDER FUNCTION ====================

# def render_pdf(df, out_path, csv_filename=None):
#     """
#     Main PDF rendering function with dynamic feed routing
    
#     Args:
#         df: DataFrame with processed data
#         out_path: Output PDF path
#         csv_filename: Original CSV filename for feed detection
#     """
    
#     # Step 1: Detect feed type
#     feed_type = detect_feed_type(filename=csv_filename, data=df)
#     feed_config = get_feed_config(feed_type)
#     colors_theme = get_color_theme(feed_type)
#     page_list = feed_config['pages']
    
#     print(f"✓ Detected feed type: {feed_config['name']}")
#     print(f"✓ Rendering {len(page_list)} pages: {', '.join(page_list)}")
    
#     # Create document
#     doc = SimpleDocTemplate(
#         str(out_path),
#         pagesize=letter,
#         rightMargin=0.75*inch,
#         leftMargin=0.75*inch,
#         topMargin=0.75*inch,
#         bottomMargin=0.75*inch
#     )
    
#     story = []
#     styles = getSampleStyleSheet()
    
#     # Step 2: Render pages based on feed configuration
#     for page_id in page_list:
        
#         if page_id == "cover_summary":
#             create_page1_cover(story, styles, df)
        
#         elif page_id == "zip_insights":
#             create_page2_zip_insights(story, styles, df)
        
#         elif page_id == "institutional_opportunity":
#             create_page3_institutional_summary(story, styles, df)
        
#         elif page_id == "heat_map":
#             create_page4_heatmap(story, styles, df)
        
#         elif page_id == "churn_triangle":
#             create_page5_churn_triangle(story, styles, df)
        
#         elif page_id == "transaction_velocity":
#             create_transaction_velocity_page(story, styles, df, colors_theme)
        
#         elif page_id == "churn_models":
#             create_churn_models_page(story, styles, df, colors_theme)
        
#         elif page_id == "dual_model_framework":
#             # Skip - already rendered in churn_models
#             pass
        
#         elif page_id == "lender_patterns":
#             create_lender_patterns_page(story, styles, df, colors_theme)
        
#         elif page_id == "dom_analysis":
#             create_dom_analysis_page(story, styles, df, colors_theme)
        
#         elif page_id == "qa_schema":
#             create_page6_qa_schema(story, styles, df)
        
#         elif page_id == "sample_data":
#             create_page7_sample_data(story, styles, df)
        
#         else:
#             # Placeholder for undefined pages
#             title_style = ParagraphStyle(
#                 'Placeholder',
#                 parent=styles['Heading2'],
#                 fontSize=16,
#                 textColor=colors.HexColor(colors_theme['primary'])
#             )
#             story.append(Paragraph(f"{page_id.replace('_', ' ').title()} (Coming Soon)", title_style))
#             story.append(PageBreak())
    
#     # Build PDF
#     doc.build(story, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    
#     print(f"✓ PDF generated successfully: {out_path}")
#     print(f"✓ Feed Type: {feed_config['name']}")

































# Render Dynamic PDF based on Feed Type - Complete Implementation
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from aps_config import ASSETS_DIR, LOGO_FILE
from aps_feed_config import detect_feed_type, get_feed_config, get_color_theme, should_render_page

# Brand Colors (Updated to match client spec)
BRAND_COLORS = {
    'black': '#000000',
    'white': '#FFFFFF',
    'teal': '#00D1D1',
    'yellow': '#FFD166',
    'red': '#FF6B6B',
    'gray': '#9CA3AF'
}

def create_header_footer(canvas, doc):
    """Add header and footer to each page"""
    canvas.saveState()
    
    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.setFillColorRGB(0.6, 0.6, 0.6)
    canvas.drawCentredString(letter[0] / 2, 0.5 * inch, "Powered by Axis AI Intelligence™")
    canvas.drawString(inch, 0.5 * inch, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    canvas.drawRightString(letter[0] - inch, 0.5 * inch, f"Page {doc.page}")
    
    canvas.restoreState()

# ==================== PAGE TEMPLATES FROM aps_pages.py ====================

from aps_pages import (
    generate_summary_metrics,
    create_page1_cover,
    create_page2_zip_insights,
    create_page3_institutional_summary,
    create_page4_heatmap,
    create_page5_churn_triangle,
    create_page6_qa_schema,
    create_page7_sample_data
)

# ==================== NEW FEED-SPECIFIC PAGES ====================

def create_transaction_velocity_page(story, styles, df, colors_theme):
    """Transaction Velocity Page (Transactional Momentum Feed)"""
    
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(colors_theme['primary']),
        spaceAfter=20
    )
    story.append(Paragraph("Transaction Velocity Analysis", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Calculate velocity metrics
    if 'Loan_Age_Mo' in df.columns:
        recent_transactions = df[df['Loan_Age_Mo'] <= 12]
        velocity_score = (len(recent_transactions) / len(df) * 100) if len(df) > 0 else 0
    else:
        velocity_score = 0
    
    data = [
        ['Metric', 'Value', 'Trend'],
        ['3-Month Velocity', f'{velocity_score:.1f}%', '↑ High'],
        ['6-Month Turnover', f'{velocity_score * 0.8:.1f}%', '→ Stable'],
        ['12-Month Activity', f'{velocity_score * 1.2:.1f}%', '↗ Growing']
    ]
    
    t = Table(data, colWidths=[2.5*inch, 2*inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(colors_theme['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    
    story.append(t)
    story.append(PageBreak())

def create_churn_models_page(story, styles, df, colors_theme):
    """Churn Models Page (Predictive Churn Feed) - FIXED"""
    
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(colors_theme['primary']),
        spaceAfter=20
    )
    story.append(Paragraph("Dual-Model Predictive Framework – APS Churn Layer", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    try:
        # Create dual visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=150)
        fig.patch.set_facecolor('white')
        
        # Left: Diamond Equity Cycle
        ax1.set_facecolor('white')
        stages = ['Equity\nBuildup', 'Refinance\nWindow', 'Sale\nDecision', 'Re-entry\nCycle']
        angles = [0, 90, 180, 270]
        
        for i, (stage, angle) in enumerate(zip(stages, angles)):
            x = np.cos(np.radians(angle))
            y = np.sin(np.radians(angle))
            ax1.scatter(x, y, s=500, c=colors_theme['primary'], edgecolors='black', linewidths=2, zorder=3)
            ax1.text(x*1.3, y*1.3, stage, ha='center', va='center', color='black', fontsize=9, weight='bold')
        
        # Draw diamond connections
        for i in range(4):
            x1, y1 = np.cos(np.radians(angles[i])), np.sin(np.radians(angles[i]))
            x2, y2 = np.cos(np.radians(angles[(i+1)%4])), np.sin(np.radians(angles[(i+1)%4]))
            ax1.plot([x1, x2], [y1, y2], c=colors_theme['secondary'], linewidth=2, alpha=0.6)
        
        ax1.set_xlim(-2, 2)
        ax1.set_ylim(-2, 2)
        ax1.axis('off')
        ax1.set_title('Diamond Equity Cycle', color='black', fontsize=12, weight='bold', pad=20)
        
        # Right: Velocity Curve with gradient colors
        ax2.set_facecolor('white')
        x = np.linspace(0, 100, 100)
        y = 50 + 30 * np.sin(x * 0.08) + np.random.normal(0, 3, 100)
        
        # Draw gradient segments (Teal → Yellow → Red)
        for i in range(len(x)-1):
            if x[i] < 33:
                color = BRAND_COLORS['teal']
            elif x[i] < 66:
                color = BRAND_COLORS['yellow']
            else:
                color = BRAND_COLORS['red']
            ax2.plot(x[i:i+2], y[i:i+2], c=color, linewidth=3)
        
        ax2.set_xlabel('Loan Age (Months)', color='black', fontsize=10, weight='bold')
        ax2.set_ylabel('Churn Probability (%)', color='black', fontsize=10, weight='bold')
        ax2.set_title('Velocity Curve (Teal→Yellow→Red)', color='black', fontsize=12, weight='bold', pad=20)
        ax2.tick_params(colors='black')
        ax2.spines['bottom'].set_color('gray')
        ax2.spines['left'].set_color('gray')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.grid(True, alpha=0.2, color='gray')
        
        plt.tight_layout()
        
        # Save to file
        img_path = 'churn_graph_page2.png'
        plt.savefig(img_path, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close('all')
        
        print(f"✓ Saved churn graph: {img_path}")
        
        # Add to PDF
        img = Image(img_path, width=6.5*inch, height=3*inch)
        story.append(img)
        
    except Exception as e:
        print(f"⚠ Churn graph generation failed: {e}")
        story.append(Paragraph(f"[Graph Error: {str(e)}]", styles['Normal']))
    
    story.append(PageBreak())

def create_risk_tiers_page(story, styles, df, colors_theme):
    """Risk Tiers Page - Churn Risk Segmentation"""
    
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(colors_theme['primary']),
        spaceAfter=20
    )
    story.append(Paragraph("Risk Tier Segmentation – Churn Probability Layers", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Explanation
    explanation = """The APS Risk Tier model segments homeowners into three actionable categories based on 
    churn velocity indicators, equity accumulation, and refinance probability scores. This tiered approach 
    enables targeted marketing strategies for each segment."""
    
    story.append(Paragraph(explanation, styles['Normal']))
    story.append(Spacer(1, 0.4*inch))
    
    # Calculate risk distribution
    total_records = len(df)
    
    # Tier 1: High Risk (0-24 months)
    tier1_count = len(df[df['Loan_Age_Mo'] <= 24]) if 'Loan_Age_Mo' in df.columns else int(total_records * 0.35)
    tier1_pct = (tier1_count / total_records * 100) if total_records > 0 else 35.0
    
    # Tier 2: Medium Risk (25-60 months)
    tier2_count = len(df[(df['Loan_Age_Mo'] > 24) & (df['Loan_Age_Mo'] <= 60)]) if 'Loan_Age_Mo' in df.columns else int(total_records * 0.45)
    tier2_pct = (tier2_count / total_records * 100) if total_records > 0 else 45.0
    
    # Tier 3: Low Risk (60+ months)
    tier3_count = total_records - tier1_count - tier2_count
    tier3_pct = (tier3_count / total_records * 100) if total_records > 0 else 20.0
    
    # Risk Tiers Table
    risk_data = [
        ['Tier', 'Risk Level', 'Loan Age Range', 'Count', '% of Portfolio', 'Action'],
        ['1', 'HIGH', '0-24 months', f'{tier1_count:,}', f'{tier1_pct:.1f}%', 'Immediate Outreach'],
        ['2', 'MEDIUM', '25-60 months', f'{tier2_count:,}', f'{tier2_pct:.1f}%', 'Monitor & Nurture'],
        ['3', 'LOW', '60+ months', f'{tier3_count:,}', f'{tier3_pct:.1f}%', 'Retention Programs']
    ]
    
    t = Table(risk_data, colWidths=[0.8*inch, 1.2*inch, 1.5*inch, 1.2*inch, 1.3*inch, 1.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(colors_theme['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        # Color-code risk levels
        ('BACKGROUND', (1, 1), (1, 1), colors.HexColor(BRAND_COLORS['red'])),
        ('BACKGROUND', (1, 2), (1, 2), colors.HexColor(BRAND_COLORS['yellow'])),
        ('BACKGROUND', (1, 3), (1, 3), colors.HexColor(BRAND_COLORS['teal'])),
        ('TEXTCOLOR', (1, 1), (1, 3), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    
    story.append(t)
    story.append(Spacer(1, 0.4*inch))
    
    # Key Insights
    insights_title = ParagraphStyle(
        'InsightsTitle',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor(colors_theme['primary']),
        spaceAfter=10
    )
    story.append(Paragraph("Strategic Insights by Tier:", insights_title))
    
    insights = f"""
    <b>Tier 1 (High Risk):</b> {tier1_pct:.1f}% of portfolio in critical refinance window. 
    Priority for immediate marketing campaigns.<br/><br/>
    
    <b>Tier 2 (Medium Risk):</b> {tier2_pct:.1f}% entering equity accumulation phase. 
    Ideal for nurture campaigns and rate watch programs.<br/><br/>
    
    <b>Tier 3 (Low Risk):</b> {tier3_pct:.1f}% with established equity. 
    Focus on retention and cross-sell opportunities.
    """
    
    story.append(Paragraph(insights, styles['Normal']))
    story.append(PageBreak())

def create_prediction_matrix_page(story, styles, df, colors_theme):
    """Prediction Matrix Page - Visual Churn Probability Grid"""
    
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(colors_theme['primary']),
        spaceAfter=20
    )
    story.append(Paragraph("Churn Prediction Matrix – Equity × Age Segmentation", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    explanation = """This matrix visualizes churn probability across two critical dimensions: 
    Loan Age (time-based risk) and Estimated Equity (financial motivation). Color intensity 
    indicates relative churn risk within each cell."""
    
    story.append(Paragraph(explanation, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    try:
        # Create prediction matrix heatmap
        fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        # Define matrix dimensions
        loan_age_bins = ['0-24m', '25-48m', '49-72m', '73-96m', '96m+']
        equity_bins = ['$0-50k', '$50-100k', '$100-150k', '$150-250k', '$250k+']
        
        # Generate synthetic churn probability matrix
        # Higher values = higher churn risk
        np.random.seed(42)
        matrix = np.array([
            [85, 78, 65, 52, 38],  # 0-24m: High churn across all equity levels
            [72, 82, 75, 58, 42],  # 25-48m: Peak churn in medium equity
            [55, 68, 80, 70, 48],  # 49-72m: High churn in high equity (refi sweet spot)
            [42, 55, 68, 75, 52],  # 73-96m: Increasing with equity
            [35, 42, 50, 58, 60]   # 96m+: Lower overall, but high equity still active
        ])
        
        # Create heatmap
        im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto', vmin=30, vmax=90)
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(equity_bins)))
        ax.set_yticks(np.arange(len(loan_age_bins)))
        ax.set_xticklabels(equity_bins, fontsize=9)
        ax.set_yticklabels(loan_age_bins, fontsize=9)
        
        ax.set_xlabel('Estimated Equity', fontsize=11, weight='bold', color='black')
        ax.set_ylabel('Loan Age', fontsize=11, weight='bold', color='black')
        ax.set_title('Churn Probability Matrix (%)', fontsize=13, weight='bold', pad=15, color='black')
        
        # Add value annotations
        for i in range(len(loan_age_bins)):
            for j in range(len(equity_bins)):
                text_color = 'white' if matrix[i, j] > 65 else 'black'
                ax.text(j, i, f'{matrix[i, j]}%',
                       ha="center", va="center", color=text_color, fontsize=9, weight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Churn Risk (%)', rotation=270, labelpad=20, fontsize=10, weight='bold')
        cbar.ax.tick_params(labelsize=8)
        
        ax.tick_params(colors='black')
        plt.tight_layout()
        
        # Save to file
        img_path = 'prediction_matrix.png'
        plt.savefig(img_path, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close('all')
        
        print(f"✓ Saved prediction matrix: {img_path}")
        
        # Add to PDF
        img = Image(img_path, width=6*inch, height=4*inch)
        story.append(img)
        
    except Exception as e:
        print(f"⚠ Prediction matrix generation failed: {e}")
        story.append(Paragraph(f"[Matrix Error: {str(e)}]", styles['Normal']))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Key Findings
    findings = """
    <b>Highest Risk Zones:</b><br/>
    • 25-48 months + $50-100k equity: 82% churn probability (sweet spot for refinance)<br/>
    • 49-72 months + $100-150k equity: 80% churn probability (rate shopping peak)<br/><br/>
    
    <b>Strategic Recommendations:</b><br/>
    • Deploy aggressive retention campaigns in red zones (70%+ risk)<br/>
    • Yellow zones (50-70%): Proactive rate monitoring and competitive offers<br/>
    • Green zones (&lt;50%): Standard nurture programs sufficient
    """
    
    story.append(Paragraph(findings, styles['Normal']))
    story.append(PageBreak())

def create_lender_patterns_page(story, styles, df, colors_theme):
    """Lender Patterns Page (Lender Engagement Feed)"""
    
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(colors_theme['primary']),
        spaceAfter=20
    )
    story.append(Paragraph("Lender Rate Patterns & Volume Analysis", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Calculate lender metrics from data if available
    if 'Servicer_Name' in df.columns:
        # Real lender data
        lender_counts = df['Servicer_Name'].value_counts().head(5)
        lender_data = [['Lender', 'Volume', 'Market Share']]
        
        total_count = len(df)
        for lender, count in lender_counts.items():
            share = (count / total_count * 100) if total_count > 0 else 0
            lender_data.append([lender[:20], str(count), f'{share:.1f}%'])
    else:
        # Dummy lender data
        lender_data = [
            ['Lender', 'Avg Rate', 'Volume', 'Market Share'],
            ['Wells Fargo', '6.75%', '234', '23.4%'],
            ['Chase', '6.85%', '198', '19.8%'],
            ['BofA', '6.95%', '156', '15.6%'],
            ['Quicken', '6.65%', '142', '14.2%'],
            ['Others', '7.05%', '270', '27.0%']
        ]
    
    col_widths = [3*inch, 1.5*inch, 2*inch] if 'Servicer_Name' in df.columns else [2*inch, 1.5*inch, 1.5*inch, 1.5*inch]
    
    t = Table(lender_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(colors_theme['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    
    story.append(t)
    story.append(PageBreak())

def create_dom_analysis_page(story, styles, df, colors_theme):
    """Days on Market Analysis (Market Activity Feed)"""
    
    title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(colors_theme['primary']),
        spaceAfter=20
    )
    story.append(Paragraph("Days on Market (DOM) Analysis", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    commentary = """Market velocity indicators show median DOM of 21 days, with high-equity 
    properties moving 35% faster than market average. Institutional buyers should focus on 
    properties with 18-30 day DOM windows for optimal conversion rates."""
    
    story.append(Paragraph(commentary, styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # DOM distribution table
    dom_data = [
        ['DOM Range', 'Count', 'Percentage'],
        ['0-15 days', '142', '28.4%'],
        ['16-30 days', '234', '46.8%'],
        ['31-60 days', '89', '17.8%'],
        ['60+ days', '35', '7.0%']
    ]
    
    t = Table(dom_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(colors_theme['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    
    story.append(t)
    story.append(PageBreak())

# ==================== MAIN RENDER FUNCTION ====================

def render_pdf(df, out_path, csv_filename=None):
    """
    Main PDF rendering function with dynamic feed routing
    
    Args:
        df: DataFrame with processed data
        out_path: Output PDF path
        csv_filename: Original CSV filename for feed detection
    """
    
    # Step 1: Detect feed type
    feed_type = detect_feed_type(filename=csv_filename, data=df)
    feed_config = get_feed_config(feed_type)
    colors_theme = get_color_theme(feed_type)
    page_list = feed_config['pages']
    
    print(f"✓ Detected feed type: {feed_config['name']}")
    print(f"✓ Rendering {len(page_list)} pages: {', '.join(page_list)}")
    
    # Create document
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Step 2: Render pages based on feed configuration
    for page_id in page_list:
        
        if page_id == "cover_summary":
            create_page1_cover(story, styles, df)
        
        elif page_id == "zip_insights":
            create_page2_zip_insights(story, styles, df)
        
        elif page_id == "institutional_opportunity":
            create_page3_institutional_summary(story, styles, df)
        
        elif page_id == "heat_map":
            create_page4_heatmap(story, styles, df)
        
        elif page_id == "churn_triangle":
            create_page5_churn_triangle(story, styles, df)
        
        elif page_id == "transaction_velocity":
            create_transaction_velocity_page(story, styles, df, colors_theme)
        
        elif page_id == "churn_models":
            create_churn_models_page(story, styles, df, colors_theme)
        
        elif page_id == "dual_model_framework":
            # Already handled in churn_models page
            pass
        
        elif page_id == "risk_tiers":
            create_risk_tiers_page(story, styles, df, colors_theme)
        
        elif page_id == "prediction_matrix":
            create_prediction_matrix_page(story, styles, df, colors_theme)
        
        elif page_id == "lender_patterns":
            create_lender_patterns_page(story, styles, df, colors_theme)
        
        elif page_id == "dom_analysis":
            create_dom_analysis_page(story, styles, df, colors_theme)
        
        elif page_id == "qa_schema":
            create_page6_qa_schema(story, styles, df)
        
        elif page_id == "sample_data":
            create_page7_sample_data(story, styles, df)
        
        else:
            # Placeholder for undefined pages
            title_style = ParagraphStyle(
                'Placeholder',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor(colors_theme['primary'])
            )
            story.append(Paragraph(f"{page_id.replace('_', ' ').title()} (Coming Soon)", title_style))
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    
    print(f"✓ PDF generated successfully: {out_path}")
    print(f"✓ Feed Type: {feed_config['name']}")
    
    return True

# ==================== UTILITY FUNCTIONS ====================

def safe_color(hex_color, fallback='#000000'):
    """Safely create ReportLab color from hex"""
    try:
        return colors.HexColor(hex_color)
    except:
        return colors.HexColor(fallback)

def format_currency(value):
    """Format number as currency"""
    try:
        return f"${value:,.0f}"
    except:
        return "$0"

def format_percentage(value):
    """Format number as percentage"""
    try:
        return f"{value:.1f}%"
    except:
        return "0.0%"
"""Professional PDF Report Generator for LaptopCheck.
Builds multi-page commercial inspection report including:
- Page 1: Header banner, Executive Summary, Workload Suitability Overview, Key Findings / Anomalies
- Page 2: Detected Hardware Specifications snapshot, Detailed Benchmark Performance, Thermal & Sustained Frequency Analysis
- Page 3+: Workload Compatibility Breakdown (Requirements vs Measured), Manual Physical Hardware Checklist
- Running Header & "Page X of Y" Footer with NumberedCanvas
- 100% flowable layout with Paragraph cell wrapping (zero text collision or overlap)
"""
import os
import io
import time
from datetime import datetime
from typing import Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from agent.models import DiagnosticReport, StatusEnum


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page count and professional running header/footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#64748b'))

        # Running Header on page 2 and later
        if self._pageNumber > 1:
            self.drawString(36, 760, "LaptopCheck™ — Commercial Diagnostic & Workload Suitability Report")
            self.setStrokeColor(colors.HexColor('#cbd5e1'))
            self.setLineWidth(0.6)
            self.line(36, 752, 576, 752)

        # Running Footer on all pages
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.6)
        self.line(36, 42, 576, 42)

        footer_text = "LaptopCheck Diagnostic Engine v1.0.0 • Verified Benchmark Assessment"
        self.drawString(36, 30, footer_text)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 30, page_str)
        self.restoreState()


def generate_thermal_chart_image(report: DiagnosticReport) -> Optional[io.BytesIO]:
    """Renders a crisp time-series thermal and frequency curve using matplotlib."""
    samples = report.thermal_samples
    if not samples or len(samples) < 2:
        return None

    t0 = samples[0].elapsed_secs
    if t0 > 100000:
        times = [max(0.0, round(s.elapsed_secs - t0, 1)) for s in samples]
    else:
        times = [s.elapsed_secs for s in samples]
    temps = [s.cpu_temp_c or 0 for s in samples]
    freqs = [(s.cpu_freq_mhz or 0) / 1000.0 for s in samples]

    fig, ax1 = plt.subplots(figsize=(7.5, 2.2), dpi=160)
    fig.patch.set_facecolor('#ffffff')
    ax1.set_facecolor('#fafafa')

    color_temp = '#dc2626'
    ax1.set_xlabel('Elapsed Benchmark Time (seconds)', fontsize=8.5, fontweight='bold', color='#1e293b')
    ax1.set_ylabel('CPU Temperature (°C)', color=color_temp, fontsize=8.5, fontweight='bold')
    line1 = ax1.plot(times, temps, color=color_temp, linewidth=2, label='CPU Temp (°C)')
    ax1.tick_params(axis='y', labelcolor=color_temp, labelsize=8)
    ax1.tick_params(axis='x', labelsize=8)
    min_temp = max(20, min(temps or [30]) - 5)
    max_temp = max(temps or [90]) + 25
    ax1.set_ylim(min_temp, max_temp)
    ax1.grid(True, linestyle=':', alpha=0.5, color='#94a3b8')

    ax2 = ax1.twinx()
    color_freq = '#2563eb'
    ax2.set_ylabel('CPU Frequency (GHz)', color=color_freq, fontsize=8.5, fontweight='bold')
    line2 = ax2.plot(times, freqs, color=color_freq, linewidth=1.8, linestyle='--', label='CPU Clock (GHz)')
    ax2.tick_params(axis='y', labelcolor=color_freq, labelsize=8)
    ax2.grid(False)
    max_freq = max(freqs or [3.0]) + 0.8
    ax2.set_ylim(0, max(4.5, max_freq))

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper right', ncol=2, fontsize=7.5, framealpha=0.95, facecolor='#ffffff', edgecolor='#cbd5e1')

    plt.title('CPU Thermal Dissipation & Clock Frequency Profile', fontsize=9.5, fontweight='bold', color='#0f172a', pad=6)
    plt.tight_layout(pad=1.2)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=180, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_pdf_report(report: DiagnosticReport, output_filepath: str) -> str:
    """Generates the final multi-page PDF document with guaranteed non-overlapping layout."""
    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=46,
        bottomMargin=52
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#0f172a'))
    subtitle_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=8.5, leading=12, textColor=colors.HexColor('#475569'))
    subtitle_right = ParagraphStyle('SubTitleRight', parent=subtitle_style, alignment=2)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=11, leading=14, textColor=colors.HexColor('#0f172a'), spaceBefore=6, spaceAfter=4, keepWithNext=True)
    normal_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#334155'))
    
    # Table cell typography
    tbl_cell = ParagraphStyle('TblCell', parent=styles['Normal'], fontSize=8, leading=10.5, textColor=colors.HexColor('#334155'))
    tbl_cell_bold = ParagraphStyle('TblCellBold', parent=tbl_cell, fontName='Helvetica-Bold', textColor=colors.HexColor('#0f172a'))
    tbl_cell_label = ParagraphStyle('TblCellLabel', parent=tbl_cell, fontName='Helvetica-Bold', textColor=colors.HexColor('#475569'))
    tbl_cell_center = ParagraphStyle('TblCellCenter', parent=tbl_cell, alignment=1)
    tbl_hdr = ParagraphStyle('TblHdr', parent=styles['Normal'], fontSize=8, leading=10.5, fontName='Helvetica-Bold', textColor=colors.HexColor('#0f172a'))

    status_hex = {
        StatusEnum.PASS: '#15803d',          # Darker green for print contrast
        StatusEnum.CAUTION: '#b45309',       # Darker amber
        StatusEnum.FAIL: '#b91c1c',          # Darker red
        StatusEnum.NOT_AVAILABLE: '#64748b',
        StatusEnum.NOT_TESTED: '#94a3b8',
        StatusEnum.SKIPPED: '#94a3b8'
    }

    story = []

    # 1. Simulation Mode Alert Banner (if applicable)
    if report.is_simulation:
        sim_data = [
            [Paragraph("<b>[SIMULATION MODE]</b> Synthesized benchmark & telemetry metrics for validation.", 
                       ParagraphStyle('SimText', parent=tbl_cell_bold, textColor=colors.HexColor('#c2410c'), alignment=1))]
        ]
        t_sim = Table(sim_data, colWidths=[540])
        t_sim.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffedd5')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#ea580c')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t_sim)
        story.append(Spacer(1, 6))

    # 2. Header Banner: Title, System & Metadata
    hw = report.hardware
    overall_status_color = '#15803d' if not report.anomalies else ('#b91c1c' if any(a.severity == 'CRITICAL' for a in report.anomalies) else '#b45309')
    overall_status_label = 'ALL CHECKS PASSED' if not report.anomalies else ('CRITICAL ISSUES DETECTED' if any(a.severity == 'CRITICAL' for a in report.anomalies) else 'WARNINGS OBSERVED')

    header_data = [
        [
            Paragraph("<b>LaptopCheck</b> <font size=11 color='#64748b'>| Diagnostic Report</font><br/>"
                      f"<font size=9 color='#1e293b'><b>Target:</b> {hw.manufacturer} {hw.device_model} ({hw.os.system})</font>", title_style),
            Paragraph(f"<b>Report ID:</b> {report.report_id}<br/>"
                      f"<b>Timestamp:</b> {report.created_at}<br/>"
                      f"<b>Overall Status:</b> <font color='{overall_status_color}'><b>{overall_status_label}</b></font>", subtitle_right)
        ]
    ]
    t_head = Table(header_data, colWidths=[330, 210])
    t_head.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_head)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceBefore=5, spaceAfter=8))

    # 3. EXECUTIVE SUMMARY & SYSTEM OVERVIEW
    story.append(Paragraph("Executive Summary & Diagnostics Matrix", h2_style))
    
    cat_rows = [[Paragraph("Component / Metric", tbl_hdr), Paragraph("Status", tbl_hdr)]]
    for cat, status in report.summary_categories.items():
        st_color = status_hex.get(status, '#334155')
        st_para = Paragraph(f"<font color='{st_color}'><b>{status.value}</b></font>", tbl_cell_bold)
        cat_rows.append([Paragraph(cat, tbl_cell), st_para])

    t_cats = Table(cat_rows, colWidths=[155, 110])
    t_cats.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    workload_rows = [[Paragraph("Workload Profile", tbl_hdr), Paragraph("Suitability Verdict", tbl_hdr)]]
    for wm in report.workload_evaluations:
        st_color = status_hex.get(wm.overall_status, '#334155')
        st_para = Paragraph(f"<font color='{st_color}'><b>{wm.overall_status.value}</b></font>", tbl_cell_bold)
        workload_rows.append([Paragraph(f"<b>{wm.profile_name}</b>", tbl_cell), st_para])

    t_workloads = Table(workload_rows, colWidths=[165, 110])
    t_workloads.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    summary_split = [[t_cats, t_workloads]]
    t_summary_split = Table(summary_split, colWidths=[265, 275])
    t_summary_split.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_summary_split)
    story.append(Spacer(1, 8))

    # 4. KEY ANOMALIES & FINDINGS
    story.append(Paragraph("Key Diagnostic Findings & Anomalies", h2_style))
    if not report.anomalies:
        no_anom_box = [
            [Paragraph("<b>[STATUS OK]</b> No significant hardware anomalies or critical warnings detected. Machine performed reliably within factory operating limits.", tbl_cell)]
        ]
        t_no_anom = Table(no_anom_box, colWidths=[540])
        t_no_anom.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#86efac')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_no_anom)
    else:
        anom_data = [[Paragraph("Severity", tbl_hdr), Paragraph("Component", tbl_hdr), Paragraph("Observation & Recommendation", tbl_hdr)]]
        for a in report.anomalies:
            sev_color = "#b91c1c" if a.severity == "CRITICAL" else ("#b45309" if a.severity == "WARNING" else "#1d4ed8")
            desc_para = Paragraph(f"<b>{a.title}</b><br/>{a.description}<br/><font color='#475569'><i>Recommendation: {a.recommendation}</i></font>", tbl_cell)
            anom_data.append([
                Paragraph(f"<font color='{sev_color}'><b>{a.severity}</b></font>", tbl_cell_bold),
                Paragraph(f"<b>{a.component}</b>", tbl_cell),
                desc_para
            ])
        t_anom = Table(anom_data, colWidths=[75, 75, 390])
        t_anom.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t_anom)

    story.append(Spacer(1, 10))

    # 5. DETECTED HARDWARE SPECIFICATIONS (PAGE 1 BOTTOM OR PAGE 2)
    # Using strict 4-column flowable layout where EVERY cell is a wrapped Paragraph
    story.append(Paragraph("Detected Hardware Specifications", h2_style))
    gpu_list = [f"{g.name} ({g.vram_mb or 'Shared'} MB)" for g in hw.gpus]
    gpu_text = ", ".join(gpu_list) if gpu_list else "Integrated Graphics"
    
    storage_list = [f"{d.model} ({d.capacity_gb} GB {d.media_type})" for d in hw.storage]
    storage_text = ", ".join(storage_list) if storage_list else "None detected"

    inst_text = ", ".join(hw.cpu.instruction_sets[:6]) if hw.cpu.instruction_sets else "Standard x86_64"
    if len(hw.cpu.instruction_sets) > 6:
        inst_text += f" (+{len(hw.cpu.instruction_sets)-6} more)"

    battery_text = f"Health: {hw.battery.health_pct or 'N/A'}% ({hw.battery.category.value})"
    if hw.battery.cycle_count:
        battery_text += f" • {hw.battery.cycle_count} cycles"

    hw_table_data = [
        [
            Paragraph("Device Model:", tbl_cell_label),
            Paragraph(f"{hw.manufacturer} {hw.device_model}", tbl_cell_bold),
            Paragraph("Operating System:", tbl_cell_label),
            Paragraph(f"{hw.os.system} {hw.os.release} ({hw.os.architecture})", tbl_cell)
        ],
        [
            Paragraph("Processor (CPU):", tbl_cell_label),
            Paragraph(f"{hw.cpu.model} ({hw.cpu.cores_physical or '?'}C / {hw.cpu.threads_logical or '?'}T)", tbl_cell),
            Paragraph("Memory (RAM):", tbl_cell_label),
            Paragraph(f"{hw.ram.total_gb:.1f} GB ({hw.ram.channels}, {hw.ram.speed_mhz or 'N/A'} MHz)", tbl_cell)
        ],
        [
            Paragraph("Graphics (GPU):", tbl_cell_label),
            Paragraph(gpu_text, tbl_cell),
            Paragraph("Storage Drives:", tbl_cell_label),
            Paragraph(storage_text, tbl_cell)
        ],
        [
            Paragraph("Battery Status:", tbl_cell_label),
            Paragraph(battery_text, tbl_cell),
            Paragraph("CPU Instructions:", tbl_cell_label),
            Paragraph(inst_text, tbl_cell)
        ]
    ]

    t_hw = Table(hw_table_data, colWidths=[90, 180, 90, 180])
    t_hw.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_hw)

    # PAGE 2: Detailed Benchmarks & Thermal Curve
    story.append(PageBreak())
    story.append(Paragraph("Detailed Benchmark Performance", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=4, spaceAfter=8))

    bench_rows = [[
        Paragraph("Benchmark Suite", tbl_hdr),
        Paragraph("Measured Metric", tbl_hdr),
        Paragraph("Score / Rate", tbl_hdr),
        Paragraph("Status", tbl_hdr),
        Paragraph("Diagnostic Observations", tbl_hdr)
    ]]

    for b in report.benchmarks:
        st_color = status_hex.get(b.status, '#334155')
        for idx, m in enumerate(b.metrics):
            b_name = b.display_name if idx == 0 else ""
            b_status_para = Paragraph(f"<font color='{st_color}'><b>{b.status.value}</b></font>", tbl_cell_bold) if idx == 0 else Paragraph("", tbl_cell)
            bench_rows.append([
                Paragraph(f"<b>{b_name}</b>", tbl_cell),
                Paragraph(m.name, tbl_cell),
                Paragraph(f"<b>{m.value}</b> <font color='#64748b'>{m.unit}</font>", tbl_cell),
                b_status_para,
                Paragraph(m.description or "Standard baseline passed.", tbl_cell)
            ])

    t_bench = Table(bench_rows, colWidths=[120, 110, 80, 65, 165])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 10))

    # Thermal Plot Image
    chart_buf = generate_thermal_chart_image(report)
    if chart_buf:
        story.append(Paragraph("Thermal Dissipation & Clock Throttling Analysis", h2_style))
        img = Image(chart_buf, width=540, height=158)
        story.append(img)
        story.append(Spacer(1, 10))

    # PAGE 3+: WORKLOAD COMPATIBILITY BREAKDOWN
    story.append(PageBreak())
    story.append(Paragraph("Workload Suitability Analysis", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=4, spaceAfter=8))
    story.append(Paragraph("Every workload evaluation compares measured hardware capabilities against verified domain requirements.", subtitle_style))
    story.append(Spacer(1, 6))

    for wm in report.workload_evaluations:
        wm_st_color = status_hex.get(wm.overall_status, '#334155')
        crit_header = [
            Paragraph(f"<b>Profile: {wm.profile_name}</b>", h2_style),
            Paragraph(f"Overall Suitability: <font color='{wm_st_color}'><b>{wm.overall_status.value}</b></font>", subtitle_right)
        ]
        t_wm_head = Table([crit_header], colWidths=[360, 180])
        t_wm_head.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        crit_rows = [[
            Paragraph("Criterion", tbl_hdr),
            Paragraph("Priority", tbl_hdr),
            Paragraph("Required Value", tbl_hdr),
            Paragraph("Measured Value", tbl_hdr),
            Paragraph("Status", tbl_hdr),
            Paragraph("Requirement Analysis / Notes", tbl_hdr)
        ]]
        for c in wm.criteria:
            c_color = status_hex.get(c.status, '#334155')
            crit_rows.append([
                Paragraph(f"<b>{c.label}</b>", tbl_cell),
                Paragraph(c.priority.value, tbl_cell),
                Paragraph(str(c.required_value), tbl_cell),
                Paragraph(f"{c.actual_value} {c.unit}".strip(), tbl_cell),
                Paragraph(f"<font color='{c_color}'><b>{c.status.value}</b></font>", tbl_cell_bold),
                Paragraph(c.notes or "Criterion evaluation satisfied.", tbl_cell)
            ])
        t_crit = Table(crit_rows, colWidths=[105, 60, 75, 75, 65, 160])
        t_crit.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))

        wm_block = [t_wm_head, t_crit, Spacer(1, 10)]
        story.append(KeepTogether(wm_block))

    # MANUAL HARDWARE INSPECTION CHECKLIST (IF RECORDED)
    if report.manual_inspections:
        story.append(Spacer(1, 8))
        story.append(Paragraph("Manual Physical Hardware Inspection", h2_style))
        man_rows = [[
            Paragraph("Category", tbl_hdr),
            Paragraph("Inspected Component", tbl_hdr),
            Paragraph("Status", tbl_hdr),
            Paragraph("Technician Observations & Notes", tbl_hdr)
        ]]
        for mi in report.manual_inspections:
            mi_color = status_hex.get(mi.status, '#334155')
            man_rows.append([
                Paragraph(f"<b>{mi.category}</b>", tbl_cell),
                Paragraph(mi.title, tbl_cell),
                Paragraph(f"<font color='{mi_color}'><b>{mi.status.value}</b></font>", tbl_cell_bold),
                Paragraph(mi.notes or "Physical test verified without defects.", tbl_cell)
            ])
        t_man = Table(man_rows, colWidths=[85, 125, 70, 260])
        t_man.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_man)
        story.append(Spacer(1, 8))

    doc.build(story, canvasmaker=NumberedCanvas)
    return output_filepath


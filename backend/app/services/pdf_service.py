import os
from datetime import datetime
from typing import Dict, List
from jinja2 import Template
import subprocess
import tempfile


PDF_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #1a1a2e; font-size: 12px; line-height: 1.6; }

  .header { background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0a2540 100%); color: white; padding: 40px; text-align: center; }
  .header h1 { font-size: 32px; margin-bottom: 8px; letter-spacing: 2px; }
  .header .subtitle { font-size: 14px; opacity: 0.8; }
  .header .scan-info { margin-top: 20px; display: flex; justify-content: center; gap: 40px; }
  .header .scan-info div { text-align: center; }
  .header .scan-info .label { font-size: 10px; text-transform: uppercase; opacity: 0.6; letter-spacing: 1px; }
  .header .scan-info .value { font-size: 18px; font-weight: bold; }

  .content { padding: 30px 40px; }
  .section { margin-bottom: 30px; }
  .section-title { font-size: 18px; font-weight: bold; color: #0a2540; border-bottom: 2px solid #0a2540; padding-bottom: 6px; margin-bottom: 15px; }

  .risk-badge { display: inline-block; padding: 8px 20px; border-radius: 6px; font-size: 24px; font-weight: bold; color: white; }
  .risk-critical { background: #dc2626; }
  .risk-high { background: #ea580c; }
  .risk-medium { background: #d97706; }
  .risk-low { background: #16a34a; }
  .risk-minimal { background: #059669; }

  .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
  .stat-card { background: #f1f5f9; padding: 15px; border-radius: 8px; text-align: center; }
  .stat-card .number { font-size: 28px; font-weight: bold; color: #0a2540; }
  .stat-card .label { font-size: 10px; text-transform: uppercase; color: #64748b; letter-spacing: 1px; }

  .summary-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
  .summary-box p { font-size: 13px; line-height: 1.8; }

  table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
  th { background: #0a2540; color: white; padding: 10px 12px; text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }
  td { padding: 8px 12px; border-bottom: 1px solid #e2e8f0; font-size: 11px; }
  tr:nth-child(even) { background: #f8fafc; }

  .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }
  .tag-critical { background: #fecaca; color: #dc2626; }
  .tag-high { background: #fed7aa; color: #ea580c; }
  .tag-medium { background: #fef3c7; color: #d97706; }
  .tag-low { background: #dcfce7; color: #16a34a; }

  .recommendation { background: #f8fafc; border-left: 4px solid #0a2540; padding: 12px 16px; margin-bottom: 12px; border-radius: 0 6px 6px 0; }
  .recommendation .title { font-weight: bold; font-size: 13px; margin-bottom: 4px; }
  .recommendation .desc { font-size: 11px; color: #475569; }

  .footer { text-align: center; padding: 20px 40px; color: #94a3b8; font-size: 10px; border-top: 1px solid #e2e8f0; }
</style>
</head>
<body>
<div class="header">
  <h1>ScanGuard AI</h1>
  <div class="subtitle">Network Security Assessment Report</div>
  <div class="scan-info">
    <div><div class="label">Target</div><div class="value">{{ target }}</div></div>
    <div><div class="label">Scan Date</div><div class="value">{{ scan_date }}</div></div>
    <div><div class="label">Scan Type</div><div class="value">{{ scan_type }}</div></div>
    <div><div class="label">Risk Score</div><div class="value">{{ risk_score }}/100</div></div>
  </div>
</div>

<div class="content">
  <div class="section">
    <div class="section-title">Risk Assessment</div>
    <div style="text-align:center; margin-bottom:20px;">
      <span class="risk-badge risk-{{ risk_label }}">{{ risk_score }} — {{ risk_label | upper }}</span>
    </div>
    <div class="stats-grid">
      <div class="stat-card"><div class="number">{{ total_ports }}</div><div class="label">Total Scanned</div></div>
      <div class="stat-card"><div class="number" style="color:#16a34a;">{{ open_ports }}</div><div class="label">Open Ports</div></div>
      <div class="stat-card"><div class="number" style="color:#dc2626;">{{ high_risk_count }}</div><div class="label">High Risk</div></div>
      <div class="stat-card"><div class="number" style="color:#d97706;">{{ outdated_count }}</div><div class="label">Outdated</div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Executive Summary</div>
    <div class="summary-box"><p>{{ ai_summary }}</p></div>
  </div>

  <div class="section">
    <div class="section-title">Open Port Analysis</div>
    <table>
      <thead>
        <tr><th>Port</th><th>Service</th><th>Software</th><th>Risk</th><th>AI Explanation</th></tr>
      </thead>
      <tbody>
        {% for port in port_details %}
        <tr>
          <td><strong>{{ port.port_number }}/{{ port.protocol }}</strong></td>
          <td>{{ port.service or 'Unknown' }}</td>
          <td>{{ port.banner or 'N/A' }}</td>
          <td><span class="tag tag-{{ port.risk_level }}">{{ port.risk_level | upper }}</span></td>
          <td>{{ port.ai_explanation[:120] }}{% if port.ai_explanation|length > 120 %}...{% endif %}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <div class="section">
    <div class="section-title">Security Recommendations</div>
    {% for rec in recommendations %}
    <div class="recommendation">
      <div class="title">{{ rec.title }} <span class="tag tag-{{ rec.severity }}">{{ rec.severity | upper }}</span></div>
      <div class="desc">{{ rec.description }}<br><em>Action: {{ rec.action }}</em></div>
    </div>
    {% endfor %}
  </div>
</div>

<div class="footer">
  Generated by ScanGuard AI — {{ generated_at }} — Confidential Security Report
</div>
</body>
</html>
"""


def generate_pdf_report(
    scan_data: Dict,
    ports: List[Dict],
    ai_summary: str,
    recommendations: List[Dict],
    output_path: str,
) -> str:
    """Generate PDF report from scan data."""
    open_ports_list = [p for p in ports if p["state"] == "open"]
    high_risk_count = len([p for p in open_ports_list if p.get("risk_level") in ("high", "critical")])
    outdated_count = len([p for p in open_ports_list if p.get("is_outdated")])

    from app.services.nmap_parser import calculate_risk_score, get_risk_label
    risk_score = scan_data.get("risk_score", calculate_risk_score(ports))
    risk_label = get_risk_label(risk_score)

    template = Template(PDF_TEMPLATE)
    html_content = template.render(
        target=scan_data.get("target", "Unknown"),
        scan_date=scan_data.get("scan_date", datetime.now().strftime("%Y-%m-%d")),
        scan_type=scan_data.get("scan_type", "Full"),
        risk_score=risk_score,
        risk_label=risk_label,
        total_ports=len(ports),
        open_ports=len(open_ports_list),
        high_risk_count=high_risk_count,
        outdated_count=outdated_count,
        ai_summary=ai_summary or "No AI summary available.",
        port_details=[p for p in open_ports_list],
        recommendations=recommendations or [],
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    )

    html_path = output_path.replace(".pdf", ".html")
    with open(html_path, "w") as f:
        f.write(html_content)

    try:
        result = subprocess.run(
            ["weasyprint", html_path, output_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            raise Exception(f"weasyprint error: {result.stderr}")
    except FileNotFoundError:
        with open(output_path.replace(".pdf", "_report.html"), "w") as f:
            f.write(html_content)
        return output_path.replace(".pdf", "_report.html")
    finally:
        if os.path.exists(html_path):
            os.remove(html_path)

    return output_path

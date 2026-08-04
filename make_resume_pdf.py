import os
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem, KeepTogether,
)

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resume.pdf")

INK = colors.HexColor("#171717")
INK_DIM = colors.HexColor("#444444")
LINE = colors.HexColor("#CCCCCC")

styles = {
    "name": ParagraphStyle("name", fontName="Times-Bold", fontSize=21, textColor=INK, leading=22, spaceAfter=0),
    "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=9.1, textColor=INK_DIM, spaceAfter=4),
    "h2": ParagraphStyle("h2", fontName="Times-Bold", fontSize=11, textColor=INK, spaceBefore=7, spaceAfter=2,
                          leading=13),
    "summary": ParagraphStyle("summary", fontName="Helvetica", fontSize=9.4, textColor=INK, leading=12.3, alignment=TA_LEFT),
    "role_title": ParagraphStyle("role_title", fontName="Helvetica-Bold", fontSize=10.1, textColor=INK, spaceBefore=5, leading=11.5),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9, textColor=INK, leading=11.3, spaceAfter=1),
    "note": ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=8.4, textColor=colors.HexColor("#666666"), spaceBefore=2, leading=10.5),
    "skill": ParagraphStyle("skill", fontName="Helvetica", fontSize=9.1, textColor=INK, leading=12, spaceAfter=2),
    "cred": ParagraphStyle("cred", fontName="Helvetica", fontSize=9, textColor=INK, leading=11.5),
}

def h2(text):
    return [
        Paragraph(text.upper(), styles["h2"]),
        HRFlowable(width="100%", thickness=0.7, color=LINE, spaceAfter=4),
    ]

def role_header(title, org, dates):
    t = Table(
        [[Paragraph(f'<b>{title}</b> <font color="#444444">— {org}</font>', styles["role_title"]),
          Paragraph(f'<i>{dates}</i>', ParagraphStyle("date", fontName="Helvetica-Oblique", fontSize=9.3,
                                                       textColor=colors.HexColor("#555555"), alignment=2))]],
        colWidths=[4.6 * inch, 2.2 * inch],
    )
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t

def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(i, styles["bullet"]), leftIndent=14, bulletColor=INK) for i in items],
        bulletType="bullet", start="•", leftIndent=14, bulletFontSize=9,
    )

doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=LETTER,
    topMargin=0.45 * inch, bottomMargin=0.45 * inch,
    leftMargin=0.7 * inch, rightMargin=0.7 * inch,
    title="Mustafa F. Sunka — Resume",
)

story = []
story.append(Paragraph("Mustafa F. Sunka", styles["name"]))
story.append(Paragraph("Frisco, TX &nbsp;&middot;&nbsp; 225-747-5703 &nbsp;&middot;&nbsp; msunka@me.com", styles["contact"]))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#999999"), spaceAfter=10))

story += h2("Professional Summary")
story.append(Paragraph(
    "Senior DevSecOps Engineer with 8+ years designing and operating highly available cloud infrastructure "
    "across AWS, Azure, and GCP in regulated, high-compliance environments. Proven record defining SLOs/SLIs, "
    "leading incident response, and driving IaC-based automation that reduced infrastructure provisioning by "
    "75% and system downtime by 75%. Recognized with the Global Circle of Excellence for building resilient, "
    "observable infrastructure at scale — with deep experience mentoring DevOps/DevSecOps teams and "
    "partnering cross-functionally to eliminate operational toil.", styles["summary"]))

story += h2("Experience")
story.append(role_header("Senior DevSecOps Engineer", "Global Payments, Dallas, TX", "Feb 2013 – Present"))
story.append(bullets([
    "Defined and enforced SLOs and SLIs for 20+ critical payment services, achieving a sustained 99.9% availability rate across hybrid cloud environments spanning AWS, Azure, and GCP.",
    "Led incident detection, root cause analysis, and production resolution for a platform processing millions of daily transactions — reducing mean time to detect (MTTD) by 40% via Splunk SIEM and LogicMonitor alerting.",
    "Drove IaC adoption across 100% of cloud provisioning by engineering reusable Terraform modules with policy-as-code guardrails, cutting infrastructure provisioning time from days to hours and deployment cycle time by 75%.",
    "Architected disaster recovery playbooks and runbooks achieving a 2-hour RTO, reducing mean time to recover by 65% compared to pre-automation manual processes.",
    "Designed and maintained observability stack — integrating LogicMonitor, Application Insights, and Splunk — providing continuous visibility into infrastructure health across 500+ monitored endpoints and reducing downtime by 75%.",
    "Ensured 100% PCI DSS compliance across 3 consecutive audit cycles by automating evidence collection and embedding 40+ security controls directly into IaC pipelines.",
    "Spearheaded 3 major cloud migrations to Azure and GCP, maintaining 99.9% uptime and zero data loss events across all cutovers.",
    "Embedded SAST/DAST scanning (Snyk, Wiz) and secrets management (HashiCorp Vault, GCP Secret Manager, Azure Key Vault) into CI/CD pipelines, eliminating credential sprawl and hardcoded secrets across all environments.",
    "Mentored 4 junior engineers through structured 1:1 coaching programs, contributing to 1 internal promotion and reducing team onboarding time by 30%.",
]))
story.append(Paragraph(
    "Previous roles at Global Payments: DevOps Engineer · Data Analyst · Account Manager · Technical Support Representative",
    styles["note"]))

story.append(role_header("Operations Manager", "Best Buy, Hammond, LA", "2005 – 2013"))
story.append(bullets([
    "Increased customer satisfaction scores by 18% and reduced staff attrition by restructuring performance evaluation and mentoring processes for a 20-person team across a $10M+ revenue location.",
]))

story += h2("Technical Skills")
skill_lines = [
    ("Cloud Platforms", "AWS, Microsoft Azure, Google Cloud Platform (GCP) — hybrid and multi-cloud environments"),
    ("SRE &amp; Reliability", "SLO/SLI definition · Incident Management · RCA · Disaster Recovery · Chaos Engineering · Runbook Authoring"),
    ("IaC &amp; Automation", "Terraform (policy-as-code, reusable modules) · ARM Templates · Ansible · PowerShell · Python · Bash"),
    ("Containers &amp; CI/CD", "Kubernetes (GKE) · Docker · Jenkins · Azure DevOps · Git · GitHub"),
    ("Observability", "Splunk · LogicMonitor · ThousandEyes · Application Insights · CloudWatch · Prometheus/Grafana"),
    ("Security &amp; Compliance", "Snyk · Wiz · HashiCorp Vault · PCI DSS · Azure Key Vault · GCP Secret Manager"),
]
for label, val in skill_lines:
    story.append(Paragraph(f'<b>{label}:</b> {val}', styles["skill"]))

story += h2("Certifications")
cert_table = Table([
    [Paragraph("Microsoft Certified: Azure Administrator Associate", styles["cred"]),
     Paragraph("Google Cloud Foundational", styles["cred"])],
    [Paragraph("Microsoft Azure Fundamentals", styles["cred"]),
     Paragraph("SAS Institute Graduate Certificate — BI &amp; Data Mining", styles["cred"])],
], colWidths=[3.4 * inch, 3.4 * inch])
cert_table.setStyle(TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
]))
story.append(cert_table)

edu_table = Table([
    [Paragraph("M.S., Information Technology Management — University of Texas at Dallas, 2018", styles["cred"]),
     Paragraph("B.A., Mass Communication — Louisiana State University, 2010", styles["cred"])],
], colWidths=[3.4 * inch, 3.4 * inch])
edu_table.setStyle(TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
]))
story.append(KeepTogether([*h2("Education"), edu_table]))

doc.build(story)
print("done")

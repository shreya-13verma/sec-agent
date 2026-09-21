import io
import csv
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from backend.app.models.host import Host, HostMissingErrata
from backend.app.models.compliance import ComplianceFramework, ComplianceScan, ComplianceFinding
from backend.app.models.remediation import RemediationPlan
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ReportService:
    """
    Generates audit-ready compliance reports and executive summaries in JSON, CSV, and PDF formats.
    """

    def generate_executive_data(self, db: Session, framework_id: Optional[int] = None) -> Dict[str, Any]:
        hosts = db.query(Host).options(
            joinedload(Host.missing_errata).joinedload(HostMissingErrata.errata)
        ).all()

        total_hosts = len(hosts)
        avg_score = round(sum(h.compliance_score for h in hosts) / total_hosts, 1) if total_hosts > 0 else 0.0
        crit_hosts = sum(1 for h in hosts if h.compliance_status == "CRITICAL" or h.critical_errata_count > 0)

        # Framework summaries
        fw_query = db.query(ComplianceFramework)
        if framework_id:
            fw_query = fw_query.filter(ComplianceFramework.id == framework_id)
        frameworks = fw_query.all()

        fw_summaries = []
        for fw in frameworks:
            scans = db.query(ComplianceScan).filter(ComplianceScan.framework_id == fw.id).all()
            latest_scan = db.query(ComplianceScan).filter(ComplianceScan.framework_id == fw.id).order_by(ComplianceScan.id.desc()).first()
            latest_score = latest_scan.overall_score if latest_scan else 0.0
            
            compliant_count = sum(1 for h in hosts if h.compliance_score >= 85.0)
            non_compliant_count = total_hosts - compliant_count

            fw_summaries.append({
                "framework_name": fw.name,
                "framework_code": fw.code,
                "total_scans": len(scans),
                "latest_score": latest_score,
                "hosts_compliant_count": compliant_count,
                "hosts_non_compliant_count": non_compliant_count
            })

        host_details = []
        for h in hosts:
            cves = [me.errata.cve_identifier for me in h.missing_errata if me.errata and me.errata.cve_identifier]
            host_details.append({
                "hostname": h.hostname,
                "ip_address": h.ip_address,
                "os_info": f"{h.os_family} {h.os_version}",
                "compliance_status": h.compliance_status,
                "compliance_score": h.compliance_score,
                "critical_errata_count": h.critical_errata_count,
                "missing_cves": cves
            })

        return {
            "generated_at": datetime.now(timezone.utc),
            "fleet_total_hosts": total_hosts,
            "fleet_average_score": avg_score,
            "fleet_critical_hosts_count": crit_hosts,
            "framework_summaries": fw_summaries,
            "host_details": host_details
        }

    def generate_csv_report(self, db: Session, framework_id: Optional[int] = None) -> str:
        data = self.generate_executive_data(db, framework_id)
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["SUSE MLM Security & Compliance Audit Report"])
        writer.writerow(["Generated At", data["generated_at"].isoformat()])
        writer.writerow(["Fleet Total Hosts", data["fleet_total_hosts"]])
        writer.writerow(["Fleet Average Score (%)", data["fleet_average_score"]])
        writer.writerow(["Fleet Critical Hosts Count", data["fleet_critical_hosts_count"]])
        writer.writerow([])

        writer.writerow(["--- Framework Posture Summary ---"])
        writer.writerow(["Framework Name", "Code", "Total Scans", "Latest Score (%)", "Compliant Hosts", "Non-Compliant Hosts"])
        for fw in data["framework_summaries"]:
            writer.writerow([
                fw["framework_name"],
                fw["framework_code"],
                fw["total_scans"],
                fw["latest_score"],
                fw["hosts_compliant_count"],
                fw["hosts_non_compliant_count"]
            ])
        writer.writerow([])

        writer.writerow(["--- Host Inventory & Compliance Details ---"])
        writer.writerow(["Hostname", "IP Address", "OS", "Status", "Score (%)", "Critical Errata Count", "Missing CVEs"])
        for h in data["host_details"]:
            writer.writerow([
                h["hostname"],
                h["ip_address"],
                h["os_info"],
                h["compliance_status"],
                h["compliance_score"],
                h["critical_errata_count"],
                "; ".join(h["missing_cves"]) if h["missing_cves"] else "None"
            ])

        return output.getvalue()

    def generate_pdf_report(self, db: Session, framework_id: Optional[int] = None) -> bytes:
        data = self.generate_executive_data(db, framework_id)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a")
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#475569")
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6
        )

        elements = []
        elements.append(Paragraph("SUSE Multi-Linux Manager — Security & Compliance Audit Dossier", title_style))
        elements.append(Paragraph(f"Generated: {data['generated_at'].strftime('%Y-%m-%d %H:%M:%S UTC')} | Target Endpoint: https://10.0.33.56/rhn/apidoc/index.jsp", subtitle_style))
        elements.append(Spacer(1, 12))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#30BA78"), spaceAfter=12))

        # Executive Metrics Table
        exec_data = [
            ["Fleet Registered Hosts", "Fleet Compliance Average", "Critical Drift / Non-Compliant Hosts"],
            [str(data["fleet_total_hosts"]), f"{data['fleet_average_score']}%", str(data["fleet_critical_hosts_count"])]
        ]
        exec_table = Table(exec_data, colWidths=[180, 180, 180])
        exec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#334155")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ]))
        elements.append(exec_table)
        elements.append(Spacer(1, 14))

        # Framework Posture Section
        elements.append(Paragraph("Regulatory & Hardening Framework Evaluation", h2_style))
        fw_table_data = [["Framework Name", "Code", "Total Scans", "Compliance Score", "Compliant / Non-Compliant"]]
        for fw in data["framework_summaries"]:
            fw_table_data.append([
                fw["framework_name"],
                fw["framework_code"],
                str(fw["total_scans"]),
                f"{fw['latest_score']}%",
                f"{fw['hosts_compliant_count']} / {fw['hosts_non_compliant_count']}"
            ])
        fw_table = Table(fw_table_data, colWidths=[160, 90, 80, 100, 110])
        fw_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        elements.append(fw_table)
        elements.append(Spacer(1, 14))

        # Host Breakdown Section
        elements.append(Paragraph("Host Fleet Posture & Missing CVE Advisories", h2_style))
        host_table_data = [["Hostname", "IP Address", "OS", "Status", "Score", "CVEs"]]
        for h in data["host_details"]:
            host_table_data.append([
                h["hostname"][:24],
                h["ip_address"],
                h["os_info"],
                h["compliance_status"],
                f"{h['compliance_score']}%",
                (", ".join(h["missing_cves"])[:20] if h["missing_cves"] else "None")
            ])
        host_table = Table(host_table_data, colWidths=[130, 90, 90, 85, 55, 90])
        host_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        elements.append(host_table)

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

report_service = ReportService()

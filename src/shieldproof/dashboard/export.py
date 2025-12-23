"""
SHIELDPROOF v2.1 Dashboard Export - Dashboard Export Functions

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

import csv
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional

from ..core import query_receipts, TENANT_ID, VERSION
from ..contract import get_contract, get_contract_milestones
from ..payment import total_paid, total_outstanding
from ..reconcile import reconcile_all, get_waste_summary
from .receipts import emit_dashboard_receipt


def export_dashboard(format: str, output_path: str) -> dict:
    """
    Generate dashboard export (v2.1 API).
    Emit dashboard_receipt.
    Return receipt.

    Args:
        format: Export format ("json" | "html" | "csv")
        output_path: Output file path

    Returns:
        Dashboard receipt
    """
    summary = generate_summary()
    reports = reconcile_all()

    if format == "json":
        export_json(output_path)
    elif format == "csv":
        export_csv(output_path)
    elif format == "html":
        _export_html(output_path, summary, reports)
    else:
        raise ValueError(f"Unsupported format: {format}")

    return emit_dashboard_receipt({
        "export_format": format,
        "output_path": output_path,
        "contract_count": summary.get("total_contracts", 0),
        "total_value_usd": summary.get("total_committed", 0),
        "total_paid_usd": summary.get("total_paid", 0),
        "contracts_over_variance": summary.get("contracts_overpaid", 0) + summary.get("contracts_unverified", 0),
    })


def dashboard_summary() -> dict:
    """
    Generate summary statistics (v2.1 API).

    Returns:
        Summary statistics dict
    """
    return generate_summary()


def contracts_by_status() -> dict:
    """
    Group contracts by variance status (v2.1 API).

    Returns:
        Dict with contracts grouped by status
    """
    reports = reconcile_all()
    result = {
        "on_track": [],
        "overpaid": [],
        "unverified": [],
        "disputed": [],
    }

    for report in reports:
        status = report.get("status", "ON_TRACK")
        if status == "ON_TRACK":
            result["on_track"].append(report)
        elif status == "OVERPAID":
            result["overpaid"].append(report)
        elif status == "UNVERIFIED_PAYMENT":
            result["unverified"].append(report)
        elif status == "DISPUTED":
            result["disputed"].append(report)

    return result


def generate_summary() -> dict:
    """
    Generate aggregate public summary of all contracts (v2.0 API).
    Shows aggregate numbers, not individual contract details.

    Returns:
        Dashboard summary dict
    """
    waste_summary = get_waste_summary()

    summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "version": VERSION,
        "tenant_id": TENANT_ID,
        "total_contracts": waste_summary["total_contracts"],
        "total_committed": waste_summary["total_committed"],
        "total_paid": waste_summary["total_paid"],
        "total_verified": waste_summary["total_verified"],
        "milestones_pending": waste_summary["milestones_pending"],
        "milestones_disputed": waste_summary["milestones_disputed"],
        "waste_identified": waste_summary["waste_identified"],
        "contracts_on_track": waste_summary["contracts_on_track"],
        "contracts_overpaid": waste_summary["contracts_overpaid"],
        "contracts_unverified": waste_summary["contracts_unverified"],
        "contracts_disputed": waste_summary["contracts_disputed"],
        "health_score": _calculate_health_score(waste_summary),
    }

    return summary


def contract_status(contract_id: str) -> dict:
    """
    Get single contract public view.

    Args:
        contract_id: Contract identifier

    Returns:
        Contract status dict (redacted for OPSEC)
    """
    contract = get_contract(contract_id)
    if not contract:
        return {"error": "Contract not found", "contract_id": contract_id}

    milestones = get_contract_milestones(contract_id)

    return {
        "contract_id": contract_id,
        "contractor": contract.get("contractor"),
        "amount_fixed": contract.get("amount_fixed", contract.get("total_value_usd")),
        "amount_paid": total_paid(contract_id),
        "amount_outstanding": total_outstanding(contract_id),
        "milestones": [
            {
                "id": m["id"],
                "status": m.get("status"),
                "amount": m.get("amount"),
            }
            for m in milestones
        ],
        "created_at": contract.get("ts"),
    }


def export_csv(filepath: str) -> None:
    """
    Export dashboard data to CSV.

    Args:
        filepath: Output file path
    """
    reports = reconcile_all()

    with open(filepath, "w", newline="") as f:
        if not reports:
            f.write("No contracts found\n")
            return

        fieldnames = [
            "contract_id",
            "contractor",
            "amount_fixed",
            "amount_paid",
            "status",
            "milestones_total",
            "milestones_verified",
            "milestones_paid",
            "milestones_pending",
            "milestones_disputed",
            "discrepancy",
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for report in reports:
            writer.writerow(report)


def export_json(filepath: str) -> None:
    """
    Export dashboard data to JSON.

    Args:
        filepath: Output file path
    """
    summary = generate_summary()
    reports = reconcile_all()

    data = {
        "summary": summary,
        "contracts": reports,
    }

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def format_currency(amount: float) -> str:
    """Format amount as currency string."""
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.2f}K"
    else:
        return f"${amount:.2f}"


def print_dashboard() -> None:
    """Print dashboard summary to stdout."""
    summary = generate_summary()

    print("\n" + "=" * 60)
    print("SHIELDPROOF v2.1 - PUBLIC AUDIT DASHBOARD")
    print("=" * 60)
    print(f"Generated: {summary['generated_at']}")
    print(f"Health Score: {summary['health_score']}%")
    print("-" * 60)
    print(f"Total Contracts:     {summary['total_contracts']}")
    print(f"Total Committed:     {format_currency(summary['total_committed'])}")
    print(f"Total Paid:          {format_currency(summary['total_paid'])}")
    print(f"Total Verified:      {format_currency(summary['total_verified'])}")
    print("-" * 60)
    print(f"Contracts On Track:  {summary['contracts_on_track']}")
    print(f"Contracts Overpaid:  {summary['contracts_overpaid']}")
    print(f"Contracts Unverified:{summary['contracts_unverified']}")
    print(f"Contracts Disputed:  {summary['contracts_disputed']}")
    print("-" * 60)
    print(f"Milestones Pending:  {summary['milestones_pending']}")
    print(f"Milestones Disputed: {summary['milestones_disputed']}")
    print(f"WASTE IDENTIFIED:    {format_currency(summary['waste_identified'])}")
    print("=" * 60 + "\n")


class DashboardHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for dashboard."""

    def do_GET(self):
        if self.path == "/" or self.path == "/summary":
            summary = generate_summary()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(summary, indent=2).encode())

        elif self.path == "/contracts":
            reports = reconcile_all()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(reports, indent=2).encode())

        elif self.path.startswith("/contract/"):
            contract_id = self.path.split("/contract/")[1]
            status = contract_status(contract_id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(status, indent=2).encode())

        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def serve(port: int = 8080) -> None:
    """
    Serve dashboard as simple HTTP server.

    Args:
        port: Port to serve on (default 8080)
    """
    server = HTTPServer(("", port), DashboardHandler)
    print(f"Dashboard serving at http://localhost:{port}")
    print("Endpoints:")
    print("  GET /         - Summary")
    print("  GET /summary  - Summary")
    print("  GET /contracts - All contract reconciliation reports")
    print("  GET /contract/{id} - Single contract status")
    print("  GET /health   - Health check")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


def check() -> bool:
    """
    Quick health check for dashboard.

    Returns:
        True if dashboard can generate summary
    """
    try:
        summary = generate_summary()
        return "generated_at" in summary and "total_contracts" in summary
    except Exception:
        return False


# === PRIVATE HELPERS ===

def _calculate_health_score(summary: dict) -> float:
    """Calculate an overall health score (0-100) for the portfolio."""
    if summary["total_contracts"] == 0:
        return 100.0

    on_track_pct = summary["contracts_on_track"] / summary["total_contracts"]

    if summary["total_paid"] > 0:
        verified_pct = summary["total_verified"] / summary["total_paid"]
    else:
        verified_pct = 1.0

    dispute_pct = 1 - (summary["contracts_disputed"] / summary["total_contracts"])

    # Weighted average: 50% on_track, 30% verified, 20% no disputes
    score = (on_track_pct * 0.5 + verified_pct * 0.3 + dispute_pct * 0.2) * 100

    return round(score, 1)


def _export_html(filepath: str, summary: dict, reports: list) -> None:
    """Export dashboard to HTML."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>SHIELDPROOF v2.1 Dashboard</title>
    <style>
        body {{ font-family: monospace; padding: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #333; color: white; }}
        .on_track {{ background-color: #90EE90; }}
        .overpaid {{ background-color: #FFB6C1; }}
        .disputed {{ background-color: #FFD700; }}
    </style>
</head>
<body>
    <h1>SHIELDPROOF v2.1 - PUBLIC AUDIT DASHBOARD</h1>
    <p>Generated: {summary['generated_at']}</p>
    <p>Health Score: {summary['health_score']}%</p>

    <h2>Summary</h2>
    <ul>
        <li>Total Contracts: {summary['total_contracts']}</li>
        <li>Total Committed: {format_currency(summary['total_committed'])}</li>
        <li>Total Paid: {format_currency(summary['total_paid'])}</li>
        <li>Waste Identified: {format_currency(summary['waste_identified'])}</li>
    </ul>

    <h2>Contracts</h2>
    <table>
        <tr>
            <th>Contract ID</th>
            <th>Contractor</th>
            <th>Fixed Amount</th>
            <th>Paid</th>
            <th>Status</th>
        </tr>
"""
    for report in reports:
        status_class = report.get('status', 'ON_TRACK').lower().replace('_', '')
        html += f"""        <tr class="{status_class}">
            <td>{report.get('contract_id')}</td>
            <td>{report.get('contractor')}</td>
            <td>{format_currency(report.get('amount_fixed', 0))}</td>
            <td>{format_currency(report.get('amount_paid', 0))}</td>
            <td>{report.get('status')}</td>
        </tr>
"""
    html += """    </table>
</body>
</html>
"""
    with open(filepath, "w") as f:
        f.write(html)

import json
import httpx
from typing import Dict, List, Optional
from app.core.config import settings


async def analyze_port_with_ai(port_data: Dict, scan_context: str = "") -> str:
    """Use OpenRouter AI to explain a port finding in simple language."""
    if not settings.OPENROUTER_API_KEY:
        return generate_fallback_explanation(port_data)

    port_num = port_data.get("port_number", 0)
    protocol = port_data.get("protocol", "tcp")
    service = port_data.get("service", "unknown")
    product = port_data.get("product", "unknown")
    version = port_data.get("version", "unknown")
    state = port_data.get("state", "unknown")
    risk = port_data.get("risk_level", "low")
    is_outdated = port_data.get("is_outdated", False)

    prompt = f"""You are a cybersecurity expert explaining Nmap scan results to a small business owner who is not technical.

Explain this finding in simple, non-technical language:

Port {port_num}/{protocol}
State: {state}
Service: {service}
Software: {product} {version}
Risk Level: {risk}
Outdated: {is_outdated}

Provide:
1. What this port/service does (in plain English)
2. Whether it's a security concern and why
3. What should be done about it

Keep it concise (3-5 sentences). Use everyday analogies when possible.
Do NOT use technical jargon. Write as if explaining to a business owner."""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.3,
                },
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception:
        pass

    return generate_fallback_explanation(port_data)


async def generate_scan_summary(
    scan_data: Dict,
    ports: List[Dict],
    risk_score: int,
) -> str:
    """Generate AI summary of the entire scan."""
    open_ports = [p for p in ports if p["state"] == "open"]
    high_risk = [p for p in open_ports if p.get("risk_level") in ("high", "critical")]
    outdated = [p for p in open_ports if p.get("is_outdated")]

    summary_data = {
        "total_scanned": len(ports),
        "open_count": len(open_ports),
        "high_risk_count": len(high_risk),
        "outdated_count": len(outdated),
        "risk_score": risk_score,
        "services": [
            f"{p['port_number']}/{p['protocol']} - {p.get('service', 'unknown')} ({p.get('product', 'unknown')} {p.get('version', '')})"
            for p in open_ports[:15]
        ],
    }

    if not settings.OPENROUTER_API_KEY:
        return generate_fallback_summary(summary_data)

    prompt = f"""You are a cybersecurity analyst writing for a small business audience.

Scan Results Summary:
- Total ports scanned: {summary_data['total_scanned']}
- Open ports: {summary_data['open_count']}
- High/critical risk findings: {summary_data['high_risk_count']}
- Outdated services: {summary_data['outdated_count']}
- Overall risk score: {summary_data['risk_score']}/100

Open Services:
{chr(10).join(summary_data['services'][:15])}

Write a brief executive summary (4-6 sentences) in plain English:
1. Overall security posture
2. Top concerns
3. Immediate actions needed
Do NOT use technical jargon. Write as if explaining to a business owner."""

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.3,
                },
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception:
        pass

    return generate_fallback_summary(summary_data)


async def generate_recommendations(
    ports: List[Dict],
    risk_score: int,
) -> List[Dict]:
    """Generate security recommendations based on findings."""
    open_ports = [p for p in ports if p["state"] == "open"]
    high_risk = [p for p in open_ports if p.get("risk_level") in ("high", "critical")]
    outdated = [p for p in open_ports if p.get("is_outdated")]

    if not settings.OPENROUTER_API_KEY:
        return generate_fallback_recommendations(open_ports, high_risk, outdated, risk_score)

    prompt = f"""Based on these scan results, provide security recommendations as a JSON array.

Risk Score: {risk_score}/100
Open Ports: {len(open_ports)}
High Risk: {len(high_risk)}
Outdated: {len(outdated)}

Top open services:
{chr(10).join(f"- Port {p['port_number']}: {p.get('service', 'unknown')} ({p.get('product', 'unknown')} {p.get('version', 'unknown')}) [{p.get('risk_level', 'low')}]" for p in open_ports[:10])}

Return a JSON array of recommendations. Each recommendation object must have:
- "title": short title (string)
- "description": explanation (string)
- "severity": "critical", "high", "medium", or "low"
- "category": "firewall", "update", "hardening", "monitoring", or "general"
- "action": specific action to take (string)

Return ONLY valid JSON array, no markdown fences."""

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.3,
                },
            )
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                content = content.removeprefix("```json").removesuffix("```").strip()
                return json.loads(content)
    except Exception:
        pass

    return generate_fallback_recommendations(open_ports, high_risk, outdated, risk_score)


def generate_fallback_explanation(port_data: Dict) -> str:
    port = port_data.get("port_number", 0)
    service = port_data.get("service", "unknown")
    product = port_data.get("product", "")
    version = port_data.get("version", "")
    risk = port_data.get("risk_level", "low")
    is_outdated = port_data.get("is_outdated", False)

    explanations = {
        "http": f"Port {port} runs a web server ({product or 'HTTP'}). This is how your website or web application is served. {'Make sure it is updated and using HTTPS.' if risk in ('high', 'medium') else 'This is generally safe if properly configured.'}",
        "https": f"Port {port} runs a secure web server ({product or 'HTTPS'}). This serves encrypted web traffic. {'Verify the TLS configuration is up to date.' if is_outdated else 'This is a standard, secure service.'}",
        "ssh": f"Port {port} runs SSH ({product or 'Secure Shell'}), used for remote server administration. {'Ensure only authorized users can access this, and consider changing the default port.' if risk in ('high', 'medium') else 'Keep it updated and use key-based authentication.'}",
        "ftp": f"Port {port} runs FTP ({product or 'File Transfer Protocol'}), which sends files in plain text including passwords. 'Consider switching to SFTP or FTPS for secure file transfers.'}",
        "mysql": f"Port {port} runs a MySQL database ({product or 'MySQL'} {version}). 'Databases should NOT be exposed to the internet. Restrict access to trusted IPs only.'}",
        "rdp": f"Port {port} runs Remote Desktop Protocol ({product or 'RDP'}). This allows remote computer access. 'This is a top target for hackers. Use a VPN instead and restrict direct access.'}",
        "smb": f"Port {port} runs SMB ({product or 'Server Message Block'}), used for file sharing on networks. 'This is frequently targeted by ransomware. Restrict access and disable if not needed.'}",
        "telnet": f"Port {port} runs Telnet, which sends all data including passwords in plain text. 'Telnet is extremely insecure. Replace with SSH immediately.'}",
        "smtp": f"Port {port} runs SMTP ({product or 'email server'}). 'Ensure it is configured as a closed relay and requires authentication.'}",
        "dns": f"Port {port} runs DNS ({product or 'Domain Name System'}). 'If this is a public-facing DNS server, ensure it is not configured as an open resolver.'}",
    }

    svc = (service or "").lower()
    if svc in explanations:
        return explanations[svc]

    risk_desc = {
        "critical": "This port has a critical security risk that needs immediate attention.",
        "high": "This port presents a significant security risk.",
        "medium": "This port has some security concerns that should be addressed.",
        "low": "This port appears to have low security risk.",
    }

    text = f"Port {port} runs {service or 'an unknown service'}"
    if product:
        text += f" ({product}"
        if version:
            text += f" {version}"
        text += ")"
    text += f". {risk_desc.get(risk, 'Review this service for security.')}"

    if is_outdated:
        text += " The software version appears outdated and may have known vulnerabilities. Update to the latest version as soon as possible."

    return text


def generate_fallback_summary(data: Dict) -> str:
    parts = []
    score = data["risk_score"]

    if score >= 80:
        parts.append("Your network scan reveals CRITICAL security issues that require immediate attention.")
    elif score >= 60:
        parts.append("Your network scan shows significant security concerns that should be addressed promptly.")
    elif score >= 40:
        parts.append("Your network has moderate security risks that should be reviewed.")
    elif score >= 20:
        parts.append("Your network appears relatively secure with minor areas for improvement.")
    else:
        parts.append("Your network looks well-secured with minimal exposure.")

    if data["high_risk_count"] > 0:
        parts.append(f"We found {data['high_risk_count']} high-risk services that could be exploited by attackers.")
    if data["outdated_count"] > 0:
        parts.append(f"{data['outdated_count']} services are running outdated software with potential known vulnerabilities.")
    if data["open_count"] > 10:
        parts.append(f"With {data['open_count']} open ports, your attack surface is larger than recommended. Consider closing unnecessary services.")

    parts.append(f"Out of {data['total_scanned']} ports scanned, {data['open_count']} are open and accepting connections.")
    return " ".join(parts)


def generate_fallback_recommendations(open_ports, high_risk, outdated, risk_score):
    recommendations = []

    if high_risk:
        recommendations.append({
            "title": "Restrict High-Risk Services",
            "description": f"Found {len(high_risk)} high-risk open services. Use firewall rules to restrict access to only trusted IP addresses.",
            "severity": "critical",
            "category": "firewall",
            "action": "Configure firewall to block unauthorized access to these ports immediately.",
        })

    telnet_ports = [p for p in open_ports if p.get("service", "").lower() == "telnet"]
    if telnet_ports:
        recommendations.append({
            "title": "Disable Telnet Immediately",
            "description": "Telnet transmits all data including passwords in plain text. Replace with SSH.",
            "severity": "critical",
            "category": "hardening",
            "action": "Uninstall telnet server and configure SSH access instead.",
        })

    if outdated:
        recommendations.append({
            "title": "Update Outdated Software",
            "description": f"{len(outdated)} services are running outdated versions that may have known vulnerabilities.",
            "severity": "high",
            "category": "update",
            "action": "Update all identified outdated services to their latest stable versions.",
        })

    db_ports = [p for p in open_ports if p.get("service", "").lower() in ("mysql", "postgresql", "ms-sql-s", "oracle")]
    if db_ports:
        recommendations.append({
            "title": "Restrict Database Access",
            "description": "Database services should not be exposed to the public internet.",
            "severity": "high",
            "category": "firewall",
            "action": "Block all external access to database ports and only allow connections from application servers.",
        })

    rdp_ports = [p for p in open_ports if p.get("port_number") == 3389 or p.get("service", "").lower() == "rdp"]
    if rdp_ports:
        recommendations.append({
            "title": "Secure Remote Desktop Access",
            "description": "RDP is one of the most attacked services. Direct exposure is dangerous.",
            "severity": "high",
            "category": "hardening",
            "action": "Use a VPN for remote access instead of exposing RDP directly. Enable NLA authentication.",
        })

    if len(open_ports) > 10:
        recommendations.append({
            "title": "Reduce Attack Surface",
            "description": "You have many open ports. Each one is a potential entry point for attackers.",
            "severity": "medium",
            "category": "firewall",
            "action": "Audit all open ports and close any that are not essential for your business operations.",
        })

    recommendations.append({
        "title": "Enable Regular Scanning",
        "description": "Schedule regular network scans to detect new vulnerabilities and misconfigurations.",
        "severity": "low",
        "category": "monitoring",
        "action": "Set up automated weekly scans and review results regularly.",
    })

    if risk_score < 40:
        recommendations.append({
            "title": "Maintain Good Security Hygiene",
            "description": "Your current posture is good. Keep it that way with regular maintenance.",
            "severity": "low",
            "category": "general",
            "action": "Continue monitoring, keep software updated, and review access controls quarterly.",
        })

    return recommendations

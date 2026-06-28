"""Sovereignty Report — what data leaves the machine, who gets it."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from visualpy.models import AnalyzedProject

from visualpy.models import SovereigntyReport


def compute_sovereignty_report(project: AnalyzedProject) -> SovereigntyReport:
    """Build a deterministic sovereignty report from project analysis data."""
    external_services: list[dict] = []
    local_ops: set[str] = set()
    credentials_used: list[dict] = []
    data_egress_count = 0

    service_scripts: dict[str, list[str]] = {}
    service_credentials: dict[str, set[str]] = {}

    for script in project.scripts:
        for svc in script.services:
            service_scripts.setdefault(svc.name, []).append(script.path)
            for secret in script.secrets:
                secret_lower = secret.lower()
                svc_lower = svc.name.lower()
                svc_lib_lower = svc.library.lower()
                if svc_lower and svc_lower in secret_lower:
                    service_credentials.setdefault(svc.name, set()).add(secret)
                if svc_lib_lower and svc_lib_lower in secret_lower:
                    service_credentials.setdefault(svc.name, set()).add(secret)

        for step in script.steps:
            if step.type == "file_io":
                local_ops.add("File reads/writes")
            if step.type == "transform":
                local_ops.add("Local data transforms")
            if step.type in ("api_call", "db_op") and step.service:
                data_egress_count += 1
                svc_name_lower = step.service.name.lower()
                for secret in script.secrets:
                    secret_lower = secret.lower()
                    if svc_name_lower and svc_name_lower in secret_lower:
                        entry = next(
                            (c for c in credentials_used if c["secret"] == secret),
                            None,
                        )
                        if entry is None:
                            entry = {
                                "secret": secret,
                                "used_by": [],
                                "transmitted_to": [],
                            }
                            credentials_used.append(entry)
                        if script.path not in entry["used_by"]:
                            entry["used_by"].append(script.path)
                        if step.service.name not in entry["transmitted_to"]:
                            entry["transmitted_to"].append(step.service.name)

    for svc_name, scripts_list in service_scripts.items():
        cred = list(service_credentials.get(svc_name, set()))
        external_services.append({
            "service": svc_name,
            "scripts": list(dict.fromkeys(scripts_list)),
            "credential": cred[0] if cred else "",
        })

    if not external_services:
        verdict = "local"
    elif local_ops and external_services:
        verdict = "mixed"
    else:
        verdict = "external"

    return SovereigntyReport(
        verdict=verdict,
        external_services=external_services,
        local_operations=sorted(local_ops),
        credentials_used=credentials_used,
        data_egress_count=data_egress_count,
    )
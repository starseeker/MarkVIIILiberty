"""Conservative production triage without turning source assertions into a BOM."""
from collections import Counter, defaultdict
import csv
import html
import json

from .evidence import STAGE, database, rows, read, sha, SURVEY, write


def dossier(part_id):
    with database() as connection:
        selected = rows(connection, "SELECT * FROM v_parts WHERE part_id=?", (part_id,))
        if not selected:
            raise ValueError("Unknown survey identity: " + part_id)
        result = {"part": selected[0]}
        for table in ["part_identifiers", "dimensions", "quantities", "part_variants", "part_figures",
                      "part_notes", "part_relations", "review_queue"]:
            result[table] = rows(connection, f"SELECT * FROM {table} WHERE part_id=?", (part_id,))
        result["evidence"] = rows(connection, "SELECT * FROM v_source_evidence WHERE part_id=?", (part_id,))
        result["children"] = rows(connection, "SELECT * FROM v_bom_edges WHERE parent_part_id=?", (part_id,))
        result["parents"] = rows(connection, "SELECT * FROM v_bom_edges WHERE child_part_id=?", (part_id,))
        result["issues"] = rows(connection, "SELECT i.* FROM issues i JOIN issue_parts p USING(issue_id) WHERE p.part_id=?", (part_id,))
        result["notes"] = rows(connection, "SELECT n.* FROM notes n JOIN part_notes p USING(note_id) WHERE p.part_id=?", (part_id,))
        return result


def build(out, model=None, instances=()):
    config = read(STAGE / "data/configuration.json")
    override = config["decisions"]
    with database() as connection:
        parts = rows(connection, "SELECT * FROM v_parts ORDER BY subsystem,canonical_name,part_id")
        known = {p["part_id"] for p in parts}
        if set(override) - known:
            raise ValueError("Configuration decision has unknown survey IDs")
        variants, quantities, issues, review, parents, sources = (defaultdict(list) for _ in range(6))
        for p in rows(connection, "SELECT * FROM part_variants"):
            variants[p["part_id"]].append(p)
        for p in rows(connection, "SELECT * FROM quantities"):
            quantities[p["part_id"]].append(p)
        for p in rows(connection, "SELECT * FROM issue_parts"):
            issues[p["part_id"]].append(p["issue_id"])
        for p in rows(connection, "SELECT * FROM review_queue"):
            review[p["part_id"]].append(p["review_id"])
        for p in rows(connection, "SELECT * FROM assembly_edges"):
            parents[p["child_part_id"]].append(p["edge_id"])
        for p in rows(connection, "SELECT DISTINCT part_id,r.source_id FROM part_evidence e JOIN source_records r USING(record_id)"):
            sources[p["part_id"]].append(p["source_id"])
        modeled = defaultdict(list)
        installed = Counter()
        if model:
            for item in instances:
                for pid in model["definitions"][item["definition"]]["survey_ids"]:
                    if item["definition"] not in modeled[pid]:
                        modeled[pid].append(item["definition"])
                    installed[pid] += 1
        ledger = []
        for part in parts:
            pid = part["part_id"]
            if part["kind"] in {"feature", "consumable", "configuration_group", "equipment_set"}:
                disposition, reason = "non_independent_solid", "Retain as integral feature, bulk material, configuration or selected equipment set; reconcile its ownership separately."
            elif any(v["variant_id"] == config["id"] for v in variants[pid]):
                disposition, reason = "production_candidate", "Explicit production evidence exists; quantity, identity and installation still need reconciliation."
            elif "SNL" in sources[pid] or "HB" in sources[pid]:
                disposition, reason = "transfer_candidate", "Tank source identifies this item; applicability to production remains provisional."
            else:
                disposition, reason = "unresolved_applicability", "Component-source or other identity requires tank/production applicability review."
            decision = override.get(pid)
            if decision:
                if decision["disposition"] not in {"included", "excluded", "non_independent_solid", "unresolved_applicability"}:
                    raise ValueError("Unsupported inventory decision: " + pid)
                if not decision.get("evidence") or not decision.get("reason"):
                    raise ValueError("Unsubstantiated inventory decision: " + pid)
                for reference in decision["evidence"]:
                    if not connection.execute("SELECT 1 FROM source_records WHERE record_id=?", (reference,)).fetchone():
                        raise ValueError("Unknown decision source record: " + reference)
                disposition, reason = decision["disposition"], decision["reason"]
            ledger.append(dict(part, disposition=disposition, disposition_reason=reason,
                               decision=decision, source_ids=sorted(sources[pid]),
                               variant_assertions=variants[pid], quantity_assertions=quantities[pid],
                               incoming_edge_ids=parents[pid], issue_ids=issues[pid], review_ids=review[pid],
                               modeled_definition_ids=modeled[pid],
                               geometry_status=(min((model["definitions"][k]["coverage"] for k in modeled[pid]),
                                                    key=lambda s: {"layout_only":0,"partial":1,"finished_approximate":2,"finished_supported":3}[s])
                                                if modeled[pid] else "not_started"),
                               modeled_occurrences=installed[pid],
                               expected_installed_count=decision.get("installed_count") if decision else None))
        report = {
            "configuration": config["id"], "survey_sha256": sha(SURVEY / "mark_viii_parts.sqlite"),
            "canonical_records": len(parts), "dispositions": dict(Counter(p["disposition"] for p in ledger)),
            "subsystems": dict(Counter(p["subsystem"] for p in ledger)),
            "review_queue": rows(connection, "SELECT * FROM review_queue"),
            "source_wide_issues": rows(connection, "SELECT * FROM issues"),
            "unquantified_gaps": config["unquantified_gaps"],
            "selected_loadout": config["selected_loadout"],
            "vehicle_occurrence_count": None,
            "warning": "Candidate classifications are triage, not completed applicability review. Quantity assertions are retained separately and never summed into an installed count.",
        }
    write(out / "inventory/ledger.json", ledger)
    write(out / "inventory/summary.json", report)
    columns = ["part_id", "canonical_name", "kind", "subsystem", "identifiers", "readiness",
               "disposition", "disposition_reason", "expected_installed_count", "geometry_status"]
    with (out / "inventory/ledger.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(ledger)
    # Plain local HTML remains usable without a server or internet access.
    table = "".join("<tr>" + "".join("<td>" + html.escape(str(p.get(k) or "")) + "</td>" for k in columns[:7]) + "</tr>" for p in ledger)
    page = """<!doctype html><meta charset="utf-8"><title>Mark VIII production inventory</title>
<style>body{font:15px system-ui;margin:2em}table{border-collapse:collapse;width:100%}td,th{padding:.35em;border:1px solid #ddd;text-align:left}thead{position:sticky;top:0;background:#eee}input{padding:.6em;width:60%}</style>
<h1>Production inventory triage</h1><p>5,482 survey records; the manufactured-piece count remains unknown.
Candidate classifications require review. Search by name, original mark, subsystem or disposition.</p>
<p><a href="summary.json">Issues and coverage</a> · <a href="ledger.csv">CSV</a> · <a href="ledger.json">Full evidence ledger</a></p>
<input id="query" placeholder="Filter records"><p id="count"></p><table><thead><tr>""" + "".join("<th>" + x + "</th>" for x in columns[:7]) + "</tr></thead><tbody>" + table + """</tbody></table>
<script>const rows=[...document.querySelectorAll('tbody tr')],q=document.getElementById('query');
q.addEventListener('input',()=>{let n=0;const s=q.value.toLowerCase();for(const r of rows){r.hidden=!r.textContent.toLowerCase().includes(s);if(!r.hidden)n++;}document.getElementById('count').textContent=n+' matching records';});q.dispatchEvent(new Event('input'));</script>"""
    (out / "inventory/index.html").write_text(page)
    return report

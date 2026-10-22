def check_report(result):
    lines = []
    for pair in sorted(result["pairs"], key=lambda p: (p["source"], p["target"])):
        if pair["state"] != "divergence":
            continue
        lines.append(f"divergence: {pair['source']} -> {pair['target']}")
        for witness in sorted(pair["imports"], key=lambda w: (w["file"], w["module"])):
            lines.append(f"    {witness['file']} imports {witness['module']}")
        if pair["reason"]:
            lines.append(f"    contract: {pair['reason']}")
        lines.append(f"    remedy: {pair['remedy'].text}")
    for breach in sorted(result.get("breaches", []),
                         key=lambda b: (b["file"], b["number"])):
        line = (f"limit breach: {breach['file']}: {breach['number']}"
                f" {breach['value']} over {breach['limit']}")
        if breach["reason"]:
            line += f" - {breach['reason']}"
        lines.append(line)
    for finding in sorted(result.get("claim_findings", []),
                          key=lambda f: f.text):
        lines.append(finding.text)
    return lines

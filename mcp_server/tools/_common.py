def entry_response(entry, speech: str) -> dict:
    """Every write returns the chain head so a client can keep an outside copy (the anchor)."""
    return {
        "entry_number": entry.seq,
        "issue_id": str(entry.issue_id),
        "chain_head": entry.hash,
        "speech": speech,
    }

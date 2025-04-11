import json

def print_doc_preview(index, doc):
    preview = doc.text.strip().splitlines()[0][:100] if doc.text else "(Empty)"
    print(f"  [{index}] Preview: {preview}")
    return preview

def write_lore_summary(summaries, filename="lore_summary.json"):
    with open(filename, "w") as f:
        json.dump(summaries, f, indent=2)
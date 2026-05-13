import json, pathlib

nb = json.loads(pathlib.Path(
    r"C:\Users\eugnm\OneDrive\Desktop\ironhack\WEEK 2\LAB 5\chunking_strategies_executed.ipynb"
).read_text(encoding="utf-8"))

for i, cell in enumerate(nb["cells"]):
    if cell.get("cell_type") != "code":
        continue
    for out in cell.get("outputs", []):
        otype = out.get("output_type", "")
        if otype == "error":
            print(f"Cell {i} ERROR: {out['ename']}: {out['evalue'][:200]}")
        elif otype in ("stream", "execute_result"):
            txt = "".join(out.get("text", out.get("data", {}).get("text/plain", [])))
            if txt.strip():
                print(f"Cell {i}: {txt[:400]}")
                print()

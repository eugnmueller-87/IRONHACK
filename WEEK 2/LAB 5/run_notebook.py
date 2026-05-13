"""Execute chunking_strategies.ipynb in-place using nbclient."""
import nbformat
from nbclient import NotebookClient
from pathlib import Path
import os

os.chdir(Path(__file__).parent)

nb_path = Path(__file__).parent / "chunking_strategies.ipynb"
with open(nb_path, encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

client = NotebookClient(
    nb,
    timeout=300,
    kernel_name="python3",
    resources={"metadata": {"path": str(Path(__file__).parent)}},
    allow_errors=True,
)

print("Executing notebook...")
client.execute()

out_path = Path(__file__).parent / "chunking_strategies_executed.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)
print(f"Done. Output saved to {out_path}")

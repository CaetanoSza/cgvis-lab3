import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).parent
SCRIPTS = [
    ROOT_DIR / "relation" / "scatterplot_pib_ica.py",
    ROOT_DIR / "relation" / "boxplot_pib_ica.py",
]


def main():
    for script in SCRIPTS:
        print(f"Executando {script.relative_to(ROOT_DIR)}...", flush=True)
        subprocess.run([sys.executable, str(script)], check=True)


if __name__ == "__main__":
    main()

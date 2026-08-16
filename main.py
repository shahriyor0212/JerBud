import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jerbud.app import Application
from jerbud.config import load_config


def main() -> None:
    config = load_config()
    app = Application(config)
    app.run()


if __name__ == "__main__":
    main()

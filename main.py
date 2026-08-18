import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jerbud import App, load_config


def main() -> None:
    config = load_config()
    app = App(config)
    app.run()


if __name__ == "__main__":
    main()

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"

REQUIRED_PARAMETERS = ("cliente", "data_inicio", "data_fim", "modo")
ALLOWED_MODES = ("producao", "homologacao", "teste")


def ensure_runtime_directories() -> None:
    for directory in (DOWNLOADS_DIR, OUTPUTS_DIR, LOGS_DIR):
        directory.mkdir(parents=True, exist_ok=True)

import json
import os
import sys
import traceback

from src.bot import run_bot


def load_parameters() -> dict:
    raw = os.getenv("TARDZ_PARAMETERS", "{}")

    try:
        params = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"TARDZ_PARAMETERS invalido: {error}") from error

    if not isinstance(params, dict):
        raise ValueError("TARDZ_PARAMETERS deve ser um objeto JSON.")

    return params


def main() -> int:
    print("[TARDZ] Iniciando robo")

    try:
        params = load_parameters()
        print(f"[TARDZ] Parametros recebidos: {list(params.keys())}")

        result = run_bot(params)

        print("[TARDZ] Robo finalizado com sucesso")
        print(f"[TARDZ] Resultado: {result}")

        return 0

    except Exception:
        print("[TARDZ] Erro durante execucao do robo")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

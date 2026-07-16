from datetime import datetime
import os
from pathlib import Path
import platform
import shutil
import sys
from time import sleep

from src.config import ALLOWED_MODES, DOWNLOADS_DIR, OUTPUTS_DIR, REQUIRED_PARAMETERS, ensure_runtime_directories
from src.logger import configure_logger


logger = configure_logger()


def _validate_required_parameters(params: dict) -> None:
    missing = [field for field in REQUIRED_PARAMETERS if not params.get(field)]
    if missing:
        raise ValueError(f"Parametros obrigatorios ausentes: {', '.join(missing)}")


def _validate_date(value: str, field_name: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError(f"Parametro {field_name} deve estar no formato YYYY-MM-DD.") from error


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized_value = value.strip().lower()
        if normalized_value in ("true", "1", "sim", "yes", "y"):
            return True
        if normalized_value in ("false", "0", "nao", "no", "n", ""):
            return False

    return bool(value)


def _log_runtime_context(validated_params: dict) -> None:
    logger.info("Diretorio atual: %s", Path.cwd())
    logger.info("Diretorio do projeto: %s", Path(__file__).resolve().parent.parent)
    logger.info("Python: %s", sys.executable)
    logger.info("Versao do Python: %s", platform.python_version())
    logger.info("Sistema operacional: %s", platform.platform())
    logger.info("Usuario: %s", os.getenv("USERNAME") or os.getenv("USER") or "nao identificado")
    logger.info("Sessao Windows: %s", os.getenv("SESSIONNAME", "nao informado"))
    logger.info("Headless: %s", validated_params["headless"])
    logger.info("Chrome informado: %s", validated_params["chrome_binary_path"] or "nao informado")
    logger.info("ChromeDriver informado: %s", validated_params["chromedriver_path"] or "nao informado")
    logger.info("Chrome no PATH: %s", shutil.which("chrome") or shutil.which("google-chrome") or "nao encontrado")
    logger.info("ChromeDriver no PATH: %s", shutil.which("chromedriver") or "nao encontrado")


def _validate_parameters(params: dict) -> dict:
    _validate_required_parameters(params)

    data_inicio = _validate_date(params["data_inicio"], "data_inicio")
    data_fim = _validate_date(params["data_fim"], "data_fim")

    if data_inicio > data_fim:
        raise ValueError("data_inicio nao pode ser maior que data_fim.")

    modo = str(params["modo"]).strip().lower()
    if modo not in ALLOWED_MODES:
        raise ValueError(f"modo deve ser um destes valores: {', '.join(ALLOWED_MODES)}")

    termo_pesquisa = str(params.get("termo_pesquisa", "Tardz Automations")).strip()
    if not termo_pesquisa:
        raise ValueError("termo_pesquisa nao pode ser vazio.")

    try:
        aguardar_segundos = int(params.get("aguardar_segundos", 3))
    except (TypeError, ValueError) as error:
        raise ValueError("aguardar_segundos deve ser um numero inteiro.") from error

    if aguardar_segundos < 0:
        raise ValueError("aguardar_segundos nao pode ser negativo.")

    try:
        intervalo_acoes = float(params.get("intervalo_acoes", 1))
    except (TypeError, ValueError) as error:
        raise ValueError("intervalo_acoes deve ser um numero.") from error

    if intervalo_acoes < 0:
        raise ValueError("intervalo_acoes nao pode ser negativo.")

    try:
        manter_aberto_segundos = int(params.get("manter_aberto_segundos", 30))
    except (TypeError, ValueError) as error:
        raise ValueError("manter_aberto_segundos deve ser um numero inteiro.") from error

    if manter_aberto_segundos < 0:
        raise ValueError("manter_aberto_segundos nao pode ser negativo.")

    return {
        "cliente": str(params["cliente"]).strip(),
        "data_inicio": data_inicio.date().isoformat(),
        "data_fim": data_fim.date().isoformat(),
        "modo": modo,
        "termo_pesquisa": termo_pesquisa,
        "aguardar_segundos": aguardar_segundos,
        "headless": _parse_bool(params.get("headless", False)),
        "intervalo_acoes": intervalo_acoes,
        "manter_aberto_segundos": manter_aberto_segundos,
        "chrome_binary_path": params.get("chrome_binary_path") or os.getenv("CHROME_BINARY_PATH"),
        "chromedriver_path": params.get("chromedriver_path") or os.getenv("CHROMEDRIVER_PATH"),
    }


def _create_chrome_driver(
    download_dir: str,
    headless: bool,
    chrome_binary_path: str | None = None,
    chromedriver_path: str | None = None,
):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "A biblioteca selenium nao esta instalada. Confirme se o runner instalou o requirements.txt "
            "antes de executar python main.py."
        ) from error

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_experimental_option("detach", not headless)

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1366,768")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    if chrome_binary_path:
        options.binary_location = chrome_binary_path

    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "safebrowsing.enabled": True,
        },
    )

    try:
        if chromedriver_path:
            return webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=options)

        return webdriver.Chrome(options=options)
    except Exception as error:
        raise RuntimeError(
            "Nao foi possivel iniciar o Google Chrome via Selenium. Verifique se o Chrome esta instalado, "
            "se o Selenium Manager pode obter o driver, se chrome_binary_path/chromedriver_path estao corretos "
            "e se o runner esta em uma sessao desktop interativa quando headless=false."
        ) from error


def _search_google(
    termo_pesquisa: str,
    aguardar_segundos: int,
    headless: bool,
    intervalo_acoes: float,
    manter_aberto_segundos: int,
    chrome_binary_path: str | None,
    chromedriver_path: str | None,
) -> dict:
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "A biblioteca selenium nao esta instalada. Confirme se o runner instalou o requirements.txt "
            "antes de executar python main.py."
        ) from error

    driver = _create_chrome_driver(str(DOWNLOADS_DIR), headless, chrome_binary_path, chromedriver_path)

    try:
        logger.info("Abrindo Google Chrome")
        driver.get("https://www.google.com/?hl=pt-BR")
        wait = WebDriverWait(driver, 20)
        wait.until(lambda current_driver: current_driver.execute_script("return document.readyState") == "complete")

        if intervalo_acoes:
            sleep(intervalo_acoes)

        logger.info("Localizando campo de pesquisa")
        search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
        search_box.click()

        if intervalo_acoes:
            sleep(intervalo_acoes)

        logger.info("Digitando termo de pesquisa: %s", termo_pesquisa)
        for character in termo_pesquisa:
            search_box.send_keys(character)
            if intervalo_acoes:
                sleep(min(intervalo_acoes, 0.15))

        if intervalo_acoes:
            sleep(intervalo_acoes)

        logger.info("Enviando pesquisa")
        search_box.send_keys(Keys.ENTER)

        wait.until(EC.presence_of_element_located((By.ID, "search")))

        if aguardar_segundos:
            sleep(aguardar_segundos)

        screenshot_path = OUTPUTS_DIR / "google-search-results.png"
        driver.save_screenshot(str(screenshot_path))

        return {
            "url_final": driver.current_url,
            "titulo_pagina": driver.title,
            "screenshot": str(screenshot_path),
        }
    finally:
        if headless:
            logger.info("Fechando Google Chrome")
            driver.quit()
        elif manter_aberto_segundos > 0:
            logger.info("Mantendo Chrome aberto por %s segundos para visualizacao", manter_aberto_segundos)
            sleep(manter_aberto_segundos)
            logger.info("Fechando Google Chrome")
            driver.quit()
        else:
            logger.info("Chrome permanecera aberto apos o fim do robo")


def run_bot(params: dict) -> dict:
    validated_params = _validate_parameters(params)
    ensure_runtime_directories()

    logger.info("Iniciando logica principal do robo")
    logger.info("Cliente: %s", validated_params["cliente"])
    logger.info("Periodo: %s ate %s", validated_params["data_inicio"], validated_params["data_fim"])
    logger.info("Modo: %s", validated_params["modo"])
    logger.info("Termo de pesquisa: %s", validated_params["termo_pesquisa"])
    _log_runtime_context(validated_params)

    search_result = _search_google(
        validated_params["termo_pesquisa"],
        validated_params["aguardar_segundos"],
        validated_params["headless"],
        validated_params["intervalo_acoes"],
        validated_params["manter_aberto_segundos"],
        validated_params["chrome_binary_path"],
        validated_params["chromedriver_path"],
    )

    return {
        "status": "success",
        "cliente": validated_params["cliente"],
        "data_inicio": validated_params["data_inicio"],
        "data_fim": validated_params["data_fim"],
        "modo": validated_params["modo"],
        "termo_pesquisa": validated_params["termo_pesquisa"],
        "resultado_pesquisa": search_result,
    }

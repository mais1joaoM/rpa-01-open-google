from datetime import datetime
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


def _validate_parameters(params: dict) -> dict:
    _validate_required_parameters(params)

    data_inicio = _validate_date(params["data_inicio"], "data_inicio")
    data_fim = _validate_date(params["data_fim"], "data_fim")

    if data_inicio > data_fim:
        raise ValueError("data_inicio nao pode ser maior que data_fim.")

    modo = str(params["modo"]).strip().lower()
    if modo not in ALLOWED_MODES:
        raise ValueError(f"modo deve ser um destes valores: {', '.join(ALLOWED_MODES)}")

    termo_pesquisa = str(params["termo_pesquisa"]).strip()
    if not termo_pesquisa:
        raise ValueError("termo_pesquisa nao pode ser vazio.")

    try:
        aguardar_segundos = int(params.get("aguardar_segundos", 3))
    except (TypeError, ValueError) as error:
        raise ValueError("aguardar_segundos deve ser um numero inteiro.") from error

    if aguardar_segundos < 0:
        raise ValueError("aguardar_segundos nao pode ser negativo.")

    return {
        "cliente": str(params["cliente"]).strip(),
        "data_inicio": data_inicio.date().isoformat(),
        "data_fim": data_fim.date().isoformat(),
        "modo": modo,
        "termo_pesquisa": termo_pesquisa,
        "aguardar_segundos": aguardar_segundos,
        "headless": _parse_bool(params.get("headless", False)),
    }


def _create_chrome_driver(download_dir: str, headless: bool):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1366,768")

    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "safebrowsing.enabled": True,
        },
    )

    return webdriver.Chrome(options=options)


def _search_google(termo_pesquisa: str, aguardar_segundos: int, headless: bool) -> dict:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    driver = _create_chrome_driver(str(DOWNLOADS_DIR), headless)

    try:
        logger.info("Abrindo Google Chrome")
        driver.get("https://www.google.com")

        logger.info("Pesquisando por: %s", termo_pesquisa)
        wait = WebDriverWait(driver, 20)
        search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.clear()
        search_box.send_keys(termo_pesquisa)
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
        logger.info("Fechando Google Chrome")
        driver.quit()


def run_bot(params: dict) -> dict:
    validated_params = _validate_parameters(params)
    ensure_runtime_directories()

    logger.info("Iniciando logica principal do robo")
    logger.info("Cliente: %s", validated_params["cliente"])
    logger.info("Periodo: %s ate %s", validated_params["data_inicio"], validated_params["data_fim"])
    logger.info("Modo: %s", validated_params["modo"])
    logger.info("Termo de pesquisa: %s", validated_params["termo_pesquisa"])

    search_result = _search_google(
        validated_params["termo_pesquisa"],
        validated_params["aguardar_segundos"],
        validated_params["headless"],
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

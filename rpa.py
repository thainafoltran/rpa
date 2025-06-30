import sqlite3
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side
from datetime import datetime 

# PARTE 1 - PAÍSES
def coletar_dados_pais(nome):
    url = f"https://restcountries.com/v3.1/name/{nome}"
    resposta = requests.get(url)

    if resposta.status_code != 200:
        print(f"Erro ao consultar o país: {nome}")
        return None

    dados = resposta.json()
    info = dados[0]

    try:
        moeda = list(info.get("currencies", {}).values())[0]
        idioma = list(info.get("languages", {}).values())[0]
    except:
        moeda = {"name": "Desconhecida", "symbol": "?"}
        idioma = "Desconhecido"

    return {
        "nome_comum": info.get("name", {}).get("common", "N/A"),
        "nome_oficial": info.get("name", {}).get("official", "N/A"),
        "capital": info.get("capital", ["N/A"])[0],
        "continente": info.get("continents", ["N/A"])[0],
        "regiao": info.get("region", "N/A"),
        "sub_regiao": info.get("subregion", "N/A"),
        "populacao": info.get("population", 0),
        "area": info.get("area", 0),
        "moeda": moeda.get("name", "N/A"),
        "simbolo_moeda": moeda.get("symbol", "?"),
        "idioma": idioma,
        "fuso_horario": info.get("timezones", ["N/A"])[0],
        "bandeira": info.get("flags", {}).get("png", "")
    }
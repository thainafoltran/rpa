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

def salvar_paises_bd(paises):
    conexao = sqlite3.connect("paises.db")
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paises (
            nome_comum TEXT, nome_oficial TEXT, capital TEXT,
            continente TEXT, regiao TEXT, sub_regiao TEXT,
            populacao INTEGER, area REAL, moeda TEXT,
            simbolo_moeda TEXT, idioma TEXT, fuso_horario TEXT,
            bandeira TEXT
        )
    ''')
    
    for pais in paises:
        cursor.execute('''
            INSERT INTO paises VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pais["nome_comum"], pais["nome_oficial"], pais["capital"],
            pais["continente"], pais["regiao"], pais["sub_regiao"],
            pais["populacao"], pais["area"], pais["moeda"],
            pais["simbolo_moeda"], pais["idioma"], pais["fuso_horario"],
            pais["bandeira"]
        ))
    
    conexao.commit()
    conexao.close()

def main():
    dados_paises = []
    qtd_paises = 0
    max_tentativas = 3 

    while len(dados_paises) < max_tentativas:
        qtd_paises += 1
        pais = input(f"Digite o nome de 3 países, lembre-se de escrever em INGLÊS e SEM ACENTOS.\n {qtd_paises}º país: ").strip()
        
        print(f"\nBuscando dados de {pais}...") 
        dados = coletar_dados_pais(pais)
        
        if dados:
            dados_paises.append(dados)
            print(f"Dados de '{pais}' coletados com sucesso!")
        else:
            print(f"País '{pais}' não encontrado. Tente novamente.\n")
            qtd_paises -= 1  
    
    salvar_paises_bd(dados_paises)
    return dados_paises

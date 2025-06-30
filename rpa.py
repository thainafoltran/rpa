import requests
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

# PARTE 2 - LIVROS
def extrair_livros():
    url = "https://books.toscrape.com"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    livros = []
   
    for artigo in soup.find_all("article", class_="product_pod")[:10]:
        titulo = artigo.h3.a["title"]
        preco = artigo.find("p", class_="price_color").text.strip()
        avaliacao = artigo.find("p", class_="star-rating")["class"][1]
        disponibilidade = artigo.find("p", class_="instock availability").text.strip()

        livros.append({
            "titulo": titulo,
            "preco": preco,
            "avaliacao": avaliacao,
            "disponibilidade": disponibilidade
        })
 
       
    return livros

def salvar_livros_bd(livros):
    conectar = sqlite3.connect("livraria.db")
    cursor = conectar.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            preco REAL,
            avaliacao TEXT,
            disponibilidade TEXT
        )
    ''')

    for livro in livros:
        cursor.execute('''
            INSERT INTO livros (titulo, preco, avaliacao, disponibilidade)
            VALUES (?, ?, ?, ?)
        ''', (livro["titulo"], livro["preco"], livro["avaliacao"], livro["disponibilidade"]))
    
    conectar.commit()
    conectar.close()

dez_livros = extrair_livros()
if dez_livros:
    salvar_livros_bd(dez_livros)



if __name__ == "__main__":
    dados_paises = main()
    livros = extrair_livros()
    salvar_livros_bd(livros)

 
    wb = Workbook()

    #PLANILHA PAÍSES
    planilha1 = wb.active
    planilha1.title = "Paises"
    cabecalhos_paises = ["Nome Comum", "Nome Oficial", "Capital", "Continente", "Região", "SubRegião",
                        "População", "Área", "Nome Moeda", "Símbolo Moeda", "Idioma", "Fuso Horário", "Bandeira"]
    planilha1.append(["Aluno:", "Thainá Foltran"])
    planilha1.append(["O arquivo foi gerado em:", datetime.now().strftime("%d/%m/%Y")])
    planilha1.append(cabecalhos_paises)

    for pais in dados_paises:
        planilha1.append([
            pais["nome_comum"], pais["nome_oficial"], pais["capital"],
            pais["continente"], pais["regiao"], pais["sub_regiao"],
            pais["populacao"], pais["area"], pais["moeda"],
            pais["simbolo_moeda"], pais["idioma"], pais["fuso_horario"],
            pais["bandeira"]
        ])

        # PLANILHA LIVRO
    planilha2 = wb.create_sheet(title="Livros")
    cabecalhos_livros = ["Título", "Preço", "Avaliação", "Disponibilidade"]
    planilha2.append(cabecalhos_livros)

    for livro in livros:  
        planilha2.append([
            livro["titulo"],
            livro["preco"],
            livro["avaliacao"],
            livro["disponibilidade"]
        ])

    #FORMATAÇÃO
    for cell in planilha1[1] + planilha1[2] + planilha1[3]:
        cell.font = Font(color='B388FF', bold=True)
        lilas_borda = Side(style='medium', color='D9B3FF')  
        cell.border = Border(left=lilas_borda, 
                     right=lilas_borda,
                     top=lilas_borda,
                     bottom=lilas_borda)

    for cell in planilha2[1]:
        cell.font = Font(color="FF8C00", bold=True)
        laranja_borda = Side(style='medium', color='FFC891')  
        cell.border = Border(left=laranja_borda, 
                     right=laranja_borda,
                     top=laranja_borda,
                     bottom=laranja_borda)
    wb.save("dados-ap2.xlsx")
    print("Arquivo Excel da AP2 de RPA foi criado com sucesso!!!")
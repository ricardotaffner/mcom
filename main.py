import requests
import json
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import pytesseract
import time
import io

# === Função para consultas ao Power BI ===
def consultar_powerbi(query, model_id):
    headers = {
        "Content-Type": "application/json"
    }
    url = f"https://wabi-south-central-us-api.analysis.windows.net/public/reports/querydata?synchronous=true"
    body = {
        "version": "1.0.0",
        "queries": [query],
        "modelId": model_id
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    return response.json()["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"]

# === Computadores para Inclusão - Doações ===
def dados_doacoes():
    query = {
        "Query": {
            "Commands": [{
                "SemanticQueryDataShapeCommand": {
                    "Query": {
                        "Version": 2,
                        "From": [{"Name": "a", "Entity": "Doacoes"}],
                        "Select": [
                            {"Column": {"Expression": {"SourceRef": {"Source": "a"}}, "Property": "UF"}, "Name": "UF"},
                            {"Measure": {"Expression": {"SourceRef": {"Source": "a"}}, "Property": "Qtde_PID"}, "Name": "PIDs"},
                            {"Measure": {"Expression": {"SourceRef": {"Source": "a"}}, "Property": "Qtde_Municipio"}, "Name": "Municípios"},
                            {"Measure": {"Expression": {"SourceRef": {"Source": "a"}}, "Property": "Qtde_Doacao"}, "Name": "Doações"},
                            {"Column": {"Expression": {"SourceRef": {"Source": "a"}}, "Property": "Ano"}}
                        ],
                        "Where": []
                    },
                    "Binding": {
                        "Primary": {"Groupings": [["UF"]]},
                        "DataReduction": {"DataVolume": 3},
                        "Version": 1
                    }
                }
            }]
        }
    }
    dados = consultar_powerbi(query, model_id=600125)
    registros = []
    for linha in dados:
        valores = linha["C"]
        registros.append({
            "UF": valores[0],
            "PID": valores[1],
            "Municípios": valores[2],
            "Doações": valores[3],
            "Ano": valores[4]
        })
    df = pd.DataFrame(registros)
    return df

# === Internet Brasil (Looker Studio via OCR) ===
def internet_brasil_ocr():
    url = "https://www.gov.br/mcom/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/internet-brasil"
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(10)
    screenshot = driver.get_screenshot_as_png()
    driver.quit()

    image = Image.open(io.BytesIO(screenshot))
    crop_area = image.crop((100, 250, 900, 800))  # ajustar se necessário
    ocr_text = pytesseract.image_to_string(crop_area, config="--psm 6")
    linhas = ocr_text.strip().split("\n")
    dados_totais = {}
    dados_uf = []
    for linha in linhas:
        if "Distribuídos" in linha or "Instituições" in linha or "Municípios" in linha:
            partes = linha.split()
            if len(partes) >= 2:
                chave = " ".join(partes[:-1])
                valor = partes[-1].replace(".", "").replace(",", "")
                dados_totais[chave] = int(valor)
        elif any(uf in linha for uf in ["PA", "MA", "BA", "PB", "PE", "AM", "MG", "RN", "RJ", "PI", "SP", "RS", "DF", "CE"]):
            try:
                partes = linha.rsplit(" ", 1)
                uf = partes[0].strip()
                valor = int(partes[1].replace(".", "").replace(",", ""))
                dados_uf.append({"UF": uf, "Chips Solicitados": valor})
            except:
                continue
    df_uf = pd.DataFrame(dados_uf)
    df_totais = pd.DataFrame([dados_totais])
    return df_totais, df_uf

# === Executa tudo e salva o Excel final ===
def executar_unificado():
    print("Extraindo dados dos painéis...")

    df_doacoes = dados_doacoes()
    df_internet_totais, df_internet_ufs = internet_brasil_ocr()

    with pd.ExcelWriter("dados_mcom_unificado.xlsx") as writer:
        df_doacoes.to_excel(writer, sheet_name="Computadores - Doações", index=False)
        df_internet_totais.to_excel(writer, sheet_name="InternetBrasil - Totais", index=False)
        df_internet_ufs.to_excel(writer, sheet_name="InternetBrasil - Chips por UF", index=False)

    print("Arquivo salvo como dados_mcom_unificado.xlsx")

if __name__ == "__main__":
    executar_unificado()

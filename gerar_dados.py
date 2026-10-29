import pandas as pd
import requests

print("A descarregar dados populacionais do IBGE...")

url_ibge = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021/variaveis/9324?localidades=N6[N3[25]]"

try:
    response = requests.get(url_ibge, timeout=90)
    data = response.json()
    resultados = data[0]['resultados'][0]['series']

    populacao = []
    for item in resultados:
        municipio = item['localidade']['nome'].split(' - ')[0]
        valor = item['serie']['2021']
        populacao.append({'Município': municipio, 'População': int(valor) if valor != '-' else 0})

    df = pd.DataFrame(populacao)
    df.to_csv('data/populacao_pb.csv', index=False)
    print("✅ Ficheiro data/populacao_pb.csv criado com sucesso!")

except Exception as e:
    print(f"❌ Erro ao descarregar dados: {e}")
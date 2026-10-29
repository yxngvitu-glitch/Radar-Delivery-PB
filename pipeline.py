import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import sys

print("🚀 Iniciando Pipeline de Dados ETL...")

# Garante que a pasta data existe
os.makedirs('data', exist_ok=True)

# --- 1. Motor de Conexão Robusto ---
def get_robust_session():
    session = requests.Session()
    # Tenta 5 vezes. Se falhar, espera progressivamente (2s, 4s, 8s, 16s...)
    retry = Retry(
        total=5, 
        backoff_factor=2, 
        status_forcelist=[403, 429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = get_robust_session()

# --- 2. Extração do IBGE (População) ---
def atualizar_ibge():
    print("\n⏳ A extrair dados do IBGE...")
    url_ibge = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021/variaveis/9324?localidades=N6[N3[25]]"
    
    try:
        # Timeout longo para APIs governamentais
        response = session.get(url_ibge, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        if not data or 'resultados' not in data[0]:
            raise ValueError("A API do IBGE devolveu um JSON vazio ou inesperado.")
            
        resultados = data[0]['resultados'][0]['series']
        populacao = []
        
        for item in resultados:
            municipio = item['localidade']['nome'].split(' - ')[0]
            valor = item['serie'].get('2021', '0')
            populacao.append({
                'Município': municipio, 
                'População': int(valor) if valor.isnumeric() else 0
            })
            
        df_pop = pd.DataFrame(populacao)
        
        # Proteção: Só guarda se tivermos dados reais (evita apagar o CSV bom se a API devolver lixo)
        if len(df_pop) > 10:
            df_pop.to_csv('data/populacao_pb.csv', index=False)
            print(f"✅ Sucesso: IBGE atualizado ({len(df_pop)} municípios).")
        else:
            print("⚠️ Aviso: IBGE devolveu poucos dados. CSV local foi mantido por segurança.")
            
    except Exception as e:
        print(f"❌ Falha no IBGE (Motor de Fallback ativado -> Mantendo CSV local). Detalhe: {e}")

# --- 3. Extração do OpenStreetMap (Restaurantes) ---
def atualizar_osm():
    print("\n⏳ A extrair dados do OpenStreetMap...")
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:90];
    area["name"="Paraíba"]["admin_level"="4"]->.searchArea;
    (
      node["amenity"="restaurant"](area.searchArea);
      node["amenity"="fast_food"](area.searchArea);
      node["amenity"="cafe"](area.searchArea);
    );
    out center;
    """
    
    # Headers profissionais evitam o bloqueio 403 (Access Blocked)
    headers = {
        'User-Agent': 'RadarDeliveryPipeline/2.0 (github.com/seu-usuario/seu-repo)',
        'Accept': 'application/json'
    }
    
    try:
        response = session.get(overpass_url, params={'data': overpass_query}, headers=headers, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        elementos = data.get('elements', [])
        
        if not elementos:
            raise ValueError("A API do OSM não devolveu nenhum estabelecimento.")
            
        estabelecimentos = []
        for el in elementos:
            estabelecimentos.append({
                'Nome': el.get('tags', {}).get('name', 'Sem Nome'),
                'Tipo': el.get('tags', {}).get('amenity', 'Desconhecido'),
                'Lat': el.get('lat'),
                'Lon': el.get('lon')
            })
            
        df_rest = pd.DataFrame(estabelecimentos)
        
        if len(df_rest) > 50:
            df_rest.to_csv('data/restaurantes_pb.csv', index=False)
            print(f"✅ Sucesso: OSM atualizado ({len(df_rest)} estabelecimentos).")
        else:
            print("⚠️ Aviso: OSM devolveu poucos dados. CSV local foi mantido por segurança.")
            
    except Exception as e:
        print(f"❌ Falha no OSM (Motor de Fallback ativado -> Mantendo CSV local). Detalhe: {e}")

# --- Execução Principal ---
if __name__ == "__main__":
    atualizar_ibge()
    atualizar_osm()
    print("\n🏁 Pipeline finalizado. O sistema não quebrou.")
    # Força saída com código 0 (Sucesso) para que o GitHub Actions não dê erro,
    # já que as falhas de API são absorvidas pelos nossos CSVs de backup.
    sys.exit(0)
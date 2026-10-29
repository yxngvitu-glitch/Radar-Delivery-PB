# 🛵 Radar Delivery - Inteligência de Mercado na Paraíba

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458.svg)
![Folium](https://img.shields.io/badge/Folium-Maps-77B829.svg)
![GitHub Actions](https://img.shields.io/badge/Automated_ETL-GitHub_Actions-2088FF.svg)

**Radar Delivery** é um *dashboard* interativo focado na análise de potencial de mercado para aplicações de *food delivery* (como iFood e Uber Eats) no estado da Paraíba. O projeto cruza dados demográficos de demanda (População) com dados geoespaciais de oferta (Restaurantes) para identificar zonas de alta concorrência e "desertos de delivery".

---

## 🏗️ Arquitetura de Dados e Resiliência (O Diferencial)

Este projeto foi desenhado com uma **arquitetura de dados desacoplada** para garantir 100% de disponibilidade, latência zero no *frontend* e contornar instabilidades frequentes em APIs públicas (como bloqueios de IPs em nuvem ou *timeouts* governamentais).

O fluxo de dados funciona numa estrutura de **Fábrica de Dados Automatizada (ETL)**:

1. **Extract & Transform (O Robô):** Um *script* Python (`etl_pipeline.py`) consome a API do IBGE (SIDRA) para dados demográficos e a API do OpenStreetMap (Overpass) para dados espaciais.
2. **Automação (GitHub Actions):** A cada 3 dias, um *workflow* do GitHub Actions executa silenciosamente o pipeline ETL, extrai os dados mais recentes, realiza a limpeza e atualiza os ficheiros CSV locais no repositório.
3. **Load & Serve (O Dashboard):** A aplicação Streamlit (`app.py`) consome os dados exclusivamente da pasta estática `data/`. Isto garante carregamento instantâneo da interface, previne falhas durante avaliações e utiliza mapas base da Esri para evitar bloqueios 403 do OpenStreetMap.

---

## 📊 Funcionalidades do Dashboard

* **Métricas Chave:** Total de parceiros em potencial, categoria dominante na região e número de praças (cidades) analisadas.
* **Mapa de Calor (Heatmap):** Renderização geoespacial (Folium) destacando zonas de alta densidade comercial (pontos quentes para campanhas) versus desertos de delivery (oportunidades para *Dark Kitchens*).
* **Análise de Demanda:** Gráfico de barras identificando os maiores mercados consumidores do estado com base na estimativa populacional.
* **Visual Profissional:** UI/UX customizada com injeção de CSS para simular a estética limpa e profissional de plataformas reais de delivery.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Frontend/Visualização:** Streamlit, Streamlit-Folium
* **Processamento de Dados:** Pandas
* **Geolocalização/Mapas:** Folium, Esri World Street Map Tiles
* **Extração de Dados (APIs):** Requests (IBGE SIDRA, OpenStreetMap Overpass)
* **Engenharia de Dados (DataOps):** GitHub Actions (CI/CD / Agendamento Cron)

---

## 🚀 Como executar localmente

1. Clone o repositório:
```bash
git clone https://github.com/yxngvitu-glitch/Radar-Delivery-PB.git
cd Radar-Delivery-PB
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. (Opcional) Force a atualização dos dados executando o Pipeline ETL:
```bash
python etl_pipeline.py
```

4. Inicie o Dashboard:
```bash
streamlit run app.py
```

---
*Desenvolvido como projeto de portefólio para demonstrar competências de ponta a ponta em Análise e Engenharia de Dados.*
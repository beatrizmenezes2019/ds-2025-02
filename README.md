# ds-2025-02
Disciplina Design de Software 2025/02

Vídeo demonstrativo MVP: https://drive.google.com/file/d/1MBBBKJhMbe3V53hnZwdeKVBIHmVnjdhn/view?usp=drive_link

# Projeto de Aferição de Glicose via WhatsApp + n8n + FastAPI

Este repositório contém o projeto completo de um sistema capaz de **analisar imagens de papel reagente impregnado com saliva** para estimar o nível de glicose do usuário. A solução integra **WhatsApp → n8n → FastAPI (com OpenCV)**, retornando ao usuário um valor estimado de glicose.

---

# 📌 1. Visão Geral do Projeto

O objetivo principal é permitir que o usuário envie uma **foto do papel reagente pelo WhatsApp**, e o sistema retorne:

* O valor estimado de glicose (mg/dL)
* A classificação clínica (normal, pré‑diabetes, hiperglicemia, hipoglicemia)
* Recomendações iniciais

O fluxo completo funciona assim:

```
Usuário → WhatsApp → n8n → Servidor glicoscan → Algoritmo de Análise da Cor → n8n → WhatsApp
```

O projeto é modular e composto por:

* **Workflow n8n** para integração e orquestração
* **API Waha** para a comunicação com o Whatsapp (webhook)
* **API glicoscan** para processamento das imagens
* **Container Docker** para deploy da API e demais ferramentas

---

# 📌 2. Arquitetura da Solução

```
┌────────────────┐      ┌─────────────┐      ┌─────────────┐
│   Usuário      │ ---> │  WhatsApp   │ ---> │     n8n     │
└────────────────┘      └─────────────┘      └─────────────┘
                                               │             
                                               │   HTTP POST 
                                               ▼             
                                        ┌─────────────┐     
                                        │  glicoscan  |
                                        │   (Docker)  │
                                        └─────────────┘
```

---

# 📌 3. Estrutura do Repositório

```
/
├── app/
│   └── main.py
|   └── preprocessing.py
|   └── model.py
|   └── preprocess_extract.py
├── arquivos/
│   └── fluxo_n8n/
|       └── workflow.json
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 📌 4. Integração com WhatsApp via n8n

A integração funciona através de:

* **Node WhatsApp (Meta Cloud API)** ou **WhatsApp Business API**
* Recebimento da imagem enviada pelo usuário
* Disparo de requisição HTTP à API FastAPI
* Retorno da resposta processada ao usuário

### Como importar o workflow no n8n

1. Abra o n8n (`http://localhost:5678`)
2. Clique em **Workflows → Import**
3. Faça upload do arquivo `workflow.json`
4. Salve o workflow
5. Adicione suas **Credenciais** (WhatsApp, HTTP Request)
6. Ative o workflow no botão **Active**

### Pontos de atenção

* A URL do Webhook muda conforme o ambiente
* Nodes de WhatsApp precisam de Token e ID de número

---

# 📌 5. API FastAPI

A API recebe um arquivo `.jpg/.png` e retorna:

```json
{
  "glucose_estimate": 134
}
```

### Endpoint

```
POST /analyze
```

# 📌 6. Pipeline de Processamento da Imagem (OpenCV)

Arquivo `preprocessing.py`

* Converte a imagem para HSV
* Calcula valor médio de brilho/intensidade
* Mapeia o valor em uma curva simples (placeholder)

---

# 📌 7. Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9197"]
```

### Como rodar com Docker

```bash
docker build -t glicoscan .
docker run -p 8000:8000 glicoscan
```

# 📌 8. Testando no Postman

### Requisição

```
POST http://localhost:9197/analyze
```

### Body

* Form‑Data
* Key: **imagem_url**
* Tipo: *Text*
* Enviar o caminho da imagem da tira reagente

---

# 📌 09. Possíveis Erros e Soluções

### ❗ Erro: "Port should be >= 0 and < 65536"

Causa:
O Postman está acessando uma URL com um caractere invisível no final da porta, por exemplo:

```
8080⁠
```

Esse caractere é um **ZERO‑WIDTH SPACE (U+2060)**.

💡 Solução: apagar a URL inteira e digitar novamente manualmente.

---

# 📌 10. Melhorias Futuras

* Modelo de regressão calibrado com amostras reais
* Normalização de iluminação usando gray‑world
* App mobile nativo
* Dashboard para profissionais de saúde

---

# 📌 11. Autores

Projeto desenvolvido para fins acadêmicos.

Integrantes:

* Beatriz Menezes
* Jannderson Oliveira
* Arthur Felipe
* Alisson Braz

Professor: **Jacson Rodrigues Barbosa**
Disciplina: **Design de Software — UFG**
Ano: **2025**

---


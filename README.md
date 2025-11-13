# Quero Economizar Já 💰

Uma aplicação web inteligente para comparação de preços de supermercados a partir de PDFs de promoções, ajudando você a economizar na sua lista de compras.

## 🎯 Visão do Negócio

O **Quero Economizar Já** nasce da necessidade de ajudar consumidores a encontrar os melhores preços em diferentes supermercados de forma rápida e eficiente. A plataforma permite:

- **Upload de PDFs** de promoções de supermercados
- **Criação de listas de compras** personalizadas
- **Comparação inteligente** de preços entre estabelecimentos
- **Identificação automática** do melhor custo-benefício
- **Economia real** no orçamento familiar

## 🚀 Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **Python** - Linguagem principal
- **MongoDB** - Banco de dados NoSQL
- **PyPDF2/pdfplumber** - Processamento de PDFs
- **Pandas/Numpy** - Análise de dados
- **Prometheus** - Coleta de métricas
- **Docker** - Containerização

### Frontend
- **React** - Biblioteca para interface
- **Tailwind CSS** - Framework de estilos
- **Vite** - Build tool moderna
- **Axios** - Cliente HTTP

### Infraestrutura
- **Docker Compose** - Orquestração de containers
- **Grafana** - Visualização de métricas
- **Prometheus** - Monitoramento

## 📦 Como Executar a Aplicação

### Pré-requisitos
- Docker
- Docker Compose

### Execução

1. **Clone o repositório**
```bash
git clone https://github.com/lucasamarante42/quero-economizar-ja.git
cd quero-economizar-ja

2. **Execute com Docker Compose**
```bash
docker compose up --build
```

3. **Acesse as aplicações**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

## 🛠️ Desenvolvimento

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📊 Funcionalidades

### Principais
- ✅ Upload de PDFs de promoções
- ✅ Extração automática de produtos e preços
- ✅ Criação de listas de compras
- ✅ Comparação em tempo real
- ✅ Identificação do melhor preço
- ✅ Cálculo de economia total

### Métricas e Monitoramento
- ✅ Métricas de performance com Prometheus
- ✅ Dashboard com Grafana
- ✅ Monitoramento de requisições
- ✅ Latência das operações
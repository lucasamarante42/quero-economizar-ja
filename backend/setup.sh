#!/bin/bash

echo "Instalando Quero Economizar Já..."

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

echo "Instalação concluída!"
echo "Para ativar o ambiente virtual: source venv/bin/activate"
echo "Para executar: uvicorn app.main:app --reload"
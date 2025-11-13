FROM node:18-alpine

WORKDIR /app

# Copia os arquivos de package primeiro (para cache de dependências)
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia o restante do código
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
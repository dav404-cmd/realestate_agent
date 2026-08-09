FROM node:24.18.0-slim

WORKDIR /app

COPY package*.json .

RUN npm install

COPY . .

CMD ["npm" , "run" , "dev" , "--" , "--host" , "0.0.0.0"]
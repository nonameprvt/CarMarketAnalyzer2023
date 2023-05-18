FROM node:alpine

WORKDIR /app

COPY client/package*.json ./

RUN npm install
ENV PATH /app/node_modules/.bin:$PATH

ADD client /app/src
WORKDIR /app/src
RUN npm run build
CMD npm run start

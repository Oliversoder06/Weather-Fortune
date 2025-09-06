FROM node:20-alpine
WORKDIR /app

# Copy lockfile for deterministic installs
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--port", "3000", "--host"]

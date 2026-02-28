FROM node:18-alpine

WORKDIR /app

# 只要必要的文件
COPY package.json package-lock.json* ./

# 安装生产依赖
RUN npm install --production

# 复制核心逻辑和脚本
COPY lib ./lib
COPY models ./models
COPY scripts ./scripts

# 启动 Worker
CMD ["node", "scripts/startWorker.js"]

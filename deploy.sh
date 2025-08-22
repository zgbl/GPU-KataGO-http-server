#!/bin/bash
# Google Cloud Run 部署脚本

set -e

# 配置变量
PROJECT_ID="your-project-id"  # 替换为你的项目ID
SERVICE_NAME="katago-analysis"
REGION="us-central1"  # 免费配额地区
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 开始部署KataGo Analysis到Google Cloud Run"

# 检查gcloud是否已登录
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ 请先登录Google Cloud: gcloud auth login"
    exit 1
fi

# 设置项目
echo "📋 设置项目: $PROJECT_ID"
gcloud config set project inspired-arena-182703

# 启用必要的API
echo "🔧 启用必要的API..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 构建镜像
echo "🏗️ 构建Docker镜像..."
gcloud builds submit --config cloudbuild.yaml .

echo "✅ 部署完成！"
echo "🌐 服务URL: https://$SERVICE_NAME-$REGION.a.run.app"
echo "🔍 查看服务状态: gcloud run services describe $SERVICE_NAME --region=$REGION"
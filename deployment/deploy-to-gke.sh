#!/bin/bash
# GKE Autopilot 部署腳本 - Alert Query Planner Agent
# 適用於私有叢集環境

# set -e  # 移除自動退出，改為手動檢查錯誤

# 錯誤處理函數
check_error() {
    if [ $? -ne 0 ]; then
        echo "❌ 錯誤：$1"
        echo "按任意鍵繼續或 Ctrl+C 退出..."
        read -n 1 -s
        return 1
    fi
    return 0
}

PROJECT_ID="cloud-sre-poc-465509"
CLUSTER_NAME="tracing-gke-cluster"
REGION="asia-east1"
ARTIFACT_REGISTRY_REPO="app-image-repo"
IMAGE_NAME="alert-query-planner"
IMAGE_TAG="latest"

echo "開始部署到 GKE Autopilot..."

# 1. 設定 gcloud 配置
echo "設定 gcloud 配置..."
gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}

# 2. 獲取 GKE 叢集憑證
echo "獲取 GKE 叢集憑證..."
gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${REGION}
if ! check_error "無法獲取 GKE 叢集憑證"; then
    echo "請檢查叢集名稱和區域設定"
fi

# 3. Artifact Registry repository 已由 Terraform 建立
echo "使用 Terraform 建立的 Artifact Registry repository: ${ARTIFACT_REGISTRY_REPO}"
echo "Repository URL: ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}"

# 4. 配置 Docker 認證
echo "配置 Docker 認證..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev
check_error "Docker 認證配置失敗"

# 5. 建構並推送 Docker 映像 (可選)
# 如果您已經使用 podman 建構並推送映像，請設定環境變數：
# $env:SKIP_BUILD = "true" (powershell)
export SKIP_BUILD=true

if [ "${SKIP_BUILD}" != "true" ]; then
    echo "建構 Docker 映像..."
    docker build -f dockerfile -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/${IMAGE_NAME}:${IMAGE_TAG} .
    if ! check_error "Docker 映像建構失敗"; then
        echo "請檢查 dockerfile 和相關檔案"
    fi
    
    echo "推送 Docker 映像到 Artifact Registry..."
    docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/${IMAGE_NAME}:${IMAGE_TAG}
    if ! check_error "Docker 映像推送失敗"; then
        echo "請檢查 Artifact Registry 權限和網路連線"
    fi
else
    echo "跳過映像建構，使用預先建構的映像..."
    echo "確認映像已推送到: ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/${IMAGE_NAME}:${IMAGE_TAG}"
fi

# 6. 設定 Workload Identity (如果尚未設定)
echo "設定 Workload Identity..."
chmod +x setup-workload-identity.sh
./setup-workload-identity.sh
if ! check_error "Workload Identity 設定失敗"; then
    echo "請檢查 GCP IAM 權限"
fi

# 7. 部署到 Kubernetes
echo "部署到 Kubernetes..."
kubectl apply -f gke-alert-query-planner.yaml
if ! check_error "Kubernetes 部署失敗"; then
    echo "請檢查 YAML 檔案和 kubectl 權限"
fi

# 8. 等待部署完成
echo "等待 Pod 就緒..."
kubectl wait --for=condition=ready pod -l app=alert-query-planner -n ai-agent --timeout=300s
if ! check_error "Pod 啟動超時或失敗"; then
    echo "請檢查 Pod 日誌: kubectl logs -l app=alert-query-planner -n ai-agent"
fi

# 9. 檢查部署狀態
echo "檢查部署狀態..."
kubectl get pods -n ai-agent -l app=alert-query-planner
kubectl get services -n ai-agent
kubectl get hpa -n ai-agent

# 10. 顯示服務端點
echo "服務端點資訊："
kubectl get service alert-query-planner-lb -n ai-agent -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null && echo " (LoadBalancer IP)" || echo "LoadBalancer IP 尚未分配"

echo "✅ 部署完成！"
echo "您可以使用以下命令查看日誌："
echo "kubectl logs -f deployment/alert-query-planner -n ai-agent"
echo ""
echo "按任意鍵退出..."
read -n 1 -s

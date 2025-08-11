#!/bin/bash
# 設定 Workload Identity 的腳本
# 適用於 GKE Autopilot 環境

set -e

PROJECT_ID="cloud-sre-poc-465509"
CLUSTER_NAME="tracing-gke-cluster"
REGION="asia-east1"
NAMESPACE="ai-agent"
KSA_NAME="alert-query-planner-sa"
GSA_NAME="alert-query-planner-sa"

echo "設定 Workload Identity..."

# 1. 創建 Google Service Account (如果不存在)
echo "檢查 Google Service Account: ${GSA_NAME}"
if gcloud iam service-accounts describe ${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com --project=${PROJECT_ID} >/dev/null 2>&1; then
    echo "Google Service Account 已存在，跳過創建"
else
    echo "創建 Google Service Account: ${GSA_NAME}"
    gcloud iam service-accounts create ${GSA_NAME} \
        --project=${PROJECT_ID} \
        --description="Alert Query Planner Service Account for GKE" \
        --display-name="Alert Query Planner SA"
fi

# 2. 授予必要的 IAM 權限 (如果尚未授予)
echo "檢查並授予 IAM 權限..."

# 定義需要的角色
ROLES=("roles/aiplatform.user" "roles/logging.logWriter" "roles/monitoring.metricWriter" "roles/cloudtrace.agent")

for role in "${ROLES[@]}"; do
    echo "檢查角色: $role"
    if gcloud projects get-iam-policy ${PROJECT_ID} --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:serviceAccount:${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com AND bindings.role:$role" | grep -q "$role"; then
        echo "角色 $role 已授予，跳過"
    else
        echo "授予角色: $role"
        gcloud projects add-iam-policy-binding ${PROJECT_ID} \
            --member="serviceAccount:${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
            --role="$role"
    fi
done

# 3. 設定 Workload Identity 繫定 (如果尚未設定)
echo "檢查 Workload Identity 繫定..."
if gcloud iam service-accounts get-iam-policy ${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com --format="value(bindings.members)" | grep -q "serviceAccount:${PROJECT_ID}.svc.id.goog\[${NAMESPACE}/${KSA_NAME}\]"; then
    echo "Workload Identity 繫定已存在，跳過"
else
    echo "設定 Workload Identity 繫定..."
    gcloud iam service-accounts add-iam-policy-binding \
        --role="roles/iam.workloadIdentityUser" \
        --member="serviceAccount:${PROJECT_ID}.svc.id.goog[${NAMESPACE}/${KSA_NAME}]" \
        ${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
fi

echo "Workload Identity 設定完成！"
echo "請確保在部署 YAML 中正確設定 serviceAccountName 和 annotation"

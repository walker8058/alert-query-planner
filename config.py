import os
from dotenv import load_dotenv
load_dotenv()
# 檢查必要環境變數是否都有設定
REQUIRED_ENV_VARS = [
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
]

def check_required_envs(required_vars: list[str] | None = None) -> dict[str, str]:
    """檢查必要的環境變數是否已設定；若缺少則拋出錯誤。回傳變數字典。"""
    vars_to_check = required_vars or REQUIRED_ENV_VARS
    missing = [v for v in vars_to_check if (os.getenv(v) is None or os.getenv(v) == "")]
    if missing:
        raise ValueError(f"以下環境變數未設定: {', '.join(missing)}")
    return {v: os.getenv(v) for v in vars_to_check}

def check_env_ver(var_name, default=None, required=False):
    value = os.getenv(var_name, default)
    if required and value is None:
        raise ValueError(f"環境變數'{var_name}'未設定。")
    return value

MODEL = check_env_ver("MODEL", "gemini-2.5-pro", required=False)
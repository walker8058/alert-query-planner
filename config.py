import os

def check_env_ver(var_name, default=None, required=False):
    value = os.getenv(var_name, default)
    if required and value is None:
        raise ValueError(f"環境變數'{var_name}'未設定。")
    return value

MODEL = check_env_ver("MODEL", "gemini-2.0-flash", required=True)

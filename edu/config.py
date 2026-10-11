"""团队配置：优先读取本机api_config.json；没有该文件时兼容环境变量。"""
import json
import os
from .bank import ROOT
KEYS={'EDU_AI_PROVIDER','MOONSHOT_API_KEY','MOONSHOT_MODEL','MOONSHOT_BASE_URL','EDU_OLLAMA_MODEL'}

def ai_config(path=None):
    path=path or ROOT/'api_config.json'
    try:
        with path.open(encoding='utf-8-sig') as f:
            text=f.read(16385)
        if len(text)>16384: raise ValueError('配置过长')
        values=json.loads(text)
        if not isinstance(values,dict) or any(k in values and not isinstance(values[k],str) for k in KEYS):
            raise ValueError('配置字段必须是字符串')
        result={k:values[k].strip() for k in KEYS if k in values}
        result.setdefault('EDU_AI_PROVIDER','kimi')
        return result
    except FileNotFoundError:
        return {key:os.environ[key].strip() for key in KEYS if key in os.environ}
    except (OSError,ValueError,UnicodeError):
        # 文件错误不能悄悄切换到环境变量里的另一把密钥。
        return {'EDU_AI_PROVIDER':'kimi','MOONSHOT_API_KEY':''}

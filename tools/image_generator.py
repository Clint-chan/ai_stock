import urllib.parse
import requests
from PIL import Image
import io
from langchain.tools import tool
from .utils.image_utils import display_image


@tool
def draw_image(prompt: str) -> str:
    """根据描述生成图片。输入一段描述文字，将直接显示图片。"""
    try:
        prompt = prompt.strip('"\'').strip()
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        img = Image.open(io.BytesIO(response.content))
        display_image(img, prompt)

        return f"图片已生成并显示"

    except requests.Timeout:
        return "生成图片超时，请重试"
    except requests.RequestException as e:
        return f"网络请求错误: {str(e)}"
    except Exception as e:
        return f"生成图片失败: {str(e)}"

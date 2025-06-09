import os
import requests
from io import BytesIO

def download_noto_sans_jp():
    """Noto Sans JPフォントをダウンロードする"""
    font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansJP-Regular.otf"
    font_path = "assets/NotoSansJP-Regular.otf"
    
    # assetsディレクトリがなければ作成
    os.makedirs('assets', exist_ok=True)
    
    # すでにフォントがあれば何もしない
    if os.path.exists(font_path):
        print(f"Font already exists at {font_path}")
        return font_path
    
    try:
        # フォントをダウンロード
        print(f"Downloading font from {font_url}...")
        response = requests.get(font_url)
        response.raise_for_status()
        
        # ファイルに保存
        with open(font_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Font downloaded to {font_path}")
        return font_path
    
    except Exception as e:
        print(f"Error downloading font: {e}")
        # ダウンロードに失敗した場合はシステムのデフォルトフォントを使用
        print("Using system default font instead")
        return None

if __name__ == "__main__":
    download_noto_sans_jp()
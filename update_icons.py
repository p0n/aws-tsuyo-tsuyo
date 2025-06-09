#!/usr/bin/env python3
import os
import random
import shutil
from PIL import Image

# AWSアイコンのディレクトリ
AWS_ICONS_DIR = "./Architecture-Service-Icons_02072025"
# アイコンを保存するディレクトリ
OUTPUT_DIR = "./assets"
# 選択するアイコンの数
NUM_ICONS = 20
# アイコンのサイズ
ICON_SIZE = (50, 50)

def find_aws_icons():
    """AWSアイコンを検索する"""
    icons = []
    # 各カテゴリディレクトリを探索
    for category in os.listdir(AWS_ICONS_DIR):
        category_path = os.path.join(AWS_ICONS_DIR, category)
        if os.path.isdir(category_path) and category.startswith("Arch_"):
            # 64x64サイズのアイコンを探す
            icon_dir = os.path.join(category_path, "64")
            if os.path.exists(icon_dir):
                for icon in os.listdir(icon_dir):
                    if icon.endswith("_64.png"):
                        icons.append(os.path.join(icon_dir, icon))
    return icons

def update_icons():
    """アイコンを更新する"""
    # 既存のアイコンを削除
    for file in os.listdir(OUTPUT_DIR):
        if file.startswith("icon_") and file.endswith(".png"):
            os.remove(os.path.join(OUTPUT_DIR, file))
    
    # AWSアイコンを検索
    aws_icons = find_aws_icons()
    print(f"Found {len(aws_icons)} AWS icons")
    
    # ランダムに選択
    if len(aws_icons) > NUM_ICONS:
        selected_icons = random.sample(aws_icons, NUM_ICONS)
    else:
        selected_icons = aws_icons
    
    # アイコンをコピーしてリサイズ
    for i, icon_path in enumerate(selected_icons):
        output_path = os.path.join(OUTPUT_DIR, f"icon_{i}.png")
        try:
            # PILを使用してリサイズ
            img = Image.open(icon_path)
            img = img.resize(ICON_SIZE)
            img.save(output_path)
            print(f"Saved {output_path}")
        except Exception as e:
            print(f"Error processing {icon_path}: {e}")
    
    print(f"Updated {len(selected_icons)} icons")

if __name__ == "__main__":
    # assetsディレクトリが存在することを確認
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    update_icons()
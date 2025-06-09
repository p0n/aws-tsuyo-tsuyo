import os
import random
from PIL import Image, ImageDraw, ImageFont

# AWSサービス名のリスト
AWS_SERVICES = [
    "EC2", "S3", "Lambda", "DynamoDB", "RDS", "CloudWatch", 
    "SNS", "SQS", "API Gateway", "CloudFront", "Route53", "VPC", 
    "IAM", "Elastic Beanstalk", "CloudFormation", "CodeCommit", 
    "CodeBuild", "CodePipeline", "ECS", "EKS", "Fargate", 
    "Step Functions", "EventBridge", "Secrets Manager"
]

# 色のリスト
COLORS = [
    (255, 153, 0),    # AWS Orange
    (35, 47, 62),     # AWS Dark Gray
    (68, 138, 255),   # Blue
    (252, 108, 133),  # Pink
    (118, 195, 65),   # Green
    (189, 99, 197),   # Purple
    (255, 193, 7),    # Yellow
    (0, 176, 255),    # Light Blue
    (255, 87, 34),    # Deep Orange
    (0, 150, 136),    # Teal
]

def create_aws_icon(service_name, size=(50, 50), bg_color=None):
    """
    AWSサービスのダミーアイコンを作成
    """
    if bg_color is None:
        bg_color = random.choice(COLORS)
    
    # 画像を作成
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # テキストを描画（サービス名の頭文字）
    try:
        # フォントがない場合はデフォルトフォントを使用
        font = ImageFont.truetype("Arial", 20)
    except IOError:
        font = ImageFont.load_default()
    
    # サービス名の頭文字を取得
    initials = ''.join([word[0] for word in service_name.split() if word])
    if len(initials) > 2:
        initials = initials[:2]
    
    # テキストのサイズを計算
    text_width, text_height = draw.textsize(initials, font=font) if hasattr(draw, 'textsize') else (20, 20)
    
    # テキストを中央に配置
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # テキストを描画
    draw.text(position, initials, fill=(255, 255, 255), font=font)
    
    return img

def download_icons(count=4, size=(50, 50)):
    """
    指定された数のAWSアイコンを作成して返す
    """
    # アイコンを保存するディレクトリを作成
    os.makedirs('assets', exist_ok=True)
    
    # ランダムにサービスを選択
    selected_services = random.sample(AWS_SERVICES, min(count, len(AWS_SERVICES)))
    icon_paths = []
    
    for i, service in enumerate(selected_services):
        try:
            # アイコンを作成
            img = create_aws_icon(service, size)
            
            # ファイルに保存
            icon_path = f'assets/icon_{i}.png'
            img.save(icon_path)
            icon_paths.append(icon_path)
            
        except Exception as e:
            print(f"Error creating icon for {service}: {e}")
    
    return icon_paths

if __name__ == "__main__":
    # テスト用に4つのアイコンを作成
    icons = download_icons(4)
    print(f"Created {len(icons)} icons: {icons}")
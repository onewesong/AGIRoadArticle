import markdown
import os
from pathlib import Path
import re
import shutil
from datetime import datetime

def convert_md_to_wechat(md_file_path, output_dir='wechat_html'):
    """将 Markdown 文件转换为微信友好的 HTML"""
    
    # 读取 Markdown 文件
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 创建 Markdown 转换器
    md = markdown.Markdown(extensions=[
        'meta',
        'tables',
        'fenced_code',
        'codehilite',
        'toc'
    ])
    
    # 转换 Markdown 为 HTML
    html_content = md.convert(md_content)
    
    # 处理图片路径
    html_content = process_images(html_content, md_file_path, output_dir)
    
    # 添加样式
    html_content = wrap_with_style(html_content)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成输出文件路径
    output_file = Path(output_dir) / f"{Path(md_file_path).stem}.html"
    
    # 写入 HTML 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_file

def process_images(html_content, md_file_path, output_dir):
    """处理文章中的图片"""
    md_dir = Path(md_file_path).parent
    img_pattern = r'<img[^>]*src="([^"]*)"[^>]*>'
    
    def replace_img(match):
        img_path = match.group(1)
        if img_path.startswith('http'):
            return match.group(0)
        
        # 处理相对路径
        abs_img_path = md_dir / img_path
        if not abs_img_path.exists():
            return match.group(0)
        
        # 复制图片到输出目录
        img_output_dir = Path(output_dir) / 'images'
        os.makedirs(img_output_dir, exist_ok=True)
        new_img_path = img_output_dir / abs_img_path.name
        shutil.copy2(abs_img_path, new_img_path)
        
        # 更新图片标签
        return f'<img src="images/{abs_img_path.name}" style="max-width:100%;height:auto;">'
    
    return re.sub(img_pattern, replace_img, html_content)

def wrap_with_style(html_content):
    """添加微信文章样式"""
    css = """
    <style>
        .wechat-article {
            font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
            color: #333;
            line-height: 1.6;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        h1, h2, h3, h4 {
            color: #222;
            margin-top: 20px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        h1 { font-size: 24px; }
        h2 { font-size: 20px; }
        h3 { font-size: 18px; }
        p { margin: 15px 0; }
        code {
            background: #f6f6f6;
            border-radius: 3px;
            padding: 2px 5px;
            font-family: Consolas, monospace;
        }
        pre {
            background: #f6f6f6;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        pre code {
            background: none;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #42b983;
            margin: 15px 0;
            padding: 10px 15px;
            background-color: #f8f8f8;
        }
        img {
            max-width: 100%;
            height: auto;
            margin: 15px 0;
            border-radius: 5px;
        }
        ul, ol {
            padding-left: 20px;
            margin: 15px 0;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f6f6f6;
        }
    </style>
    """
    
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {css}
    </head>
    <body>
        <div class="wechat-article">
            {html_content}
        </div>
    </body>
    </html>
    """
    
    return template

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python md2wechat.py <markdown_file>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    output_file = convert_md_to_wechat(md_file)
    print(f"已生成微信文章HTML: {output_file}") 
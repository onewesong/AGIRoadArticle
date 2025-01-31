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
    
    # 处理外部链接为脚注
    html_content = process_links_to_footnotes(html_content)
    
    # 添加样式
    html_content = wrap_with_style(html_content)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成输出文件路径
    output_file = Path(output_dir) / f"{Path(md_file_path).stem}.html"
    
    # 写入 HTML 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n提示: 请查看 {output_dir}/upload_guide.md 获取图片上传指南")
    return output_file

def process_images(html_content, md_file_path, output_dir):
    """处理文章中的图片,生成上传清单"""
    md_dir = Path(md_file_path).parent
    img_pattern = r'<img[^>]*src="([^"]*)"[^>]*>'
    
    # 用于记录需要上传的图片
    images_to_upload = []
    
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
        
        # 记录需要上传的图片
        images_to_upload.append({
            'file_path': str(new_img_path),
            'placeholder': f'{{{{图片_{len(images_to_upload)+1}}}}}',
            'original_name': abs_img_path.name
        })
        
        # 使用占位符替换图片
        return f'<img src="{images_to_upload[-1]["placeholder"]}" style="max-width:100%;height:auto;">'
    
    html_content = re.sub(img_pattern, replace_img, html_content)
    
    # 生成图片上传指南
    if images_to_upload:
        upload_guide = generate_upload_guide(images_to_upload)
        with open(Path(output_dir) / 'upload_guide.md', 'w', encoding='utf-8') as f:
            f.write(upload_guide)
    
    return html_content

def generate_upload_guide(images):
    """生成图片上传指南"""
    guide = """# 微信图片上传指南

请按照以下步骤操作:

1. 打开微信公众号后台
2. 进入"素材管理" -> "图片素材"
3. 按顺序上传以下图片:

"""
    for i, img in enumerate(images, 1):
        guide += f"\n## 图片 {i}\n"
        guide += f"- 文件路径: {img['file_path']}\n"
        guide += f"- 原始文件名: {img['original_name']}\n"
        guide += f"- 上传后将文章中的 `{img['placeholder']}` 替换为上传后的图片\n"
    
    guide += """
\n## 注意事项
- 请按顺序上传图片并替换占位符
- 建议在预览模式下检查图片是否正确显示
- 图片上传后会自动压缩,可在预览中确认效果
"""
    return guide

def process_links_to_footnotes(html_content):
    """将外部链接转换为脚注格式"""
    link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
    footnotes = []
    
    def replace_link(match):
        url = match.group(1)
        text = match.group(2)
        
        # 跳过内部链接和图片链接
        if url.startswith('#') or url.startswith('/') or text.strip().startswith('<img'):
            return match.group(0)
            
        # 跳过邮件链接
        if url.startswith('mailto:'):
            return text
        
        # 添加脚注
        footnote_index = len(footnotes) + 1
        footnotes.append(url)
        
        # 返回带有脚注标记的文本
        return f'{text}<sup>[{footnote_index}]</sup>'
    
    # 替换链接
    html_content = re.sub(link_pattern, replace_link, html_content)
    
    # 如果有脚注，添加脚注部分
    if footnotes:
        footnote_html = '\n<hr style="margin-top: 40px; margin-bottom: 20px;">\n'
        footnote_html += '<ol style="font-size: 14px; color: #666; padding-left: 20px;">\n'
        for i, url in enumerate(footnotes, 1):
            footnote_html += f'<li id="fn{i}">链接: {url}</li>\n'
        footnote_html += '</ol>\n'
        
        # 在文章末尾添加脚注
        html_content += footnote_html
    
    return html_content

def wrap_with_style(html_content):
    """添加微信文章样式"""
    css = """
    <style>
        /* 微信编辑器特殊样式 */
        .wechat-article {
            color: #333;
            line-height: 1.8;
            font-size: 16px;
            word-wrap: break-word;
        }
        
        /* 代码块样式优化 */
        .highlight {
            background: #f8f8f8;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
            font-size: 14px;
            color: #333;
            border: 1px solid #e8e8e8;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        /* 引用块样式 */
        blockquote {
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #42b983;
            background: #f8f8f8;
            color: #666;
        }
        
        /* 标题样式优化 */
        h1 {
            font-size: 24px;
            margin-top: 40px;
            margin-bottom: 20px;
            font-weight: bold;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        
        h2 {
            font-size: 20px;
            margin-top: 30px;
            margin-bottom: 15px;
            font-weight: bold;
        }
        
        h3 {
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        
        /* 列表样式优化 */
        ul, ol {
            padding-left: 28px;
            margin: 15px 0;
        }
        
        /* 链接样式 */
        a {
            color: #42b983;
            text-decoration: none;
        }
        
        /* 图片样式优化 */
        img {
            max-width: 100% !important;
            height: auto !important;
            margin: 20px auto;
            display: block;
        }
        
        /* 表格样式优化 */
        table {
            border-collapse: collapse;
            margin: 15px 0;
            width: 100%;
            display: block;
            overflow-x: auto;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px 15px;
            text-align: left;
        }
        
        th {
            background-color: #f8f8f8;
            font-weight: bold;
        }
        
        /* 行内代码样式 */
        code {
            background: #f3f3f3;
            padding: 2px 5px;
            border-radius: 3px;
            color: #e96900;
            font-family: Consolas, monospace;
        }
        
        /* 段落间距优化 */
        p {
            margin: 15px 0;
            line-height: 1.8;
        }
        
        /* 脚注样式 */
        sup {
            font-size: 12px;
            color: #42b983;
            margin: 0 2px;
        }
        
        hr {
            border: none;
            border-top: 1px solid #eee;
        }
        
        /* 脚注列表样式 */
        ol li {
            color: #666;
            font-size: 14px;
            margin: 8px 0;
        }
    </style>
    """
    
    # 处理代码块的语法高亮
    html_content = html_content.replace('<pre><code>', '<pre class="highlight"><code>')
    
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
        <p style="text-align: center; color: #999; font-size: 14px; margin-top: 40px;">
            - EOF -
        </p>
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
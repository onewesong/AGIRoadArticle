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
    
    # 预处理 Markdown 内容，确保列表格式正确
    md_content = preprocess_markdown(md_content)
    
    # 创建 Markdown 转换器，添加额外的扩展
    md = markdown.Markdown(extensions=[
        'meta',
        'tables',
        'fenced_code',
        'codehilite',
        'toc',
        'nl2br',        # 添加换行支持
        'sane_lists',   # 添加更好的列表支持
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
    
    return output_file

def process_images(html_content, md_file_path, output_dir):
    """处理文章中的图片,上传并替换图片链接"""
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
            
        # 记录需要上传的图片
        images_to_upload.append(str(abs_img_path))
        
        # 暂时使用原始文件名作为占位符
        return f'<img src="{{{{IMAGE_PLACEHOLDER_{abs_img_path.name}}}}}" style="max-width:100%;height:auto;">'
    
    html_content = re.sub(img_pattern, replace_img, html_content)
    
    # 如果有图片需要上传
    if images_to_upload:
        try:
            # 调用上传脚本
            image_urls = upload_images(images_to_upload)
            
            # 替换占位符为实际的图片URL
            for img_path in images_to_upload:
                img_name = Path(img_path).name
                if img_name in image_urls:
                    placeholder = f'{{{{IMAGE_PLACEHOLDER_{img_name}}}}}'
                    html_content = html_content.replace(placeholder, image_urls[img_name])
        except Exception as e:
            print(f"警告: 图片上传失败 - {str(e)}")
            # 如果上传失败，使用本地图片路径
            for img_path in images_to_upload:
                img_name = Path(img_path).name
                placeholder = f'{{{{IMAGE_PLACEHOLDER_{img_name}}}}}'
                html_content = html_content.replace(placeholder, f'images/{img_name}')
    
    return html_content

def upload_images(image_paths):
    """调用upload_image.sh脚本上传图片"""
    import subprocess
    import os
    import json
    
    # 获取IMAGE_SRC_PREFIX环境变量
    image_src_prefix = os.getenv('IMAGE_SRC_PREFIX')
    if not image_src_prefix:
        raise ValueError("环境变量 IMAGE_SRC_PREFIX 未设置")
    
    # 准备上传脚本路径
    script_path = Path(__file__).parent / 'upload_image.sh'
    if not script_path.exists():
        raise FileNotFoundError(f"上传脚本不存在: {script_path}")
    
    # 调用上传脚本
    try:
        cmd = [str(script_path)] + image_paths
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # 处理上传结果
        image_urls = {}
        for img_path in image_paths:
            img_name = Path(img_path).name
            image_urls[img_name] = f"{image_src_prefix}/{img_name}"
            
        return image_urls
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"图片上传失败: {e.stderr}")

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
            position: relative;
            font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
        }
        
        /* 代码语言标签 */
        .highlight::before {
            content: attr(data-language);
            position: absolute;
            top: 0;
            right: 0;
            padding: 2px 8px;
            font-size: 12px;
            color: #666;
            background: #e8e8e8;
            border-radius: 0 4px 0 4px;
        }
        
        /* 代码高亮样式 */
        .highlight .keyword { color: #c678dd; }  /* 关键字 */
        .highlight .builtin { color: #56b6c2; }  /* 内置函数 */
        .highlight .string { color: #98c379; }   /* 字符串 */
        .highlight .number { color: #d19a66; }   /* 数字 */
        .highlight .comment { color: #5c6370; font-style: italic; }  /* 注释 */
        .highlight .operator { color: #56b6c2; } /* 运算符 */
        .highlight .function { color: #61afef; } /* 函数名 */
        .highlight .class { color: #e5c07b; }    /* 类名 */
        .highlight .variable { color: #e06c75; } /* 变量 */
        
        /* 特定语言的样式 */
        .language-python .decorator { color: #56b6c2; }
        .language-javascript .regex { color: #98c379; }
        .language-html .tag { color: #e06c75; }
        .language-html .attr { color: #d19a66; }
        .language-css .property { color: #56b6c2; }
        .language-css .value { color: #98c379; }
        
        /* 行内代码样式 */
        code:not(.highlight code) {
            background: #f3f3f3;
            padding: 2px 5px;
            border-radius: 3px;
            color: #e96900;
            font-family: Consolas, Monaco, monospace;
            font-size: 0.9em;
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
            color: #2c3e50;  /* 深蓝灰色 */
        }
        
        h2 {
            font-size: 20px;
            margin-top: 30px;
            margin-bottom: 15px;
            font-weight: bold;
            color: #34495e;  /* 稍浅的蓝灰色 */
        }
        
        h3 {
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
            font-weight: bold;
            color: #3498db;  /* 蓝色 */
        }
        
        h4 {
            font-size: 16px;
            margin-top: 15px;
            margin-bottom: 8px;
            font-weight: bold;
            color: #2980b9;  /* 深蓝色 */
        }
        
        /* 加粗文本样式 */
        strong {
            color: #e67e22;  /* 橙色 */
            font-weight: bold;
            padding: 0 2px;  /* 左右添加小间距 */
        }
        
        /* 强调文本悬停效果 */
        strong:hover {
            background-color: rgba(230, 126, 34, 0.1);  /* 橙色背景，低透明度 */
            border-radius: 2px;
            transition: background-color 0.3s ease;
        }
        
        /* 标题悬停效果 */
        h1:hover, h2:hover, h3:hover, h4:hover {
            background: linear-gradient(to right, rgba(52, 152, 219, 0.1), transparent);
            border-radius: 4px;
            transition: background 0.3s ease;
        }
        
        /* 标题前的装饰 */
        h2::before {
            content: "##";
            color: #bdc3c7;
            margin-right: 8px;
            font-weight: normal;
            opacity: 0.6;
        }
        
        h3::before {
            content: "###";
            color: #bdc3c7;
            margin-right: 8px;
            font-weight: normal;
            opacity: 0.6;
        }
        
        /* 增强列表样式 */
        ul, ol {
            padding-left: 28px;
            margin: 15px 0;
            list-style-position: outside;
        }
        
        ul li, ol li {
            margin: 8px 0;
            line-height: 1.6;
            position: relative;
            display: list-item !important;
            text-align: -webkit-match-parent;
        }
        
        ul li {
            list-style: disc !important;
        }
        
        ul ul li {
            list-style: circle !important;
        }
        
        ul ul ul li {
            list-style: square !important;
        }
        
        ol li {
            list-style: decimal !important;
        }
        
        /* 确保列表项之间有足够的间距 */
        li + li {
            margin-top: 8px;
        }
        
        /* 确保列表项内容正确换行 */
        li p {
            margin: 0;
            display: inline-block;
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
    </style>
    """
    
    def process_code_blocks(html):
        """处理代码块，添加语言标识和高亮"""
        # 匹配代码块的正则表达式
        code_block_pattern = r'<pre class="highlight"><code class="language-([^"]+)">(.*?)</code></pre>'
        
        def replace_code_block(match):
            language = match.group(1)
            code = match.group(2)
            
            # 添加语言标识和类名
            return f'<pre class="highlight language-{language}" data-language="{language}"><code class="language-{language}">{code}</code></pre>'
        
        return re.sub(code_block_pattern, replace_code_block, html, flags=re.DOTALL)
    
    # 处理代码块
    html_content = process_code_blocks(html_content)
    
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {css}
        <!-- 添加 highlight.js 支持 -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-light.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', (event) => {{
                document.querySelectorAll('pre code').forEach((block) => {{
                    hljs.highlightBlock(block);
                }});
            }});
        </script>
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

def preprocess_markdown(content):
    """预处理 Markdown 内容，确保列表格式正确"""
    lines = content.split('\n')
    processed_lines = []
    
    for i, line in enumerate(lines):
        # 处理列表项
        if line.strip().startswith('- '):
            # 如果前一行不是空行且不是列表项，添加一个空行
            if i > 0 and not lines[i-1].strip() == '' and not lines[i-1].strip().startswith('- '):
                processed_lines.append('')
            # 确保列表项有正确的缩进和格式
            processed_lines.append(line)
            # 如果下一行不是列表项且不是空行，添加一个空行
            if i < len(lines)-1 and not lines[i+1].strip().startswith('- ') and not lines[i+1].strip() == '':
                processed_lines.append('')
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python md2wechat.py <markdown_file>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    output_file = convert_md_to_wechat(md_file)
    print(f"已生成微信文章HTML: {output_file}") 
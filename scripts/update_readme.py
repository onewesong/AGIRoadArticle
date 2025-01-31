import re
from pathlib import Path
import yaml
from datetime import datetime

def extract_frontmatter(content):
    """提取文章的 frontmatter 信息"""
    pattern = r'^---\n(.*?)\n---'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    return None

def get_articles():
    """获取 articles 目录下的所有文章"""
    articles_dir = Path('articles')
    if not articles_dir.exists():
        return []
    
    articles = []
    for file in articles_dir.glob('**/*.md'):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = extract_frontmatter(content)
        if metadata:
            articles.append({
                'path': str(file.relative_to('.')),
                'title': metadata.get('title', file.stem),
                'date': metadata.get('date'),
                'category': metadata.get('category', '未分类'),
            })
    
    # 按日期排序
    articles.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
    return articles

def generate_article_list():
    """生成文章列表的 Markdown 内容"""
    articles = get_articles()
    
    # 按分类组织文章
    categories = {}
    for article in articles:
        category = article['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(article)
    
    # 生成 Markdown 内容
    content = []
    
    for category, category_articles in categories.items():
        content.append(f"### {category}")
        for article in category_articles:
            date_str = article['date'].strftime('%Y-%m-%d') if article['date'] else ''
            content.append(f"- [{article['title']}]({article['path']}) {date_str}")
        content.append("")
    
    return "\n".join(content)

def update_readme():
    """更新 README.md 文件"""
    template_path = 'readme_template.md'
    readme_path = 'README.md'
    
    # 读取模板
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 生成文章列表
    article_list = generate_article_list()
    
    # 替换模板中的占位符
    new_content = template_content.replace('{article_list}', article_list.strip())
    
    # 写入 README.md
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == '__main__':
    update_readme()
    print("README.md 更新完成") 
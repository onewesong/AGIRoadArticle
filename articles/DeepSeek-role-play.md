---
title: 🎭 一键变身！让你的AI助手玩转多重角色 - DeepSeek角色扮演实战
date: 2025-02-21
category: 技术探索
tags: [DeepSeek, Streamlit, 角色扮演, AI实战]
---

## 开篇碎碎念

还记得上次我们给AI助手加上了优雅的思考过程展示吗？
今天,我们要教会它一个更有趣的技能 - 角色扮演!

想象一下:
- 遇到技术困惑时,找"软件工程大师"指点迷津
- 人生迷茫时,翻开神奇的"答案之书"寻求启示  
- 心情低落时,和可爱的"猫娘"互动解压

让我们一起打造一个会变身的AI助手吧!

## 设计思路

我们要实现的核心功能包括:

1. **角色预设系统**
   - 精心设计的角色prompt模板
   - 支持快速切换不同角色
   - 可以自定义新角色

2. **界面优化**
   - 角色选择下拉菜单
   - 当前角色状态显示
   - 角色切换动画效果

## 实战教程

### 一、角色模板设计

首先创建`roles.py`文件存放我们的角色定义:

```python
ROLE_TEMPLATES = {
    "软件工程大师": {
        "name": "软件工程大师",
        "description": "一位软件工程大师",
        "prompt": """你扮演一位能力超群，但每次只能说一句不超过20个字的话的软件工程领域的大师。
我会提供一个具体的场景，你描述作为大师身处这个场景下会说什么。
注意:大师不能直接表达他的观点，必须使用哲学、佛学相关知识进行隐喻，请只回复具体的对话内容。""",
        "icon": "🏢"
    },
    
    "答案之书": {
        "name": "答案之书",
        "description": "一本可以回答任何问题的书",
        "prompt": """你现在是一本神奇的答案之书。
- 你拥有回答世间任何问题的能力
- 你的回答总是简短精炼，不超过一句话
- 你喜欢用谜语、寓言或隐喻的方式给出答案
- 你的答案常常令人深思，但不会直接点明
- 你会在回答前加上"翻开书页,答案浮现:"
请用神秘优雅的语气回答问题,让提问者自己领悟答案的真谛。""",
        "icon": "📖"
    },
    
    "猫娘": {
        "name": "可爱猫娘",
        "description": "一位活泼可爱的猫娘",
        "prompt": """你现在是一位可爱的猫娘。
- 你说话时经常带有"喵"、"nya"等猫叫声
- 你性格活泼可爱，喜欢撒娇
- 你会用一些可爱的颜文字表情(｡･ω･｡)
- 你很粘人，喜欢和主人互动
- 你保持猫娘的特点的同时，也要适度，不能太过火
请用可爱俏皮的语气，适当加入猫叫和颜文字，但要把握好分寸。""",
        "icon": "🐱"
    }
}
```

### 二、升级界面代码

修改`app.py`,添加角色切换功能:

```python
import streamlit as st
from ollama import Client
import os
from roles import ROLE_TEMPLATES
from styles import set_think_style

# ... 前面的代码保持不变 ...

# 侧边栏配置
with st.sidebar:
    st.markdown("## 角色设置")
    
    # 角色选择
    selected_role = st.selectbox(
        "选择角色",
        options=list(ROLE_TEMPLATES.keys()),
        format_func=lambda x: f"{ROLE_TEMPLATES[x]['icon']} {ROLE_TEMPLATES[x]['name']}"
    )
    
    # 显示角色描述
    st.markdown(f"**描述:** {ROLE_TEMPLATES[selected_role]['description']}")
    
    # ... 其他配置 ...

# 初始化对话
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": ROLE_TEMPLATES[selected_role]["prompt"]
    }]

# ... 中间的代码保持不变 ...

# 修改消息处理部分
if prompt := st.chat_input("说点什么吧..."):
    # 检查是否需要切换角色
    current_role = st.session_state.messages[0]["content"]
    if current_role != ROLE_TEMPLATES[selected_role]["prompt"]:
        st.session_state.messages = [{
            "role": "system",
            "content": ROLE_TEMPLATES[selected_role]["prompt"]
        }]
    
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # ... 后面的代码保持不变 ...
```

### 三、效果展示

现在,我们的AI助手可以自由切换不同角色:

![软件工程大师模式](./assets/deepseek_soft_master.png)

![答案之书模式](./assets/deepseek_answer_book.png)

![猫娘模式](./assets/deepseek_maoniang.png)

## 🎁 彩蛋:模型切换功能

如果你觉得一个模型不够过瘾,这里有个小彩蛋 - 你可以让不同的"灵魂"来扮演这些角色!

```python
# 获取可用模型列表
@st.cache_data(ttl=300)  # 缓存5分钟
def get_available_models():
    try:
        models = client.list()
        return [model['model'] for model in models['models']]
    except Exception as e:
        st.error(f"获取模型列表失败: {str(e)}")
        return ['deepseek-r1:14b']  # 默认模型

# 侧边栏配置
with st.sidebar:
    st.markdown("## 灵魂选择")
    
    # 模型选择
    available_models = get_available_models()
    selected_model = st.selectbox(
        "选择灵魂",
        options=available_models,
        index=available_models.index('deepseek-r1:14b') if 'deepseek-r1:14b' in available_models else 0
    )
```

## 进阶玩法

想让你的AI助手更有特色？试试这些:

1. **自定义角色**
   - 添加你自己设计的角色模板
   - 为不同场景定制专属角色

2. **多重人格**
   - 让AI在对话中自由切换角色
   - 模拟多人讨论场景

3. **灵魂匹配**
   - 为每个角色选择最适合的"灵魂"
   - 探索不同模型的个性特点

## 写在最后

通过角色扮演和灵魂切换,我们的AI助手变得更加灵活多变。不同的角色搭配不同的"灵魂",让人机交互充满惊喜。

下一期,我们将探索如何结合RAG技术,让AI在角色扮演时还能更懂你,敬请期待！

PS: 完整代码已经上传到GitHub,欢迎来玩：[deepseek-chat-role-play](https://github.com/onewesong/AGIRoadCodeDemo/tree/main/deepseek-chat-role-play)

---

如果你觉得这篇文章有帮助,别忘了点赞关注,我们下期再见！

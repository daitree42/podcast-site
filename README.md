# 播客笔记 · 转录存档站

播客转录存档站，基于静态生成器自动构建。

## 目录结构

```
├── src/                    ← 生成器源码（日常维护在这里）
│   ├── build.py            ← 构建脚本
│   ├── requirements.txt
│   ├── data/shows.yaml     ← 节目配置（名称/简介/分类/颜色）
│   ├── content/            ← 文字稿 Markdown 文件
│   │   └── <show-slug>/
│   │       └── YYYY-MM-DD-title.md
│   ├── templates/          ← Jinja2 页面模板
│   └── static/             ← CSS / JS 源文件
├── index.html              ← 生成后的首页（无需手动编辑）
├── show/                   ← 生成后的节目页
├── episode/                ← 生成后的单集页
├── updates/                ← 生成后的更新时间线
└── static/                 ← 生成后的静态资源
```

## 日常维护

### 新增一篇文字稿

在 `src/content/<节目slug>/` 下新建 `.md` 文件，格式如下：

```markdown
---
title: 中文标题
date: 2026-07-29
show: the-daily              # 必须和 shows.yaml 里的 slug 一致
summary: 一两句话的摘要
tags: [标签1, 标签2]
source_episode: 原始期数
source_url: https://...
processed_date: 2026-07-29
original_language: EN
---

## 正文开始

Markdown 内容……
```

### 重新生成并部署

```bash
pip install -r src/requirements.txt
python src/build.py
git add -A
git commit -m "新增文字稿：xxx"
git push
```

## 功能

- 🔍 实时搜索（标题/节目/摘要/标签）
- 🏷️ 分类筛选（历史/科技/新闻时事/深度调查/财经…）
- 🆕 最近更新区块 + NEW 角标
- 📋 全部更新时间线页
- 🌙 深色模式自动适配
- 📊 自动统计节目数和文字稿数

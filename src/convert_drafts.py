#!/usr/bin/env python3
"""
把 blog-pages/articles/ 下的播客文字稿批量转换为 podcast-site content 格式。
"""

import re
from pathlib import Path

DRAFTS_DIR = Path("C:/cc/blog-pages/articles")
CONTENT_DIR = Path("C:/cc/podcast-site/src/content")

# slug 映射
SHOW_MAP = {
    "the daily（纽约时报）": "the-daily",
    "the daily": "the-daily",
    "this american life（美国生活）": "this-american-life",
    "this american life": "this-american-life",
}

# 要转换的目录列表（手动指定，避免误转换非播客文章）
TARGET_DIRS = [
    "2026-07-28-The_Daily-Can_a_Bad_Man_Be_a_Good_F",
    "2026-07-28-The_Daily-Cuba_Under_Siege",
    "2026-07-28-The_Daily-The_Mother_Who_Changed_a",
    "2026-07-28-The_Daily-What_AI_Is_Actually_Doing",
    "2026-07-28-The_Daily-What_Do_You_Do_When_a_Fam",
    "2026-07-28-The_Daily-Why_Do_Some_Memories_Surv",
    "892_Trapped_on_a_Bus",
]


def strip_common_tags(tags_str):
    """清洗标签"""
    if not tags_str:
        return []
    tags = re.split(r"[，,、]", tags_str)
    tags = [t.strip() for t in tags if t.strip()]
    skip = {"播客", "podcast", "翻译", "Podcast"}
    return [t for t in tags if t not in skip]


def extract_summary(text):
    """从 blockquote 中提取摘要"""
    # 尝试多种格式
    m = re.search(r">\s*\*\*摘要[：:]\*\*\s*(.+?)(?:\n>|\n\n|$)", text)
    if m:
        return m.group(1).strip()
    m = re.search(r">\s*\*\*本期摘要[：:]\*\*\s*(.+?)(?:\n>|\n\n|$)", text)
    if m:
        return m.group(1).strip()
    return ""


def convert():
    for dirname in TARGET_DIRS:
        draft_path = DRAFTS_DIR / dirname / "draft.md"
        if not draft_path.exists():
            print(f"[SKIP] {dirname}: draft.md 不存在")
            continue

        text = draft_path.read_text("utf-8")

        # --- 提取标题 ---
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else dirname

        # --- 提取元数据 ---
        # show name
        show_m = re.search(r">\s*\*\*播客[：:]\*\*\s*(.+)", text)
        show_name = show_m.group(1).strip().lower() if show_m else ""
        slug = SHOW_MAP.get(show_name, "")

        # date
        date_m = re.search(r">\s*\*\*日期[：:]\*\*\s*(\d{4}-\d{2}-\d{2})", text)
        date_str = date_m.group(1) if date_m else "2026-01-01"

        # episode
        ep_m = re.search(r">\s*\*\*期数[：:]\*\*\s*(.+)", text)
        episode = ep_m.group(1).strip() if ep_m else ""

        # source url
        url_m = re.search(r">\s*\*\*原始链接[：:]\*\*\s*\[.+?\]\((.+?)\)", text)
        source_url = url_m.group(1) if url_m else ""

        # tags
        tags_m = re.search(r">\s*\*\*标签[：:]\*\*\s*(.+)", text)
        raw_tags = tags_m.group(1) if tags_m else ""
        tags = strip_common_tags(raw_tags)

        # summary
        summary = extract_summary(text)

        if not slug:
            print(f"[SKIP] {dirname}: 无法识别播客「{show_name}」，跳过")
            continue

        # --- 提取正文（去掉 frontmatter 和末尾的 --- 部分）---
        body_start = None
        for i, line in enumerate(text.split("\n")):
            if line.startswith("> "):
                continue
            stripped = line.strip()
            if stripped and not stripped.startswith("# "):
                # 找到正文起点（第一行非空、非标题、非 blockquote 的行）
                body_start = text.find(line, text.find("\n> "))
                break

        if body_start is None:
            print(f"[SKIP] {dirname}: 找不到正文")
            continue

        # 找到可选的分隔线 --- 位置（去掉末尾的 Source / 英文原文）
        body_text = text[body_start:]
        # 去掉末尾 --- 及之后的内容
        sep_match = re.search(r"\n---\s*\n", body_text)
        if sep_match:
            body_text = body_text[:sep_match.start()]

        body_text = body_text.strip()

        # --- 构造输出文件 ---
        short_slug = dirname
        short_slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", short_slug)
        short_slug = re.sub(r"[^a-zA-Z0-9-]+", "-", short_slug).strip("-").lower()
        short_slug = short_slug[:60]

        tags_yaml = "[" + ", ".join(f'"{t}"' for t in tags) + "]" if tags else "[]"

        frontmatter = f"""---
title: {title}
date: {date_str}
show: {slug}
summary: {summary}
tags: {tags_yaml}
source_episode: {episode}
source_url: {source_url}
processed_date: {date_str}
original_language: EN
---
"""

        # 写入
        show_dir = CONTENT_DIR / slug
        show_dir.mkdir(parents=True, exist_ok=True)
        out_file = show_dir / f"{date_str}-{short_slug}.md"
        out_file.write_text(frontmatter + "\n" + body_text, encoding="utf-8")
        print(f"[OK] {dirname} → {out_file.relative_to(CONTENT_DIR.parent.parent)}")


if __name__ == "__main__":
    convert()

"""Ticket Assistant Tool

This script assists technical support staff in processing tickets written in
English or Japanese. It detects the language, translates to Chinese if
necessary, and then invokes the OpenAI GPT API to analyse the issue.

The output is saved as Markdown so that it can be viewed or copied easily.

TODO: add FAQ retrieval capability in the future.
"""

import os
import argparse
from langdetect import detect
import openai

# Default model can be overridden via environment variable
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Cache API key for reuse
API_KEY = os.getenv("OPENAI_API_KEY")


def detect_language(text: str) -> str:
    """Detect the language of the input text."""
    try:
        return detect(text)
    except Exception:
        return "unknown"


def translate_to_chinese(text: str) -> str:
    """Translate English or Japanese text to Chinese using OpenAI GPT."""
    openai.api_key = API_KEY
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not set")

    messages = [
        {"role": "system", "content": "You translate English or Japanese to Chinese."},
        {"role": "user", "content": text},
    ]
    resp = openai.ChatCompletion.create(model=DEFAULT_MODEL, messages=messages)
    return resp.choices[0].message.content.strip()


def analyze_ticket(chinese_text: str) -> str:
    """Analyze the Chinese ticket text and return structured markdown."""
    openai.api_key = API_KEY
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not set")

    prompt = (
        "请根据以下工单内容给出分析结果，使用 Markdown 返回并严格按照以下结构排版：\n"
        "🧠 用户问题概括\n"
        "<一到两句概括>\n\n"
        "⚙️ 涉及模块\n"
        "模块列表，每行一个\n\n"
        "🔍 可能原因\n"
        "原因列表，每行一个\n\n"
        "✉️ 推荐英文回复语\n"
        "正式风格\n"
        "<正式英文回复>\n\n"
        "轻松风格\n"
        "<轻松英文回复>"
    )

    messages = [
        {"role": "system", "content": "You are a technical support analysis assistant."},
        {"role": "user", "content": prompt + "\n\n" + chinese_text},
    ]
    resp = openai.ChatCompletion.create(model=DEFAULT_MODEL, messages=messages)
    return resp.choices[0].message.content.strip()


def build_output(original: str, lang: str, chinese: str, analysis: str) -> str:
    """Assemble the final markdown output."""
    sections = [
        f"原始内容（{lang}）",
        original,
        "",
        "中文翻译",
        chinese,
        "",
        "分析结果",
        analysis,
    ]
    return "\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ticket assistant")
    parser.add_argument("--input", required=True, help="Input ticket file path")
    parser.add_argument("--output", required=True, help="Output markdown file path")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        original_text = f.read().strip()

    lang = detect_language(original_text)
    chinese_text = original_text
    if lang in ("en", "ja"):
        chinese_text = translate_to_chinese(original_text)

    analysis = analyze_ticket(chinese_text)
    output_md = build_output(original_text, lang, chinese_text, analysis)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(output_md)


if __name__ == "__main__":
    main()

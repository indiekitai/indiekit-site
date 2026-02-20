---
title: "用 Gemini 做票据识别：从图片到结构化数据的实战"
date: 2026-02-18
description: "传统 OCR 识别率差、字段提取难，用 Gemini Flash 做票据识别，便宜、快、效果够用。"
tags: ["AI", "Gemini", "OCR", "票据识别", "Python"]
featured: false
---

做财务系统时需要自动识别用户上传的票据。传统 OCR 识别率差、字段提取难，试了下 Gemini，效果出奇的好。

---

## 需求场景

公司每月有大量报销票据需要录入：超市采购单、加油票、杂项票据。

人工录入痛点：
- 票据格式五花八门
- 字段位置不固定
- 手写/模糊/褶皱常见

**目标**：上传票据图片 → 自动提取日期、金额、商家、类别

## 为什么选 Gemini Flash

| 方案 | 问题 |
|------|------|
| 传统 OCR（Tesseract） | 识别率低，字段提取要写大量正则 |
| 专用票据 OCR 服务 | 贵，非标准票据效果差 |
| GPT-4V | 效果好但贵，延迟高 |
| **Gemini Flash** | 便宜、快、效果够用 |

## 核心实现

### 1. 定义输出 Schema

关键是让 AI 输出结构化 JSON：

```python
prompt = """
Analyze this receipt image and extract:

{
    "receipt_date": "YYYY-MM-DD",
    "amount": total in cents (e.g., $15.68 → 1568),
    "category": 0=grocery, 1=gas station, 2=other,
    "vendor_name": "merchant name",
    "payment_method": 0=credit, 1=debit, null=unknown
}

Rules:
- If a field cannot be identified, return null
- For amount: Extract TOTAL (including tax), convert to cents
- For date: If only month/day shown, use year {reference_year}
"""
```

**技巧**：
- **金额用分**：避免浮点数问题，`$15.68` → `1568`
- **类别用枚举**：比字符串可靠，直接存数据库
- **允许 null**：比强制猜测更好

### 2. 调用 Gemini

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        prompt,
        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
    ],
)
```

### 3. 解析响应

Gemini 有时会包一层 markdown，需要清理：

```python
def parse_json(text):
    text = text.strip()
    # 清理 ```json ... ```
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        # 容错：正则提取
        match = re.search(r'{[\s\S]*}', text)
        if match:
            return json.loads(match.group())
        raise
```

### 4. 日期推断

票据经常只写 `12/20` 没有年份。传入上下文：

```python
date_hint = f"This receipt belongs to batch {batch_month}."
```

AI 看到 `12/20` + 批次 `2025-12` 会推断为 `2025-12-20`。

## 生产环境处理

```python
# 状态字段
ai_status: 0=待识别, 1=成功, 2=失败

# 异步任务（Celery）
@celery.task
def process_receipt(receipt_id):
    try:
        result = extract_with_gemini(...)
        update(receipt_id, ai_status=1, **result)
    except Exception as e:
        update(receipt_id, ai_status=2, ai_error=str(e))
```

## 效果

| 字段 | 准确率 |
|------|--------|
| 金额 | ~98% |
| 日期 | ~95% |
| 商家 | ~90% |

**成本**：约 $0.001/张，几乎可以忽略

**效率**：比纯人工录入提升 5-10 倍（AI 识别 + 人工确认）

## 踩过的坑

1. **图片太大**：超 20MB 会超时，先压缩
2. **Rate Limit**：批量处理要加延迟
3. **年份推断**：必须给上下文，否则会猜错

## 开源工具

基于这个实践，我做了一个开源工具 [receipt-ocr](https://github.com/indiekitai/receipt-ocr)：

```bash
pip install gemini-receipt-ocr

# CLI
export GEMINI_API_KEY=your_key
receipt-ocr receipt.jpg

# Python
from receipt_ocr import extract
result = extract("receipt.jpg")
```

## 适用场景

✅ 票据格式多样、数量中等（几千/月）
✅ 允许人工复核
✅ 不需要 100% 准确率

❌ 超高准确率要求（金融审计）
❌ 海量数据

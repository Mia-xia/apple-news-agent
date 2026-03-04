# Apple News Agent

一个用于每日生成 **Apple 产品/公司热点速览** 的自动化 Agent，输出风格面向科技媒体与财经简报场景。

## 核心能力

- 每日抓取 Apple 相关新闻源（RSS）
- 自动筛选并排序“热点优先”内容（股价/财报/新品/供应链/监管/爆料）
- 生成中文快讯，支持两段结构：
  - `一、品牌核心动态`
  - `二、社交飙升话题`
- 输出为可直接分发的 Markdown 文稿

## 当前输出规则（已固化）

- 每条必须是完整中文段落
- 不出现英文残缺标题
- 不出现“更多…”“详情见…”等未完成句式
- 不写成碎片化说明句
- 每条控制在约 3-5 行
- 文风为科技媒体 + 财经简报
- 避免模板化重复句式

## 项目结构

- `agent.py`：主流程调度（抓取、过滤、生成、投递）
- `fetchers.py`：新闻抓取器
- `formatter.py`：中文热点文案生成与格式控制
- `delivery.py`：文件/邮件/Slack 投递
- `config.py`：新闻源与关键词配置
- `docs/`：项目文档（API、快速开始、进阶说明）
- `deploy/`：部署文件（`docker-compose.yml`、`apple-news-agent.service`）
- `logs/`：运行日志目录
- `outputs/`：简报输出目录

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

测试模式（仅生成文件，不发送邮件）：

```bash
python3 agent.py --test
```

单次正式执行：

```bash
python3 agent.py --once
```

默认输出文件：

- `outputs/test_briefing.md`（测试模式）
- `outputs/apple_news_brief.md`（正式模式）

## 说明

当前运行环境如无法访问外部 RSS 或翻译服务，测试结果可能为 0 条新闻。项目已在 `formatter.py` 中增加了中文化与热点提炼兜底逻辑，保证格式稳定。

## License

MIT

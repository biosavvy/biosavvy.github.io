# BioSavvy 推广方案

## 🟢 已完成（自动运行中）

| 渠道 | 状态 | 说明 |
|------|------|------|
| Google SEO | ✅ 已提交 | IndexNow 自动提交 24 个 URL，每周日自动 ping |
| Bing/Yandex | ✅ 已提交 | 通过 IndexNow 协议即时索引 |
| RSS Feed | ✅ 已生成 | `feed.xml` 可被 RSS 阅读器发现 |
| 结构化数据 | ✅ Schema.org | Google 可识别网站类型 |
| 社交分享标签 | ✅ og:image + twitter | 分享到社交平台时有预览图 |

---

## 🟡 需要你设置一次（之后全自动）

### 1. Dev.to（技术博客平台，免费）
- 注册：https://dev.to/accounts/new
- 获取 API Key：https://dev.to/settings/extensions → Generate API Key
- 在 GitHub 仓库 → Settings → Secrets → 添加 `DEVTO_API_KEY`
- **效果**：每次发新文章自动同步到 Dev.to

### 2. Reddit（全球最大论坛，免费）
- 注册：https://www.reddit.com/register
- 创建 App：https://www.reddit.com/prefs/apps → 选 "script" 类型
- 在 GitHub 仓库 → Settings → Secrets → 添加：
  - `REDDIT_CLIENT_ID`
  - `REDDIT_CLIENT_SECRET`
  - `REDDIT_USERNAME`
  - `REDDIT_PASSWORD`
- **效果**：每周二、五自动发到 r/BuyItForLife, r/Gadgets 等社区

### 3. Google Search Console 重新提交 Sitemap
- 进入 https://search.google.com/search-console
- Sitemaps → 移除旧的 → 重新提交 `sitemap.xml`
- 等待 24-48 小时生效

---

## 🔵 免费手动推广（建议每周做 1-2 次）

### Hacker News（科技圈流量大）
1. 去 https://news.ycombinator.com/submit
2. Title: `Show HN: BioSavvy – Evidence-based health product reviews`
3. URL: `https://biosavvy.github.io`
4. Text: 简单介绍网站理念

### Product Hunt（产品发布平台）
1. 去 https://www.producthunt.com/posts/new
2. 填写产品信息 + 截图
3. 选类别：Health & Fitness / Productivity

### Quora（问答引流）
- 搜索 "best massage gun 2026" 等问题
- 回答时引用 BioSavvy 的评测数据
- 每天回答 2-3 个相关问题

### 小红书/知乎（中文流量）
- 将文章内容改写成中文
- 发布到知乎专栏 + 小红书笔记
- 标题如："2026年最值得买的筋膜枪评测"

---

## 📈 SEO 长尾关键词策略

以下是竞争度低、容易被 Google 收录的关键词：

| 关键词 | 竞争度 | 对应文章 |
|--------|--------|----------|
| best infrared sauna blanket 2026 | 低 | article14 |
| best electric foot bath device review | 低 | article6 |
| best acupressure mat for feet | 低 | article21 |
| best pure titanium thermos cup | 极低 | article11 |
| best smart posture corrector 2026 | 低 | article15 |
| best herbal foot bath product | 极低 | article9 |
| best infrared therapy mattress | 低 | article17 |

**建议**：每篇文章标题可加入 "review" "tested" "ranked" "2026" 等搜索热词。

---

## 🔄 自动化工作流一览

| Workflow | 触发条件 | 功能 |
|----------|----------|------|
| SEO Auto-Indexer | 每次 push + 每周日 | 通知 Google/Bing 抓取 |
| Auto Publisher | push 新文章 + 每周二/五 | 自动发到 Dev.to/Reddit |
| Scheduled Articles | 每天自动 | 到日期的文章自动上线 |

---

## ⚡ 优先级建议

1. **立即做**：Google Search Console 重新提交 sitemap
2. **今天做**：注册 Dev.to + Reddit，配置 GitHub Secrets
3. **本周做**：Hacker News 发一个 Show HN 帖子
4. **持续做**：每周在 Quora/知乎回答 2-3 个相关问题

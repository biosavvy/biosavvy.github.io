# 多平台自动发布 — 设置指南

## 总览

一次设置，三个平台全自动发布：
- **Dev.to** — 开发者/科技社区，高权重，利于 SEO
- **Medium** — 全球最大博客平台，文章容易被 Google 收录
- **Reddit** — 全球最大社区之一，精准引流

设置完成 → GitHub Actions 每周自动运行 → 完全脱离人工。

---

## 平台 1：Dev.to（最简单，2 分钟）

### 步骤

1. 访问 https://dev.to/
2. 用 GitHub 账号注册（或直接注册）
3. 登录后进入 https://dev.to/settings/extensions
4. 找到 **API Keys** → 输入名称 `BioSavvy` → 点击 **Generate**
5. 复制生成的 API Key

### 添加到 GitHub

仓库 → Settings → Secrets → Actions → New secret：

| Name | Value |
|------|-------|
| `DEVTO_API_KEY` | 复制的 API Key |

---

## 平台 2：Medium（2 分钟）

### 步骤

1. 访问 https://medium.com/
2. 注册/登录
3. 点击右上角头像 → Settings
4. 左侧菜单 → **Security**
5. 找到 **Integration tokens** → 输入名称 `BioSavvy` → 点击 **Generate token**
6. 复制生成的 token（只显示一次！）

### 添加到 GitHub

| Name | Value |
|------|-------|
| `MEDIUM_TOKEN` | 复制的 integration token |

---

## 平台 3：Reddit（5 分钟）

### 步骤

1. 访问 https://www.reddit.com/prefs/apps
2. 点击 **create another app...** (底部)
3. 填写：
   - **name**: `BioSavvy`
   - 选择 **script**
   - **redirect uri**: `http://localhost:8080`
4. 点击 **create app**
5. 记录：
   - **Client ID** — 在 app 名字下方的一串字符
   - **Client Secret** — 在 "secret" 旁边

### 添加到 GitHub

| Name | Value |
|------|-------|
| `REDDIT_CLIENT_ID` | Client ID |
| `REDDIT_SECRET` | Client Secret |
| `REDDIT_USERNAME` | 你的 Reddit 用户名 |
| `REDDIT_PASSWORD` | 你的 Reddit 密码 |

---

## 运行

所有 secret 添加完成后：

1. 到仓库的 **Actions** 页面
2. 选择 **Multi-Platform Auto Publisher**
3. 点击 **Run workflow**
4. 选择平台（默认 `all` = 三个都发）
5. 点击 **Run workflow**

### 自动运行

- 每周二、周五自动发布
- 无需任何操作

---

## 常见问题

| 问题 | 解决 |
|------|------|
| Dev.to 报 422 | 文章标题重复，已自动跳过 |
| Medium 报 401 | Token 过期，重新生成 |
| Reddit 报 403 | 账号太新（需要 30 天以上）或 karma 不足 |
| Reddit 报 429 | 发帖频率太高，等几分钟再试 |

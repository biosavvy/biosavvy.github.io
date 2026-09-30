# Pinterest 自动化设置指南

## 为什么需要一次性设置？

Pinterest 官方 API 是唯一能**完全脱离人工**的方式。API 调用不会触发验证码，因为它是 Pinterest 官方授权的接口。

设置过程只需 **5 分钟**，之后所有操作自动运行。

---

## 设置步骤（共 9 步）

### 第 1 步：注册 Pinterest 开发者账号

1. 访问 https://developers.pinterest.com/
2. 用你的 Pinterest 账号登录（biosavvy）
3. 点击 "Get started" 或 "Sign up"

### 第 2 步：创建开发者应用

1. 进入 https://developers.pinterest.com/apps/
2. 点击 "Create app"
3. 填写信息：
   - **App name**: BioSavvy
   - **App description**: BioSavvy content management
   - **Business use case**: Content management
4. 点击 "Create"

### 第 3 步：配置应用权限（Scopes）

在应用设置中找到 "Scopes" 或 "Permissions"，添加以下权限：
- `boards:read` — 读取看板
- `boards:write` — 创建看板
- `pins:read` — 读取 Pin
- `pins:write` — 创建 Pin
- `user_accounts:read` — 读取用户信息

### 第 4 步：配置重定向 URI

在 "OAuth settings" 中，添加重定向 URI：
```
https://localhost/callback
```

### 第 5 步：记录应用凭证

在应用页面记录：
- **App ID**（Client ID）— 类似 `1234567890`
- **App Secret**（Client Secret）— 一串随机字符串

> ⚠️ App Secret 只显示一次，务必立即保存！

### 第 6 步：授权应用（OAuth 流程）

1. 在浏览器打开以下 URL（把 `YOUR_APP_ID` 替换为你的 App ID）：

```
https://www.pinterest.com/oauth/?client_id=YOUR_APP_ID&redirect_uri=https://localhost/callback&response_type=code&scope=boards:read+boards:write+pins:read+pins:write+user_accounts:read
```

2. 登录你的 Pinterest 账号（biosavvy）
3. 点击 "Authorize" / "Allow"
4. 浏览器会跳转到 `https://localhost/callback?code=XXXXXXXX`
5. 复制 URL 中的 `code` 值

### 第 7 步：用 code 换取 access token

在本地终端运行（需要能访问 Pinterest）：

```bash
curl -X POST https://api.pinterest.com/v5/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=你复制的CODE值" \
  -d "client_id=你的APP_ID" \
  -d "client_secret=你的APP_SECRET" \
  -d "redirect_uri=https://localhost/callback"
```

返回的 JSON 中包含：
```json
{
  "access_token": "pina.xxxxx...",
  "refresh_token": "pinr.xxxxx...",
  "expires_in": 2592000
}
```

保存这三个值：
- `access_token` — 用于 API 调用
- `refresh_token` — 用于自动续期
- `client_id` 和 `client_secret` — 上面已记录

### 第 8 步：添加 GitHub Secrets

进入你的 GitHub 仓库 → Settings → Secrets and variables → Actions

添加以下 4 个 Secret：

| Secret 名称 | 值 |
|---|---|
| `PINTEREST_ACCESS_TOKEN` | 上面获取的 `access_token` |
| `PINTEREST_REFRESH_TOKEN` | 上面获取的 `refresh_token` |
| `PINTEREST_CLIENT_ID` | 你的 App ID |
| `PINTEREST_CLIENT_SECRET` | 你的 App Secret |

### 第 9 步：运行自动化

1. 进入仓库的 **Actions** 页面
2. 选择 **Pinterest API Automation**
3. 先运行 **test-token** 验证连接
4. 验证通过后，运行 **boards-and-pins** 一次性创建所有内容

---

## 自动运行说明

设置完成后：

- **定时任务**：每周一自动运行，检查并创建内容
- **手动触发**：在 Actions 页面手动运行
- **自动续期**：refresh_token 自动获取新的 access_token

### 可选择的运行模式

| 模式 | 说明 |
|---|---|
| `test-token` | 测试 token 是否有效 |
| `boards-only` | 只创建 5 个看板 |
| `pins-only` | 只创建 13 个 Pin（需先有看板）|
| `boards-and-pins` | 创建看板 + Pin（完整流程）|

---

## 如果 access_token 过期了怎么办？

脚本会自动用 refresh_token 续期。如果 refresh_token 也过期了（通常几个月），只需重复第 6-8 步重新授权。

---

## 故障排除

| 问题 | 解决方案 |
|---|---|
| `401 Unauthorized` | Token 过期，检查是否设置了 refresh_token |
| `boards:write scope required` | 在应用设置中重新添加权限 |
| `redirect_uri mismatch` | 确保 OAuth 设置中的 URI 是 `https://localhost/callback` |

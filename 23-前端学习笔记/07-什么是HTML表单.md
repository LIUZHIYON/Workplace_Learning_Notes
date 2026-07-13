# HTML 表单是什么？

**HTML 表单（`<form>`）就是网页上让用户输入数据、然后提交给服务器的交互区域。**

你见过的所有输入框、下拉菜单、勾选框、提交按钮都是表单的一部分。

---

## 最简单的例子

```html
<form action="/login" method="POST">
  <label>用户名：</label>
  <input type="text" name="username">
  
  <label>密码：</label>
  <input type="password" name="password">
  
  <button type="submit">登录</button>
</form>
```

填完点"登录"，浏览器把数据发到 `/login` 这个地址。

---

## 关键属性

| 属性 | 作用 |
|------|------|
| `action` | 数据发到哪里（URL） |
| `method` | 怎么发 — `GET` 或 `POST` |

```html
<!-- GET：数据在 URL 里，适合搜索 -->
<form action="/search" method="GET">

<!-- POST：数据在请求体里，适合登录、注册 -->
<form action="/submit" method="POST">
```

---

## 常用的输入类型

| 类型 | 代码 | 效果 |
|------|------|------|
| 文本 | `<input type="text">` | 单行输入框 |
| 密码 | `<input type="password">` | 输入内容被遮盖 |
| 数字 | `<input type="number">` | 只能输数字，有上下箭头 |
| 邮箱 | `<input type="email">` | 会自动验证格式 |
| 复选框 | `<input type="checkbox">` | 可多选 |
| 单选框 | `<input type="radio">` | 只能选一个 |
| 下拉选择 | `<select><option>` | 下拉菜单 |
| 文本区域 | `<textarea>` | 多行文本输入 |
| 文件上传 | `<input type="file">` | 选文件 |
| 日期 | `<input type="date">` | 日期选择器 |
| 滑块 | `<input type="range">` | 拖动选择数值 |
| 隐藏 | `<input type="hidden">` | 看不见，但会提交数据 |

---

## name 属性 — 关键中的关键

每个输入控件都要有 `name`，不然提交了服务器也不知道这个值对应什么字段。

```html
<input type="text" name="username">
<!-- 提交后服务器收到：username=用户填的内容 -->
```

**没有 `name` 的输入框，提交时不会发送。**

---

## 数据提交流程

### 传统方式（页面刷新）
```
浏览器 → POST /login（数据在请求体里）
       ← 服务器返回新 HTML 页面（页面刷新/跳转）
```

### 现代方式（AJAX / Fetch，不刷新页面）
```
浏览器 → fetch('/api/login', { method: 'POST', body: JSON.stringify(...) })
       ← 返回 JSON（{"ok": true}）
       → 前端 JS 自己更新 UI（页面不刷新）
```

---

## 必知必会的几个点

### 1. label 标签
```html
<label for="username">用户名：</label>
<input id="username" type="text" name="username">
<!-- 点"用户名"文字，光标自动跳到输入框 -->
```

### 2. 表单验证
```html
<input type="email" required>          <!-- 必填 -->
<input type="number" min="1" max="100"> <!-- 范围限制 -->
<input pattern="[0-9]{11}">            <!-- 正则校验手机号 -->
```

### 3. 阻止默认提交（前端 JS 处理）
```js
document.querySelector('form').addEventListener('submit', (e) => {
  e.preventDefault()          // 阻止页面刷新
  const data = new FormData(e.target)
  fetch('/api/submit', { method: 'POST', body: data })
})
```

> **总结：表单就是网页跟用户"要数据"的标准方式。** 后端（Flask/Django/PHP）收到表单数据后，存数据库、发邮件、处理文件……一切的 Web 交互基本都从表单开始。

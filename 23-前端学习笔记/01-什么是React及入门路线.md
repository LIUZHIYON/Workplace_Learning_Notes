# React 是什么？

React 是 Facebook（Meta）开源的 **JavaScript 前端库**，用于构建用户界面（UI）。

> **用组件的方式构建 UI，数据变了，UI 自动更新。**

---

## 核心思想

### 1. 组件化
一切皆组件。每个组件是一个独立、可复用的 UI 块，有自己的逻辑和样式。

```
App
├── Header
├── Sidebar
│   └── MenuItem × N
├── MainContent
│   ├── PostCard × N
│   └── Pagination
└── Footer
```

### 2. 声明式
你**声明** UI 应该长什么样，React 帮你搞定怎么更新。

```jsx
function App() {
  const [visible, setVisible] = useState(false)
  return (
    <button onClick={() => setVisible(true)}>
      {visible ? 'Hello!' : '点我'}
    </button>
  )
}
```

### 3. 单向数据流
数据从父组件流向子组件，单向传递。

### 4. Virtual DOM
React 维护一个虚拟 DOM 树，数据变化时先在虚拟 DOM 上算出差异，再批量更新真实 DOM。

---

## 入门学习路线

### 🟢 第一阶段：JavaScript 基础（必须先搞定）

- ES6+ 语法：`let/const`、箭头函数、解构赋值、模板字符串、展开运算符
- 数组方法：`map()`、`filter()`、`reduce()`
- Promise / async-await
- 模块化：`import / export`
- `this` 和作用域理解

### 🟢 第二阶段：React 核心概念

**必须掌握（按顺序）：**

| 概念 | 说明 |
|------|------|
| JSX | 在 JS 里写 HTML 的语法糖 |
| 组件（Component） | 函数组件写法 |
| Props | 父传子数据 |
| State（useState） | 组件自己的数据，变了就重新渲染 |
| 事件处理 | onClick、onChange 等 |
| 条件渲染 | if、三元、&& |
| 列表渲染 | map() + key |
| useEffect | 副作用：发请求、订阅、操作 DOM |
| 表单受控组件 | input 的值和 state 绑定 |

**之后学的：**

- useRef
- useContext
- 自定义 Hook
- React Router

### 🟢 第三阶段：配套工具链

| 工具 | 用途 | 是否必须 |
|------|------|---------|
| Vite | 项目脚手架 | ✅ 必装 |
| ESLint + Prettier | 代码规范和格式化 | ✅ 推荐 |
| Tailwind CSS | 写样式效率高 | ⭐ 推荐 |
| React DevTools | 浏览器调试组件/状态 | ✅ 必装 |

### 🟢 第四阶段：状态管理 & 数据请求

**状态管理：** Zustand（推荐入门用）→ Redux Toolkit（项目大了再用）

**数据请求：** fetch（原生）→ React Query / TanStack Query

### 🟢 第五阶段：进阶

- Next.js（全栈框架，SSR/SSG）
- TypeScript + React
- 测试：Vitest + React Testing Library

---

## 入门路线图总结

```
JavaScript 基础（1-2周）
   ↓
React 核心（2-3周）
  ├─ JSX, 组件, Props
  ├─ useState, useEffect
  ├─ 条件/列表渲染, 事件
   ↓
React Router + 项目实战（2-3周）
  └─ 做个 Todo App / 博客 / 简易后台
   ↓
Next.js + TypeScript（3-4周）
   ↓
状态管理 + 数据请求库
```

> **建议：不要光看文档，边学边写。花一个周末搭个 Todo App，比看完一整本书都管用。**

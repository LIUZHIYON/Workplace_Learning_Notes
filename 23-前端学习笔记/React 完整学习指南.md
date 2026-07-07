# ⚛️ React 完整学习指南

> 从入门到熟练 · 所有常用知识点一站式整理

---

## 📑 目录

- [01 什么是 React](#01-什么是-react)
- [02 JSX 语法](#02-jsx-语法)
- [03 组件](#03-组件)
- [04 Props](#04-props)
- [05 State & 事件处理](#05-state--事件处理)
- [06 条件渲染 & 列表渲染](#06-条件渲染--列表渲染)
- [07 组件通信](#07-组件通信)
- [08 表单处理](#08-表单处理)
- [09 Hooks 核心三件套](#09-hooks-核心三件套)
- [10 Hooks 进阶](#10-hooks-进阶)
- [11 Context](#11-context)
- [12 useReducer](#12-usereducer)
- [13 自定义 Hook](#13-自定义-hook)
- [14 性能优化](#14-性能优化)
- [15 React Router](#15-react-router)
- [16 状态管理方案](#16-状态管理方案)
- [17 项目架构指南](#17-项目架构指南)
- [18 常见陷阱 & 避坑指南](#18-常见陷阱--避坑指南)
- [🎯 学习路线图](#-学习路线图)

---

## 01 什么是 React

### 一句话定义

React 是一个用于构建**用户界面**的 JavaScript **库**（不是框架）。

- ✅ **声明式** — 描述"界面长什么样"，React 负责更新
- ✅ **组件化** — 把 UI 拆成独立、可复用的零件
- ✅ **跨平台** — Web (React DOM) / 移动端 (React Native)

> **React 不是框架，是个库。** 它只关心"怎么渲染 UI"，路由、状态管理、HTTP 请求这些需要你自己选工具。

### 核心思想：声明式 vs 命令式

```js
// ❌ 命令式（jQuery 风格）—— 手把手教浏览器做事
const btn = document.getElementById('btn')
btn.addEventListener('click', () => {
  const div = document.getElementById('root')
  div.innerHTML = '点了'
})

// ✅ 声明式（React 风格）—— 描述结果，React 搞定过程
<button onClick={() => setClicked(true)}>
  {clicked ? '点了' : '点我'}
</button>
```

### Virtual DOM — React 快的秘密

```
状态变化 → 生成新 VDOM → Diff 对比 → 只更新有变化的部分 → 真实 DOM
```

Virtual DOM = 内存中的"轻量 DOM"。每次状态变，React 先在 VDOM 上算出最小更新范围，再批量打到真实 DOM，比直接操作真实 DOM 快很多。

---

## 02 JSX 语法

### JSX 是什么？

JSX = JavaScript + XML。让你在 JS 里直接写 HTML 标签。

```jsx
const element = <h1>你好，React</h1>
```

最终会被编译成 `React.createElement()` 调用。

### JSX 规则速览

```jsx
/* 1. 只能有一个根元素 */
<div>
  <h1>标题</h1>
  <p>内容</p>
</div>
// ↑ 或者用 <></> (Fragment)

/* 2. {} 嵌入 JS 表达式 */
<p>结果：{1 + 2}，{user.name}</p>

/* 3. class → className */
<div className="container">

/* 4. 标签必须闭合 */
<br />  <img src="..." />
```

---

## 03 组件

### 函数组件（现代写法）

```jsx
function Welcome({ name }) {
  return <h1>你好，{name}</h1>
}

// 使用
<Welcome name="小明" />
```

### Class 组件（旧的，了解即可）

```jsx
class Welcome extends React.Component {
  render() {
    return <h1>你好，{this.props.name}</h1>
  }
}
```

### 组件命名规则

**大写字母开头** — React 区分组件和普通 HTML 标签的唯一方式。

`<div>` → HTML div 标签 `<Welcome />` → Welcome 组件

### 组件嵌套

```
App（根组件）
├── Header（头部）
├── Sidebar（侧栏）
├── Main（主区域）
└── Footer（底部）
```

---

## 04 Props

父组件传数据给子组件，**只读的**。

### 基本用法

```jsx
// 父组件
function App() {
  return (
    <UserCard
      name="小明"
      age={25}
      hobbies={['游泳', '编程']}
    />
  )
}

// 子组件 — 通过参数接收 props
function UserCard({ name, age, hobbies }) {
  return (
    <div>
      <h3>{name}</h3>
      <p>年龄：{age}</p>
      <ul>
        {hobbies.map(h => <li>{h}</li>)}
      </ul>
    </div>
  )
}
```

### Props 规则

- **只读** — 子组件不能修改 props，改了也是父组件改
- 可以传任意类型 — 字符串、数字、数组、对象、函数、甚至组件
- `children` — 特殊 prop，表示标签里的子元素

### children 示例

```jsx
function Card({ children }) {
  return <div className="card">{children}</div>
}

// 使用
<Card>
  <h2>卡片标题</h2>
  <p>这是卡片内容</p>
</Card>
```

---

## 05 State & 事件处理

### useState 基础

```jsx
import { useState } from 'react'

function Counter() {
  const [count, setCount] = useState(0)
  //       ↑ 当前值   ↑ 更新函数        ↑ 初始值

  return (
    <button onClick={() => setCount(count + 1)}>
      点了 {count} 次
    </button>
  )
}
```

### setState 的两种用法

```jsx
// 方式1：直接传新值
setCount(count + 1)

// 方式2：传函数（基于前一个值计算）
setCount(prev => prev + 1)
// ↑ 多次调用时用这个，避免闭包陷阱

// 示例：想一次加3
const handleClick = () => {
  setCount(prev => prev + 1)
  setCount(prev => prev + 1)
  setCount(prev => prev + 1)
}  // ← 点一次，+3
```

### 事件处理速查

```jsx
// 常见事件
<button onClick={() => ...}>点击</button>
<input onChange={(e) => setText(e.target.value)} />
<form onSubmit={(e) => { e.preventDefault(); ... }}/>
<input onBlur={() => ...} />   // 失去焦点
```

---

## 06 条件渲染 & 列表渲染

### 条件渲染

```jsx
// 1. 三元运算符（最常用）
return (
  <div>
    {isLoggedIn ? <UserPanel /> : <LoginBtn />}
  </div>
)

// 2. && 短路（条件为真才渲染）
{unreadCount > 0 && <Badge count={unreadCount} />}

// 3. if-else（抽成函数）
if (loading) return <Spinner />
if (error) return <ErrorMsg />
return <DataView />
```

### 列表渲染

```jsx
const todos = ['学习React', '写代码', '睡觉']

return (
  <ul>
    {todos.map((todo, index) => (
      <li key={index}>{todo}</li>
    ))}
  </ul>
)
```

> **⚠️ key 属性**：每个列表项要唯一。用数据的 id，不要用 index（除非静态列表）。

---

## 07 组件通信

```
App → Parent → Child
       ↓ props        ↑ 回调函数
```

### 1️⃣ 父 → 子（Props）

```jsx
<Child title="标题" data={data} />
```

### 2️⃣ 子 → 父（回调函数）

```jsx
// 父传函数
<Child onDelete={(id) => handleDelete(id)} />

// 子组件调用
<button onClick={() => onDelete(id)}>删除</button>
```

### 3️⃣ 兄弟通信（状态提升）

state 提到共同父组件，通过 props 下发。

```
App（state: searchText）
├── SearchBar（onSearch → setSearchText）
└── List（filter={searchText}）
```

---

## 08 表单处理

### 受控组件 — state 作为唯一数据源

```jsx
function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()        // 阻止页面刷新
    console.log({ email, password })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">登录</button>
    </form>
  )
}
```

### 常见表单元素

```jsx
// 复选框
<input type="checkbox"
  checked={agree}
  onChange={(e) => setAgree(e.target.checked)} />

// 下拉框
<select value={city}
  onChange={(e) => setCity(e.target.value)}>
  <option value="bj">北京</option>
  <option value="sh">上海</option>
</select>
```

> **受控 vs 非受控：** 受控 = React 管理输入值（state 控制 value）；非受控 = DOM 自己管理（用 `useRef` 取 defaultValue）

---

## 09 Hooks 核心三件套

### useState — 让函数组件有"记忆"

```jsx
const [count, setCount] = useState(0)
```

### useEffect — 处理副作用（请求、订阅、DOM）

```jsx
useEffect(() => {
  // 做点事...
  return () => {} // 清理
}, [deps])
```

### useEffect 的四种模式

| 模式 | 写法 | 执行时机 |
|------|------|---------|
| 每次都执行 | `useEffect(() => {...})` | 每次渲染后 |
| 只挂载一次 | `useEffect(() => {...}, [])` | 组件挂载时 |
| 依赖变化才执行 | `useEffect(() => {...}, [userId])` | userId 变化时 |
| 带清理 | `useEffect(() => { return () => {...} }, [])` | 卸载时或下次执行前 |

### useRef — 可变引用，改值不触发渲染

```jsx
const timerRef = useRef(null)
timerRef.current = 123   // 改值不触发重新渲染
```

| 特性 | useState | useRef |
|------|----------|--------|
| 改值触发重新渲染 | ✅ | ❌ |
| 存定时器 ID | ❌ | ✅ |
| 获取 DOM 节点 | ❌ | ✅ |

> 这三个 Hook 在配套的 **React Hooks 可视化详解** 文件中有更详细的拆解和流程图。

---

## 10 Hooks 进阶

### useMemo — 缓存计算结果

避免每次渲染都重复计算复杂值。

```jsx
const sortedList = useMemo(
  () => {
    // 只有 list 或 sortBy 变了才重新计算
    return [...list].sort(sortBy)
  },
  [list, sortBy]
)
```

### useCallback — 缓存函数引用

避免子组件因父组件重新渲染而"无辜"重渲染。

```jsx
const handleClick = useCallback(
  () => {
    setCount(prev => prev + 1)
  },
  []
)
```

### useMemo vs useCallback

```jsx
// useMemo → 缓存结果值
useMemo(() => value, deps)

// useCallback → 缓存函数本身
useCallback(fn, deps)

// useCallback(fn, deps) 等价于
useMemo(() => fn, deps)
```

### useTransition — 标记低优先级更新（React 18）

```jsx
const [isPending, startTransition] = useTransition()

const handleSearch = (value) => {
  startTransition(() => {
    setSearchQuery(value)  // ← 低优先级更新
  })
}
```

### useDeferredValue — 延迟更新

类似防抖，但 React 内部调度。

```jsx
const [query, setQuery] = useState('')
const deferredQuery = useDeferredValue(query)
// deferredQuery 会比 query 慢一拍更新
```

### useId — 唯一 ID 生成

```jsx
const id = useId()

<label htmlFor={id}>用户名</label>
<input id={id} />
```

---

## 11 Context

### 什么时候用 Context？

避免 Props 层层传递（Props Drilling）：

```
App → Layout → Navbar → UserMenu
```

如果不做 Context，UserMenu 需要 theme 数据，就要从 App 层层传，中间组件用不着也得传。

### 使用步骤

```jsx
// 1. 创建 Context
const ThemeContext = createContext('light')

// 2. 提供 Context（在 App 里）
function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Layout />
    </ThemeContext.Provider>
  )
}

// 3. 消费 Context（子组件直接拿）
function UserMenu() {
  const theme = useContext(ThemeContext)
  // ← 直接拿，不需要经过中间组件
  return <div className={`menu-${theme}`}>...</div>
}
```

---

## 12 useReducer

### 什么时候用它？

- 多个 state 之间存在关联
- 更新逻辑复杂（比如多层嵌套对象）
- 下一个 state 依赖前一个 state

### 基本用法

```jsx
// 1. 定义 reducer（就是个纯函数）
function todoReducer(state, action) {
  switch (action.type) {
    case 'ADD':
      return [...state, action.payload]
    case 'TOGGLE':
      return state.map(todo =>
        todo.id === action.id
          ? {...todo, done: !todo.done}
          : todo
      )
    default:
      return state
  }
}

// 2. 使用 useReducer
const [todos, dispatch] = useReducer(todoReducer, [])

// 3. 触发更新（通过 dispatch 派发 action）
dispatch({ type: 'ADD', payload: { id: 1, text: '学React' } })
dispatch({ type: 'TOGGLE', id: 1 })
```

### 流程图

```
用户操作 → dispatch(action) → Reducer 纯函数 → 新 State → 重新渲染
```

> **useReducer + Context = 小 Redux：** 用 Context 把 dispatch 和 state 传到子树，实现全局状态管理，不需要额外库。

---

## 13 自定义 Hook

### 示例：网络请求 Hook

```jsx
function useFetch(url) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [url])

  return { data, loading, error }
}
```

### 使用：一行搞定请求

```jsx
function UserList() {
  const { data, loading, error } = useFetch('/api/users')

  if (loading) return <Spinner />
  if (error) return <Error msg={error} />
  return <UserList data={data} />
}
```

> **自定义 Hook 的命名规则：** 函数名以 `use` 开头（React 靠这个检查 Hook 规则），内部可以调用其他 Hook。就像"乐高积木"——把 useState + useEffect 等基础 Hook 组合成你自己的高阶功能块。

---

## 14 性能优化

### React.memo — 避免不必要的重渲染

```jsx
const MyComponent = React.memo(({ data }) => {
  // props 没变就不重新执行
  return <div>{data}</div>
})
```

### 懒加载 — 按需加载

```jsx
const HeavyComponent = lazy(() => import('./Heavy'))

<Suspense fallback={<Loading />}>
  <HeavyComponent />
</Suspense>
```

### 虚拟列表 — 万条数据不卡

推荐库：`react-window` / `react-virtuoso`

```jsx
import { FixedSizeList } from 'react-window'

<FixedSizeList height={500} itemCount={10000} itemSize={50}>
  {({ index, style }) => (
    <div style={style}>第 {index} 行</div>
  )}
</FixedSizeList>
```

### 性能排查 Checklist

| 问题 | 方案 |
|------|------|
| 列表卡顿 | 虚拟列表 |
| 大组件重复渲染 | React.memo |
| 重复计算 | useMemo |
| 函数引用变化 | useCallback |
| 首屏太大 | 懒加载 + 代码分割 |
| 图片太多 | 懒加载 + 压缩 |

---

## 15 React Router

### 安装

```bash
npm install react-router-dom
```

### 基本使用

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/user/:id" element={<User />} />
      </Routes>
    </BrowserRouter>
  )
}
```

### 页面跳转

```jsx
import { Link, useNavigate } from 'react-router-dom'

function Nav() {
  const navigate = useNavigate()

  return (
    <nav>
      <Link to="/">首页</Link>
      <Link to="/about">关于</Link>

      {/* 编程式导航 */}
      <button onClick={() => navigate('/user/123')}>
        去用户页
      </button>
    </nav>
  )
}
```

### 获取 URL 参数

```jsx
import { useParams } from 'react-router-dom'

function User() {
  const { id } = useParams()  // /user/123 → id=123
  return <h1>用户：{id}</h1>
}
```

---

## 16 状态管理方案

| 方案 | 适用场景 | 复杂度 |
|------|---------|--------|
| **useState/useReducer** | 组件内部状态，够用就行 | 🟢 简单 |
| **Context + useReducer** | 跨组件共享，中小项目 | 🟡 中等 |
| **Zustand** | 大型项目，API 简洁 | 🔴 复杂 |
| **Redux Toolkit** | 大型团队，约定统一 | 🔴 复杂 |

### 选择建议

```
组件内部用 → useState
跨组件共享 → Context + useReducer
复杂大项目 → Zustand
```

### Zustand 示例

```js
import { create } from 'zustand'

const useStore = create((set) => ({
  count: 0,
  inc: () => set((s) => ({ count: s.count + 1 })),
  reset: () => set({ count: 0 }),
}))
```

---

## 17 项目架构指南

### 推荐目录结构

```
src/
├── components/          # 通用组件
│   ├── Button/
│   ├── Modal/
│   └── Loading/
├── pages/               # 页面组件
│   ├── Home/
│   ├── About/
│   └── User/
├── hooks/               # 自定义 Hook
│   ├── useFetch.js
│   └── useAuth.js
├── context/             # Context
├── services/            # API 请求
├── utils/               # 工具函数
├── styles/              # 样式
└── App.jsx
```

### 组件设计原则

- **单一职责** — 一个组件只做一件事
- **状态下沉** — 状态放在需要它的最底层组件
- **组件拆分** — 超过 200 行考虑拆分
- **容器 vs 展示** — 逻辑组件和数据展示组件分离

> 如果一个组件要写注释才能看懂它在做什么，就该拆分了。

---

## 18 常见陷阱 & 避坑指南

### ⚠️ 闭包陷阱

```jsx
// ❌ useEffect 里用旧的 state
useEffect(() => {
  const timer = setInterval(() => {
    setCount(count + 1)  // ← count 永远是初始值！
  }, 1000)
  return () => clearInterval(timer)
}, [])

// ✅ 用函数形式更新
setCount(prev => prev + 1)
```

### ⚠️ useEffect 无限循环

```jsx
// ❌ 依赖数组里放了对象/数组
useEffect(() => {
  fetchData(options)     // 不停重请求
}, [options])            // ← options 每次渲染都是新引用

// ✅ 拆开传基本类型
}, [options.page, options.size])
```

### ⚠️ 直接修改 State

```jsx
// ❌ 直接修改对象
const [user, setUser] = useState({ name: 'Xia', age: 18 })
user.age = 19           // ❌ React 检测不到变化
setUser(user)

// ✅ 创建新对象
setUser({ ...user, age: 19 })
```

### ⚠️ setState 是异步的

```jsx
// 一个事件处理函数内多次 setState
const handleClick = () => {
  setCount(count + 1)
  setCount(count + 1)
  setCount(count + 1)
  // count 只加了 1！React 会批量合并
}

// ✅ 用函数形式
setCount(prev => prev + 1)
setCount(prev => prev + 1)
setCount(prev => prev + 1)
```

### ⚠️ set 后不能马上获取新值

```jsx
const handleAdd = () => {
  setItems([...items, newItem])
  console.log(items.length)  // ❌ 旧的长度！渲染后才更新
}

// ✅ 用 useEffect 监听
useEffect(() => {
  console.log('items 变了', items.length)
}, [items])
```

### ⚠️ key 用 index

```jsx
// ❌ 用 index 做 key
{items.map((item, i) => (
  <ListItem key={i} />  // ← 列表增删会出 bug
))}

// ✅ 用唯一 id
{items.map(item => (
  <ListItem key={item.id} />
))}
```

---

## 🎯 学习路线图

```
HTML/CSS 基础 → JavaScript ES6+ → React 基础 → Hooks → 进阶 → 实战
                                    (JSX/组件/  (useState/  (Context/    (项目+
                                     props/     useEffect/  Router/      状态
                                     state)     useRef)     性能优化)    管理)
```

### 学习建议

1. 先把 **JSX + 组件 + Props + State** 搞熟，这 4 个够写 80% 的页面了
2. 然后 **useEffect** 处理 API 请求和副作用
3. 遇到复杂状态用 **useReducer**，跨组件用 **Context**
4. 项目大了再学 **React Router、性能优化、状态管理库**
5. 别一开始就想全学完——写几个项目自然就熟了

---

> 配套可视化文件：`React Hooks 可视化详解.html`（交互式图解，建议配合阅读）

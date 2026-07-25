# Docker 入门理解 — 装修比喻版

## 用搬家/装修来理解 Docker

### 📦 镜像（Image）= 装修图纸 + 材料清单

你想在 RK3576 上跑一个 Python 程序。正常操作：装系统 → 装 Python → 装 OpenCV → 装你的代码。但换个板子就得重新来一遍。

**Docker 镜像就是把这整套环境打包成一个"只读压缩包"**。里面有什么、什么版本、怎么配的，全锁死了。

```
my-app 镜像里面：
 ┌─────────────────┐
 │ Ubuntu 22.04 │ ← 基础系统
 │ Python 3.10 │ ← 运行时
 │ OpenCV 4.8 │ ← 依赖库
 │ 你的代码 │ ← 应用程序
 └─────────────────┘
```

拉镜像 = 别人已经装好了一个环境包，你直接下载：
```bash
docker pull nginx
# 相当于：去官网下载一个"已经配好的 Nginx 服务器压缩包"
```

### 🏃 容器（Container）= 按图纸装修好的房间

镜像是个**只读模板**，不能直接住人。容器就是**拿这个模板造出来的一个能跑的房间**。

```bash
docker run -d -p 80:80 nginx
# 翻译：拿 nginx 这个图纸，给我盖一间房，后台运行，门口挂个牌子 "80号门"
```

关键点：
- **一个镜像可以造 N 个容器**。就像你拿同一张图纸，盖十间一模一样的房子
- **容器之间互相隔离**。这间房炸了，不影响隔壁
- **容器很轻**。不是装一整个 Windows 虚拟机，只是开了一个"隔间"，共享主机内核

### 📝 Dockerfile = 施工说明书

你不想下载别人的图纸，想自己写一份。Dockerfile 就是：

```dockerfile
# 施工步骤
FROM ubuntu:22.04 # 1. 地基用 Ubuntu 22.04
RUN apt install python3 # 2. 装上 Python
COPY ./app /app # 3. 把代码复制进去
CMD ["python3", "/app/main.py"] # 4. 开机跑这个命令
```

这相当于你写了一份 Word 文档：
```
第1步：买一套毛坯房（Ubuntu）
第2步：铺地板、刷墙（装 Python）
第3步：把我的家具搬进去（复制代码）
第4步：每次进门先打开投影仪（跑 main.py）
```

然后 `docker build -t my-app .` = 把这份施工说明书**执行一遍**，最后得到一个叫 `my-app` 的镜像（装修好的房子）。

### 🏪 仓库（Registry）= 建材市场 / 应用商店

Docker Hub 就像一个**建材大市场**，你想要的镜像都在上面：
- 想要 Ubuntu 基础系统？去搜 `ubuntu`
- 想要现成的 Nginx？搜 `nginx`
- 想要一个装好 Python + OpenCV 的环境？有人已经做好了

```bash
docker pull nginx
# 从建材市场搬一箱"Nginx 预制房"回家
```

你自己也能把盖好的房推上去给别人用：
```bash
docker push 你的用户名/my-app
# 把你盖的房子挂到市场上卖（分享）
```

---

## 用你熟悉的场景举例

### 🎯 场景一：你做的 RKCamRecord3

你现在要在 RK3576 上跑一个 Python 相机录制服务。没 Docker 的话：

```
1. 装 Ubuntu 系统
2. 装 Python
3. 装 OpenCV
4. 装 GStreamer 和插件
5. pip install flask numpy opencv-python
6. 复制代码过去
7. 发现少了个库 → 再装
8. 换个板子 → 从头再来一遍 😭
```

有 Docker 的话：

```dockerfile
FROM ubuntu:22.04
RUN apt update && apt install -y python3 python3-pip \
 gstreamer1.0-tools libgstreamer1.0-dev \
 python3-opencv
COPY ./board_cam_record.py /app/
CMD ["python3", "/app/board_cam_record.py"]
```

```bash
# 只做一次
docker build -t cam-record .

# 任何板子上跑
docker run -d --device /dev/video0 cam-record
```

换板子？一条命令的事。环境一毛一样，不存在"在我电脑上明明能跑"。

### 🎯 场景二：同时跑 Python 2 和 Python 3

```
# 容器的隔离性
docker run -it python:2.7 bash # 一个容器里是 Python 2.7
docker run -it python:3.11 bash # 另一个容器里是 Python 3.11
# 两个互不干扰！不用在那个系统里装两套环境打架
```

### 🎯 场景三：你开发完想发给别人

没 Docker：
> "你先装 Python 3.10，然后 pip install -r requirements.txt，哦对了 OpenCV 要用 contrib 版本，还有你系统是 Ubuntu 吗？CentOS 要装这个那个..."

有 Docker：
> `docker pull my-app && docker run my-app`

完事。这就是 Docker 最大的价值：**环境一致性**。

---

## 一句话总结

| 概念 | 比喻 | 本质 |
|------|------|------|
| **镜像** | 装修图纸（只读方案） | 打包好的环境模板 |
| **容器** | 按图纸造出来的房间 | 一个运行的隔离实例 |
| **Dockerfile** | 施工说明书 | 自动化构建脚本 |
| **仓库** | 建材市场 | 存镜像的地方 |

**Docker 就是："把你的环境和代码打包成一个箱子，拿到哪都能直接打开用。"**

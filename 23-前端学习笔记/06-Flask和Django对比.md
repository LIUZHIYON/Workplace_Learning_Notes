# Flask vs Django 对比

## 一句话区别

```
Flask  = 自己组装的拼装电脑 → 轻、灵活、你要啥自己加
Django = 品牌整机 → 开机就能用，但换零件麻烦
```

---

## Django 是什么？

Django 是 Python 另一个 Web 框架，**大而全，啥都给你安排好了**。

### Django 全家桶自带哪些东西？

| 模块 | 干啥的 | 没它你得自己搞 |
|------|--------|--------------|
| **ORM** | 操作数据库，不用写 SQL | SQLAlchemy |
| **Admin 后台** | 自动生成数据管理界面 | 自己写页面 |
| **URL 路由** | URL 分发 | Flask 自带，但 Django 更强 |
| **模板引擎** | 服务端渲染 HTML | Jinja2（Flask 也用） |
| **表单处理** | 表单验证 + 渲染 | WTForms |
| **认证系统** | 用户登录/注册/权限 | Flask-Login |
| **安全防护** | CSRF、XSS、SQL注入防护 | 要自己加 |
| **序列化** | 把数据转成 JSON/XML | 手动搞 |
| **迁移工具** | 数据库表结构变更管理 | Alembic |

> Flask 装一圈扩展 = Django 开箱自带。

---

## Django 有什么用？

1. **内容型网站** — 新闻、博客、文档站（ORM + Admin 后台管内容太方便了，Instagram 早期就是 Django）
2. **电商平台** — 用户、商品、订单、支付
3. **企业级应用** — ERP、CRM、权限控制
4. **社交平台 / 论坛** — 认证 + 权限系统直接能用
5. **API 后端** — 加 `djangorestframework`（DRF）

---

## Flask vs Django 选型指南

| 场景 | 选谁 |
|------|------|
| 给开发板搭 Web 控制界面 | **Flask** |
| 写一个小 API | **Flask** |
| 快速原型 / MVP | **Flask** |
| 大型 Web 应用（电商/社交/企业系统） | **Django** |
| 内容管理网站（博客/新闻/CMS） | **Django**（Admin 后台太好用） |
| 团队项目，多人协作 | **Django**（结构统一） |
| 跟 AI / 机器学习集成 | **Flask** |

---

## 代码对比：做一个用户 API

### Flask
```python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

@app.route('/users')
def list_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'name': u.name} for u in users])
```

### Django
```python
# models.py
class User(models.Model):
    name = models.CharField(max_length=80)

# serializers.py
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']

# views.py
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# urls.py
urlpatterns = [path('users/', UserList.as_view())]
```

Django 代码多几行，但 **Admin 后台自动有了、ORM 是同套体系、迁移自动生成** —— 项目大了你就知道这些"多的"其实是省事。

---

## 总结

- **Flask** — 灵活自由的轻量选手，适合小型项目、API、硬件控制
- **Django** — 啥都配好的重武器，适合正经的 Web 应用

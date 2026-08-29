# 元素之诗QQ助手（官方API版）

基于QQ官方机器人API的元素之诗Wiki查询助手。

## 与旧版的区别

| 特性 | 旧版（NapCat） | 新版（官方API） |
|------|---------------|----------------|
| 连接方式 | WebSocket连接NapCat | Webhook/WebSocket官方SDK |
| 登录方式 | 需要扫码 | AppID + Token |
| 稳定性 | 频繁掉线 | 官方服务稳定 |
| 依赖 | NapCat容器 | 无额外依赖 |

## 快速开始

### 1. 获取QQ开放平台凭证

1. 访问 [QQ开放平台](https://q.qq.com/)
2. 创建机器人应用
3. 获取 AppID、Secret、Token

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的凭证
```

### 3. 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动机器人
python -m bot.main
```

### 4. Docker运行

```bash
docker-compose up -d
```

## 测试流程（使用cpolar内网穿透）

### 1. 安装cpolar

```bash
# macOS
brew install cpolar

# 注册并登录
cpolar authtoken <你的token>
```

### 2. 启动服务

```bash
# 终端1：启动机器人
python -m bot.main

# 终端2：启动内网穿透
cpolar http 8080
```

### 3. 配置回调URL

1. 访问 cpolar 界面获取临时URL（如 `https://xxxx.cpolar.top`）
2. 在QQ开放平台「机器人」→「回调配置」中填入：`https://xxxx.cpolar.top/callback`

### 4. 测试命令

在测试群发送以下命令：
- `菜单` - 查看主菜单
- `纹章` - 查看纹章列表
- `装备继承` - 查看装备继承关系
- `进本条件 霾火` - 查询副本进本条件
- `ping` - 测试连接

## 项目结构

```
元素之诗QQ助手-official/
├── bot/                    # 机器人核心代码
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── main.py            # 入口（官方SDK）
│   └── handler.py         # 消息处理
├── core/                   # 核心功能
│   ├── alias.py           # 命令别名
│   ├── calculator.py      # 计算器
│   ├── database.py        # 数据库操作
│   └── renderer.py        # 图片渲染
├── modules/                # 业务模块
│   ├── boss.py            # Boss属性
│   ├── seal.py            # 纹章查询
│   ├── equip.py           # 装备继承
│   ├── forge.py           # 锻造系统
│   ├── magic.py           # 魔素解构
│   ├── dungeon.py         # 副本查询
│   ├── menu.py            # 菜单系统
│   ├── index.py           # 关键词索引
│   ├── feedback.py        # 反馈系统
│   └── seal_calc.py       # 纹章计算
├── data/                   # 数据文件
│   ├── bot.db             # SQLite数据库
│   ├── init.sql           # 建表SQL
│   └── seeds/             # 种子数据
├── templates/              # 图片模板
├── .env.example           # 环境变量示例
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 常见问题

### Q: 如何获取QQ_TOKEN？

A: 在QQ开放平台创建应用后，进入「开发设置」→「机器人」，可以获取Token。

### Q: cpolar免费版有什么限制？

A: 免费版每次重启会更换域名，需要重新配置回调URL。稳定后可升级付费版固定域名。

### Q: 如何部署到云服务器？

A: 参考计划文档中的「方案A 公服务器详细说明」，需要：
1. 购买云服务器（2核2G即可）
2. 配置Nginx反向代理
3. 申请SSL证书（Let's Encrypt免费）
4. 部署Docker服务

## 相关文档

- [QQ开放平台文档](https://bot.q.qq.com/wiki/)
- [qq-botpy SDK文档](https://github.com/tencent/qq-botpy)

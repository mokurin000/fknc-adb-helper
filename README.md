# fknc-adb-helper

基于 adb 实现的疯狂农场道具刷新检测&推送。

## Roadmap

- [ ] 基于图片匹配实现天气判断

## 环境支持

任意支持 adb 、pytorch + CUDA 的环境。

## 部署

1. 配置任意一款支持 Milky 协议的 [bot 服务端](https://milky.ntqqrev.org/awesome#%E5%8D%8F%E8%AE%AE%E5%AE%9E%E7%8E%B0)
2. 在安装好 NVIDIA CUDA 12.6 驱动的环境中，

```bash
uv run fknc-adb-helper
```

即可使用。

3. 确保每个整十分钟时，游戏处于疯狂农场闲置状态，没有打开仓库、活动、历史收益提示、回顾界面等。

## 配置

在运行目录编写文件 `.env`：

```bash
# Milky API 结点
MILKY_API=http://localhost:3010
# Milky access token
MILKY_TOKEN=
# Milky 客户端通信超时秒数
MILKY_TIMEOUT=30

# 0:00~6:00 不推送
NO_DISTURB=974846788
# 订阅推送的群组 ID
SUBSCRIBE_GROUPS=12345678,87654321
# 订阅常规天气
COMMON_WEATHER_GROUPS=12345678,87654321

# 添加 -e / -d / -s serial / -t transportId 等
ADB_OPTIONS=
```

## Copyright

`weather/*.png`、`pics/*.png` 均为《蛋仔派对》游戏截图，其相关版权归原所属公司所有。本项目不持有上述素材的版权，仅将其用于识别与匹配功能的实现。

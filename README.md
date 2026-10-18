# 鹰猫加速器 逆向与改造

`com.yingmao.clash`（Clash 内核加速器）的静态分析与 smali 层改造记录。
设备：一加 PGEM10 / Android 14 / arm64 / KernelSU root。

> 结论先行：**客户端补丁能解除本地限制，但造不出节点。**
> 服务端一停，客户端再干净也连不上。这一点在 `docs/过期诊断报告.md` 里有完整论证。

---

## 目录

```
patches/           smali 层补丁脚本（apktool 反编译后直接改文本）
docs/              4 份分析报告
hookproj/          Frida 动态取证脚本
images/            运行截图
```

---

## 补丁清单

| 脚本 | 作用 | 关键点 |
|---|---|---|
| `patch_smali.py` | 解除本地限制 | `com/cncat/vpn/core/Clash` 4 个取钥方法硬编码密钥；`HomeFragment.g()` 恒 true；`UserData.getExpired/getNeedBuy` → false；`getVpnExpireTime` → 2099；MMKV `expired` 强制 false |
| `patch2.py` | 加固 | 强制 `endTimeDay` 写大值，保证剩余天数不为 0 |
| `patch_dialog.py` | 弹窗抑制 | `SubscriptionRsp` 响应实体改写，阻断"已过期"弹窗 |
| `patch_identity.py` | 身份随机化 | `Utils.getUniqueID` / OAID 随机，用于注册新试用账号 |
| `patch_timer_renew.py` | 定时续期 | `RestoreSessionHelper` 判断账号存活 >23h 触发 `AutoRenew`；`SplashActivity` 注册成功打时间戳；5 分钟冷却 |
| `patch_autorenew.py` | 自动续期 | 命中 `airportNode code != 1000` + msg 含"过期"时清凭证并重启进程，重新注册试用 |

### 使用前必改

每个脚本顶部的 `ROOT` / `BASE` 是硬编码的绝对路径，指向 apktool 反编译输出：

```python
ROOT = pathlib.Path(r"...\yingmao\apktool_out")
BASE = r"...\yingmao\mod_out2"
```

改成你自己的目录，或者改成相对路径。

---

## 工作流

```bash
# 1. 反编译
java -jar apktool.jar d phone_base.apk -o apktool_out

# 2. 打补丁（按需）
python patches/patch_smali.py
python patches/patch_dialog.py
python patches/patch_identity.py
python patches/patch_timer_renew.py
python patches/patch_autorenew.py
python patches/patch2.py

# 3. 回编译 + 签名
java -jar apktool.jar b apktool_out -o mod.apk
java -jar uber-apk-signer.jar -a mod.apk -o out
```

---

## Frida 动态取证

`hookproj/` 下是 Node 端 Frida 脚本：

| 文件 | 用途 |
|---|---|
| `myprobe.mjs` | 通用探针，打印关键方法调用 |
| `fire5.mjs` | 触发指定代码路径 |
| `set_age25.mjs` | 把账号创建时间改成 25 小时前，触发续期分支 |
| `reset_renew.mjs` | 清续期时间戳 |
| `tracer.mjs` | 方法级追踪 |
| `run_spawn.js` / `run_persist.js` | spawn 注入 / 常驻注入 |

```bash
npm install
node run_spawn.js
```

---

## 分析报告

| 文档 | 内容 |
|---|---|
| `docs/逆向分析报告.md` | 静态反编译（jadx / apktool / capstone）+ 动态取证（frida / tcpdump）全流程 |
| `docs/无限制改造报告.md` | 第一轮 smali 最小补丁记录，改造前后对比 |
| `docs/过期诊断报告.md` | 为什么补丁会"失效"——服务端封禁与客户端补丁的边界 |
| `docs/账户过期解决方案.md` | 自动续期方案，原有功能完整保留 |

---

## 边界

| 能做 | 不能做 |
|---|---|
| 解除本地过期闸门 | 生成节点 |
| 抑制过期弹窗 | 绕过服务端封禁 |
| 随机设备身份注册试用号 | 恢复被停用的账号 |
| 定时重新注册 | 保证长期可用 |

服务端判定与客户端补丁是两条线。补丁只解决"客户端不让用"，不解决"服务端不给用"。

---

## License

MIT

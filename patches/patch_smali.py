#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""com.yingmao.clash 无限制补丁（smali 层）
补丁点：
 1. com/cncat/vpn/core/Clash  4 个取钥方法 -> 硬编码密钥（重签名后仍可用）
 2. HomeFragment.g()          -> 恒定返回 true（永不过期闸门）
 3. UserData.getExpired/getNeedBuy -> FALSE；getVpnExpireTime -> 2099
 4. UIMainActivity 写 MMKV expired -> 强制 false
"""
import re, sys, pathlib

ROOT = pathlib.Path(r"C:\Users\33176\WorkBuddy AI\2026-10-13-20-59-50\yingmao\apktool_out")

KEYS = {
    "getRegisterKey": "M8T74hb17KR183b6",
    "getRegisterKiv": "242itTn000C480h1",
    "getSS1": "rwb6c4e7fz$6el%0",
    "getSS2": "z1b6c3t4e5f6k7w8",
}

def replace_method(text, sig, new_body):
    """替换 .method <sig> ... .end method 整块"""
    start = text.find(".method " + sig)
    if start == -1:
        return None, "method not found: " + sig
    end = text.find(".end method", start)
    if end == -1:
        return text, "end not found"
    end += len(".end method")
    return text[:start] + new_body + text[end:], "ok"

def patch_file(rel, patches):
    p = ROOT / rel
    if not p.exists():
        print(f"[!] missing {rel}")
        return False
    text = p.read_text(encoding="utf-8")
    orig = text
    for sig, body in patches:
        text, st = replace_method(text, sig, body)
        print(f"    {sig[:60]:60s} -> {st}")
    if text != orig:
        p.write_text(text, encoding="utf-8")
        print(f"[+] patched {rel}")
        return True
    print(f"[-] no change {rel}")
    return False

print("== 1) Clash.smali 密钥硬编码 ==")
clash_patches = []
for name, key in KEYS.items():
    body = (
        f'.method public final {name}(Ljava/lang/String;)Ljava/lang/String;\n'
        f'    .locals 0\n'
        f'    const-string v0, "{key}"\n'
        f'    return-object v0\n'
        f'.end method'
    )
    clash_patches.append((f"public final {name}(Ljava/lang/String;)Ljava/lang/String;", body))
patch_file(r"smali_classes2\com\cncat\vpn\core\Clash.smali", clash_patches)

print("\n== 2) HomeFragment.g() 永不过期 ==")
g_body = (
    '.method public static g()Z\n'
    '    .locals 1\n'
    '    const/4 v0, 0x1\n'
    '    return v0\n'
    '.end method'
)
patch_file(r"smali_classes3\com\yingmao\clash\fragment\home\HomeFragment.smali",
           [("public static g()Z", g_body)])

print("\n== 3) UserData 会员字段 ==")
bool_false = (
    '.method public final {name}()Ljava/lang/Boolean;\n'
    '    .locals 1\n'
    '    sget-object v0, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;\n'
    '    return-object v0\n'
    '.end method'
)
bool_true = (
    '.method public final {name}()Ljava/lang/Boolean;\n'
    '    .locals 1\n'
    '    sget-object v0, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;\n'
    '    return-object v0\n'
    '.end method'
)
ud_patches = [
    ("public final getExpired()Ljava/lang/Boolean;", bool_false.format(name="getExpired")),
    ("public final getNeedBuy()Ljava/lang/Boolean;", bool_false.format(name="getNeedBuy")),
    ("public final getOpenVpn()Ljava/lang/Boolean;", bool_true.format(name="getOpenVpn")),
    ("public final getVpnExpireTime()J",
     '.method public final getVpnExpireTime()J\n'
     '    .locals 2\n'
     '    const-wide v0, 0x3b3b16dc200     # 2099-01-01 00:00:00 (ms)\n'
     '    return-wide v0\n'
     '.end method'),
]
patch_file(r"smali_classes3\com\yingmao\clash\entity\UserData.smali", ud_patches)

print("\n== 4) UIMainActivity expired 写入强制 false ==")
p = ROOT / r"smali_classes3\com\yingmao\clash\act\UIMainActivity.smali"
if p.exists():
    t = p.read_text(encoding="utf-8")
    old = """    if-eqz v1, :cond_c

    .line 46
    invoke-virtual {v1}, Ljava/lang/Boolean;->booleanValue()Z

    move-result v9

    goto :goto_0

    :cond_c
    const/4 v9, 0x1

    :goto_0"""
    new = """    const/4 v9, 0x0

    goto :goto_0

    :cond_c
    const/4 v9, 0x0

    :goto_0"""
    if old in t:
        t = t.replace(old, new)
        p.write_text(t, encoding="utf-8")
        print("[+] patched UIMainActivity expired -> false")
    else:
        print("[-] pattern not found; trying loose match")
        m = re.search(r"(    :cond_c\n    const/4 v9, 0x1\n)", t)
        if m:
            t = t[:m.start(1)] + "    :cond_c\n    const/4 v9, 0x0\n" + t[m.end(1):]
            p.write_text(t, encoding="utf-8")
            print("[+] patched (loose)")
        else:
            print("[!] UIMainActivity pattern missing")
print("\n[done] smali patch finished")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""加固补丁：除原 6 处外，强制 endTimeDay 写大值（保证剩余天数不为 0）。"""
import re, pathlib
ROOT = pathlib.Path(r"C:\Users\33176\WorkBuddy AI\2026-10-13-20-59-50\yingmao\apktool_out")

def patch(rel, old, new):
    p = ROOT / rel
    t = p.read_text(encoding="utf-8")
    if old not in t:
        print(f"  [-] {rel}: pattern not found")
        return False
    t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")
    print(f"  [+] {rel}: patched")
    return True

# httpSuccess$8 (SubscriptionRsp -> endTimeDay) —— 把 v1 写 99999
for f in [
    r"smali_classes3\com\yingmao\clash\act\UIMainActivity$httpSuccess$8.smali",
    r"smali_classes3\com\yingmao\clash\act\UIMainActivity$httpSuccess$9.smali",
]:
    p = ROOT / f
    if not p.exists():
        print(f"  [-] {f}: not found"); continue
    t = p.read_text(encoding="utf-8")
    # 找到 const-string v0, "endTimeDay" 之后的 invoke-virtual encode 前，把 v1 置 99999
    # 模式（httpSuccess$8 实际是 parseInt/endTimeDay → store MMKV encode）
    # 用简单替换：在 const-string v0, "endTimeDay" 紧接的前一行注入 const/4 v1, 0x1869f (99999)
    new_t = re.sub(
        r'const-string v0, "endTimeDay"',
        'const/4 v1, 0x186a0\n    const-string v0, "endTimeDay"',
        t
    )
    if new_t != t:
        p.write_text(new_t, encoding="utf-8")
        print(f"  [+] {f}: endTimeDay -> 99999")
    else:
        print(f"  [-] {f}: no change")

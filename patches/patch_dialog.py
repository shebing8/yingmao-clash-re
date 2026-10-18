#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib, re

ROOT = pathlib.Path(r"C:\Users\33176\WorkBuddy AI\2026-10-13-20-59-50\yingmao\apktool_out")

def patch_subscription_rsp():
    p = ROOT / r"smali_classes3\com\yingmao\clash\net\http\entity\SubscriptionRsp.smali"
    if not p.exists():
        print("[-] SubscriptionRsp.smali not found")
        return
    text = p.read_text(encoding="utf-8")
    target = """.method public final getCode()Ljava/lang/String;
    .locals 1
    .annotation build Lorg/jetbrains/annotations/Nullable;
    .end annotation

    iget-object v0, p0, Lcom/yingmao/clash/net/http/entity/SubscriptionRsp;->code:Ljava/lang/String;

    return-object v0
.end method"""

    replacement = """.method public final getCode()Ljava/lang/String;
    .locals 1
    .annotation build Lorg/jetbrains/annotations/Nullable;
    .end annotation

    const-string v0, "1000"

    return-object v0
.end method"""

    if target in text:
        text = text.replace(target, replacement)
        p.write_text(text, encoding="utf-8")
        print("[+] Patched SubscriptionRsp.getCode -> '1000'")
    else:
        print("[-] Target not found in SubscriptionRsp.smali")

def patch_uimainactivity():
    p = ROOT / r"smali_classes3\com\yingmao\clash\act\UIMainActivity.smali"
    if not p.exists():
        print("[-] UIMainActivity.smali not found")
        return
    text = p.read_text(encoding="utf-8")
    
    # 替换 if-nez v2, :cond_15 -> goto :goto_a
    old_code = """    invoke-virtual {v1}, Lcom/yingmao/clash/net/http/entity/SubscriptionRsp;->getCode()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2, v4}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v2

    if-nez v2, :cond_15"""

    new_code = """    invoke-virtual {v1}, Lcom/yingmao/clash/net/http/entity/SubscriptionRsp;->getCode()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2, v4}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v2

    goto :goto_a"""

    if old_code in text:
        text = text.replace(old_code, new_code)
        p.write_text(text, encoding="utf-8")
        print("[+] Patched UIMainActivity pswitch_6 exitend dialog -> bypassed")
    else:
        print("[-] old_code not found in UIMainActivity.smali")

def patch_dialog_classes():
    for rel_path in [
        r"smali_classes3\com\yingmao\clash\view\dialog\EndTimeViewDialog.smali",
        r"smali_classes3\com\yingmao\clash\view\dialog\ActivityViewDialog.smali",
    ]:
        p = ROOT / rel_path
        if not p.exists():
            print(f"[-] {rel_path} not found")
            continue
        text = p.read_text(encoding="utf-8")
        if ".method public show()V" in text:
            print(f"[!] show() already exists in {rel_path}")
            continue
        # 插入在最后一个 .end method 之后
        idx = text.rfind(".end method")
        if idx != -1:
            show_method = """

.method public show()V
    .locals 0

    return-void
.end method
"""
            text = text[:idx + len(".end method")] + show_method + text[idx + len(".end method"):]
            p.write_text(text, encoding="utf-8")
            print(f"[+] Added dummy show() to {rel_path}")
        else:
            print(f"[-] Could not find .end method in {rel_path}")

if __name__ == "__main__":
    patch_subscription_rsp()
    patch_uimainactivity()
    patch_dialog_classes()
    print("[done] All dialog patches applied.")

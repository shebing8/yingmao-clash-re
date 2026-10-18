# -*- coding: utf-8 -*-
"""Auto-renew patch: on account-expiry (airportNode code!=1000 + msg contains 过期),
clear credentials and restart the process so the app auto-registers a fresh trial account."""
import re

BASE = r"C:\Users\33176\WorkBuddy AI\2026-10-13-20-59-50\yingmao\mod_out2"
UIMAIN = BASE + r"\smali_classes3\com\yingmao\clash\act\UIMainActivity.smali"

with open(UIMAIN, "r", encoding="utf-8") as f:
    src = f.read()

# Anchor: inside pswitch_6, after the code!="1000" check falls through (before dialog build)
anchor = """    invoke-static {v2, v4}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v2

    if-nez v2, :cond_15
"""
assert anchor in src, "pswitch_6 anchor not found"

inject = anchor + """
    invoke-virtual {v1}, Lcom/yingmao/clash/net/http/entity/SubscriptionRsp;->getMessage()Ljava/lang/String;

    move-result-object v2

    if-eqz v2, :cond_show_dialog

    const-string v3, "\\u8fc7\\u671f"

    invoke-virtual {v2, v3}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v3

    if-eqz v3, :cond_show_dialog

    invoke-static {v0}, Lcom/yingmao/clash/util/AutoRenew;->autoRenew(Landroid/app/Activity;)V

    goto/16 :goto_a

    :cond_show_dialog
"""

src = src.replace(anchor, inject, 1)
with open(UIMAIN, "w", encoding="utf-8", newline="\n") as f:
    f.write(src)
print("Patched UIMainActivity pswitch_6 -> AutoRenew.autoRenew")

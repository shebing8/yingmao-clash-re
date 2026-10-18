# -*- coding: utf-8 -*-
"""Identity patch: random getUniqueID + random OAID for fresh trial accounts."""
import re, sys

BASE = r"C:\Users\33176\WorkBuddy AI\2026-10-13-20-59-50\yingmao\mod_out2"
UTILS = BASE + r"\smali_classes3\com\yingmao\clash\util\Utils.smali"
COMPANION = BASE + r"\smali_classes3\com\yingmao\clash\app\MainApplication$Companion.smali"

def read(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def write(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

# ---------- Patch 1: Utils.getUniqueID ----------
src = read(UTILS)
m = re.search(r"\.method public final getUniqueID\(Landroid/content/Context;\)Ljava/lang/String;.*?\n\.end method", src, re.S)
assert m, "getUniqueID method not found"
new_method = """.method public final getUniqueID(Landroid/content/Context;)Ljava/lang/String;
    .locals 3

    sget-object v0, Lcom/yingmao/clash/util/Utils;->patchedId:Ljava/lang/String;

    if-eqz v0, :cond_random

    return-object v0

    :cond_random
    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;

    move-result-object v0

    invoke-virtual {v0}, Ljava/util/UUID;->toString()Ljava/lang/String;

    move-result-object v0

    const-string v1, "-"

    const-string v2, ""

    invoke-virtual {v0, v1, v2}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object v0

    const/4 v1, 0x0

    const/16 v2, 0x8

    invoke-virtual {v0, v1, v2}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v0

    sput-object v0, Lcom/yingmao/clash/util/Utils;->patchedId:Ljava/lang/String;

    return-object v0
.end method"""
src = src[:m.start()] + new_method + src[m.end():]
# add static field once (right after the .class line)
if "patchedId" not in src.split(".method")[0]:
    src = re.sub(r"(\.class public final Lcom/yingmao/clash/util/Utils;\n)",
                 r"\1\n.field public static patchedId:Ljava/lang/String;\n", src, count=1)
write(UTILS, src)
print("Patched Utils.getUniqueID")

# ---------- Patch 2: MainApplication$Companion.getOAID ----------
src = read(COMPANION)
m = re.search(r"\.method public final getOAID\(\)Ljava/lang/String;.*?\n\.end method", src, re.S)
assert m, "getOAID method not found"
new_method = """.method public final getOAID()Ljava/lang/String;
    .locals 3

    sget-object v0, Lcom/yingmao/clash/app/MainApplication$Companion;->patchedOaid:Ljava/lang/String;

    if-eqz v0, :cond_random

    return-object v0

    :cond_random
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;

    move-result-object v1

    invoke-virtual {v1}, Ljava/util/UUID;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;

    move-result-object v1

    invoke-virtual {v1}, Ljava/util/UUID;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    const-string v1, "-"

    const-string v2, ""

    invoke-virtual {v0, v1, v2}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object v0

    sput-object v0, Lcom/yingmao/clash/app/MainApplication$Companion;->patchedOaid:Ljava/lang/String;

    return-object v0
.end method"""
src = src[:m.start()] + new_method + src[m.end():]
if "patchedOaid" not in src.split(".method")[0]:
    src = re.sub(r"(\.class public final Lcom/yingmao/clash/app/MainApplication\$Companion;\n)",
                 r"\1\n.field public static patchedOaid:Ljava/lang/String;\n", src, count=1)
write(COMPANION, src)
print("Patched MainApplication$Companion.getOAID")
print("DONE")

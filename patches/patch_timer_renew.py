# -*- coding: utf-8 -*-
"""Timer-based auto-renew:
1) RestoreSessionHelper.startRestoreSession: if saved account older than 23h -> AutoRenew
2) SplashActivity registration success (new account + 20062): stamp acct_born=now
3) AutoRenew: add 5-min cooldown guard + last_renew stamp
"""
BASE = r"C:\Users\33176\WorkBuddy AI\2026-10-13-20-59-50\yingmao\mod_out2"
HELPER = BASE + r"\smali_classes3\com\yingmao\clash\act\RestoreSessionHelper.smali"
SPLASH = BASE + r"\smali_classes3\com\yingmao\clash\act\SplashActivity.smali"
RENEW = BASE + r"\smali_classes3\com\yingmao\clash\util\AutoRenew.smali"

def read(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def write(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

# ---------- 1) RestoreSessionHelper: age check at startRestoreSession ----------
src = read(HELPER)
anchor = """.method public final startRestoreSession()V
    .locals 6
"""
assert anchor in src, "startRestoreSession anchor not found"
inject = anchor + """
    invoke-static {}, Lcom/tencent/mmkv/MMKV;->defaultMMKV()Lcom/tencent/mmkv/MMKV;

    move-result-object v0

    const-string v1, "remember_username"

    invoke-virtual {v0, v1}, Lcom/tencent/mmkv/MMKV;->decodeString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :cond_age_ok

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    invoke-static {}, Lcom/tencent/mmkv/MMKV;->defaultMMKV()Lcom/tencent/mmkv/MMKV;

    move-result-object v2

    const-string v3, "acct_born"

    const-wide/16 v4, 0x0

    invoke-virtual {v2, v3, v4, v5}, Lcom/tencent/mmkv/MMKV;->decodeLong(Ljava/lang/String;J)J

    move-result-wide v4

    sub-long/2addr v0, v4

    const-wide v4, 0x4EF6D80L

    cmp-long v0, v0, v4

    if-lez v0, :cond_age_ok

    iget-object v0, p0, Lcom/yingmao/clash/act/RestoreSessionHelper;->a:Lcom/yingmao/clash/act/SplashActivity;

    invoke-static {v0}, Lcom/yingmao/clash/util/AutoRenew;->autoRenew(Landroid/app/Activity;)V

    return-void

    :cond_age_ok
"""
src = src.replace(anchor, inject, 1)
write(HELPER, src)
print("[1] RestoreSessionHelper age-check injected")

# ---------- 2) SplashActivity :goto_f (new registration success) ----------
src = read(SPLASH)
anchor = """    invoke-virtual {v3}, Lcom/yingmao/clash/act/RestoreSessionHelper;->markDone()V
"""
assert anchor in src, "goto_f markDone anchor not found"
inject = anchor + """
    invoke-static {}, Lcom/tencent/mmkv/MMKV;->defaultMMKV()Lcom/tencent/mmkv/MMKV;

    move-result-object v0

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v3

    const-string v5, "acct_born"

    invoke-virtual {v0, v5, v3, v4}, Lcom/tencent/mmkv/MMKV;->encode(Ljava/lang/String;J)Z
"""
src = src.replace(anchor, inject, 1)
print("[2] goto_f acct_born stamp injected")

# ---------- 3) SplashActivity 20062 branch ----------
anchor = """    const-string v5, "REGISTER: 20062 \\u81ea\\u52a8\\u767b\\u5f55, loginUsername="
"""
assert anchor in src, "20062 branch anchor not found"
inject = """    invoke-static {}, Lcom/tencent/mmkv/MMKV;->defaultMMKV()Lcom/tencent/mmkv/MMKV;

    move-result-object v7

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v8

    const-string v0, "acct_born"

    invoke-virtual {v7, v0, v8, v9}, Lcom/tencent/mmkv/MMKV;->encode(Ljava/lang/String;J)Z

""" + anchor
src = src.replace(anchor, inject, 1)
write(SPLASH, src)
print("[3] 20062 acct_born stamp injected")

# ---------- 4) AutoRenew: cooldown guard ----------
src = read(RENEW)
anchor = """.method public static autoRenew(Landroid/app/Activity;)V
    .locals 5
"""
assert anchor in src, "AutoRenew anchor not found"
inject = """.method public static autoRenew(Landroid/app/Activity;)V
    .locals 6

    invoke-static {}, Lcom/tencent/mmkv/MMKV;->defaultMMKV()Lcom/tencent/mmkv/MMKV;

    move-result-object v0

    const-string v1, "last_renew"

    const-wide/16 v2, 0x0

    invoke-virtual {v0, v1, v2, v3}, Lcom/tencent/mmkv/MMKV;->decodeLong(Ljava/lang/String;J)J

    move-result-wide v2

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v4

    sub-long v2, v4, v2

    const-wide v4, 0x493E0L

    cmp-long v2, v2, v4

    if-gtz v2, :cond_skip
"""
src = src.replace(anchor, inject, 1)

# stamp last_renew before restart
anchor2 = """    invoke-virtual {p0}, Landroid/app/Activity;->getPackageManager()Landroid/content/pm/PackageManager;
"""
assert anchor2 in src, "restart anchor not found"
inject2 = """    invoke-static {}, Lcom/tencent/mmkv/MMKV;->defaultMMKV()Lcom/tencent/mmkv/MMKV;

    move-result-object v1

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v2

    const-string v4, "last_renew"

    invoke-virtual {v1, v4, v2, v3}, Lcom/tencent/mmkv/MMKV;->encode(Ljava/lang/String;J)Z

""" + anchor2
src = src.replace(anchor2, inject2, 1)

# skip label at method end
anchor3 = """    invoke-static {v2}, Landroid/os/Process;->killProcess(I)V

    return-void
.end method"""
assert anchor3 in src, "method end anchor not found"
src = src.replace(anchor3, """    invoke-static {v2}, Landroid/os/Process;->killProcess(I)V

    return-void

    :cond_skip
    return-void
.end method""", 1)
write(RENEW, src)
print("[4] AutoRenew cooldown guard injected")
print("ALL DONE")

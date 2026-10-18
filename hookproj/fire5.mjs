import Java from 'frida-java-bridge';
function log(){ console.log("[F5] " + Array.prototype.join.call(arguments, " ")); }
Java.perform(function () {
    var MMKV = Java.use("com.tencent.mmkv.MMKV");
    var Long = Java.use("java.lang.Long");
    var RSH = Java.use("com.yingmao.clash.act.RestoreSessionHelper");
    var empty = Java.array("java.lang.Class", []);

    RSH.startRestoreSession.implementation = function () {
        log(">>> startRestoreSession CALLED");
        var r = this.startRestoreSession();
        log("<<< startRestoreSession RETURNED");
        return r;
    };
    try {
        var AR = Java.use("com.yingmao.clash.util.AutoRenew");
        AR.autoRenew.overload("android.app.Activity").implementation = function (a) {
            log(">>> AutoRenew.autoRenew CALLED");
            return this.autoRenew(a);
        };
    } catch (e) { log("AR hook err " + e); }

    // 观察 decodeLong 调用
    MMKV.decodeLong.overload("java.lang.String", "long").implementation = function (k, d) {
        var v = this.decodeLong(k, d);
        log("decodeLong('" + k + "') = " + v);
        return v;
    };

    // 打印当前值
    var mmkv = MMKV.defaultMMKV();
    log("acct_born=" + mmkv.decodeLong("acct_born", Long.valueOf(0).longValue()) +
        " now=" + Java.use("java.lang.System").currentTimeMillis());

    Java.choose("com.yingmao.clash.act.SplashActivity", {
        onMatch: function (a) {
            try {
                var m = a.getClass().getDeclaredMethod("k", empty);
                m.setAccessible(true);
                var helper = Java.cast(m.invoke(a, Java.array("java.lang.Object", [])), RSH);
                log("helper=" + helper);
                helper.startRestoreSession();
                log("invoke done");
            } catch (e) { log("ERR " + e); }
        },
        onComplete: function () { log("choose complete"); }
    });
});

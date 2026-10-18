import Java from 'frida-java-bridge';

function log(){ console.log("[PROBE] " + Array.prototype.join.call(arguments, " ")); }

Java.perform(function () {
    var MMKV = Java.use("com.tencent.mmkv.MMKV");
    var mmkv = MMKV.defaultMMKV();
    var Long = Java.use("java.lang.Long");
    var keys = ["remember_username","remember_password","ph_token","token","user_id",
                "is_register","expired","acct_born","last_renew","userCommand","isPerfect","logSwitch"];
    keys.forEach(function(k){
        try {
            log("MMKV " + k + " -> str=" + mmkv.decodeString(k) + " long=" + mmkv.decodeLong(k, Long.valueOf(-1).longValue()));
        } catch (e) { log("MMKV " + k + " ERR " + e); }
    });
    log("now=" + Java.use("java.lang.System").currentTimeMillis());

    var RSH = Java.use("com.yingmao.clash.act.RestoreSessionHelper");
    RSH.startRestoreSession.implementation = function () {
        log(">>> startRestoreSession CALLED");
        var r = this.startRestoreSession();
        log("<<< startRestoreSession returned");
        return r;
    };
    log("RSH hooked");

    try {
        var AR = Java.use("com.yingmao.clash.util.AutoRenew");
        AR.autoRenew.overload("android.app.Activity").implementation = function (a) {
            log(">>> AutoRenew.autoRenew CALLED act=" + a);
            return this.autoRenew(a);
        };
        log("AutoRenew hooked OK");
    } catch (e) { log("AutoRenew hook err: " + e); }
});

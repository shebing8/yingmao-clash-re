import Java from 'frida-java-bridge';
function log(){ console.log("[TRACE] " + Array.prototype.join.call(arguments, " ")); }

Java.perform(function () {
    var targets = [
        "com.yingmao.clash.act.SplashActivity",
        "com.yingmao.clash.act.RestoreSessionHelper",
        "com.yingmao.clash.vm.SplashAtyVM",
        "q.a2",
        "c9.d2"
    ];
    targets.forEach(function (cn) {
        try {
            var C = Java.use(cn);
            var methods = C.class.getDeclaredMethods();
            for (var i = 0; i < methods.length; i++) {
                var m = methods[i];
                var name = m.getName();
                if (name === "access$isNeedRegister") {
                    try {
                        C.access$isNeedRegister.implementation = function (a, b) {
                            log("access$isNeedRegister(" + b + ")");
                            return this.access$isNeedRegister(a, b);
                        };
                        log("hooked " + cn + ".access$isNeedRegister");
                    } catch (e) {}
                    continue;
                }
                if (name.indexOf("access$") === 0) continue;
                try {
                    var overloads = C[name];
                    if (overloads && overloads.overloads) {
                        overloads.overloads.forEach(function (ov, idx) {
                            try {
                                ov.implementation = function () {
                                    log(cn.substring(cn.lastIndexOf('.') + 1) + "." + name + "()");
                                    return ov.apply(this, arguments);
                                };
                            } catch (e) {}
                        });
                    }
                } catch (e) {}
            }
            log("class ready: " + cn);
        } catch (e) { log("skip " + cn + ": " + e); }
    });
});

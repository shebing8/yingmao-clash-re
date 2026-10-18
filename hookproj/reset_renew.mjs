import Java from 'frida-java-bridge';
Java.perform(function () {
    var MMKV = Java.use('com.tencent.mmkv.MMKV');
    var Long = Java.use('java.lang.Long');
    var m = MMKV.defaultMMKV();
    console.log('[*] before last_renew=' + m.decodeLong('last_renew', Long.valueOf(-1).longValue()));
    m.encode('last_renew', Long.valueOf(0).longValue());
    m.apply();
    console.log('[+] last_renew reset to 0, readback=' + m.decodeLong('last_renew', Long.valueOf(-1).longValue()));
    console.log('[*] username=' + m.decodeString('remember_username') + ' acct_born=' + m.decodeLong('acct_born', Long.valueOf(0).longValue()));
});

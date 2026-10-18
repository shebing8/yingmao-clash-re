import Java from 'frida-java-bridge';

Java.perform(function () {
    var MMKV = Java.use('com.tencent.mmkv.MMKV');
    var mmkv = MMKV.defaultMMKV();
    var Long = Java.use('java.lang.Long');
    console.log('[*] username=' + mmkv.decodeString('remember_username'));
    console.log('[*] acct_born=' + mmkv.decodeLong('acct_born', 0));
    console.log('[*] now=' + Java.use('java.lang.System').currentTimeMillis());
    // set acct_born to 25h ago using proper java long
    var now = Java.use('java.lang.System').currentTimeMillis();
    var born = Long.valueOf(now - 25 * 3600 * 1000);
    mmkv.encode('acct_born', born.longValue());
    mmkv.apply();
    console.log('[+] acct_born set to 25h ago, readback=' + mmkv.decodeLong('acct_born', 0));
});

const frida = require('frida');
const fs = require('fs');
(async function () {
    const bundle = process.argv[2];
    const dev = await frida.getUsbDevice(15000);
    const pid = await dev.spawn(['com.yingmao.clash'], {});
    console.log("spawned pid=" + pid);
    const session = await dev.attach(pid);
    const script = await session.createScript(fs.readFileSync(bundle, 'utf8'));
    script.message.connect(m => {
        const p = m.payload !== undefined ? m.payload : m;
        if (typeof p === 'string') console.log(p);
        else if (p && p.type === 'error') console.log('SCRIPT ERROR: ' + p.description + '\n' + p.stack);
        else console.log(JSON.stringify(p));
    });
    script.detached.connect((r) => { console.log("script detached: " + r); process.exit(0); });
    await script.load();
    await dev.resume(pid);
    console.log("resumed, waiting...");
    await new Promise(() => {});
})().catch(e => { console.error('ERR', e); process.exit(1); });

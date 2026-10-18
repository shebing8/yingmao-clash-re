const frida = require('frida');
const fs = require('fs');
(async function () {
    const pid = parseInt(process.argv[2]);
    const src = process.argv[3];
    const dev = await frida.getUsbDevice(15000);
    const session = await dev.attach(pid);
    const script = await session.createScript(fs.readFileSync(src, 'utf8'));
    script.message.connect(m => {
        const p = m.payload !== undefined ? m.payload : m;
        if (typeof p === 'string') console.log(p);
        else if (p && p.type === 'error') console.log('SCRIPT ERROR: ' + p.description + '\n' + p.stack);
        else console.log(JSON.stringify(p));
    });
    await script.load();
    await new Promise(() => {});
    process.exit(0);
})().catch(e => { console.error('ERR', e); process.exit(1); });

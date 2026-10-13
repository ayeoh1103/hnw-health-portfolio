// 运行时冒烟：用 DOM 桩执行页面应用逻辑，验证数据取值路径与图表配置完整性
const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const appCode = blocks[blocks.length - 1];
const dataCode = blocks[blocks.length - 2];

const els = {};
const setOptionCalls = [];
global.window = { addEventListener: () => {} };
global.document = {
  getElementById: (id) => {
    if (!els[id]) els[id] = { id, innerHTML: '', textContent: '', style: {} };
    return els[id];
  },
};
global.echarts = {
  init: () => ({
    setOption: (opt) => setOptionCalls.push(opt),
    resize: () => {},
  }),
};

try {
  // 浏览器中两个 <script> 共享全局词法作用域；此处合并执行以复现该行为
  eval(dataCode + '\n;dataObj = D;\n' + appCode);
} catch (e) {
  console.error('APP RUNTIME ERROR:', e.message, '\n', e.stack.split('\n').slice(0, 4).join('\n'));
  process.exit(1);
}

console.log('图表渲染调用数:', setOptionCalls.length);
console.log('写入 DOM 的元素数:', Object.keys(els).length);

// 检查每个图表配置中的异常值
let issues = 0;
setOptionCalls.forEach((opt, i) => {
  const s = JSON.stringify(opt, (k, v) => {
    if (typeof v === 'number' && !Number.isFinite(v)) { issues++; return 'BAD_NUMBER'; }
    if (v === undefined) { issues++; return 'UNDEFINED'; }
    return v;
  });
  const series = opt.series || [];
  const hasNaN = /BAD_NUMBER|UNDEFINED/.test(s);
  console.log(`  chart#${i}: series=${series.length} ${hasNaN ? '⚠ 存在异常值' : 'ok'}`);
});

// 校验关键 DOM 输出非空
['kpis', 'metrics', 'insights', 'seg-cards', 'use-cards', 'tbl-core', 'tbl-strata', 'tbl-rule', 'tbl-dict']
  .forEach(id => {
    const v = els[id] ? els[id].innerHTML.length : 0;
    console.log(`  #${id}: ${v > 50 ? 'ok (' + v + ' 字符)' : '⚠ 空或过短 (' + v + ')'}`);
  });

console.log(issues === 0 ? '\nSMOKE TEST PASSED' : `\nSMOKE TEST 存在 ${issues} 处异常值`);

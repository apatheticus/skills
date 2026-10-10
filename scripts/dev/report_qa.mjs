#!/usr/bin/env node
/**
 * Headless QA for the reflect report: the browser half of "Open the sample in light
 * and dark before shipping" in skills/reflect/assets/template.html's header.
 *
 * Renders the report (the template's sample data, or --data), serves it on 127.0.0.1,
 * and drives playwright-cli through 1280px and 375px in light and dark with reduced
 * motion, then once more at 1280px with motion on, scrolling to the bottom. It fails on
 *   - horizontal overflow (names the first offending elements)
 *   - any console error
 *   - any request that leaves 127.0.0.1
 *   - an h2 sequence that is empty or differs between variants
 * and saves a full-page PNG per variant to --out for a human look.
 *
 * Usage:
 *   node scripts/dev/report_qa.mjs                       sample data, temp out dir
 *   node scripts/dev/report_qa.mjs --data <json> --out <dir>
 *
 * Dev-only: lives outside skills/ so it never ships. Needs python3 and playwright-cli
 * on PATH (file:// is blocked by playwright-cli, hence the local server). No npm deps.
 */

import { execFile } from 'node:child_process';
import { createServer } from 'node:http';
import { mkdtempSync, mkdirSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

const run = promisify(execFile);
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const RENDER = join(ROOT, 'skills', 'reflect', 'scripts', 'render_report.py');

const arg = (name) => {
  const i = process.argv.indexOf(name);
  return i > 0 ? process.argv[i + 1] : undefined;
};
const OUT = resolve(arg('--out') ?? mkdtempSync(join(tmpdir(), 'reflect-qa-')));
const DATA = arg('--data');
mkdirSync(OUT, { recursive: true });

const VIEWPORTS = [
  [1280, 900],
  [375, 812],
];
const SCHEMES = ['light', 'dark'];
const SESSION = `-s=reflect-qa-${process.pid}`;

const failures = [];
const fail = (msg) => failures.push(msg);

// ------------------------------------------------------------------ render

const report = join(OUT, 'report.html');
const renderArgs = DATA
  ? [RENDER, '--data', resolve(DATA), '--status', join(OUT, 'reflect-status.json'), '--out', report]
  : [RENDER, '--sample', '--out', report];
try {
  const { stdout } = await run('python3', renderArgs, { cwd: ROOT });
  console.log(`render: ${stdout.trim().split('\n').at(-1)}`);
} catch (e) {
  console.error(`render failed:\n${e.stdout ?? ''}${e.stderr ?? e.message}`);
  process.exit(1);
}

// ------------------------------------------------------------------- serve

const html = readFileSync(report);
const server = createServer((req, res) => {
  if (req.url === '/report.html') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(html);
  } else {
    // 204, not 404: the browser asks for /favicon.ico on its own, and a 404 there
    // would read as a console error the report never caused.
    res.writeHead(req.url === '/favicon.ico' ? 204 : 404);
    res.end();
  }
});
await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
const origin = `http://127.0.0.1:${server.address().port}`;
const url = `${origin}/report.html`;

// ---------------------------------------------------------------- browser

// cwd: OUT, because playwright-cli writes a page snapshot into ./.playwright-cli/ on
// every navigation, and the repo root is no place for those.
const cli = async (...args) =>
  (await run('playwright-cli', [SESSION, ...args], { cwd: OUT, maxBuffer: 1 << 24 })).stdout;
const evalJson = async (fn) => JSON.parse(await cli('--raw', 'eval', fn));
const consoleErrors = async () => {
  const out = await cli('console', 'error');
  const n = Number(out.match(/Errors: (\d+)/)?.[1] ?? 0);
  return n ? out.split('\n').filter((l) => l.startsWith('[ERROR]')) : [];
};

const PROBE = `async () => {
  await new Promise((r) => setTimeout(r, 400));
  const w = innerWidth;
  const scrollWidth = document.documentElement.scrollWidth;
  // An element past the right edge only widens the page if no ancestor clips it, so
  // skip anything inside an overflow box and name the outermost offenders.
  const clipped = (el) => {
    for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
      if (getComputedStyle(a).overflowX !== 'visible') return true;
    }
    return false;
  };
  const wide = scrollWidth > w + 1
    ? [...document.querySelectorAll('body *')].filter((el) =>
        el.getBoundingClientRect().right > w + 1 && getComputedStyle(el).position !== 'fixed' && !clipped(el))
    : [];
  const offenders = wide
    .filter((el) => !wide.includes(el.parentElement))
    .slice(0, 3)
    .map((el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
      (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\\s+/).join('.') : ''));
  return {
    scrollWidth,
    width: w,
    offenders,
    theme: document.documentElement.dataset.theme || null,
    h2: [...document.querySelectorAll('h2')].map((h) => h.textContent.trim()),
    resources: performance.getEntriesByType('resource').map((e) => e.name),
  };
}`;

const SCROLL_THROUGH = `async () => {
  for (let y = 0; y < document.documentElement.scrollHeight; y += 500) {
    scrollTo(0, y);
    await new Promise((r) => setTimeout(r, 120));
  }
  await new Promise((r) => setTimeout(r, 800));
  return document.documentElement.scrollHeight;
}`;

const offsite = (urls) =>
  urls.filter((u) => !u.startsWith(origin) && !u.startsWith('data:') && !u.startsWith('blob:'));

let h2Baseline = null;
try {
  await cli('open', url);
  await cli('set-reduced-motion', 'reduce');

  for (const [w, h] of VIEWPORTS) {
    for (const scheme of SCHEMES) {
      const tag = `${w}px ${scheme}`;
      await cli('resize', String(w), String(h));
      await cli('set-color-scheme', scheme);
      await cli('goto', url);
      const p = await evalJson(PROBE);

      if (p.scrollWidth > p.width + 1) {
        fail(`${tag}: horizontal overflow, ${p.scrollWidth}px in a ${p.width}px viewport (${p.offenders.join(', ') || 'no single element'})`);
      }
      if (p.theme && p.theme !== scheme) fail(`${tag}: data-theme is ${p.theme}`);
      if (!p.h2.length) fail(`${tag}: no h2 headings rendered`);
      h2Baseline ??= p.h2;
      if (p.h2.join('|') !== h2Baseline.join('|')) fail(`${tag}: h2 sequence differs from ${VIEWPORTS[0][0]}px light`);
      for (const u of offsite(p.resources)) fail(`${tag}: request left 127.0.0.1: ${u}`);
      for (const e of await consoleErrors()) fail(`${tag}: ${e}`);

      const png = join(OUT, `qa-${w}-${scheme}.png`);
      await cli('screenshot', '--full-page', `--filename=${png}`);
      console.log(`${tag}: ${p.h2.length} h2, ${p.scrollWidth}px wide, screenshot ${png}`);
    }
  }

  // Motion pass: GSAP only runs its tweens without reduced motion, and its errors
  // surface only once the scroll reaches the sections that animate.
  await cli('clear-reduced-motion');
  await cli('resize', String(VIEWPORTS[0][0]), String(VIEWPORTS[0][1]));
  await cli('set-color-scheme', 'light');
  await cli('goto', url);
  const height = await evalJson(SCROLL_THROUGH);
  for (const e of await consoleErrors()) fail(`motion pass: ${e}`);
  console.log(`motion pass: scrolled ${height}px with motion on`);
} catch (e) {
  fail(`playwright-cli: ${(e.stderr || e.stdout || e.message).trim().split('\n')[0]}`);
} finally {
  await cli('close').catch(() => {});
  server.close();
}

// ------------------------------------------------------------------ report

if (h2Baseline) console.log(`h2 order: ${h2Baseline.join(' → ')}`);
for (const f of failures) console.error(`FAIL  ${f}`);
console.log(failures.length ? `\n${failures.length} failure(s); screenshots in ${OUT}` : `\nok — screenshots in ${OUT}`);
process.exit(failures.length ? 1 : 0);

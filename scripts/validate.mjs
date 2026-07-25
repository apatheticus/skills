#!/usr/bin/env node
/**
 * Validates the repository against both distribution conventions:
 *   - `npx skills add <owner>/<repo>`  -> skills/<name>/SKILL.md
 *   - `/plugin marketplace add <owner>/<repo>` -> .claude-plugin/{marketplace,plugin}.json
 *
 * Usage:
 *   node scripts/validate.mjs          check only, exit 1 on error
 *   node scripts/validate.mjs --sync   rewrite plugin.json skills[] from disk, then check
 *
 * No dependencies. Node >= 18.
 */

import { readdirSync, readFileSync, writeFileSync, existsSync, statSync } from 'node:fs';
import { join, dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SKILLS_DIR = join(ROOT, 'skills');
const PLUGIN_MANIFEST = join(ROOT, '.claude-plugin', 'plugin.json');
const MARKETPLACE_MANIFEST = join(ROOT, '.claude-plugin', 'marketplace.json');

const SYNC = process.argv.includes('--sync');

const NAME_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const MAX_NAME = 64;
const MAX_DESCRIPTION = 1024;

const KNOWN_KEYS = new Set([
  'name',
  'description',
  'allowed-tools',
  'disable-model-invocation',
  'user-invocable',
  'argument-hint',
  'version',
  'license',
  'metadata',
  'compatibility',
  'homepage',
  'repository',
  'author',
]);

const errors = [];
const warnings = [];
const err = (file, msg) => errors.push(`${file}: ${msg}`);
const warn = (file, msg) => warnings.push(`${file}: ${msg}`);
const rel = (p) => relative(ROOT, p) || '.';

/** Minimal YAML frontmatter reader — flat scalar keys only, which is all a SKILL.md needs. */
function parseFrontmatter(source, file) {
  const lines = source.split(/\r?\n/);
  if (lines[0]?.trim() !== '---') {
    err(file, 'missing YAML frontmatter — the first line must be exactly `---`');
    return null;
  }
  const close = lines.indexOf('---', 1);
  if (close === -1) {
    err(file, 'frontmatter is never closed with `---`');
    return null;
  }

  const data = {};
  let lastKey = null;
  for (let i = 1; i < close; i++) {
    const line = lines[i];
    if (!line.trim() || line.trimStart().startsWith('#')) continue;

    // Nested/blocked values (metadata maps, list items) — record the parent key, skip the value.
    if (/^\s/.test(line)) {
      if (lastKey) data[lastKey] ??= '';
      continue;
    }

    const match = line.match(/^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$/);
    if (!match) {
      err(file, `frontmatter line ${i + 1} is not \`key: value\` -> ${line.trim()}`);
      continue;
    }
    const [, key, rawValue] = match;
    if (key in data) err(file, `duplicate frontmatter key \`${key}\``);
    lastKey = key;
    let value = rawValue.trim();
    const quoted =
      (value.startsWith('"') && value.endsWith('"') && value.length > 1) ||
      (value.startsWith("'") && value.endsWith("'") && value.length > 1);
    if (quoted) {
      value = value.slice(1, -1);
    } else if (/:\s/.test(value) || value.endsWith(':')) {
      // A real YAML parser reads `key: some text: more` as a nested mapping and throws
      // ("Nested mappings are not allowed in compact mappings"), which makes installers
      // skip the whole skill. This parser is naive enough to accept it, so check it here.
      err(
        file,
        `frontmatter key \`${key}\` has an unquoted value containing a colon followed by a ` +
          `space, which is not valid YAML — rewrite the colon (an em dash reads well) or ` +
          `quote the whole value`
      );
    }
    data[key] = value;
  }
  return data;
}

function readJson(path) {
  if (!existsSync(path)) {
    err(rel(path), 'file is missing');
    return null;
  }
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (e) {
    err(rel(path), `invalid JSON — ${e.message}`);
    return null;
  }
}

/** Every directory under skills/ that holds a SKILL.md, nesting allowed (skills/<group>/<name>). */
function findSkillDirs(dir, found = []) {
  if (!existsSync(dir)) return found;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name.startsWith('.')) continue;
    const child = join(dir, entry.name);
    if (existsSync(join(child, 'SKILL.md'))) found.push(child);
    else findSkillDirs(child, found);
  }
  return found;
}

// ---------------------------------------------------------------- skills

const skillDirs = findSkillDirs(SKILLS_DIR).sort();
const seenNames = new Map();

if (skillDirs.length === 0) {
  err('skills/', 'no skills found — expected at least one skills/<name>/SKILL.md');
}

for (const dir of skillDirs) {
  const skillFile = join(dir, 'SKILL.md');
  const label = rel(skillFile);
  const dirName = dir.split('/').pop();

  const source = readFileSync(skillFile, 'utf8');
  const fm = parseFrontmatter(source, label);
  if (!fm) continue;

  for (const key of Object.keys(fm)) {
    if (!KNOWN_KEYS.has(key)) warn(label, `unrecognized frontmatter key \`${key}\``);
  }

  const name = fm.name;
  if (!name) {
    err(label, 'frontmatter is missing required key `name`');
  } else {
    if (!NAME_RE.test(name)) err(label, `name \`${name}\` must be lowercase kebab-case`);
    if (name.length > MAX_NAME) err(label, `name is ${name.length} chars, max ${MAX_NAME}`);
    if (name !== dirName) err(label, `name \`${name}\` does not match its directory \`${dirName}\``);
    if (seenNames.has(name)) {
      err(label, `duplicate skill name \`${name}\`, already used by ${seenNames.get(name)}`);
    } else {
      seenNames.set(name, rel(dir));
    }
  }

  const description = fm.description;
  if (!description) {
    err(label, 'frontmatter is missing required key `description`');
  } else {
    if (description.length > MAX_DESCRIPTION) {
      err(label, `description is ${description.length} chars, max ${MAX_DESCRIPTION}`);
    }
    if (description.length < 40) {
      warn(label, 'description is very short — say what it does AND when to trigger it');
    }
  }

  for (const bool of ['disable-model-invocation', 'user-invocable']) {
    if (bool in fm && !['true', 'false'].includes(String(fm[bool]))) {
      err(label, `\`${bool}\` must be true or false, got \`${fm[bool]}\``);
    }
  }

  const body = source.split(/\r?\n/).slice(source.split(/\r?\n/).indexOf('---', 1) + 1);
  if (body.join('').trim() === '') err(label, 'skill body is empty');
  if (body.length > 500) warn(label, `body is ${body.length} lines — move detail into reference/`);
}

// ------------------------------------------------------------ plugin.json

const expectedSkills = skillDirs.map((d) => `./${rel(d)}`).sort();

if (SYNC && existsSync(PLUGIN_MANIFEST)) {
  const raw = readJson(PLUGIN_MANIFEST);
  if (raw) {
    raw.skills = expectedSkills;
    writeFileSync(PLUGIN_MANIFEST, `${JSON.stringify(raw, null, 2)}\n`);
    console.log(`synced ${rel(PLUGIN_MANIFEST)} -> ${expectedSkills.length} skill(s)`);
  }
}

const plugin = readJson(PLUGIN_MANIFEST);
if (plugin) {
  const label = rel(PLUGIN_MANIFEST);
  for (const key of ['name', 'description', 'version']) {
    if (!plugin[key]) err(label, `missing required key \`${key}\``);
  }
  if (plugin.name && !NAME_RE.test(plugin.name)) {
    err(label, `plugin name \`${plugin.name}\` must be lowercase kebab-case`);
  }
  if (plugin.version && !/^\d+\.\d+\.\d+/.test(plugin.version)) {
    err(label, `version \`${plugin.version}\` is not semver`);
  }

  const listed = Array.isArray(plugin.skills) ? plugin.skills : [];
  if (!Array.isArray(plugin.skills)) {
    err(label, '`skills` must be an array of paths');
  }
  for (const entry of listed) {
    const target = resolve(ROOT, entry);
    if (!existsSync(join(target, 'SKILL.md'))) {
      err(label, `listed skill \`${entry}\` has no SKILL.md on disk`);
    }
  }
  const listedSet = new Set(listed.map((e) => `./${rel(resolve(ROOT, e))}`));
  for (const expected of expectedSkills) {
    if (!listedSet.has(expected)) {
      err(label, `skill \`${expected}\` exists on disk but is not listed — run \`npm run sync\``);
    }
  }

  for (const dirKey of ['commands', 'agents', 'hooks', 'mcpServers']) {
    const value = plugin[dirKey];
    if (typeof value === 'string' && !existsSync(resolve(ROOT, value))) {
      err(label, `\`${dirKey}\` points at \`${value}\`, which does not exist`);
    }
  }
}

// ------------------------------------------------------- marketplace.json

const marketplace = readJson(MARKETPLACE_MANIFEST);
if (marketplace) {
  const label = rel(MARKETPLACE_MANIFEST);
  if (!marketplace.name) err(label, 'missing required key `name`');
  else if (!NAME_RE.test(marketplace.name)) {
    err(label, `marketplace name \`${marketplace.name}\` must be lowercase kebab-case`);
  }
  if (!marketplace.owner?.name) err(label, 'missing required key `owner.name`');

  const plugins = marketplace.plugins;
  if (!Array.isArray(plugins) || plugins.length === 0) {
    err(label, '`plugins` must be a non-empty array');
  } else {
    for (const [i, entry] of plugins.entries()) {
      const at = `plugins[${i}]`;
      if (!entry.name) err(label, `${at} is missing \`name\``);
      if (!entry.description) err(label, `${at} is missing \`description\``);
      if (!entry.source) {
        err(label, `${at} is missing \`source\``);
      } else if (typeof entry.source === 'string') {
        const target = resolve(ROOT, entry.source);
        if (!existsSync(target) || !statSync(target).isDirectory()) {
          err(label, `${at} source \`${entry.source}\` is not a directory in this repo`);
        } else if (!existsSync(join(target, '.claude-plugin', 'plugin.json'))) {
          err(label, `${at} source \`${entry.source}\` has no .claude-plugin/plugin.json`);
        }
      }
      if (entry.source === './' && plugin && entry.name !== plugin.name) {
        err(
          label,
          `${at} name \`${entry.name}\` must match plugin.json name \`${plugin.name}\``,
        );
      }
    }
  }
}

// ------------------------------------------------------------ README table

/**
 * The Skills table is the only place a human learns a skill exists, so a new skill that
 * never gets a row ships invisible. Columns 1 and 3 are derivable and checked exactly;
 * column 2 is prose written at a human — the frontmatter `description` is written at an
 * agent and runs 4-6x longer, so it is deliberately NOT reused here. Presence only.
 */
const README = join(ROOT, 'README.md');
const TABLE_START = '<!-- skills:table start -->';
const TABLE_END = '<!-- skills:table end -->';

/** `https://github.com/owner/repo` -> `owner/repo`, so the install command is never hardcoded. */
function repoSlug(source) {
  const raw = typeof source === 'string' ? source : source?.url;
  return String(raw ?? '').match(/github\.com[/:]([^/]+\/[^/.]+?)(?:\.git)?\/*$/)?.[1] ?? null;
}

/** Split a markdown table row into cells, honouring `\|` escapes inside a cell. */
const cellsOf = (row) =>
  row
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split(/(?<!\\)\|/)
    .map((c) => c.trim());

if (!existsSync(README)) {
  err('README.md', 'file is missing');
} else {
  const label = 'README.md';
  const source = readFileSync(README, 'utf8');
  const start = source.indexOf(TABLE_START);
  const end = source.indexOf(TABLE_END);
  const slug = repoSlug(plugin?.repository);

  if (start === -1 || end === -1 || end < start) {
    err(label, `the Skills table must be wrapped in \`${TABLE_START}\` and \`${TABLE_END}\``);
  } else if (!slug) {
    err(
      rel(PLUGIN_MANIFEST),
      '`repository` is not a github.com URL, so the install command cannot be derived',
    );
  } else {
    const lines = source
      .slice(start + TABLE_START.length, end)
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter((l) => l.startsWith('|') && !/^\|[\s|:-]+\|$/.test(l));

    const [header, ...rows] = lines;
    if (!header || cellsOf(header).length !== 3) {
      err(label, 'the Skills table needs exactly 3 columns: skill, description, install command');
    }

    const rowNames = new Map();
    for (const row of rows) {
      const cells = cellsOf(row);
      if (cells.length !== 3) {
        err(label, `Skills table row has ${cells.length} columns, expected 3 -> ${row.slice(0, 60)}`);
        continue;
      }
      const [first, description, command] = cells;
      const link = first.match(/^\[`([^`]+)`\]\(\.\/(.+?)\/?\)$/);
      if (!link) {
        err(label, `Skills table column 1 must be \`[\`name\`](./skills/name)\` -> ${first}`);
        continue;
      }
      const [, name, path] = link;

      if (rowNames.has(name)) err(label, `Skills table lists \`${name}\` twice`);
      rowNames.set(name, true);

      const dir = seenNames.get(name);
      if (!dir) {
        err(label, `Skills table row \`${name}\` matches no skill under skills/`);
        continue;
      }
      if (path !== dir) err(label, `row \`${name}\` links to \`./${path}\`, but the skill is at \`./${dir}\``);
      if (!description) err(label, `row \`${name}\` has an empty description — write one, do not paste the frontmatter`);

      const expected = `\`npx skills add ${slug} -s ${name}\``;
      if (command !== expected) {
        err(label, `row \`${name}\` column 3 should be ${expected}, got ${command || '(empty)'}`);
      }
    }

    for (const name of seenNames.keys()) {
      if (!rowNames.has(name)) {
        err(label, `skill \`${name}\` has no row in the Skills table — add one, all three columns`);
      }
    }
  }
}

// ------------------------------------------------------------------ report

for (const w of warnings) console.warn(`warn  ${w}`);
for (const e of errors) console.error(`ERROR ${e}`);

if (errors.length > 0) {
  console.error(`\n${errors.length} error(s), ${warnings.length} warning(s)`);
  process.exit(1);
}

console.log(
  `ok — ${skillDirs.length} skill(s) validated, manifests consistent` +
    (warnings.length ? `, ${warnings.length} warning(s)` : ''),
);

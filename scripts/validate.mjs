#!/usr/bin/env node
/**
 * Validates the repository against both distribution conventions:
 *   - `npx skills add <owner>/<repo>`  -> skills/<name>/SKILL.md
 *   - `/plugin marketplace add <owner>/<repo>` -> .claude-plugin/marketplace.json
 *
 * The marketplace is the only plugin manifest. Each entry shares `source: "./"` and
 * declares its own `skills[]` under `strict: false`, which is how one repository root
 * publishes several disjoint plugins without a `plugin.json` at that root.
 *
 * Usage:
 *   node scripts/validate.mjs          check only, exit 1 on error
 *   node scripts/validate.mjs --sync   sort each entry's skills[], then check
 *
 * `--sync` never assigns a skill to a plugin — which set a new skill belongs in is a
 * judgement call, so it is hand-written and the membership invariant below enforces
 * that every skill lands in exactly one entry.
 *
 * No dependencies. Node >= 18.
 */

import { readdirSync, readFileSync, writeFileSync, existsSync, statSync } from 'node:fs';
import { join, dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SKILLS_DIR = join(ROOT, 'skills');
const MARKETPLACE_MANIFEST = join(ROOT, '.claude-plugin', 'marketplace.json');
const PACKAGE_MANIFEST = join(ROOT, 'package.json');

const SYNC = process.argv.includes('--sync');

const NAME_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const MAX_NAME = 64;
// Claude Code renders `description` and `when_to_use` as one string in the skill
// listing and truncates the pair at 1,536 characters (`skillListingMaxDescChars`).
// The budget is therefore on the SUM, not on either field, and truncation is from
// the end -- so the key trigger belongs at the front of `description`.
// See https://code.claude.com/docs/en/skills.
const MAX_LISTING = 1536;

const KNOWN_KEYS = new Set([
  'name',
  'description',
  'when_to_use',
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
  const whenToUse = fm.when_to_use ?? '';
  if (!description) {
    err(label, 'frontmatter is missing required key `description`');
  } else {
    const listing = description.length + whenToUse.length;
    if (listing > MAX_LISTING) {
      err(
        label,
        `description (${description.length}) + when_to_use (${whenToUse.length}) ` +
          `is ${listing} chars, max ${MAX_LISTING} — cut whichever half is less load-bearing`,
      );
    }
    if (description.length < 40) {
      warn(label, 'description is very short — say what it does AND when to trigger it');
    }
  }

  // A capability nobody can name is a capability nobody reaches. Every diagram type
  // this skill can draw must appear in the text the model sees before deciding to
  // load the skill, so adding a type to diagrams.json costs trigger surface by
  // construction rather than by discipline.
  const diagramCatalog = join(dir, 'scripts', 'diagrams.json');
  if (existsSync(diagramCatalog)) {
    const catalog = readJson(diagramCatalog);
    const listing = `${description ?? ''}\n${whenToUse}`;
    const missing = Object.keys(catalog?.types ?? {}).filter((slug) => !listing.includes(slug));
    if (missing.length) {
      err(
        label,
        `${missing.length} diagram type(s) in scripts/diagrams.json never appear in ` +
          `description or when_to_use: ${missing.join(', ')}`,
      );
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

// ------------------------------------------------------- marketplace.json

const diskSkills = skillDirs.map((d) => `./${rel(d)}`).sort();
const SEMVER_RE = /^\d+\.\d+\.\d+/;

/** `./skills/<name>` -> the one plugin entry that lists it. */
const membership = new Map();
/** skill name -> plugin name, for the README table's Plugin column. */
const pluginOfSkill = new Map();

if (SYNC && existsSync(MARKETPLACE_MANIFEST)) {
  const raw = readJson(MARKETPLACE_MANIFEST);
  if (raw && Array.isArray(raw.plugins)) {
    for (const entry of raw.plugins) {
      if (Array.isArray(entry.skills)) entry.skills = [...entry.skills].sort();
    }
    // Node's JSON.stringify leaves non-ASCII alone, so the `ø` in `Zerø Effort` survives.
    // Never round-trip this file through a serializer that escapes it (Python's json.dumps
    // defaults to ensure_ascii=True and mangles it in a way this validator cannot see).
    writeFileSync(MARKETPLACE_MANIFEST, `${JSON.stringify(raw, null, 2)}\n`);
    console.log(`synced ${rel(MARKETPLACE_MANIFEST)} -> ${raw.plugins.length} plugin(s)`);
  }
}

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
    const pluginNames = [];
    for (const [i, entry] of plugins.entries()) {
      const at = entry.name ? `plugins[${i}] \`${entry.name}\`` : `plugins[${i}]`;

      if (!entry.name) {
        err(label, `${at} is missing \`name\``);
      } else {
        if (!NAME_RE.test(entry.name)) {
          err(label, `${at} plugin name must be lowercase kebab-case`);
        }
        if (pluginNames.includes(entry.name)) err(label, `${at} is declared twice`);
        pluginNames.push(entry.name);
      }
      if (!entry.description) err(label, `${at} is missing \`description\``);
      if (!entry.version) err(label, `${at} is missing \`version\``);
      else if (!SEMVER_RE.test(entry.version)) {
        err(label, `${at} version \`${entry.version}\` is not semver`);
      }

      let sourceDir = null;
      if (!entry.source) {
        err(label, `${at} is missing \`source\``);
      } else if (typeof entry.source === 'string') {
        const target = resolve(ROOT, entry.source);
        if (!existsSync(target) || !statSync(target).isDirectory()) {
          err(label, `${at} source \`${entry.source}\` is not a directory in this repo`);
        } else {
          sourceDir = target;
        }
      }

      // Several entries share one source directory, so that directory carries no
      // plugin.json and each entry must instead declare its own skills[] under
      // `strict: false`. An entry that is neither will not resolve at install time.
      if (sourceDir && !existsSync(join(sourceDir, '.claude-plugin', 'plugin.json'))) {
        if (entry.strict !== false) {
          err(
            label,
            `${at} source \`${entry.source}\` has no .claude-plugin/plugin.json, so the ` +
              'entry must set `"strict": false`',
          );
        }
        if (!Array.isArray(entry.skills) || entry.skills.length === 0) {
          err(
            label,
            `${at} source \`${entry.source}\` has no .claude-plugin/plugin.json, so the ` +
              'entry must list its own `skills[]`',
          );
        }
      }

      for (const listed of Array.isArray(entry.skills) ? entry.skills : []) {
        const target = resolve(ROOT, listed);
        if (!existsSync(join(target, 'SKILL.md'))) {
          err(label, `${at} lists \`${listed}\`, which has no SKILL.md on disk`);
          continue;
        }
        const key = `./${rel(target)}`;
        const owner = membership.get(key);
        if (owner) {
          err(
            label,
            owner === entry.name
              ? `${at} lists \`${key}\` twice`
              : `skill \`${key}\` is listed by both \`${owner}\` and \`${entry.name}\` — ` +
                'a skill belongs to exactly one plugin',
          );
          continue;
        }
        membership.set(key, entry.name);
        pluginOfSkill.set(key.split('/').pop(), entry.name);
      }

      for (const dirKey of ['commands', 'agents', 'hooks', 'mcpServers']) {
        const value = entry[dirKey];
        if (typeof value === 'string' && !existsSync(resolve(ROOT, value))) {
          err(label, `${at} \`${dirKey}\` points at \`${value}\`, which does not exist`);
        }
      }
    }

    // Set membership is a judgement call, so `--sync` will not guess it. A skill that
    // no plugin lists ships invisible on the plugin channel, which is why this errors
    // rather than warns.
    for (const onDisk of diskSkills) {
      if (!membership.has(onDisk)) {
        err(
          label,
          `skill \`${onDisk}\` exists on disk but no plugin lists it — add it to exactly ` +
            `one of: ${pluginNames.join(', ') || '(no named plugins)'}`,
        );
      }
    }
  }
}

// ------------------------------------------------------------ README table

/**
 * The Skills table is the only place a human learns a skill exists, so a new skill that
 * never gets a row ships invisible. Columns 1, 2 and 4 are derivable and checked exactly;
 * column 3 is prose written at a human — the frontmatter `description` is written at an
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
  const slug = repoSlug(readJson(PACKAGE_MANIFEST)?.repository);

  if (start === -1 || end === -1 || end < start) {
    err(label, `the Skills table must be wrapped in \`${TABLE_START}\` and \`${TABLE_END}\``);
  } else if (!slug) {
    err(
      rel(PACKAGE_MANIFEST),
      '`repository` is not a github.com URL, so the install command cannot be derived',
    );
  } else {
    const lines = source
      .slice(start + TABLE_START.length, end)
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter((l) => l.startsWith('|') && !/^\|[\s|:-]+\|$/.test(l));

    const [header, ...rows] = lines;
    if (!header || cellsOf(header).length !== 4) {
      err(
        label,
        'the Skills table needs exactly 4 columns: skill, plugin, description, install command',
      );
    }

    const rowNames = new Map();
    for (const row of rows) {
      const cells = cellsOf(row);
      if (cells.length !== 4) {
        err(label, `Skills table row has ${cells.length} columns, expected 4 -> ${row.slice(0, 60)}`);
        continue;
      }
      const [first, pluginCell, description, command] = cells;
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

      const owner = pluginOfSkill.get(name);
      const expectedPlugin = owner ? `\`${owner}\`` : null;
      if (expectedPlugin && pluginCell !== expectedPlugin) {
        err(
          label,
          `row \`${name}\` column 2 should be ${expectedPlugin}, got ${pluginCell || '(empty)'}`,
        );
      }

      const expected = `\`npx skills add ${slug} -s ${name}\``;
      if (command !== expected) {
        err(label, `row \`${name}\` column 3 should be ${expected}, got ${command || '(empty)'}`);
      }
    }

    for (const name of seenNames.keys()) {
      if (!rowNames.has(name)) {
        err(label, `skill \`${name}\` has no row in the Skills table — add one, all four columns`);
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

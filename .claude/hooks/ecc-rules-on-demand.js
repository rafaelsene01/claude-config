#!/usr/bin/env node
// UserPromptSubmit hook: injects the ECC rules only when the prompt invokes an
// `ecc:*` skill/command. The rules live in ~/.claude/ecc-rules (outside
// ~/.claude/rules) so Claude Code does not auto-load them every session.
//
// A rule file with no `paths:` frontmatter is always included. A file with
// `paths:` is included only when the project actually contains a file with one
// of the extensions listed in its globs.

const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const RULES_ROOT = path.join(os.homedir(), '.claude', 'ecc-rules');
const TRIGGER = /(^|[\s/(`"'])ecc:/;

// Framework rule directories whose `paths:` globs also match plain .ts/.js, so
// extension matching alone cannot rule them out. Each name doubles as the npm
// package that must be a project dependency for the directory to apply.
const FRAMEWORK_DIRS = new Set(['react', 'vue', 'nuxt', 'angular', 'react-native', 'svelte']);

function readStdin() {
  try {
    return fs.readFileSync(0, 'utf8');
  } catch {
    return '';
  }
}

function listMarkdown(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...listMarkdown(full));
    else if (entry.name.endsWith('.md')) out.push(full);
  }
  return out;
}

function globExtensions(content) {
  if (!content.startsWith('---')) return null;
  const end = content.indexOf('\n---', 3);
  if (end === -1) return null;
  const frontmatter = content.slice(0, end);
  if (!/^paths:/m.test(frontmatter)) return null;
  const extensions = new Set();
  for (const match of frontmatter.matchAll(/\*\*\/\*(\.[A-Za-z0-9]+)/g)) {
    extensions.add(match[1].toLowerCase());
  }
  return extensions;
}

function projectExtensions() {
  const extensions = new Set();
  try {
    const files = execFileSync('git', ['ls-files'], { encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
    for (const file of files.split('\n')) {
      const ext = path.extname(file).toLowerCase();
      if (ext) extensions.add(ext);
    }
  } catch {
    // Not a git repository: fall back to including every rule.
  }
  return extensions;
}

function projectDependencies() {
  try {
    const pkg = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'package.json'), 'utf8'));
    return new Set([...Object.keys(pkg.dependencies || {}), ...Object.keys(pkg.devDependencies || {})]);
  } catch {
    return null; // No package.json: cannot rule frameworks out, so keep them.
  }
}

function main() {
  let prompt = '';
  try {
    prompt = JSON.parse(readStdin() || '{}').prompt || '';
  } catch {
    return;
  }
  if (!TRIGGER.test(prompt)) return;
  if (!fs.existsSync(RULES_ROOT)) return;

  const inProject = projectExtensions();
  const dependencies = projectDependencies();
  const sections = [];

  for (const file of listMarkdown(RULES_ROOT).sort()) {
    const relative = path.relative(RULES_ROOT, file);
    const group = relative.split(path.sep)[0];
    if (dependencies && FRAMEWORK_DIRS.has(group) && !dependencies.has(group)) continue;

    const content = fs.readFileSync(file, 'utf8');
    const wanted = globExtensions(content);
    const applies =
      wanted === null ||
      wanted.size === 0 ||
      inProject.size === 0 ||
      [...wanted].some((ext) => inProject.has(ext));
    if (applies) sections.push(`## ${relative}\n\n${content.trim()}`);
  }

  if (sections.length === 0) return;
  process.stdout.write(`# ECC rules (loaded because this prompt uses an ecc:* skill)\n\n${sections.join('\n\n')}\n`);
}

main();

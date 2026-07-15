#!/usr/bin/env node

import { readdir, readFile, stat } from "node:fs/promises";
import { resolve } from "node:path";

const MAX_PROSE_LINE_LENGTH = 120;
const MARKDOWN_EXTENSION = ".md";

async function markdownFiles(path) {
  const fileStat = await stat(path);
  if (fileStat.isFile()) return path.endsWith(MARKDOWN_EXTENSION) ? [path] : [];

  const entries = await readdir(path, { withFileTypes: true });
  const files = await Promise.all(
    entries.map((entry) => markdownFiles(resolve(path, entry.name))),
  );
  return files.flat();
}

function isHeading(line) {
  return /^(#{1,6})\s+\S/.exec(line);
}

function previousNonBlankLine(lines, index) {
  for (let cursor = index - 1; cursor >= 0; cursor -= 1) {
    if (lines[cursor].trim() !== "") return cursor;
  }
  return -1;
}

function blankLinesBefore(lines, index) {
  let count = 0;
  for (let cursor = index - 1; cursor >= 0 && lines[cursor].trim() === ""; cursor -= 1) {
    count += 1;
  }
  return count;
}

function validateFile(path, contents) {
  const errors = [];
  const lines = contents.split("\n");
  let fenceDelimiter = null;

  if (!/^#\s+\S/.test(lines[0] ?? "")) {
    errors.push("1: Markdown documents must begin with one H1 title.");
  }

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const lineNumber = index + 1;
    const fence = /^\s*(`{3,})(.*)$/.exec(line);

    if (fence) {
      if (fenceDelimiter && fence[1] === fenceDelimiter) {
        fenceDelimiter = null;
        continue;
      }
      if (!fenceDelimiter && fence[2].trim() === "") {
        errors.push(`${lineNumber}: Fenced code blocks must declare a language.`);
      }
      if (!fenceDelimiter && /^(bash|sh)\s*$/.test(fence[2].trim())) {
        errors.push(`${lineNumber}: Use the shell fence language instead of ${fence[2].trim()}.`);
      }
      if (!fenceDelimiter) fenceDelimiter = fence[1];
      continue;
    }

    if (/\s+$/.test(line)) errors.push(`${lineNumber}: Trailing whitespace.`);
    if (fenceDelimiter || /^\|/.test(line)) continue;
    if (line.length > MAX_PROSE_LINE_LENGTH) {
      errors.push(`${lineNumber}: Prose exceeds ${MAX_PROSE_LINE_LENGTH} characters.`);
    }

    const heading = isHeading(line);
    if (!heading || index === 0) continue;

    const level = heading[1].length;
    if (level >= 5) errors.push(`${lineNumber}: Avoid heading levels 5 and deeper.`);
    if (/\*\*/.test(line)) errors.push(`${lineNumber}: Do not use bold text in headings.`);
    if (/[.:;!?]$/.test(line)) errors.push(`${lineNumber}: Headings must not end with punctuation.`);

    const priorIndex = previousNonBlankLine(lines, index);
    const priorLine = lines[priorIndex] ?? "";
    const priorHeading = isHeading(priorLine);
    const expectedBlankLines = priorLine === "----" || (priorHeading && level > priorHeading[1].length)
      ? 1
      : 2;
    const actualBlankLines = blankLinesBefore(lines, index);

    if (actualBlankLines !== expectedBlankLines) {
      errors.push(
        `${lineNumber}: Expected ${expectedBlankLines} blank line(s) before this heading; found ${actualBlankLines}.`,
      );
    }
  }

  return errors.map((error) => `${path}:${error}`);
}

const paths = process.argv.slice(2);
if (paths.length === 0) {
  console.error("Usage: node check-markdown-format.mjs <file-or-directory> [...]");
  process.exit(2);
}

const files = (await Promise.all(paths.map(markdownFiles))).flat();
const errors = (
  await Promise.all(files.map(async (path) => validateFile(path, await readFile(path, "utf8"))))
).flat();

if (errors.length > 0) {
  console.error(errors.join("\n"));
  process.exit(1);
}

console.log(`Markdown format check passed for ${files.length} file(s).`);

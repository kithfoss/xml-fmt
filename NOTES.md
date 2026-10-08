# NOTES.md — xml-fmt build log

## Week 49 — 2026-10-06

### Scope decision

Chosen Monday as the natural companion to `json-fmt` (already shipped). XML formatting is a consistent gap — `xmllint --format` works but requires libxml2, isn't always installed, and has rough edges on some platforms. `python -m xml.etree.ElementTree` doesn't exist as a command. This fills that gap with one stdlib script.

### Implementation decisions

**ET for validation, minidom for formatting.** `xml.etree.ElementTree` gives clean `ParseError` with `.position` (line, col) — the best error messages. `xml.dom.minidom` handles pretty-printing and compact formatting with `toprettyxml()` / `toxml()`. Split responsibilities, both stdlib.

**Blank-line stripping.** minidom's `toprettyxml()` inserts `\n` text nodes between sibling elements, which produces blank lines after stripping the extra indentation. We strip them with `[l for l in lines if l.strip()]`. This is the right call for a formatter — blank lines between XML elements are not semantically significant.

**Whitespace node stripping for compact.** minidom's `toxml()` preserves existing whitespace text nodes from already-formatted input. We traverse and remove them before calling `toxml()` so `--compact` always produces true compact output regardless of input formatting.

**Declaration replacement.** Both `toprettyxml()` and `toxml()` prepend `<?xml version="1.0" ?>` (no encoding). We strip it and replace with `<?xml version="1.0" encoding="UTF-8"?>` — more informative, consistent across invocations.

**`--no-declaration` flag.** Useful when embedding fragments, piping into other tools, or diffing output where the declaration adds noise.

### Test results

32 test functions → 75 checks. 75/75 pass. First run clean.

### What works

- Pretty-print (2-space default, configurable indent)
- Minify / compact (strips all inter-element whitespace)
- Validate-only mode (exits 0/1, line:col error messages)
- Multiple file processing (continues past errors)
- Stdin via `-` or implicit
- Namespaces, CDATA, comments, attributes
- UTF-8 encoded declaration
- `--no-declaration` for fragment use

### What doesn't / known limitations

- Attribute order: XML spec allows any order, minidom doesn't guarantee preservation. A `--sort-attrs` flag could be added later.
- Mixed content (text + child elements like `<p>Hello <em>world</em></p>`): whitespace stripping in compact mode can alter text node spacing in edge cases. Correct behavior for mixed content is complex; documented as a limitation.
- DTD/entity validation: well-formedness only.

### Status

75/75 tests. Clean. Blocked on GH_TOKEN for release (same as json-path, wait-for).

# xml-fmt

Format and validate XML files.

```
xml-fmt file.xml                    pretty-print with 2-space indent
xml-fmt --indent 4 file.xml         use 4-space indent
xml-fmt --compact file.xml          minify (remove all whitespace)
xml-fmt --validate file.xml         validate only, exit 0/1
xml-fmt --no-declaration file.xml   omit XML declaration header
cat file.xml | xml-fmt              read from stdin
xml-fmt a.xml b.xml                 format multiple files
```

## Install

No dependencies. Python 3.6+ stdlib only.

```bash
chmod +x xml-fmt.py
cp xml-fmt.py /usr/local/bin/xml-fmt
```

## Options

| Flag | Description |
|------|-------------|
| `--compact`, `-c` | Minify output (remove all whitespace between elements) |
| `--indent N`, `-i N` | Indent size in spaces (default: 2) |
| `--validate`, `-V` | Validate only; no output. Exit 0 if valid, 1 if not |
| `--no-declaration` | Omit the `<?xml version="1.0" encoding="UTF-8"?>` header |
| `--version` | Print version and exit |

## Examples

**Pretty-print a config file:**
```bash
xml-fmt pom.xml
```

**Minify for deployment:**
```bash
xml-fmt --compact --no-declaration app.xml > app.min.xml
```

**Validate in CI:**
```bash
xml-fmt --validate config.xml && echo "config is valid"
```

**Validate multiple files:**
```bash
xml-fmt --validate *.xml
```

**Reformat from stdin:**
```bash
curl -s https://example.com/feed.rss | xml-fmt
```

## Exit codes

- `0` — success (valid XML, formatted)
- `1` — invalid XML (parse error reported to stderr)

## Notes

- Replaces the XML declaration with `<?xml version="1.0" encoding="UTF-8"?>` for consistency
- Comments and CDATA sections are preserved
- Namespaces are preserved
- When formatting multiple files, each file's output is written to stdout in sequence
- Whitespace inside text content is preserved (only inter-element whitespace is normalized)

## Limitations

- Attribute order is not guaranteed (XML spec permits any order)
- DTD/external entity declarations are not validated (just passed through)
- Not a full XML schema validator — checks well-formedness only

## Earn model

Free.

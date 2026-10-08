#!/usr/bin/env python3
"""xml-fmt — Format and validate XML files."""

import argparse
import sys
import xml.dom
import xml.dom.minidom
import xml.etree.ElementTree as ET
from pathlib import Path

VERSION = "0.1.0"


def read_source(path):
    if path == "-":
        return sys.stdin.buffer.read()
    try:
        return Path(path).read_bytes()
    except FileNotFoundError:
        print(f"xml-fmt: {path}: file not found", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"xml-fmt: {path}: permission denied", file=sys.stderr)
        sys.exit(1)


def validate(data, label):
    """Return (ok, error_msg). ET gives good line/col parse errors."""
    try:
        ET.fromstring(data)
        return True, None
    except ET.ParseError as e:
        line, col = e.position
        return False, f"{label}:{line}:{col}: {e}"


def _strip_whitespace_text_nodes(node):
    """Remove whitespace-only text nodes so compact output is clean."""
    to_remove = []
    for child in node.childNodes:
        if child.nodeType == xml.dom.Node.TEXT_NODE and not child.data.strip():
            to_remove.append(child)
        elif child.hasChildNodes():
            _strip_whitespace_text_nodes(child)
    for child in to_remove:
        node.removeChild(child)


def pretty_format(data, indent, no_declaration):
    dom = xml.dom.minidom.parseString(data)
    indent_str = " " * indent
    text = dom.toprettyxml(indent=indent_str, encoding=None)
    # toprettyxml always prepends <?xml version="1.0" ?> — strip it
    lines = text.split("\n")
    if lines and lines[0].startswith("<?xml"):
        lines = lines[1:]
    # Remove blank lines minidom inserts between sibling elements
    lines = [l for l in lines if l.strip()]
    body = "\n".join(lines)
    if no_declaration:
        return body + "\n"
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n"


def compact_format(data, no_declaration):
    dom = xml.dom.minidom.parseString(data)
    _strip_whitespace_text_nodes(dom)
    text = dom.toxml(encoding=None)
    # toxml prepends <?xml version="1.0" ?> — strip it
    if text.startswith("<?xml"):
        idx = text.index("?>")
        body = text[idx + 2:].lstrip()
    else:
        body = text
    if no_declaration:
        return body + "\n"
    return '<?xml version="1.0" encoding="UTF-8"?>' + body + "\n"


def main():
    parser = argparse.ArgumentParser(
        prog="xml-fmt",
        description="Format and validate XML files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  xml-fmt file.xml                   pretty-print with 2-space indent
  xml-fmt --indent 4 file.xml        use 4-space indent
  xml-fmt --compact file.xml         minify (remove all whitespace)
  xml-fmt --validate file.xml        validate only, exit 0/1
  xml-fmt --no-declaration file.xml  omit XML declaration header
  cat file.xml | xml-fmt             read from stdin
  xml-fmt a.xml b.xml                format multiple files
""",
    )
    parser.add_argument(
        "files", nargs="*", metavar="FILE",
        help="XML file(s) to format (default: stdin)",
    )
    parser.add_argument(
        "--compact", "-c", action="store_true",
        help="minify output (remove whitespace)",
    )
    parser.add_argument(
        "--indent", "-i", type=int, default=2, metavar="N",
        help="indent size in spaces (default: 2)",
    )
    parser.add_argument(
        "--validate", "-V", action="store_true",
        help="validate only, no output (exit 0 if valid, 1 if not)",
    )
    parser.add_argument(
        "--no-declaration", action="store_true",
        help="omit the <?xml ...?> declaration line",
    )
    parser.add_argument("--version", action="version", version=f"xml-fmt {VERSION}")
    args = parser.parse_args()

    sources = args.files if args.files else ["-"]
    exit_code = 0

    for path in sources:
        label = path if path != "-" else "<stdin>"
        data = read_source(path)

        ok, err = validate(data, label)
        if not ok:
            print(f"xml-fmt: {err}", file=sys.stderr)
            exit_code = 1
            continue

        if args.validate:
            if len(sources) > 1:
                print(f"{label}: OK")
            continue

        try:
            if args.compact:
                result = compact_format(data, args.no_declaration)
            else:
                result = pretty_format(data, args.indent, args.no_declaration)
            sys.stdout.write(result)
        except Exception as e:
            print(f"xml-fmt: {label}: {e}", file=sys.stderr)
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

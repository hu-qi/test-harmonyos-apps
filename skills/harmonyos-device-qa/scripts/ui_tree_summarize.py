#!/usr/bin/env python3
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable

INTERACTIVE_ATTRS = ('clickable', 'long-clickable', 'longClickable', 'scrollable', 'focusable', 'enabled')
STATE_ATTRS = ('checked', 'selected', 'focused')
DISPLAY_ATTRS = ('text', 'content-desc', 'contentDesc', 'description', 'label', 'resource-id', 'resourceId', 'id')
CHILD_KEYS = ('children', 'childNodes', 'items', 'nodes')
MAX_DEPTH = 20


def node_payload(node: Any) -> Any:
    if isinstance(node, dict) and isinstance(node.get('attributes'), dict):
        return node['attributes']
    return node


def clean_text(value: Any) -> str:
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value)).strip()


def is_true(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() == 'true'


def simplify_resource_id(value: str) -> str:
    if ':id/' in value:
        prefix, rest = value.split(':id/', 1)
        if prefix and prefix != 'android':
            return 'id/' + rest
    return value


def extract_labels(node: Any) -> tuple[str, str, str]:
    if isinstance(node, ET.Element):
        text = clean_text(node.attrib.get('text', ''))
        desc = clean_text(node.attrib.get('content-desc', '') or node.attrib.get('contentDesc', ''))
        resource_id = simplify_resource_id(clean_text(node.attrib.get('resource-id', '') or node.attrib.get('resourceId', '')))
        return text, desc, resource_id
    node = node_payload(node)
    text = clean_text(node.get('text') or node.get('label') or node.get('description'))
    desc = clean_text(node.get('content-desc') or node.get('contentDesc'))
    resource_id = simplify_resource_id(clean_text(node.get('resource-id') or node.get('resourceId') or node.get('id')))
    return text, desc, resource_id


def node_class(node: Any) -> str:
    if isinstance(node, ET.Element):
        value = clean_text(node.attrib.get('class', ''))
    else:
        node = node_payload(node)
        value = clean_text(node.get('class') or node.get('type') or node.get('name'))
    return value.split('.')[-1] if value else 'Node'


def is_interactive(node: Any) -> bool:
    if isinstance(node, ET.Element):
        return any(is_true(node.attrib.get(key, 'false')) for key in INTERACTIVE_ATTRS)
    node = node_payload(node)
    return any(is_true(node.get(key, False)) for key in INTERACTIVE_ATTRS)


def has_display(node: Any) -> bool:
    text, desc, resource_id = extract_labels(node)
    return bool(text or desc or resource_id)


def keep_node(node: Any) -> bool:
    if isinstance(node, ET.Element):
        scrollable = is_true(node.attrib.get('scrollable', 'false'))
    else:
        node = node_payload(node)
        scrollable = is_true(node.get('scrollable', False))
    return has_display(node) or is_interactive(node) or scrollable


def bounds_repr(node: Any) -> str:
    if isinstance(node, ET.Element):
        return clean_text(node.attrib.get('bounds', ''))
    node = node_payload(node)
    for key in ('bounds', 'rect', 'rectInScreen', 'visibleBounds', 'region'):
        value = node.get(key)
        if isinstance(value, str):
            return clean_text(value)
        if isinstance(value, dict):
            left = value.get('left', value.get('x', value.get('startX')))
            top = value.get('top', value.get('y', value.get('startY')))
            right = value.get('right', value.get('endX'))
            bottom = value.get('bottom', value.get('endY'))
            width = value.get('width')
            height = value.get('height')
            if right is None and left is not None and width is not None:
                right = int(left) + int(width)
            if bottom is None and top is not None and height is not None:
                bottom = int(top) + int(height)
            if None not in (left, top, right, bottom):
                return f'[{left},{top}][{right},{bottom}]'
    return ''


def iter_children(node: Any) -> Iterable[Any]:
    if isinstance(node, ET.Element):
        yield from list(node)
        return
    if isinstance(node, dict) and isinstance(node.get('children'), list):
        yield from node['children']
        return
    for key in CHILD_KEYS:
        value = node.get(key)
        if isinstance(value, list):
            yield from value


def format_node(node: Any) -> str:
    class_name = node_class(node)
    text, desc, resource_id = extract_labels(node)
    parts = [class_name]
    if resource_id:
        parts.append(f'id={resource_id}')
    if text:
        parts.append(f'text="{text}"')
    if desc:
        parts.append(f'desc="{desc}"')
    flags = []
    source = node.attrib if isinstance(node, ET.Element) else node_payload(node)
    for key in INTERACTIVE_ATTRS:
        value = source.get(key, False)
        if is_true(value):
            flags.append(key)
    for key in STATE_ATTRS:
        value = source.get(key, False)
        if is_true(value):
            flags.append(key)
    if flags:
        parts.append('flags=' + ','.join(flags))
    bounds = bounds_repr(node)
    if bounds and (is_interactive(node) or has_display(node)):
        parts.append(f'bounds={bounds}')
    return ' '.join(parts)


def build_lines(node: Any, depth: int) -> list[str]:
    if depth > MAX_DEPTH:
        return []
    include = keep_node(node)
    child_depth = depth + 1 if include else depth
    lines = []
    if include:
        lines.append(('  ' * depth) + format_node(node))
    for child in iter_children(node):
        lines.extend(build_lines(child, child_depth))
    return lines


def xml_root(path: Path) -> ET.Element:
    xml_text = path.read_text(encoding='utf-8')
    end_marker = '</hierarchy>'
    end_index = xml_text.rfind(end_marker)
    if end_index != -1:
        xml_text = xml_text[: end_index + len(end_marker)]
    return ET.fromstring(xml_text)


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit('usage: ui_tree_summarize.py <input.{json|xml}> <output.txt>')
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    text = input_path.read_text(encoding='utf-8')
    stripped = text.lstrip()
    if stripped.startswith('{') or stripped.startswith('['):
        root = json.loads(text)
        roots = root if isinstance(root, list) else [root]
    else:
        parsed = xml_root(input_path)
        roots = list(parsed)

    lines: list[str] = []
    for child in roots:
        lines.extend(build_lines(child, 0))

    output_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

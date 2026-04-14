#!/usr/bin/env python3
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable


TEXT_KEYS = (
    'text',
    'content-desc',
    'contentDesc',
    'description',
    'label',
    'id',
    'resource-id',
    'resourceId',
    'key',
)


def node_payload(node: Any) -> Any:
    if isinstance(node, dict) and isinstance(node.get('attributes'), dict):
        return node['attributes']
    return node


def clean_text(value: str | None) -> str:
    if not value:
        return ''
    return re.sub(r'\s+', ' ', value).strip()


def normalized_strings(node: Any) -> Iterable[str]:
    node = node_payload(node)
    if isinstance(node, dict):
        for key in TEXT_KEYS:
            value = node.get(key)
            if isinstance(value, str):
                cleaned = clean_text(value)
                if cleaned:
                    yield cleaned
    elif isinstance(node, ET.Element):
        for key in TEXT_KEYS:
            value = node.attrib.get(key)
            cleaned = clean_text(value)
            if cleaned:
                yield cleaned


def parse_bounds_string(bounds: str) -> tuple[int, int] | None:
    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return ((x1 + x2) // 2, (y1 + y2) // 2)


def parse_rect_mapping(node: dict[str, Any]) -> tuple[int, int] | None:
    node = node_payload(node)
    rect = None
    for key in ('bounds', 'rect', 'rectInScreen', 'visibleBounds', 'region'):
        value = node.get(key)
        if isinstance(value, dict):
            rect = value
            break
    if rect is None:
        rect = node
    left = rect.get('left', rect.get('x', rect.get('startX')))
    top = rect.get('top', rect.get('y', rect.get('startY')))
    right = rect.get('right', rect.get('endX'))
    bottom = rect.get('bottom', rect.get('endY'))
    width = rect.get('width')
    height = rect.get('height')
    if right is None and left is not None and width is not None:
        right = int(left) + int(width)
    if bottom is None and top is not None and height is not None:
        bottom = int(top) + int(height)
    if None in (left, top, right, bottom):
        return None
    return ((int(left) + int(right)) // 2, (int(top) + int(bottom)) // 2)


def center_from_node(node: Any) -> tuple[int, int] | None:
    if isinstance(node, ET.Element):
        bounds = node.attrib.get('bounds', '')
        return parse_bounds_string(bounds)
    if isinstance(node, dict):
        node = node_payload(node)
        bounds = node.get('bounds')
        if isinstance(bounds, str):
            center = parse_bounds_string(bounds)
            if center is not None:
                return center
        return parse_rect_mapping(node)
    return None


def iter_json_nodes(node: Any) -> Iterable[Any]:
    if isinstance(node, dict):
        yield node
        children = node.get('children')
        if isinstance(children, list):
            for item in children:
                yield from iter_json_nodes(item)
        for key, value in node.items():
            if key == 'children':
                continue
            if isinstance(value, list):
                for item in value:
                    yield from iter_json_nodes(item)
    elif isinstance(node, list):
        for item in node:
            yield from iter_json_nodes(item)


def read_xml_root(path: Path) -> ET.Element:
    text = path.read_text(encoding='utf-8')
    end = text.rfind('</hierarchy>')
    if end != -1:
        text = text[: end + len('</hierarchy>')]
    return ET.fromstring(text)


def find_json_node(root: Any, target: str) -> Any | None:
    normalized_target = clean_text(target)
    for node in iter_json_nodes(root):
        if normalized_target in normalized_strings(node):
            return node
    return None


def find_xml_node(root: ET.Element, target: str) -> ET.Element | None:
    normalized_target = clean_text(target)
    for node in root.iter():
        if normalized_target in normalized_strings(node):
            return node
    return None


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: ui_pick.py <ui_dump.{json|xml}> <target_text>', file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    target = sys.argv[2]

    try:
        text = path.read_text(encoding='utf-8')
    except OSError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2

    stripped = text.lstrip()
    try:
        if stripped.startswith('{') or stripped.startswith('['):
            root = json.loads(text)
            node = find_json_node(root, target)
        else:
            root = read_xml_root(path)
            node = find_xml_node(root, target)
    except (json.JSONDecodeError, ET.ParseError, ValueError) as exc:
        print(f'error: failed to parse dump: {exc}', file=sys.stderr)
        return 2

    if node is None:
        print('error: node not found', file=sys.stderr)
        return 2

    center = center_from_node(node)
    if center is None:
        print('error: bounds not found', file=sys.stderr)
        return 2

    print(f'{center[0]} {center[1]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

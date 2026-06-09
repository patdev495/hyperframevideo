from __future__ import annotations


def partition_markdown_field(line: str) -> tuple[str, str, str]:
    label, separator, value = line.strip().partition(":")
    if not separator:
        return label, separator, value

    normalized_label = label.strip()
    while normalized_label.startswith("*"):
        normalized_label = normalized_label[1:].strip()
    while normalized_label.endswith("*"):
        normalized_label = normalized_label[:-1].strip()

    normalized_value = value.strip()
    while normalized_value.startswith("*"):
        normalized_value = normalized_value[1:].strip()

    return normalized_label, separator, normalized_value

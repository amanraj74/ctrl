"""Tests for JSON repair utility."""

import pytest
from app.utils.json_repair import (
    strip_markdown_fences,
    fix_trailing_commas,
    balance_braces,
    extract_json_object,
    repair_json,
)


class TestStripMarkdownFences:
    def test_json_fence(self):
        text = '```json\n{"key": "value"}\n```'
        assert strip_markdown_fences(text) == '{"key": "value"}'

    def test_plain_fence(self):
        text = '```\n{"key": "value"}\n```'
        assert strip_markdown_fences(text) == '{"key": "value"}'

    def test_no_fence(self):
        text = '{"key": "value"}'
        assert strip_markdown_fences(text) == '{"key": "value"}'


class TestFixTrailingCommas:
    def test_trailing_comma_object(self):
        assert fix_trailing_commas('{"a": 1, "b": 2,}') == '{"a": 1, "b": 2}'

    def test_trailing_comma_array(self):
        assert fix_trailing_commas('[1, 2, 3,]') == '[1, 2, 3]'

    def test_no_trailing_comma(self):
        text = '{"a": 1}'
        assert fix_trailing_commas(text) == text


class TestBalanceBraces:
    def test_missing_closing_brace(self):
        assert balance_braces('{"a": 1') == '{"a": 1}'

    def test_balanced(self):
        text = '{"a": 1}'
        assert balance_braces(text) == text

    def test_missing_bracket(self):
        assert balance_braces('[1, 2') == '[1, 2]'


class TestExtractJsonObject:
    def test_with_prefix(self):
        text = 'Here is the JSON: {"key": "value"}'
        assert extract_json_object(text) == '{"key": "value"}'

    def test_with_suffix(self):
        text = '{"key": "value"} and more text'
        assert extract_json_object(text) == '{"key": "value"}'

    def test_array(self):
        text = 'Result: [1, 2, 3]'
        assert extract_json_object(text) == '[1, 2, 3]'


class TestRepairJson:
    def test_valid_json(self):
        text = '{"a": 1, "b": "hello"}'
        assert repair_json(text) == text

    def test_markdown_fence(self):
        text = '```json\n{"a": 1}\n```'
        result = repair_json(text)
        assert '"a"' in result

    def test_trailing_comma(self):
        text = '{"a": 1, "b": 2,}'
        result = repair_json(text)
        import json
        data = json.loads(result)
        assert data["a"] == 1

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            repair_json("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            repair_json("   ")

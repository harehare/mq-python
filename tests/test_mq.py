import pytest
import mq


@pytest.mark.parametrize(
    "code, content, expected",
    [
        (".h1", "# Hello World\n\n## Heading2\n\nText", ["# Hello World"]),
        (".h2", "# Hello World\n\n## Heading2\n\nText", ["## Heading2"]),
        (
            ".h2",
            "# Main Title\n\n## Heading2A\n\nText\n\n## Heading2B\n\nMore text",
            ["## Heading2A", "## Heading2B"],
        ),
        (
            '.h2 | select(contains("Feature"))',
            "# Product\n\n## Features\n\nText\n\n## Installation\n\nMore text",
            ["## Features"],
        ),
        (
            ".[]",
            "# List\n\n- Item 1\n- Item 2\n- Item 3",
            ["- Item 1", "- Item 2", "- Item 3"],
        ),
        (
            ".code",
            "# Code\n\n```python\nprint('Hello')\n```",
            ["```python\nprint('Hello')\n```"],
        ),
    ],
)
def test_mq_queries(code, content, expected):
    result = mq.run(code, content, None)
    assert result.values == expected


@pytest.mark.parametrize(
    "input_format, code, content, expected",
    [
        (
            mq.InputFormat.TEXT,
            'select(contains("2"))',
            "Line 1\nLine 2\nLine 3",
            ["Line 2"],
        ),
        (
            mq.InputFormat.MDX,
            "select(is_mdx())",
            "# MDX Content\n\n<Component />",
            ["<Component />"],
        ),
        (
            mq.InputFormat.HTML,
            'select(contains("Hello"))',
            "<h1>Hello</h1><p>World</p>",
            ["# Hello"],
        ),
    ],
)
def test_input_formats(input_format, code, content, expected):
    options = mq.Options()
    options.input_format = input_format

    result = mq.run(code, content, options)
    assert result.values == expected


def test_invalid_query():
    with pytest.raises(Exception) as exc_info:
        mq.run(".invalid_selector!!!", "# Heading", None)

    assert "Error evaluating query" in str(exc_info.value)


def test_html_to_markdown():
    html_content = "<h1>Hello World</h1><p>This is a <strong>test</strong>.</p>"
    expected_markdown = "# Hello World\n\nThis is a **test**."
    markdown = mq.html_to_markdown(html_content)
    assert markdown.strip() == expected_markdown


def test_position_heading():
    result = mq.run(".h", "# Heading")
    pos = result[0].position
    assert pos is not None
    assert (pos.start.line, pos.start.column) == (1, 1)
    assert (pos.end.line, pos.end.column) == (1, 10)


def test_position_multiline():
    result = mq.run(".code", "text\n\n```py\nx = 1\n```\n")
    pos = next(v.position for v in (result[i] for i in range(len(result))) if v)
    assert pos.start.line == 3
    assert pos.end.line == 5


def test_position_none_for_computed_value():
    result = mq.run('"abc"', "# Heading")
    assert result[0].position is None


def test_html_to_markdown_options():
    html = "<html><head><title>Page</title></head><body><p>Body</p></body></html>"
    options = mq.ConversionOptions()
    options.use_title_as_h1 = True
    assert "# Page" in mq.html_to_markdown(html, options)

    options = mq.ConversionOptions()
    assert options.use_title_as_h1 is False
    assert options.generate_front_matter is False
    assert options.extract_scripts_as_code_blocks is False


def test_options_defaults():
    options = mq.Options()
    assert options.input_format is None
    assert options.output_format is None
    assert options.list_style is None
    assert options.link_title_style is None
    assert options.link_url_style is None


def test_options_keyword_arguments():
    options = mq.Options(
        input_format=mq.InputFormat.HTML,
        output_format=mq.OutputFormat.TEXT,
        list_style=mq.ListStyle.STAR,
        link_title_style=mq.TitleSurroundStyle.PAREN,
        link_url_style=mq.UrlSurroundStyle.ANGLE,
    )
    assert options.input_format == mq.InputFormat.HTML
    assert options.output_format == mq.OutputFormat.TEXT
    assert options.list_style == mq.ListStyle.STAR
    assert options.link_title_style == mq.TitleSurroundStyle.PAREN
    assert options.link_url_style == mq.UrlSurroundStyle.ANGLE


def test_options_keyword_matches_attribute():
    options = mq.Options()
    options.input_format = mq.InputFormat.HTML
    assert options == mq.Options(input_format=mq.InputFormat.HTML)


def test_options_keyword_input_format():
    result = mq.run(
        'select(contains("Hello"))',
        "<h1>Hello</h1><p>World</p>",
        mq.Options(input_format=mq.InputFormat.HTML),
    )
    assert result.values == ["# Hello"]


def test_options_unknown_keyword():
    with pytest.raises(TypeError):
        mq.Options(unknown=1)


MARKDOWN = '# Title\n\n- Item 1\n- Item 2\n\n[link](https://example.com "title")\n'


def test_render_default_is_markdown():
    result = mq.run(".", MARKDOWN)
    assert result.render() == MARKDOWN
    assert result.render(mq.OutputFormat.MARKDOWN) == MARKDOWN


def test_render_html():
    html = mq.run(".", MARKDOWN).render(mq.OutputFormat.HTML)
    assert "<h1>Title</h1>" in html
    assert "<li>Item 1</li>" in html
    assert '<a href="https://example.com" title="title">link</a>' in html


def test_render_text():
    text = mq.run(".", MARKDOWN).render(mq.OutputFormat.TEXT)
    assert text.splitlines() == ["Title", "Item 1", "Item 2", "https://example.com"]


def test_render_uses_output_format_option():
    result = mq.run(".h1", "# Hello", mq.Options(output_format=mq.OutputFormat.HTML))
    assert result.render() == "<h1>Hello</h1>\n"


def test_render_argument_overrides_option():
    result = mq.run(".h1", "# Hello", mq.Options(output_format=mq.OutputFormat.HTML))
    assert result.render(mq.OutputFormat.MARKDOWN) == "# Hello\n"


@pytest.mark.parametrize(
    "style, marker",
    [
        (mq.ListStyle.DASH, "-"),
        (mq.ListStyle.PLUS, "+"),
        (mq.ListStyle.STAR, "*"),
    ],
)
def test_render_list_style(style, marker):
    result = mq.run(".", "- a\n- b\n", mq.Options(list_style=style))
    assert result.render() == f"{marker} a\n{marker} b\n"


@pytest.mark.parametrize(
    "style, expected",
    [
        (mq.TitleSurroundStyle.DOUBLE, '[x](https://e.com "t")'),
        (mq.TitleSurroundStyle.SINGLE, "[x](https://e.com 't')"),
        (mq.TitleSurroundStyle.PAREN, "[x](https://e.com (t))"),
    ],
)
def test_render_link_title_style(style, expected):
    result = mq.run(".", '[x](https://e.com "t")', mq.Options(link_title_style=style))
    assert result.render().strip() == expected


def test_render_link_url_style():
    result = mq.run(
        ".",
        '[x](https://e.com "t")',
        mq.Options(link_url_style=mq.UrlSurroundStyle.ANGLE),
    )
    assert result.render().strip() == '[x](<https://e.com> "t")'


def test_render_non_markdown_values():
    result = mq.run('"hello"', "# Heading", mq.Options(input_format=mq.InputFormat.NULL))
    assert result.render(mq.OutputFormat.TEXT).strip() == "hello"


def test_runtime_error_message():
    with pytest.raises(RuntimeError, match="Error evaluating query"):
        mq.run("undefined_function()", "# Heading")


def test_result_protocol():
    result = mq.run(".h", "# H1\n\n## H2\n\n### H3")
    assert len(result) == 3
    assert result[0].text == "# H1"
    assert result.text == "# H1\n## H2\n### H3"
    assert str(result) == result.text
    assert "3 items" in repr(result)
    with pytest.raises(IndexError):
        result[3]


def test_result_empty():
    result = mq.run(".h1", "no heading here")
    assert result.values == []
    assert result.text == ""


def test_value_properties():
    result = mq.run(".h", "# H1\n\n```python\nx\n```")
    value = result[0]
    assert value.is_markdown()
    assert not value.is_array()
    assert value.markdown_type == mq.MarkdownType.Heading
    assert value.text == "# H1"
    assert value.values == [value]
    assert bool(value)


def test_value_index_out_of_range():
    value = mq.run(".h1", "# A")[0]
    assert value[0] == value
    with pytest.raises(IndexError):
        value[1]


def test_value_comparison():
    a = mq.run(".h1", "# A")[0]
    b = mq.run(".h1", "# A")[0]
    c = mq.run(".h1", "# B")[0]
    assert a == b
    assert a != c
    assert a < c
    assert c > a


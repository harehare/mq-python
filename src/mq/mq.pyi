from typing import List, Optional
from enum import Enum

class InputFormat(Enum):
    """The format of the input document."""

    MARKDOWN = 1
    MDX = 2
    TEXT = 3
    HTML = 4
    RAW = 5
    NULL = 6

class OutputFormat(Enum):
    """The format used when rendering a result with `MQResult.render()`."""

    MARKDOWN = 1
    HTML = 2
    TEXT = 3

class ListStyle(Enum):
    """Style to use for markdown lists."""

    DASH = 1
    PLUS = 2
    STAR = 3

class TitleSurroundStyle(Enum):
    """Style for surrounding link titles."""

    DOUBLE = 1
    SINGLE = 2
    PAREN = 3

class UrlSurroundStyle(Enum):
    """Style for surrounding URLs."""

    ANGLE = 1
    NONE = 2

class Options:
    """Configuration options for mq processing.

    All options can be passed as keyword arguments or set as attributes.
    """

    input_format: Optional[InputFormat]
    output_format: Optional[OutputFormat]
    list_style: Optional[ListStyle]
    link_title_style: Optional[TitleSurroundStyle]
    link_url_style: Optional[UrlSurroundStyle]

    def __init__(
        self,
        input_format: Optional[InputFormat] = None,
        output_format: Optional[OutputFormat] = None,
        list_style: Optional[ListStyle] = None,
        link_title_style: Optional[TitleSurroundStyle] = None,
        link_url_style: Optional[UrlSurroundStyle] = None,
    ) -> None: ...

class ConversionOptions:
    """Options for `html_to_markdown`."""

    extract_scripts_as_code_blocks: bool
    generate_front_matter: bool
    use_title_as_h1: bool

    def __init__(self) -> None: ...

class MarkdownType(Enum):
    """Types of Markdown elements."""

    Blockquote = 1
    Break = 2
    Definition = 3
    Delete = 4
    Heading = 5
    Emphasis = 6
    Footnote = 7
    FootnoteRef = 8
    Html = 9
    Yaml = 10
    Toml = 11
    Image = 12
    ImageRef = 13
    CodeInline = 14
    MathInline = 15
    Link = 16
    LinkRef = 17
    Math = 18
    List = 19
    TableHeader = 20
    TableRow = 21
    TableCell = 22
    Code = 23
    Strong = 24
    HorizontalRule = 25
    MdxFlowExpression = 26
    MdxJsxFlowElement = 27
    MdxJsxTextElement = 28
    MdxTextExpression = 29
    MdxJsEsm = 30
    Text = 31
    Empty = 32

class Point:
    """A location in the source document (1-based)."""

    @property
    def line(self) -> int: ...
    @property
    def column(self) -> int: ...

class Position:
    """The start and end location of a node in the source document."""

    @property
    def start(self) -> Point: ...
    @property
    def end(self) -> Point: ...

class MQValue:
    """
    Represents a value in the mq query result.
    """

    @property
    def position(self) -> Optional[Position]:
        """
        Get the position of the node in the source document.

        Returns:
            Optional[Position]: The start/end line and column, or None if the
            value has no source position (e.g. computed strings, numbers).
        """

    @property
    def text(self) -> str:
        """
        Get the text representation of the value.

        Returns:
            str: The text representation of the value
        """

    @property
    def values(self) -> List["MQValue"]:
        """
        Get the value as a list of values.

        Returns:
            List[MQValue]: The elements if this value is an array,
            otherwise a list containing only this value.
        """

    @property
    def markdown_type(self) -> Optional[MarkdownType]:
        """
        Get the markdown type of the document.

        Returns:
            Optional[MarkdownType]: The markdown type of the document, or None if not applicable.
        """

    def is_array(self) -> bool:
        """
        Check if this value is an array.

        Returns:
            True if this value is an array, False otherwise
        """

    def is_markdown(self) -> bool:
        """
        Check if this value is a markdown node.

        Returns:
            True if this value is a markdown node, False otherwise
        """

    def __getitem__(self, idx: int) -> "MQValue": ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __bool__(self) -> bool: ...
    def __len__(self) -> int: ...
    def __eq__(self, other: "MQValue") -> bool: ...
    def __ne__(self, other: "MQValue") -> bool: ...
    def __lt__(self, other: "MQValue") -> bool: ...
    def __gt__(self, other: "MQValue") -> bool: ...

class MQResult:
    """
    Result of a query execution.
    """

    @property
    def text(self) -> str:
        """
        Get the text representation of all values.

        Returns:
            Text representation of all values joined by newlines
        """

    @property
    def values(self) -> List[str]:
        """
        Get a list of non-empty text values as strings.

        This returns the text representations of all non-empty values
        in the result set.

        Returns:
            List of non-empty text values as strings
        """

    def render(self, output_format: Optional[OutputFormat] = None) -> str:
        """
        Render the result in the given output format.

        The rendering options (list_style, link_title_style, link_url_style)
        passed to `run` are applied.

        Args:
            output_format: The output format. If None, the `output_format` of
                the options passed to `run` is used (Markdown by default).

        Returns:
            The rendered result as a string
        """

    def __contains__(self, item: "MQValue") -> bool: ...
    def __getitem__(self, idx: int) -> MQValue: ...
    def __len__(self) -> int: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: "MQResult") -> bool: ...
    def __ne__(self, other: "MQResult") -> bool: ...
    def __lt__(self, other: "MQResult") -> bool: ...
    def __gt__(self, other: "MQResult") -> bool: ...

# Function to run mq queries
def run(code: str, content: str, options: Optional[Options] = None) -> MQResult:
    """
    Run an mq query against markdown content with the specified options.

    This is the main entry point for processing markdown with mq from Python.
    It takes a query written in the mq query language, applies it to the provided
    markdown content, and returns the results.

    Args:
        code: The mq query string to run against the content
        content: The markdown content to process (or text depending on options)
        options: Configuration options for processing. If None, default options are used.

    Returns:
        MQResult object containing the query results

    Raises:
        RuntimeError: If there's an error parsing the markdown or evaluating the query

    Example:
        ```python
        import mq

        # Create query to extract all headings
        query = ".h1"

        # Markdown content
        content = "# Title\\n\\nSome content\\n\\n## Subtitle\\n\\nMore content"

        # Run the query
        result = mq.run(query, content)

        # Print the extracted headings
        print(result.text)
        # Output: "# Title\n## Subtitle"
        ```
    """

def html_to_markdown(content: str, options: Optional[ConversionOptions] = None) -> str:
    """
    Convert HTML to Markdown.

    Args:
        content: The HTML content to convert
        options: Conversion options. If None, default options are used.

    Returns:
        The converted Markdown

    Raises:
        RuntimeError: If the conversion fails
    """

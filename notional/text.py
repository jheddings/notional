"""Utilities for working text, markdown & Rich Text in Notion."""

from enum import Enum

from .core import DataObject, NestedObject, TypedObject

# this might be a place to capture other utilities for working with markdown, text
# rich text, etc...  the challenge is not importing types due to a circular ref.


def plain_text(*rtf):
    """Return the combined plain text from the list of RichText objects."""
    return ("".join(text.plain_text for text in rtf if text)).strip()


def markdown(*rtf):
    """Return text as markdown from the list of RichText objects."""
    return ("".join(str(text) for text in rtf)).strip()


class Color(str, Enum):
    """Basic color values."""

    default = "default"
    gray = "gray"
    brown = "brown"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    blue = "blue"
    purple = "purple"
    pink = "pink"
    red = "red"


class FullColor(str, Enum):
    """Extended color values, including backgounds."""

    default = "default"
    gray = "gray"
    brown = "brown"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    blue = "blue"
    purple = "purple"
    pink = "pink"
    red = "red"

    gray_background = "gray_background"
    brown_background = "brown_background"
    orange_background = "orange_background"
    yellow_background = "yellow_background"
    green_background = "green_background"
    blue_background = "blue_background"
    purple_background = "purple_background"
    pink_background = "pink_background"
    red_background = "red_background"


class LinkObject(DataObject):
    """Reference a URL."""

    type: str = "url"
    url: str = None


class Annotations(DataObject):
    """Style information for RichTextObject's."""

    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: FullColor = None

    @property
    def is_plain(self):
        if self.bold:
            return False
        if self.italic:
            return False
        if self.strikethrough:
            return False
        if self.underline:
            return False
        if self.code:
            return False
        if self.color is not None:
            return False
        return True


class RichTextObject(TypedObject):
    """Base class for Notion rich text elements."""

    plain_text: str
    href: str = None
    annotations: Annotations = None

    def __str__(self):
        """Return a string representation of this object."""

        if self.href is None:
            text = self.plain_text or ""
        elif self.plain_text is None or len(self.plain_text) == 0:
            text = f"({self.href})"
        else:
            text = f"[{self.plain_text}]({self.href})"

        if self.annotations:
            if self.annotations.bold:
                text = f"*{text}*"
            if self.annotations.italic:
                text = f"**{text}**"
            if self.annotations.underline:
                text = f"_{text}_"
            if self.annotations.strikethrough:
                text = f"~{text}~"
            if self.annotations.code:
                text = f"`{text}`"

        return text


class TextObject(RichTextObject, type="text"):
    """Notion text element."""

    class NestedData(NestedObject):
        content: str
        link: LinkObject = None

    text: NestedData = None

    @classmethod
    def from_value(cls, string=None, href=None, **annotate):
        """Return a TextObject from the native string."""

        if string is None:
            return None

        # TODO convert markdown in string to RichText

        style = Annotations(**annotate) if annotate else None
        link = LinkObject(url=href) if href else None
        text = cls.NestedData(content=str(string), link=link)

        return cls(plain_text=str(string), text=text, href=href, annotations=style)


class CodingLanguage(str, Enum):
    """Available coding languages."""

    abap = "abap"
    arduino = "arduino"
    bash = "bash"
    basic = "basic"
    c = "c"
    clojure = "clojure"
    coffeescript = "coffeescript"
    cpp = "c++"
    csharp = "c#"
    css = "css"
    dart = "dart"
    diff = "diff"
    docker = "docker"
    elixir = "elixir"
    elm = "elm"
    erlang = "erlang"
    flow = "flow"
    fortran = "fortran"
    fsharp = "f#"
    gherkin = "gherkin"
    glsl = "glsl"
    go = "go"
    graphql = "graphql"
    groovy = "groovy"
    haskell = "haskell"
    html = "html"
    java = "java"
    javascript = "javascript"
    json = "json"
    julia = "julia"
    kotlin = "kotlin"
    latex = "latex"
    less = "less"
    lisp = "lisp"
    livescript = "livescript"
    lua = "lua"
    makefile = "makefile"
    markdown = "markdown"
    markup = "markup"
    matlab = "matlab"
    mermaid = "mermaid"
    nix = "nix"
    objective_c = "objective-c"
    ocaml = "ocaml"
    pascal = "pascal"
    perl = "perl"
    php = "php"
    plain_text = "plain text"
    powershell = "powershell"
    prolog = "prolog"
    protobuf = "protobuf"
    python = "python"
    r = "r"
    reason = "reason"
    ruby = "ruby"
    rust = "rust"
    sass = "sass"
    scala = "scala"
    scheme = "scheme"
    scss = "scss"
    shell = "shell"
    sql = "sql"
    swift = "swift"
    typescript = "typescript"
    vb_net = "vb.net"
    verilog = "verilog"
    vhdl = "vhdl"
    visual_basic = "visual basic"
    webassembly = "webassembly"
    xml = "xml"
    yaml = "yaml"
    misc = "java/c/c++/c#"

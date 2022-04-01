"""Utilities for parsing other document types in Notion.

These parsers provide an alternative to the "Import" cabilities of the Notion client
and Notion Web Clipper.  Perhaps that capability will be exposed to the API in the
future, which would effectively render these parsers unnecessary.
"""

# FIXME improve extra spacing around text elements

# TODO add more options for callers to customize output
# TODO look for options to handle text styled using CSS
# TODO consider how to handle <form> content

import logging
import re
from abc import ABC, abstractmethod
from xml.etree import ElementTree

import html5lib

from notional.text import Annotations, TextObject

from . import blocks, types

log = logging.getLogger(__name__)

# parse embedded image data
img_data_re = re.compile("^data:image/([^;]+);([^,]+),(.+)$")


def normalize_text(text):
    if text is None:
        return None

    text = re.sub(r"\s+", " ", text, flags=re.MULTILINE)

    return text or None


def gather_text(elem):
    text = "".join(elem.itertext())
    text = text.strip()
    text = normalize_text(text)
    return text or None


class DocumentParser(ABC):

    title: str
    content: list()

    def __init__(self):
        self.title = None
        self.content = list()

    @abstractmethod
    def parse(self, data):
        pass


class HtmlParser(DocumentParser):
    """An HTML parser that leverages the WHATWG HTML spec."""

    meta: dict()

    def __init__(self, base=None):
        super().__init__()

        self._base_url = base

        self.meta = dict()

        self._current_href = None
        self._current_text_style = Annotations()

    def parse(self, html):

        log.debug("BEGIN parsing")

        # alternative: use lxml.etree interchangeably...
        # doc = lxml.etree.HTML(html)

        doc = html5lib.parse(html, namespaceHTMLElements=False)

        self._render(doc)

        log.debug("END parsing")

    def _render(self, elem, parent=None):
        log.debug("rendering element - %s :: [%s]", elem.tag, parent)

        if parent is None:
            parent = self.content

        if hasattr(self, f"_render_{elem.tag}"):
            log.debug("handler func -- _render_%s", elem.tag)
            pfunc = getattr(self, f"_render_{elem.tag}")
            pfunc(elem, parent)

        log.debug("block complete; %d content block(s)", len(self.content))

    def _render_a(self, elem, parent):
        self._current_href = elem.get("href")
        self._process_contents(elem, parent=parent)
        self._current_href = None

    def _render_b(self, elem, parent):
        self._current_text_style.bold = True
        self._process_contents(elem, parent=parent)
        self._current_text_style.bold = False

    def _render_base(self, elem, parent):
        base = elem.get("href")
        if base is not None:
            self._base_url = base

    def _render_blockquote(self, elem, parent):
        block = blocks.Quote()
        self._process_contents(elem, parent=block)
        parent.append(block)

    def _render_body(self, elem, parent):
        self._process_contents(elem, parent=parent)

    def _render_br(self, elem, parent):
        if isinstance(parent, blocks.TextBlock):
            parent.concat("\n")

    def _render_code(self, elem, parent):
        self._current_text_style.code = True
        self._process_contents(elem, parent=parent)
        self._current_text_style.code = False

    def _render_dd(self, elem, parent):
        self._process_contents(elem, parent=parent)

    def _render_del(self, elem, parent):
        self._render_strike(elem, parent)

    def _render_div(self, elem, parent):
        self._process_contents(elem, parent)

    def _render_dl(self, elem, parent):
        dl = blocks.Paragraph()
        self._process_contents(elem, parent=dl)
        parent.append(dl)

    def _render_dt(self, elem, parent):
        self._process_contents(elem, parent=parent)

    def _render_em(self, elem, parent):
        self._render_i(elem, parent)

    def _render_h1(self, elem, parent):
        h1 = blocks.Heading1()
        self._process_contents(elem, parent=h1)
        parent.append(h1)

    def _render_h2(self, elem, parent):
        h2 = blocks.Heading2()
        self._process_contents(elem, parent=h2)
        parent.append(h2)

    def _render_h3(self, elem, parent):
        h3 = blocks.Heading3()
        self._process_contents(elem, parent=h3)
        parent.append(h3)

    def _render_head(self, elem, parent):
        self._process_contents(elem, parent=parent)

    def _render_hr(self, elem, parent):
        parent.append(blocks.Divider())

    def _render_html(self, elem, parent):
        self._process_contents(elem, parent=parent)

    def _render_i(self, elem, parent):
        self._current_text_style.italic = True
        self._process_contents(elem, parent=parent)
        self._current_text_style.italic = False

    def _render_iframe(self, elem, parent):
        src = elem.get("src")
        if src is not None:
            block = blocks.Embed.from_url(src)
            parent.append(block)

    def _render_img(self, elem, parent):
        src = elem.get("src")

        # TODO use self._base_url for relative paths
        # TODO support embedded images (data:image) as HostedFile...

        if src is not None:
            file = types.ExternalFile.from_url(src)
            img = blocks.Image(image=file)

            parent.append(img)

    def _render_ins(self, elem, parent):
        self._render_u(elem, parent)

    def _render_kbd(self, elem, parent):
        self._render_code(elem, parent)

    def _render_li(self, elem, parent):
        self._process_contents(elem, parent)

    def _render_menu(self, elem, parent):
        self._render_ul(elem, parent)

    def _render_meta(self, elem, parent):
        name = elem.get("name")
        value = elem.get("content")
        if name and value:
            self.meta[name] = value

    def _render_object(self, elem, parent):
        # XXX support 'data' attribute as an embed or upload?
        self._process_contents(elem, parent=parent)

    def _render_ol(self, elem, parent):
        for li in elem.findall("li"):
            block = blocks.NumberedListItem()
            self._render(li, parent=block)
            parent.append(block)

    def _render_p(self, elem, parent):
        para = blocks.Paragraph()
        self._process_contents(elem, parent=para)
        parent.append(para)

    def _render_pre(self, elem, parent):
        block = blocks.Code()
        self._process_contents(elem, parent=block)
        parent.append(block)

    def _render_s(self, elem, parent):
        self._render_strike(self, elem, parent)

    def _render_samp(self, elem, parent):
        self._render_code(elem, parent)

    def _render_strike(self, elem, parent):
        self._current_text_style.strikethrough = True
        self._process_contents(elem, parent=parent)
        self._current_text_style.strikethrough = False

    def _render_strong(self, elem, parent):
        self._render_b(elem, parent)

    def _render_table(self, elem, parent):
        table = blocks.Table()
        self._process_contents(elem, parent=table)

        if table.Width > 0:
            parent.append(table)

    def _render_tbody(self, elem, parent):
        self._process_contents(elem, parent)

    def _render_td(self, elem, parent):
        if elem.text is None:
            self._process_text(" ", parent)
        else:
            self._process_contents(elem, parent=parent)

    def _render_tfoot(self, elem, parent):
        self._process_contents(elem, parent)

    def _render_th(self, elem, parent):
        self._render_td(elem, parent=parent)

    def _render_thead(self, elem, parent):
        parent.table.has_column_header = True
        self._process_contents(elem, parent=parent)

    def _render_title(self, elem, parent):
        self.title = gather_text(elem)

    def _render_tr(self, elem, parent):
        row = blocks.TableRow()
        for td in elem.findall("td"):
            self._render(td, parent=row)
        parent.append(row)

    def _render_tt(self, elem, parent):
        self._render_pre(elem, parent)

    def _render_u(self, elem, parent):
        self._current_text_style.underline = True
        self._process_contents(elem, parent=parent)
        self._current_text_style.underline = False

    def _render_ul(self, elem, parent):
        for li in elem.findall("li"):
            block = blocks.BulletedListItem()
            self._render(li, parent=block)
            parent.append(block)

    def _render_var(self, elem, parent):
        self._render_code(elem, parent)

    def _process_text(self, text, parent):
        if not isinstance(parent, blocks.Code):
            text = normalize_text(text)

        style = self._current_text_style.dict()
        href = self._current_href
        obj = TextObject.from_value(text, href=href, **style)

        if isinstance(parent, blocks.TextBlock):
            if obj is not None:
                parent.concat(obj)

        elif isinstance(parent, blocks.TableRow):
            parent.append(obj)

    def _process_contents(self, elem, parent):
        log.debug("processing contents :: %s [%s]", elem, parent)

        #if isinstance(parent, blocks.TextBlock):
        #    text_parent = parent

        #elif isinstance(parent, blocks.TableRow):
        #    text_parent = parent

        #else:
        #    text_parent = blocks.Paragraph()
        #    parent.append(text_parent)

        self._process_text(elem.text, parent)

        for child in elem:
            self._render(child, parent)
            self._process_text(child.tail, parent)

    def _process_img_data(self, elem):
        import base64
        import tempfile

        log.debug("processing image")

        # TODO this probably needs more error handling and better flow

        img_src = elem["src"]
        m = img_data_re.match(img_src)

        if m is None:
            raise ValueError("Image data missing")

        img_type = m.groups()[0]
        img_data_enc = m.groups()[1]
        img_data_str = m.groups()[2]

        log.debug("decoding embedded image: %s [%s]", img_type, img_data_enc)

        if img_data_enc == "base64":
            log.debug("decoding base64 image: %d bytes", len(img_data_str))
            img_data_b64 = img_data_str.encode("ascii")
            img_data = base64.b64decode(img_data_b64)
        else:
            raise ValueError(f"Unsupported img encoding: {img_data_enc}")

        log.debug("preparing %d bytes for image upload", len(img_data))

        with tempfile.NamedTemporaryFile(suffix=f".{img_type}") as fp:
            log.debug("using temporary file: %s", fp.name)
            fp.write(img_data)

            # TODO upload the image to Notion

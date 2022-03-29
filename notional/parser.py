"""Utilities for parsing other document types in Notion.

NOTE: this is a _very_ prelimiary implementation and will likely change frequently.
"""

# TODO add more options for callers to customize output
# TODO look for options to handle text styled using CSS
# TODO consider using lxml.etree - reduce dependencies

import logging
import re

from bs4 import BeautifulSoup, Comment, Doctype, NavigableString

from notional.text import Annotations, TextObject

from . import blocks, types

log = logging.getLogger(__name__)

# parse embedded image data
img_data_re = re.compile("^data:image/([^;]+);([^,]+),(.+)$")


def gather_text(elem, strip=True, collapse=True):
    text = " ".join(elem.strings)

    if strip:
        text = text.strip()

    if collapse and text:
        text = re.sub(r"\s+", " ", text, flags=re.MULTILINE)

    return text or None


class HtmlDocumentParser(object):
    def __init__(self, base=None):
        self.base = base

        self.title = None
        self.meta = dict()
        self.doctype = None
        self.comments = list()
        self.content = list()

        # XXX this leads to some limitations with improperly balanced style tags
        self._current_text_style = Annotations()

    def parse(self, html):

        log.debug("BEGIN parsing")

        soup = BeautifulSoup(html, "html.parser")
        self._handle_element(soup)

        log.debug("END parsing")

    def _handle_element(self, elem, parent=None):
        log.debug("processing element - %s :: [%s]", elem.name, parent)

        if parent is None:
            parent = self.content

        for child in elem.children:

            # keep comments just for fun...
            if isinstance(child, Comment):
                text = gather_text(child)
                self.comments.append(text)

            # grab the doctype just in case..
            elif isinstance(child, Doctype):
                self.doctype = gather_text(child)

            # handle text elements...
            elif isinstance(child, NavigableString):
                self._handle_text(child, parent)

            # handle known blocks...
            elif hasattr(self, f"_handle_{child.name}"):
                log.debug("handler -- _handle_%s", child.name)
                pfunc = getattr(self, f"_handle_{child.name}")
                pfunc(child, parent)

            # otherwise, just keep digging...
            else:
                self._handle_element(child, parent)

        log.debug("block complete; %d content block(s)", len(self.content))

    def _handle_text(self, elem, parent):
        if isinstance(parent, blocks.Code):
            text = gather_text(elem, strip=False, collapse=False)
        else:
            text = gather_text(elem, strip=False, collapse=True)

        style = self._current_text_style.dict()
        obj = TextObject.from_value(text, **style)

        if isinstance(parent, blocks.TextBlock):
            if obj is not None and len(text) > 0:
                parent.concat(obj)

        elif isinstance(parent, blocks.TableRow):
            parent.append(obj)

    def _handle_meta(self, elem, parent):
        name = elem.get("name")
        value = elem.get("content")
        if name and value:
            self.meta[name] = value

    def _handle_script(self, elem, parent):
        pass

    def _handle_link(self, elem, parent):
        pass

    def _handle_style(self, elem, parent):
        pass

    def _handle_title(self, elem, parent):
        self.title = gather_text(elem)

    def _handle_br(self, elem, parent):
        if isinstance(parent, blocks.TextBlock):
            parent.concat("\n")

    def _handle_hr(self, elem, parent):
        parent.append(blocks.Divider())

    def _handle_h1(self, elem, parent):
        heading = blocks.Heading1()
        self._handle_element(elem, parent=heading)
        parent.append(heading)

    def _handle_h2(self, elem, parent):
        heading = blocks.Heading2()
        self._handle_element(elem, parent=heading)
        parent.append(heading)

    def _handle_h3(self, elem, parent):
        heading = blocks.Heading3()
        self._handle_element(elem, parent=heading)
        parent.append(heading)

    def _handle_p(self, elem, parent):
        para = blocks.Paragraph()
        self._handle_element(elem, parent=para)
        parent.append(para)

    def _handle_tt(self, elem, parent):
        self._handle_pre(elem, parent)

    def _handle_pre(self, elem, parent):
        block = blocks.Code()
        self._handle_element(elem, parent=block)
        parent.append(block)

    def _handle_blockquote(self, elem, parent):
        block = blocks.Quote()
        self._handle_element(elem, parent=block)
        parent.append(block)

    def _handle_b(self, elem, parent):
        self._handle_strong(elem, parent)

    def _handle_strong(self, elem, parent):
        self._current_text_style.bold = True
        self._handle_element(elem, parent=parent)
        self._current_text_style.bold = False

    def _handle_i(self, elem, parent):
        self._handle_em(elem, parent)

    def _handle_em(self, elem, parent):
        self._current_text_style.italic = True
        self._handle_element(elem, parent=parent)
        self._current_text_style.italic = False

    def _handle_u(self, elem, parent):
        self._handle_ins(elem, parent)

    def _handle_ins(self, elem, parent):
        self._current_text_style.underline = True
        self._handle_element(elem, parent=parent)
        self._current_text_style.underline = False

    def _handle_strike(self, elem, parent):
        self._handle_del(elem, parent)

    def _handle_del(self, elem, parent):
        self._current_text_style.strikethrough = True
        self._handle_element(elem, parent=parent)
        self._current_text_style.strikethrough = False

    def _handle_kbd(self, elem, parent):
        self._handle_code(elem, parent)

    def _handle_code(self, elem, parent):
        self._current_text_style.code = True
        self._handle_element(elem, parent=parent)
        self._current_text_style.code = False

    def _handle_li(self, elem, parent):
        if elem.parent.name == "ol":
            li = blocks.NumberedListItem()
        else:
            li = blocks.BulletedListItem()

        self._handle_element(elem, li)
        parent.append(li)

    def _handle_dl(self, elem, parent):
        dl = blocks.Paragraph()
        self._handle_element(elem, parent=dl)
        parent.append(dl)

    def _handle_table(self, elem, parent):
        table = blocks.Table()
        self._handle_element(elem, parent=table)

        if table.Width > 0:
            parent.append(table)

    def _handle_thead(self, elem, parent):
        parent.table.has_column_header = True
        self._handle_element(elem, parent)

    def _handle_tr(self, elem, parent):
        row = blocks.TableRow()
        for td in elem("td"):
            self._handle_element(td, parent=row)
        parent.append(row)

    def _handle_object(self, elem, parent):
        # TODO support 'data' attribute as an embed or upload?
        self._handle_element(elem, parent)

    def _handle_iframe(self, elem, parent):
        src = elem.get("src")
        if src is not None:
            block = blocks.Embed.from_url(src)
            parent.append(block)

    def _handle_img(self, elem, parent):
        src = elem["src"]

        # TODO use self.base for relative paths - or upload as HostedFile?
        # TODO support embedded images (data:image) as HostedFile...

        file = types.ExternalFile.from_url(src)
        img = blocks.Image(image=file)

        parent.append(img)

    def _handle_img_data(self, elem):
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

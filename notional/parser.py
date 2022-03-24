"""Utilities for parsing other document types in Notion.

NOTE: this is a _very_ prelimiary implementation and will likely change frequently.
"""

# TODO preserve all text formatting when combining styles
# TODO support embedded pictures (e.g. from Apple Notes) - API limitation
# TODO consider using lxml.etree for consistency with other parsers
# TODO add more options for callers to customize output

import logging
import re

from bs4 import BeautifulSoup, NavigableString

from . import blocks, types

log = logging.getLogger(__name__)

# parse embedded image data
img_data_re = re.compile("^data:image/([^;]+);([^,]+),(.+)$")


def gather_text(elem, stripped=True, condensed=True):
    text = " ".join(elem.strings)

    if stripped and text:
        text = text.strip()

    if condensed and text:
        text = re.sub(r"\s+", " ", text, flags=re.MULTILINE)

    return text or None


class HtmlDocumentParser(object):
    def __init__(self, base=None):
        self.base = base

        self.title = None
        self.content = list()
        self.meta = dict()
        self.comments = list()

    def parse(self, html):

        log.debug("BEGIN parsing")

        soup = BeautifulSoup(html, "html.parser")
        self._process(soup)

        log.debug("END parsing")

    def _process(self, elem, parent=None):
        log.debug("processing element - %s", elem.name)

        if parent is None:
            parent = self.content

        for child in elem.children:
            self._parse_elem(child, parent)

        log.debug("block complete; %d content block(s)", len(self.content))

    def _parse_elem(self, elem, parent=None):
        if elem is None:
            return

        log.debug("parsing element - %s", elem.name)

        # handle known blocks...
        if hasattr(self, f"_parse_{elem.name}"):
            log.debug("parser func -- _parse_%s", elem.name)
            pfunc = getattr(self, f"_parse_{elem.name}")

            pfunc(elem, parent)

        # grab all possible text...
        else:
            self._parse_p(elem, parent)

    def _parse_html(self, elem, parent):
        self._process(elem, parent)

    def _parse_head(self, elem, parent):
        self._process(elem, parent)

    def _parse_script(self, elem, parent):
        pass

    def _parse_meta(self, elem, parent):
        name = elem.get("name")
        if name is not None:
            value = elem.get("content")
            if value is not None:
                self.meta[name] = value

    def _parse_link(self, elem, parent):
        pass

    def _parse_style(self, elem, parent):
        pass

    def _parse_title(self, elem, parent):
        self.title = gather_text(elem)

    def _parse_body(self, elem, parent):
        self._process(elem, parent)

    def _parse_br(self, elem, parent):
        pass

    def _parse_hr(self, elem, parent):
        block = blocks.Divider()
        parent.append(block)

    def _parse_iframe(self, elem, parent):
        src = elem.get("src")
        if src is not None:
            block = blocks.Embed.from_url(src)
            parent.append(block)

    def _parse_div(self, elem, parent):
        self._process(elem, parent)

    def _parse_object(self, elem, parent):
        self._process(elem, parent)

    def _parse_h1(self, elem, parent):
        text = gather_text(elem)
        block = blocks.Heading1.from_text(text)
        parent.append(block)

    def _parse_h2(self, elem, parent):
        text = gather_text(elem)
        block = blocks.Heading2.from_text(text)
        parent.append(block)

    def _parse_h3(self, elem, parent):
        text = gather_text(elem)
        block = blocks.Heading3.from_text(text)
        parent.append(block)

    def _parse_p(self, elem, parent):
        text = gather_text(elem)
        if text is not None and len(text) > 0:
            block = blocks.Paragraph.from_text(text)
            parent.append(block)

    def _parse_list(self, elem, parent, list_type):
        item = None

        # lists are tricky since we have to keep an eye on the containing element,
        # which tells us the type of list item to create in Notion

        for child in elem.children:

            if child.name == "li":
                text = gather_text(child)

                if text is not None:
                    item = list_type.from_text(text)
                    parent.append(item)

            else:
                self._parse_elem(child, item)

    def _parse_ul(self, elem, parent):
        self._parse_list(elem, parent, blocks.BulletedListItem)

    def _parse_ol(self, elem, parent):
        self._parse_list(elem, parent, blocks.NumberedListItem)

    # def _parse_dl(self, elem, parent):
    # def _parse_dd(self, elem, parent):
    # def _parse_dt(self, elem, parent):

    def _parse_tt(self, elem, parent):
        self._parse_pre(elem, parent=parent)

    def _parse_pre(self, elem, parent):
        text = gather_text(elem, condensed=False)
        block = blocks.Code.from_text(text)
        parent.append(block)

    def _parse_blockquote(self, elem, parent):
        text = gather_text(elem)
        block = blocks.Quote.from_text(text)
        parent.append(block)

    def _parse_table(self, elem, parent):
        log.debug("building table")

        table = blocks.Table()

        self._process(elem, parent=table)

        if table.Width > 0:
            parent.append(table)

    def _parse_thead(self, elem, parent):
        parent.table.has_column_header = True
        self._process(elem, parent=parent)

    def _parse_tbody(self, elem, parent):
        self._process(elem, parent=parent)

    def _parse_tfoot(self, elem, parent):
        self._process(elem, parent=parent)

    def _parse_tr(self, elem, parent):
        # table rows must be directly appended to the table
        row = blocks.TableRow()
        self._process(elem, parent=row)
        parent.append(row)

    def _parse_th(self, elem, parent):
        self._parse_td(elem, parent)

    def _parse_td(self, elem, parent):
        # table data must be directly appended to the row
        text = gather_text(elem)
        parent.append(text or "")

    def _parse_img(self, elem, parent):
        href = elem["src"]

        # TODO use self.base for relative paths - or upload as HostedFile?
        # TODO support embedded images (data:image) as HostedFile...

        src = types.ExternalFile.from_url(href)
        img = blocks.Image(image=src)

        parent.append(img)

    def _parse_img_data(self, elem, parent):
        import base64
        import tempfile

        log.debug("processing image")

        # TODO this probably needs more error handling and better flow

        img_src = elem["src"]
        m = img_data_re.match(img_src)

        if m is None:
            log.warning("Unsupported image in note")
            return

        img_type = m.groups()[0]
        img_data_enc = m.groups()[1]
        img_data_str = m.groups()[2]

        log.debug("found embedded image: %s [%s]", img_type, img_data_enc)

        if img_data_enc == "base64":
            log.debug("decoding base64 image: %d bytes", len(img_data_str))
            img_data_b64 = img_data_str.encode("ascii")
            img_data = base64.b64decode(img_data_b64)
        else:
            log.warning("Unsupported img encoding: %s", img_data_enc)
            return

        log.debug("preparing %d bytes for image upload", len(img_data))

        with tempfile.NamedTemporaryFile(suffix=f".{img_type}") as fp:
            log.debug("using temporary file: %s", fp.name)
            fp.write(img_data)

            # TODO upload the image to Notion

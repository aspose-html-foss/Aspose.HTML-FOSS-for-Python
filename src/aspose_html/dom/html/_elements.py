"""Re-export shim — all HTML element classes.

All concrete element classes live in per-family submodules under
``src/aspose_html/dom/html/``.  This file re-exports every name so
that existing import paths (``from aspose_html.dom.html._elements
import X``) continue to work without change.

See  for the split rationale and family assignments.

Examples
--------
>>> from aspose_html.dom.html._elements import HTMLInputElement, HTMLAnchorElement
>>> HTMLInputElement.__name__
'HTMLInputElement'
>>> HTMLAnchorElement.__name__
'HTMLAnchorElement'
"""
from __future__ import annotations

from aspose_html.dom._html_element import HTMLElement
from aspose_html.dom.html._anchor_elements import (
    HTMLAnchorElement,
    HTMLAreaElement,
    HTMLMapElement,
    _get_base_url,
    _resolve_anchor_href,
    _resolve_area_href,
)
from aspose_html.dom.html._form_elements import (
    HTMLButtonElement,
    HTMLDataListElement,
    HTMLFieldSetElement,
    HTMLFormElement,
    HTMLInputElement,
    HTMLLabelElement,
    HTMLLegendElement,
    HTMLMeterElement,
    HTMLOptGroupElement,
    HTMLOptionElement,
    HTMLOutputElement,
    HTMLProgressElement,
    HTMLSelectElement,
    HTMLTextAreaElement,
    _get_form_owner,
)
from aspose_html.dom.html._table_elements import (
    HTMLTableCaptionElement,
    HTMLTableCellElement,
    HTMLTableColElement,
    HTMLTableElement,
    HTMLTableRowElement,
    HTMLTableSectionElement,
)
from aspose_html.dom.html._list_elements import (
    HTMLDListElement,
    HTMLLIElement,
    HTMLOListElement,
    HTMLUListElement,
)
from aspose_html.dom.html._media_elements import (
    HTMLAudioElement,
    HTMLMediaElement,
    HTMLPictureElement,
    HTMLSourceElement,
    HTMLTrackElement,
    HTMLVideoElement,
)
from aspose_html.dom.html._metadata_elements import (
    HTMLBaseElement,
    HTMLLinkElement,
    HTMLMetaElement,
    HTMLScriptElement,
    HTMLStyleElement,
    HTMLTitleElement,
)
from aspose_html.dom.html._sectioning_elements import (
    HTMLAddressElement,
    HTMLArticleElement,
    HTMLAsideElement,
    HTMLBodyElement,
    HTMLBRElement,
    HTMLDetailsElement,
    HTMLDialogElement,
    HTMLFigCaptionElement,
    HTMLFigureElement,
    HTMLFooterElement,
    HTMLHeadElement,
    HTMLHeaderElement,
    HTMLHRElement,
    HTMLHtmlElement,
    HTMLMainElement,
    HTMLMarkElement,
    HTMLMenuElement,
    HTMLModElement,
    HTMLNavElement,
    HTMLNoScriptElement,
    HTMLPreElement,
    HTMLRubyElement,
    HTMLSectionElement,
    HTMLSmallElement,
    HTMLSummaryElement,
    HTMLTemplateElement,
    HTMLWBRElement,
)
from aspose_html.dom.html._embedded_elements import (
    HTMLCanvasElement,
    HTMLEmbedElement,
    HTMLIFrameElement,
    HTMLImageElement,
    HTMLObjectElement,
    HTMLParamElement,
)
from aspose_html.dom.html._text_elements import (
    HTMLDataElement,
    HTMLDivElement,
    HTMLHeadingElement,
    HTMLParagraphElement,
    HTMLQuoteElement,
    HTMLSpanElement,
    HTMLTimeElement,
    HTMLUnknownElement,
)

__all__ = [
    # anchor family
    "HTMLAnchorElement", "HTMLAreaElement", "HTMLMapElement",
    "_get_base_url", "_resolve_anchor_href", "_resolve_area_href",
    # form family
    "HTMLFormElement", "HTMLInputElement", "HTMLButtonElement",
    "HTMLSelectElement", "HTMLTextAreaElement", "HTMLFieldSetElement",
    "HTMLOptionElement", "HTMLOptGroupElement", "HTMLOutputElement",
    "HTMLDataListElement", "HTMLProgressElement", "HTMLMeterElement",
    "HTMLLabelElement", "HTMLLegendElement", "_get_form_owner",
    # table family
    "HTMLTableElement", "HTMLTableSectionElement", "HTMLTableRowElement",
    "HTMLTableCellElement", "HTMLTableCaptionElement", "HTMLTableColElement",
    # list family
    "HTMLUListElement", "HTMLOListElement", "HTMLLIElement", "HTMLDListElement",
    # media family
    "HTMLMediaElement", "HTMLVideoElement", "HTMLAudioElement",
    "HTMLSourceElement", "HTMLTrackElement", "HTMLPictureElement",
    # metadata family
    "HTMLScriptElement", "HTMLLinkElement", "HTMLMetaElement",
    "HTMLTitleElement", "HTMLStyleElement", "HTMLBaseElement",
    # sectioning family
    "HTMLHtmlElement", "HTMLHeadElement", "HTMLBodyElement",
    "HTMLBRElement", "HTMLHRElement", "HTMLPreElement", "HTMLModElement",
    "HTMLDetailsElement", "HTMLDialogElement", "HTMLSummaryElement",
    "HTMLMenuElement", "HTMLTemplateElement",
    "HTMLNavElement", "HTMLSectionElement", "HTMLArticleElement",
    "HTMLAsideElement", "HTMLHeaderElement", "HTMLFooterElement",
    "HTMLMainElement", "HTMLFigureElement", "HTMLFigCaptionElement",
    "HTMLAddressElement", "HTMLWBRElement", "HTMLNoScriptElement",
    "HTMLMarkElement", "HTMLSmallElement", "HTMLRubyElement",
    # embedded family
    "HTMLImageElement", "HTMLIFrameElement", "HTMLEmbedElement",
    "HTMLObjectElement", "HTMLCanvasElement", "HTMLParamElement",
    # text/flow family
    "HTMLDivElement", "HTMLSpanElement", "HTMLParagraphElement",
    "HTMLHeadingElement", "HTMLQuoteElement", "HTMLTimeElement",
    "HTMLDataElement", "HTMLUnknownElement",
    # base class (re-exported for backward compat)
    "HTMLElement",
]

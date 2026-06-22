"""Foreign content (SVG/MathML) helpers — §13.2.6.5.

Provides integration point detection and attribute case adjustments for
elements in SVG and MathML namespaces.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aspose_html.dom import Element

SVG_NAMESPACE = "http://www.w3.org/2000/svg"
MATHML_NAMESPACE = "http://www.w3.org/1998/Math/MathML"
HTML_NAMESPACE = "http://www.w3.org/1999/xhtml"

# §13.2.6.5 — MathML text integration points
_MATHML_TEXT_INTEGRATION_POINTS: frozenset[str] = frozenset({
    "mi", "mo", "mn", "ms", "mtext",
})

# §13.2.6.5 — HTML integration points (SVG elements)
_SVG_HTML_INTEGRATION_POINTS: frozenset[str] = frozenset({
    "foreignobject", "desc", "title",
})

# §13.2.6.5 — SVG attribute case adjustments table
_SVG_ATTR_ADJUSTMENTS: dict[str, str] = {
    "attributename": "attributeName",
    "attributetype": "attributeType",
    "basefrequency": "baseFrequency",
    "baseprofile": "baseProfile",
    "calcmode": "calcMode",
    "clippathunits": "clipPathUnits",
    "diffuseconstant": "diffuseConstant",
    "edgemode": "edgeMode",
    "filterunits": "filterUnits",
    "glyphref": "glyphRef",
    "gradienttransform": "gradientTransform",
    "gradientunits": "gradientUnits",
    "kernelmatrix": "kernelMatrix",
    "kernelunitlength": "kernelUnitLength",
    "keypoints": "keyPoints",
    "keysplines": "keySplines",
    "keytimes": "keyTimes",
    "lengthadjust": "lengthAdjust",
    "limitingconeangle": "limitingConeAngle",
    "markerheight": "markerHeight",
    "markerunits": "markerUnits",
    "markerwidth": "markerWidth",
    "maskcontentunits": "maskContentUnits",
    "maskunits": "maskUnits",
    "numoctaves": "numOctaves",
    "pathlength": "pathLength",
    "patterncontentunits": "patternContentUnits",
    "patterntransform": "patternTransform",
    "patternunits": "patternUnits",
    "pointsatx": "pointsAtX",
    "pointsaty": "pointsAtY",
    "pointsatz": "pointsAtZ",
    "preservealpha": "preserveAlpha",
    "preserveaspectratio": "preserveAspectRatio",
    "primitiveunits": "primitiveUnits",
    "refx": "refX",
    "refy": "refY",
    "repeatcount": "repeatCount",
    "repeatdur": "repeatDur",
    "requiredextensions": "requiredExtensions",
    "requiredfeatures": "requiredFeatures",
    "specularconstant": "specularConstant",
    "specularexponent": "specularExponent",
    "spreadmethod": "spreadMethod",
    "startoffset": "startOffset",
    "stddeviation": "stdDeviation",
    "stitchtiles": "stitchTiles",
    "surfacescale": "surfaceScale",
    "systemlanguage": "systemLanguage",
    "tablevalues": "tableValues",
    "targetx": "targetX",
    "targety": "targetY",
    "textlength": "textLength",
    "viewbox": "viewBox",
    "viewtarget": "viewTarget",
    "xchannelselector": "xChannelSelector",
    "ychannelselector": "yChannelSelector",
    "zoomandpan": "zoomAndPan",
}

# §13.2.6.5 — MathML attribute case adjustments (only definitionURL)
_MATHML_ATTR_ADJUSTMENTS: dict[str, str] = {
    "definitionurl": "definitionURL",
}


def is_mathml_text_integration_point(element: Element) -> bool:
    """True if element is a MathML text integration point per §13.2.6.5."""
    return (
        element._namespace_uri == MATHML_NAMESPACE  # type: ignore[union-attr]
        and element._local_name in _MATHML_TEXT_INTEGRATION_POINTS  # type: ignore[union-attr]
    )


def is_html_integration_point(element: Element) -> bool:
    """True if element is an HTML integration point per §13.2.6.5."""
    if element._namespace_uri == SVG_NAMESPACE:  # type: ignore[union-attr]
        if element._local_name in _SVG_HTML_INTEGRATION_POINTS:  # type: ignore[union-attr]
            return True
    # annotation-xml in MathML namespace is an HTML integration point
    # if it has encoding attribute that is "text/html" or "application/xhtml+xml"
    if (
        element._namespace_uri == MATHML_NAMESPACE  # type: ignore[union-attr]
        and element._local_name == "annotation-xml"  # type: ignore[union-attr]
    ):
        enc = element.get_attribute("encoding")  # type: ignore[union-attr]
        if enc and enc.lower() in ("text/html", "application/xhtml+xml"):
            return True
    return False


def adjust_svg_attributes(
    attrs: tuple[tuple[str, str], ...]
) -> list[tuple[str, str]]:
    """Apply the SVG attribute case adjustments per §13.2.6.5 table."""
    result = []
    for name, value in attrs:
        adjusted = _SVG_ATTR_ADJUSTMENTS.get(name.lower(), name)
        result.append((adjusted, value))
    return result


def adjust_mathml_attributes(
    attrs: tuple[tuple[str, str], ...]
) -> list[tuple[str, str]]:
    """Apply the MathML attribute case adjustments per §13.2.6.5 table."""
    result = []
    for name, value in attrs:
        adjusted = _MATHML_ATTR_ADJUSTMENTS.get(name.lower(), name)
        result.append((adjusted, value))
    return result


def adjust_foreign_attributes(
    attrs: tuple[tuple[str, str], ...]
) -> list[tuple[str, str]]:
    """Apply the foreign attribute adjustments per §13.2.6.5 table.

    Handles namespaced attributes like xlink:href, xml:lang, xmlns:*.
    For v1.0 we pass them through as-is since we don't track attribute namespaces.
    """
    return list(attrs)

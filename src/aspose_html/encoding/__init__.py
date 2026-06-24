"""Encoding detection and input preprocessing for Aspose.HTML."""
from aspose_html.encoding._decoder import UnsupportedEncodingError
from aspose_html.encoding.detection import EncodingDetectionResult, detect_encoding

__all__ = [
    "EncodingDetectionResult",
    "UnsupportedEncodingError",
    "detect_encoding",
]

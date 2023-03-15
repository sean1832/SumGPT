from pytube import YouTube
import xml.etree.ElementTree as ET


def extract_xml_caption(xml: str) -> str:
    """Extracts the text content from the <s> elements of an XML string."""
    root = ET.fromstring(xml)
    text_content = ''
    for child in root.iter('s'):
        text_content += child.text
    return text_content.strip()


def get_transcript(url: str, lang_code: str = 'a.en') -> str:
    """Extracts the transcript from a YouTube video."""
    yt = YouTube(url)
    caption = yt.captions[lang_code]
    xml_caption = caption.xml_captions
    return extract_xml_caption(xml_caption)
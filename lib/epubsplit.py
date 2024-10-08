#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__   = 'GPL v3'
__copyright__ = '2021, Jim Miller'
__docformat__ = 'restructuredtext en'

import sys, re, os, traceback, copy
from posixpath import normpath
import logging
logger = logging.getLogger(__name__)

from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED

from xml.dom.minidom import parse, parseString, getDOMImplementation, Element
from time import time

import six
from six.moves.urllib.parse import unquote
from six import string_types, text_type as unicode
from six import unichr

from bs4 import BeautifulSoup
import re
import os

def sanitize_filename(filename):
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Trim spaces and periods from the end
    filename = filename.rstrip('. ')
    # Ensure the filename isn't empty and doesn't exceed max length
    filename = filename[:255] or 'untitled'
    return filename


## font decoding code lifted from
## calibre/src/calibre/ebooks/conversion/plugins/epub_input.py
## copyright '2009, Kovid Goyal <kovid@kovidgoyal.net>'
## don't bug Kovid about this use of it.

ADOBE_OBFUSCATION =  'http://ns.adobe.com/pdf/enc#RC'
IDPF_OBFUSCATION = 'http://www.idpf.org/2008/embedding'
from itertools import cycle

class FontDecrypter:
    def __init__(self, epub, content_dom):
        self.epub = epub
        self.content_dom = content_dom
        self.encryption = {}
        self.old_uuid = None

    def get_file(self,href):
        return self.epub.read(href)

    def get_encrypted_fontfiles(self):
        if not self.encryption:
            ## Find the .opf file.
            try:
                # <encryption xmlns="urn:oasis:names:tc:opendocument:xmlns:container"
                #             xmlns:enc="http://www.w3.org/2001/04/xmlenc#"
                #             xmlns:deenc="http://ns.adobe.com/digitaleditions/enc">
                #   <enc:EncryptedData>
                #     <enc:EncryptionMethod Algorithm="http://ns.adobe.com/pdf/enc#RC"/>
                #     <enc:CipherData>
                #       <enc:CipherReference URI="fonts/00017.ttf"/>
                #     </enc:CipherData>
                #   </enc:EncryptedData>
                # </encryption>
                encryption = self.epub.read("META-INF/encryption.xml")
                encryptiondom = parseString(encryption)
                # print(encryptiondom.toprettyxml(indent='   '))
                for encdata in encryptiondom.getElementsByTagName('enc:EncryptedData'):
                    # print(encdata.toprettyxml(indent='   '))
                    algorithm = encdata.getElementsByTagName('enc:EncryptionMethod')[0].getAttribute('Algorithm')
                    if algorithm not in {ADOBE_OBFUSCATION, IDPF_OBFUSCATION}:
                        print("Unknown font encryption: %s"%algorithm)
                    else:
                        # print(algorithm)
                        for encref in encdata.getElementsByTagName('enc:CipherReference'):
                            # print(encref.getAttribute('URI'))
                            self.encryption[encref.getAttribute('URI')]=algorithm
            except KeyError as ke:
                self.encryption = {}
        return self.encryption

    def get_old_uuid(self):
        if not self.old_uuid:
            contentdom = self.content_dom
            uidkey = contentdom.getElementsByTagName("package")[0].getAttribute("unique-identifier")
            for dcid in contentdom.getElementsByTagName("dc:identifier"):
                if dcid.getAttribute("id") == uidkey and dcid.getAttribute("opf:scheme") == "uuid":
                    self.old_uuid = dcid.firstChild.data
        return self.old_uuid

    def get_idpf_key(self):
        # idpf key:urn:uuid:221c69fe-29f3-4cb4-bb3f-58c430261cc6
        # idpf key:b'\xfb\xa9\x03N}\xae~\x12 \xaa\xe0\xc11\xe2\xe7\x1b\xf6\xa5\xcas'
        idpf_key = self.get_old_uuid()
        import uuid, hashlib
        idpf_key = re.sub('[\u0020\u0009\u000d\u000a]', '', idpf_key)
        idpf_key = hashlib.sha1(idpf_key.encode('utf-8')).digest()
        return idpf_key

    def get_adobe_key(self):
        # adobe key:221c69fe-29f3-4cb4-bb3f-58c430261cc6
        # adobe key:b'"\x1ci\xfe)\xf3L\xb4\xbb?X\xc40&\x1c\xc6'
        adobe_key = self.get_old_uuid()
        import uuid
        adobe_key = adobe_key.rpartition(':')[-1] # skip urn:uuid:
        adobe_key = uuid.UUID(adobe_key).bytes
        return adobe_key

    def get_decrypted_font_data(self, uri):
        # print(self.get_old_uuid())
        # print("idpf : %s"%self.get_idpf_key())
        # print("adobe: %s"%self.get_adobe_key())
        # print("uri:%s"%uri)
        font_data = self.get_file(uri)
        if uri in self.get_encrypted_fontfiles():
            key = self.get_adobe_key() if self.get_encrypted_fontfiles()[uri] == ADOBE_OBFUSCATION else self.get_idpf_key()
            font_data =  self.decrypt_font_data(key, font_data, self.get_encrypted_fontfiles()[uri])
        return font_data

    def decrypt_font_data(self, key, data, algorithm):
        is_adobe = algorithm == ADOBE_OBFUSCATION
        crypt_len = 1024 if is_adobe else 1040
        crypt = bytearray(data[:crypt_len])
        key = cycle(iter(bytearray(key)))
        decrypt = bytes(bytearray(x^next(key) for x in crypt))
        return decrypt + data[crypt_len:]

def _unirepl(match):
    "Return the unicode string for a decimal number"
    if match.group(1).startswith('x'):
        radix=16
        s = match.group(1)[1:]
    else:
        radix=10
        s = match.group(1)
    try:
        value = int(s, radix)
        retval = "%s%s"%(unichr(value),match.group(2))
    except:
        # This way, at least if there's more of entities out there
        # that fail, it doesn't blow the entire download.
        print("Numeric entity translation failed, skipping: &#x%s%s"%(match.group(1),match.group(2)))
        retval = ""
    return retval

def _replaceNumberEntities(data):
    # The same brokenish entity parsing in SGMLParser that inserts ';'
    # after non-entities will also insert ';' incorrectly after number
    # entities, including part of the next word if it's a-z.
    # "Don't&#8212ever&#8212do&#8212that&#8212again," becomes
    # "Don't&#8212e;ver&#8212d;o&#8212;that&#8212a;gain,"
    # Also need to allow for 5 digit decimal entities &#27861;
    # Last expression didn't allow for 2 digit hex correctly: &#xE9;
    p = re.compile(r'&#(x[0-9a-fA-F]{,4}|[0-9]{,5})([0-9a-fA-F]*?);')
    return p.sub(_unirepl, data)

def _replaceNotEntities(data):
    # not just \w or \S.  regexp from c:\Python25\lib\sgmllib.py
    # (or equiv), SGMLParser, entityref
    p = re.compile(r'&([a-zA-Z][-.a-zA-Z0-9]*);')
    return p.sub(r'&\1', data)

def stripHTML(soup):
    return removeAllEntities(re.sub(r'<[^>]+>','',"%s" % soup)).strip()

def conditionalRemoveEntities(value):
    if isinstance(value,string_types) :
        return removeEntities(value).strip()
    else:
        return value

def removeAllEntities(text):
    # Remove &lt; &lt; and &amp;
    return removeEntities(text).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

def removeEntities(text):

    if text is None:
        return ""
    if not (isinstance(text,string_types)):
        return str(text)

    try:
        t = unicode(text) #.decode('utf-8')
    except UnicodeEncodeError as e:
        try:
            t = text.encode ('ascii', 'xmlcharrefreplace')
        except UnicodeEncodeError as e:
            t = text
    text = t
    # replace numeric versions of [&<>] with named versions,
    # then replace named versions with actual characters,
    text = re.sub(r'&#0*38;','&amp;',text)
    text = re.sub(r'&#0*60;','&lt;',text)
    text = re.sub(r'&#0*62;','&gt;',text)

    # replace remaining &#000; entities with unicode value, such as &#039; -> '
    text = _replaceNumberEntities(text)

    # replace several named entities with character, such as &mdash; -> -
    # see constants.py for the list.
    # reverse sort will put entities with ; before the same one without, when valid.
    for e in reversed(sorted(entities.keys())):
        v = entities[e]
        try:
            text = text.replace(e, v)
        except UnicodeDecodeError as ex:
            # for the pound symbol in constants.py
            text = text.replace(e, v.decode('utf-8'))

    # SGMLParser, and in turn, BeautifulStoneSoup doesn't parse
    # entities terribly well and inserts (;) after something that
    # it thinks might be an entity.  AT&T becomes AT&T; All of my
    # attempts to fix this by changing the input to
    # BeautifulStoneSoup break something else instead.  But at
    # this point, there should be *no* real entities left, so find
    # these not-entities and removing them here should be safe.
    text = _replaceNotEntities(text)

    # &lt; &lt; and &amp; are the only html entities allowed in xhtml, put those back.
    return text.replace('&', '&amp;').replace('&amp;lt', '&lt;').replace('&amp;gt', '&gt;')

# entity list from http://code.google.com/p/doctype/wiki/CharacterEntitiesConsistent
entities = { '&aacute;' : 'á',
         '&Aacute;' : 'Á',
         '&Aacute' : 'Á',
         '&aacute' : 'á',
         '&acirc;' : 'â',
         '&Acirc;' : 'Â',
         '&Acirc' : 'Â',
         '&acirc' : 'â',
         '&acute;' : '´',
         '&acute' : '´',
         '&AElig;' : 'Æ',
         '&aelig;' : 'æ',
         '&AElig' : 'Æ',
         '&aelig' : 'æ',
         '&agrave;' : 'à',
         '&Agrave;' : 'À',
         '&Agrave' : 'À',
         '&agrave' : 'à',
         '&alefsym;' : 'ℵ',
         '&alpha;' : 'α',
         '&Alpha;' : 'Α',
         '&amp;' : '&',
         '&AMP;' : '&',
         '&AMP' : '&',
         '&amp' : '&',
         '&and;' : '∧',
         '&ang;' : '∠',
         '&aring;' : 'å',
         '&Aring;' : 'Å',
         '&Aring' : 'Å',
         '&aring' : 'å',
         '&asymp;' : '≈',
         '&atilde;' : 'ã',
         '&Atilde;' : 'Ã',
         '&Atilde' : 'Ã',
         '&atilde' : 'ã',
         '&auml;' : 'ä',
         '&Auml;' : 'Ä',
         '&Auml' : 'Ä',
         '&auml' : 'ä',
         '&bdquo;' : '„',
         '&beta;' : 'β',
         '&Beta;' : 'Β',
         '&brvbar;' : '¦',
         '&brvbar' : '¦',
         '&bull;' : '•',
         '&cap;' : '∩',
         '&ccedil;' : 'ç',
         '&Ccedil;' : 'Ç',
         '&Ccedil' : 'Ç',
         '&ccedil' : 'ç',
         '&cedil;' : '¸',
         '&cedil' : '¸',
         '&cent;' : '¢',
         '&cent' : '¢',
         '&chi;' : 'χ',
         '&Chi;' : 'Χ',
         '&circ;' : 'ˆ',
         '&clubs;' : '♣',
         '&cong;' : '≅',
         '&copy;' : '©',
         '&COPY;' : '©',
         '&COPY' : '©',
         '&copy' : '©',
         '&crarr;' : '↵',
         '&cup;' : '∪',
         '&curren;' : '¤',
         '&curren' : '¤',
         '&dagger;' : '†',
         '&Dagger;' : '‡',
         '&darr;' : '↓',
         '&dArr;' : '⇓',
         '&deg;' : '°',
         '&deg' : '°',
         '&delta;' : 'δ',
         '&Delta;' : 'Δ',
         '&diams;' : '♦',
         '&divide;' : '÷',
         '&divide' : '÷',
         '&eacute;' : 'é',
         '&Eacute;' : 'É',
         '&Eacute' : 'É',
         '&eacute' : 'é',
         '&ecirc;' : 'ê',
         '&Ecirc;' : 'Ê',
         '&Ecirc' : 'Ê',
         '&ecirc' : 'ê',
         '&egrave;' : 'è',
         '&Egrave;' : 'È',
         '&Egrave' : 'È',
         '&egrave' : 'è',
         '&empty;' : '∅',
         '&emsp;' : ' ',
         '&ensp;' : ' ',
         '&epsilon;' : 'ε',
         '&Epsilon;' : 'Ε',
         '&equiv;' : '≡',
         '&eta;' : 'η',
         '&Eta;' : 'Η',
         '&eth;' : 'ð',
         '&ETH;' : 'Ð',
         '&ETH' : 'Ð',
         '&eth' : 'ð',
         '&euml;' : 'ë',
         '&Euml;' : 'Ë',
         '&Euml' : 'Ë',
         '&euml' : 'ë',
         '&euro;' : '€',
         '&exist;' : '∃',
         '&fnof;' : 'ƒ',
         '&forall;' : '∀',
         '&frac12;' : '½',
         '&frac12' : '½',
         '&frac14;' : '¼',
         '&frac14' : '¼',
         '&frac34;' : '¾',
         '&frac34' : '¾',
         '&frasl;' : '⁄',
         '&gamma;' : 'γ',
         '&Gamma;' : 'Γ',
         '&ge;' : '≥',
         #'&gt;' : '>',
         #'&GT;' : '>',
         #'&GT' : '>',
         #'&gt' : '>',
         '&harr;' : '↔',
         '&hArr;' : '⇔',
         '&hearts;' : '♥',
         '&hellip;' : '…',
         '&iacute;' : 'í',
         '&Iacute;' : 'Í',
         '&Iacute' : 'Í',
         '&iacute' : 'í',
         '&icirc;' : 'î',
         '&Icirc;' : 'Î',
         '&Icirc' : 'Î',
         '&icirc' : 'î',
         '&iexcl;' : '¡',
         '&iexcl' : '¡',
         '&igrave;' : 'ì',
         '&Igrave;' : 'Ì',
         '&Igrave' : 'Ì',
         '&igrave' : 'ì',
         '&image;' : 'ℑ',
         '&infin;' : '∞',
         '&int;' : '∫',
         '&iota;' : 'ι',
         '&Iota;' : 'Ι',
         '&iquest;' : '¿',
         '&iquest' : '¿',
         '&isin;' : '∈',
         '&iuml;' : 'ï',
         '&Iuml;' : 'Ï',
         '&Iuml' : 'Ï',
         '&iuml' : 'ï',
         '&kappa;' : 'κ',
         '&Kappa;' : 'Κ',
         '&lambda;' : 'λ',
         '&Lambda;' : 'Λ',
         '&laquo;' : '«',
         '&laquo' : '«',
         '&larr;' : '←',
         '&lArr;' : '⇐',
         '&lceil;' : '⌈',
         '&ldquo;' : '“',
         '&le;' : '≤',
         '&lfloor;' : '⌊',
         '&lowast;' : '∗',
         '&loz;' : '◊',
         '&lrm;' : '‎',
         '&lsaquo;' : '‹',
         '&lsquo;' : '‘',
         #'&lt;' : '<',
         #'&LT;' : '<',
         #'&LT' : '<',
         #'&lt' : '<',
         '&macr;' : '¯',
         '&macr' : '¯',
         '&mdash;' : '—',
         '&micro;' : 'µ',
         '&micro' : 'µ',
         '&middot;' : '·',
         '&middot' : '·',
         '&minus;' : '−',
         '&mu;' : 'μ',
         '&Mu;' : 'Μ',
         '&nabla;' : '∇',
         '&nbsp;' : ' ',
         '&nbsp' : ' ',
         '&ndash;' : '–',
         '&ne;' : '≠',
         '&ni;' : '∋',
         '&not;' : '¬',
         '&not' : '¬',
         '&notin;' : '∉',
         '&nsub;' : '⊄',
         '&ntilde;' : 'ñ',
         '&Ntilde;' : 'Ñ',
         '&Ntilde' : 'Ñ',
         '&ntilde' : 'ñ',
         '&nu;' : 'ν',
         '&Nu;' : 'Ν',
         '&oacute;' : 'ó',
         '&Oacute;' : 'Ó',
         '&Oacute' : 'Ó',
         '&oacute' : 'ó',
         '&ocirc;' : 'ô',
         '&Ocirc;' : 'Ô',
         '&Ocirc' : 'Ô',
         '&ocirc' : 'ô',
         '&OElig;' : 'Œ',
         '&oelig;' : 'œ',
         '&ograve;' : 'ò',
         '&Ograve;' : 'Ò',
         '&Ograve' : 'Ò',
         '&ograve' : 'ò',
         '&oline;' : '‾',
         '&omega;' : 'ω',
         '&Omega;' : 'Ω',
         '&omicron;' : 'ο',
         '&Omicron;' : 'Ο',
         '&oplus;' : '⊕',
         '&or;' : '∨',
         '&ordf;' : 'ª',
         '&ordf' : 'ª',
         '&ordm;' : 'º',
         '&ordm' : 'º',
         '&oslash;' : 'ø',
         '&Oslash;' : 'Ø',
         '&Oslash' : 'Ø',
         '&oslash' : 'ø',
         '&otilde;' : 'õ',
         '&Otilde;' : 'Õ',
         '&Otilde' : 'Õ',
         '&otilde' : 'õ',
         '&otimes;' : '⊗',
         '&ouml;' : 'ö',
         '&Ouml;' : 'Ö',
         '&Ouml' : 'Ö',
         '&ouml' : 'ö',
         '&para;' : '¶',
         '&para' : '¶',
         '&part;' : '∂',
         '&permil;' : '‰',
         '&perp;' : '⊥',
         '&phi;' : 'φ',
         '&Phi;' : 'Φ',
         '&pi;' : 'π',
         '&Pi;' : 'Π',
         '&piv;' : 'ϖ',
         '&plusmn;' : '±',
         '&plusmn' : '±',
         '&pound;' : '£',
         '&pound' : '£',
         '&prime;' : '′',
         '&Prime;' : '″',
         '&prod;' : '∏',
         '&prop;' : '∝',
         '&psi;' : 'ψ',
         '&Psi;' : 'Ψ',
         '&quot;' : '"',
         '&QUOT;' : '"',
         '&QUOT' : '"',
         '&quot' : '"',
         '&radic;' : '√',
         '&raquo;' : '»',
         '&raquo' : '»',
         '&rarr;' : '→',
         '&rArr;' : '⇒',
         '&rceil;' : '⌉',
         '&rdquo;' : '”',
         '&real;' : 'ℜ',
         '&reg;' : '®',
         '&REG;' : '®',
         '&REG' : '®',
         '&reg' : '®',
         '&rfloor;' : '⌋',
         '&rho;' : 'ρ',
         '&Rho;' : 'Ρ',
         '&rlm;' : '‏',
         '&rsaquo;' : '›',
         '&rsquo;' : '’',
         '&sbquo;' : '‚',
         '&scaron;' : 'š',
         '&Scaron;' : 'Š',
         '&sdot;' : '⋅',
         '&sect;' : '§',
         '&sect' : '§',
         '&shy;' : '­', # strange optional hyphenation control character, not just a dash
         '&shy' : '­',
         '&sigma;' : 'σ',
         '&Sigma;' : 'Σ',
         '&sigmaf;' : 'ς',
         '&sim;' : '∼',
         '&spades;' : '♠',
         '&sub;' : '⊂',
         '&sube;' : '⊆',
         '&sum;' : '∑',
         '&sup1;' : '¹',
         '&sup1' : '¹',
         '&sup2;' : '²',
         '&sup2' : '²',
         '&sup3;' : '³',
         '&sup3' : '³',
         '&sup;' : '⊃',
         '&supe;' : '⊇',
         '&szlig;' : 'ß',
         '&szlig' : 'ß',
         '&tau;' : 'τ',
         '&Tau;' : 'Τ',
         '&there4;' : '∴',
         '&theta;' : 'θ',
         '&Theta;' : 'Θ',
         '&thetasym;' : 'ϑ',
         '&thinsp;' : ' ',
         '&thorn;' : 'þ',
         '&THORN;' : 'Þ',
         '&THORN' : 'Þ',
         '&thorn' : 'þ',
         '&tilde;' : '˜',
         '&times;' : '×',
         '&times' : '×',
         '&trade;' : '™',
         '&uacute;' : 'ú',
         '&Uacute;' : 'Ú',
         '&Uacute' : 'Ú',
         '&uacute' : 'ú',
         '&uarr;' : '↑',
         '&uArr;' : '⇑',
         '&ucirc;' : 'û',
         '&Ucirc;' : 'Û',
         '&Ucirc' : 'Û',
         '&ucirc' : 'û',
         '&ugrave;' : 'ù',
         '&Ugrave;' : 'Ù',
         '&Ugrave' : 'Ù',
         '&ugrave' : 'ù',
         '&uml;' : '¨',
         '&uml' : '¨',
         '&upsih;' : 'ϒ',
         '&upsilon;' : 'υ',
         '&Upsilon;' : 'Υ',
         '&uuml;' : 'ü',
         '&Uuml;' : 'Ü',
         '&Uuml' : 'Ü',
         '&uuml' : 'ü',
         '&weierp;' : '℘',
         '&xi;' : 'ξ',
         '&Xi;' : 'Ξ',
         '&yacute;' : 'ý',
         '&Yacute;' : 'Ý',
         '&Yacute' : 'Ý',
         '&yacute' : 'ý',
         '&yen;' : '¥',
         '&yen' : '¥',
         '&yuml;' : 'ÿ',
         '&Yuml;' : 'Ÿ',
         '&yuml' : 'ÿ',
         '&zeta;' : 'ζ',
         '&Zeta;' : 'Ζ',
         '&zwj;' : '‍',  # strange spacing control character, not just a space
         '&zwnj;' : '‌',  # strange spacing control character, not just a space
         }

class SplitEpub:

    def __init__(self, inputio):
        self.epub = ZipFile(inputio, 'r')
        self.content_dom = None
        self.content_relpath = None
        self.manifest_items = None
        self.guide_items = None
        self.toc_dom = None
        self.toc_map = None
        self.split_lines = None
        self.origauthors = []
        self.origtitle = None

    def get_file(self,href):
        return self.epub.read(href)

    def get_content_dom(self):
        if not self.content_dom:
            ## Find the .opf file.
            container = self.epub.read("META-INF/container.xml")
            containerdom = parseString(container)
            rootfilenodelist = containerdom.getElementsByTagName("rootfile")
            rootfilename = rootfilenodelist[0].getAttribute("full-path")

            self.content_dom = parseString(self.epub.read(rootfilename))
            self.content_relpath = get_path_part(rootfilename)
        return self.content_dom

    def get_content_relpath(self):
        ## Save the path to the .opf file--hrefs inside it are relative to it.
        if not self.content_relpath:
            self.get_content_dom() # sets self.content_relpath also.
        return self.content_relpath

    def get_manifest_items(self):
        if not self.manifest_items:
            self.manifest_items = {}

            for item in self.get_content_dom().getElementsByTagName("item"):
                fullhref=normpath(unquote(self.get_content_relpath()+item.getAttribute("href")))
                #print("---- item fullhref:%s"%(fullhref))
                self.manifest_items["h:"+fullhref]=(item.getAttribute("id"),item.getAttribute("media-type"))
                self.manifest_items["i:"+item.getAttribute("id")]=(fullhref,item.getAttribute("media-type"))

                if( item.getAttribute("media-type") == "application/x-dtbncx+xml" ):
                    # TOC file is only one with this type--as far as I know.
                    self.toc_dom = parseString(self.epub.read(fullhref))

        return self.manifest_items

    def get_guide_items(self):
        if not self.guide_items:
            self.guide_items = {}

            for item in self.get_content_dom().getElementsByTagName("reference"):
                fullhref=normpath(unquote(self.get_content_relpath()+item.getAttribute("href")))
                self.guide_items[fullhref]=(item.getAttribute("type"),item.getAttribute("title"))
                #print("---- reference href:%s value:%s"%(fullhref,self.guide_items[fullhref],))
                #self.guide_items[item.getAttribute("type")]=(fullhref,item.getAttribute("media-type"))

        return self.guide_items

    def get_toc_dom(self):
        if not self.toc_dom:
            self.get_manifest_items() # also sets self.toc_dom
        return self.toc_dom

    # dict() of href->[(text,anchor),...],...
    # eg: "file0001.html"->[("Introduction","anchor01"),("Chapter 1","anchor02")],...
    def get_toc_map(self):
        if not self.toc_map:
            self.toc_map = {}
            # update all navpoint ids with bookid for uniqueness.
            for navpoint in self.get_toc_dom().getElementsByTagName("navPoint"):
                src = normpath(unquote(self.get_content_relpath()+navpoint.getElementsByTagName("content")[0].getAttribute("src")))
                if '#' in src:
                    (href,anchor)=src.split("#")
                else:
                    (href,anchor)=(src,None)

                # The first of these in each navPoint should be the appropriate one.
                # (may be others due to nesting.
                try:
                    text = unicode(navpoint.getElementsByTagName("text")[0].firstChild.data)
                except:
                    #print("No chapter title found in TOC for (%s)"%src)
                    text = ""

                if href not in self.toc_map:
                    self.toc_map[href] = []
                if anchor == None:
                    # put file links ahead of ancher links.  Otherwise
                    # a non-linear anchor link may take precedence,
                    # which will confuse EpubSplit.  This will cause
                    # split lines to possibly be out of order from
                    # TOC, but the alternative is worse.  Should be a
                    # rare corner case.
                    self.toc_map[href].insert(0,(text,anchor))
                else:
                    self.toc_map[href].append((text,anchor))

        return self.toc_map

    # list of dicts with href, anchor & toc text.
    # 'split lines' are all the points that the epub can be split on.
    # Offer a split at each spine file and each ToC point.
    def get_split_lines(self):

        metadom = self.get_content_dom()
        ## Save indiv book title
        try:
            self.origtitle = metadom.getElementsByTagName("dc:title")[0].firstChild.data
        except:
            self.origtitle = "(Title Missing)"

        ## Save authors.
        for creator in metadom.getElementsByTagName("dc:creator"):
            try:
                if( creator.getAttribute("opf:role") == "aut" or not creator.hasAttribute("opf:role") and creator.firstChild != None):
                    if creator.firstChild.data not in self.origauthors:
                        self.origauthors.append(creator.firstChild.data)
            except:
                pass
        if len(self.origauthors) == 0:
            self.origauthors.append("(Authors Missing)")

        self.split_lines = [] # list of dicts with href, anchor and toc
        # spin on spine files.
        count=0
        for itemref in metadom.getElementsByTagName("itemref"):
            idref = itemref.getAttribute("idref")
            (href,type) = self.get_manifest_items()["i:"+idref]
            current = {}
            self.split_lines.append(current)
            current['href']=href
            current['anchor']=None
            current['toc'] = []
            if href in self.get_guide_items():
                current['guide'] = self.get_guide_items()[href]
            current['id'] = idref
            current['type'] = type
            current['num'] = count
            t=self.epub.read(href).decode('utf-8')
            if len(t) > 1500 : t = t[:1500] + "..."
            current['sample']=t
            count += 1
            #print("spine:%s->%s"%(idref,href))

            # if href is in the toc.
            if href in self.get_toc_map():
                # For each toc entry, check to see if there's an anchor, if so,
                # make a new split line.
                for tocitem in self.get_toc_map()[href]:
                    (text,anchor) = tocitem
                    # XXX for outputing to screen in CLI--hopefully won't need in plugin?
                    try:
                        text = "%s"%text
                    except:
                        text = "(error text)"

                    if anchor:
                        #print("breakpoint: %d"%count)
                        current = {}
                        self.split_lines.append(current)
                        current['href']=href
                        current['anchor']=anchor
                        current['toc']=[]
                        current['id'] = idref
                        current['type'] = type
                        current['num'] = count
                        # anchor, need to split first, then reduce to 1500.
                        t=splitHtml(self.epub.read(href).decode('utf-8'),anchor,before=False)
                        if len(t) > 1500 : t = t[:1500] + "..."
                        current['sample']=t
                        count += 1
                    # There can be more than one toc to the same split line.
                    # This won't find multiple toc to the same anchor yet.
                    current['toc'].append(text)
                    #print("\ttoc:'%s' %s#%s"%(text,href,anchor))
        return self.split_lines

    # pass in list of line numbers(?)
    def get_split_files(self,linenums):

        self.filecache = FileCache(self.get_manifest_items())

        # set include flag in split_lines.
        if not self.split_lines:
            self.get_split_lines()
        lines = self.split_lines

        lines_set = set([int(k) for k in linenums])
        for j in range(len(lines)):
            lines[j]['include'] = j in lines_set

        # loop through finding 'chunks' -- contiguous pieces in the
        # same file.  Each included file is at least one chunk, but if
        # parts are left out, one original file can end up being more
        # than one chunk.
        outchunks = [] # list of tuples=(filename,start,end) 'end' is not inclusive.
        inchunk = False
        currentfile = None
        start = None
        for line in lines:
            if line['include']:
                if not inchunk: # start new chunk
                    inchunk = True
                    currentfile = line['href']
                    start = line
                else: # inchunk
                    # different file, new chunk.
                    if currentfile != line['href']:
                        outchunks.append((currentfile,start,line))
                        inchunk=True
                        currentfile=line['href']
                        start=line
            else: # not include
                if inchunk: # save previous chunk.
                    outchunks.append((currentfile,start,line))
                    inchunk=False

        # final chunk for when last in list is include.
        if inchunk:
            outchunks.append((currentfile,start,None))

        outfiles=[]  # tuples, (filename,type,data) -- filename changed to unique
        for (href,start,end) in outchunks:
            filedata = self.epub.read(href).decode('utf-8')

            # discard before start if anchor.
            if start['anchor'] != None:
                filedata = splitHtml(filedata,start['anchor'],before=False)

            # discard from end anchor on(inclusive), but only if same file.  If
            # different file, keep rest of file.  If no 'end', then it was the
            # last chunk and went to the end of the last file.
            if end != None and end['anchor'] != None and end['href']==href:
                filedata = splitHtml(filedata,end['anchor'],before=True)

            filename = self.filecache.add_content_file(href,filedata)
            outfiles.append([filename,start['id'],start['type'],filedata])

        # print("self.oldnew:%s"%self.filecache.oldnew)
        # print("self.newold:%s"%self.filecache.newold)
        # print("\nanchors:%s\n"%self.filecache.anchors)
        # print("\nlinkedfiles:%s\n"%self.filecache.linkedfiles)
        # print("relpath:%s"%get_path_part())

        # Spin through to replace internal URLs
        for fl in outfiles:
            #print("file:%s"%fl[0])
            soup = BeautifulSoup(fl[3],'html5lib')
            changed = False
            for a in soup.findAll('a'):
                if a.has_attr('href'):
                    path = normpath(unquote("%s%s"%(get_path_part(fl[0]),a['href'])))
                    #print("full a['href']:%s"%path)
                    if path in self.filecache.anchors and self.filecache.anchors[path] != path:
                        a['href'] = self.filecache.anchors[path][len(get_path_part(fl[0])):]
                        #print("replacement path:%s"%a['href'])
                        changed = True
            if changed:
                fl[3] = unicode(soup)

        return outfiles

    def write_split_epub(self,
                         outputio,
                         linenums,
                         changedtocs={},
                         authoropts=[],
                         titleopt=None,
                         descopt=None,
                         tags=[],
                         languages=['en'],
                         coverjpgpath=None):

        files = self.get_split_files(linenums)

        ## Write mimetype file, must be first and uncompressed.
        ## Older versions of python(2.4/5) don't allow you to specify
        ## compression by individual file.
        ## Overwrite if existing output file.
        outputepub = ZipFile(outputio, "w", compression=ZIP_STORED)
        outputepub.debug = 3
        outputepub.writestr("mimetype", "application/epub+zip")
        outputepub.close()

        ## Re-open file for content.
        outputepub = ZipFile(outputio, "a", compression=ZIP_DEFLATED)
        outputepub.debug = 3

        ## Create META-INF/container.xml file.  The only thing it does is
        ## point to content.opf
        containerdom = getDOMImplementation().createDocument(None, "container", None)
        containertop = containerdom.documentElement
        containertop.setAttribute("version","1.0")
        containertop.setAttribute("xmlns","urn:oasis:names:tc:opendocument:xmlns:container")
        rootfiles = containerdom.createElement("rootfiles")
        containertop.appendChild(rootfiles)
        rootfiles.appendChild(newTag(containerdom,"rootfile",{"full-path":"content.opf",
                                                              "media-type":"application/oebps-package+xml"}))
        outputepub.writestr("META-INF/container.xml",containerdom.toprettyxml(indent='   ',encoding='utf-8'))


####    ## create content.opf file.
        uniqueid="epubsplit-uid-%d" % time() # real sophisticated uid scheme.
        contentdom = getDOMImplementation().createDocument(None, "package", None)
        package = contentdom.documentElement

        package.setAttribute("version","2.0")
        package.setAttribute("xmlns","http://www.idpf.org/2007/opf")
        package.setAttribute("unique-identifier","epubsplit-id")
        metadata=newTag(contentdom,"metadata",
                        attrs={"xmlns:dc":"http://purl.org/dc/elements/1.1/",
                               "xmlns:opf":"http://www.idpf.org/2007/opf"})
        metadata.appendChild(newTag(contentdom,"dc:identifier",text=uniqueid,attrs={"id":"epubsplit-id"}))
        if( titleopt is None ):
            titleopt = self.origtitle+" Split"
        metadata.appendChild(newTag(contentdom,"dc:title",text=titleopt))

        if( authoropts and len(authoropts) > 0  ):
            useauthors=authoropts
        else:
            useauthors=self.origauthors

        usedauthors=dict()
        for author in useauthors:
            if( author not in usedauthors ):
                usedauthors[author]=author
                metadata.appendChild(newTag(contentdom,"dc:creator",
                                            attrs={"opf:role":"aut"},
                                            text=author))

        metadata.appendChild(newTag(contentdom,"dc:contributor",text="epubsplit",attrs={"opf:role":"bkp"}))
        metadata.appendChild(newTag(contentdom,"dc:rights",text="Copyrights as per source stories"))

        if languages:
            for l in languages:
                metadata.appendChild(newTag(contentdom,"dc:language",text=l))
        else:
            metadata.appendChild(newTag(contentdom,"dc:language",text="en"))

        if not descopt:
            # created now, but not filled in until TOC generation to save loops.
            description = newTag(contentdom,"dc:description",text="Split from %s by %s."%(self.origtitle,", ".join(self.origauthors)))
        else:
            description = newTag(contentdom,"dc:description",text=descopt)
        metadata.appendChild(description)

        for tag in tags:
            metadata.appendChild(newTag(contentdom,"dc:subject",text=tag))

        package.appendChild(metadata)

        manifest = contentdom.createElement("manifest")
        package.appendChild(manifest)
        spine = newTag(contentdom,"spine",attrs={"toc":"ncx"})
        package.appendChild(spine)

        manifest.appendChild(newTag(contentdom,"item",
                                    attrs={'id':'ncx',
                                           'href':'toc.ncx',
                                           'media-type':'application/x-dtbncx+xml'}))

        if coverjpgpath:
            # <meta name="cover" content="cover.jpg"/>
            metadata.appendChild(newTag(contentdom,"meta",{"name":"cover",
                                                           "content":"coverimageid"}))
            # cover stuff for later:
            # at end of <package>:
            # <guide>
            # <reference type="cover" title="Cover" href="Text/cover.xhtml"/>
            # </guide>
            guide = newTag(contentdom,"guide")
            guide.appendChild(newTag(contentdom,"reference",attrs={"type":"cover",
                                                       "title":"Cover",
                                                       "href":"cover.xhtml"}))
            package.appendChild(guide)

            manifest.appendChild(newTag(contentdom,"item",
                                        attrs={'id':"coverimageid",
                                               'href':"cover.jpg",
                                               'media-type':"image/jpeg"}))

            # Note that the id of the cover xhmtl *must* be 'cover'
            # for it to work on Nook.
            manifest.appendChild(newTag(contentdom,"item",
                                        attrs={'id':"cover",
                                               'href':"cover.xhtml",
                                               'media-type':"application/xhtml+xml"}))

            spine.appendChild(newTag(contentdom,"itemref",
                                     attrs={"idref":"cover",
                                            "linear":"yes"}))

        contentcount=0
        for (filename,id,type,filedata) in files:
            #filename = self.filecache.addHtml(href,filedata)
            #print("writing :%s"%filename)
            # add to manifest and spine

            if coverjpgpath and filename == "cover.xhtml":
                continue # don't dup cover.

            outputepub.writestr(filename,filedata.encode('utf-8'))
            id = "a%d"%contentcount
            contentcount += 1
            manifest.appendChild(newTag(contentdom,"item",
                                        attrs={'id':id,
                                               'href':filename,
                                               'media-type':type}))
            spine.appendChild(newTag(contentdom,"itemref",
                                     attrs={"idref":id,
                                            "linear":"yes"}))

        fontdecrypter = FontDecrypter(self.epub,self.get_content_dom())
        linked=''
        for (linked,type) in self.filecache.linkedfiles:
            # print("linked files:(%s,%s)"%(linked,type))
            # add to manifest
            if coverjpgpath and linked == "cover.jpg":
                continue # don't dup cover.

            try:
                linkeddata = self.get_file(linked)
                if linked in fontdecrypter.get_encrypted_fontfiles():
                    print("Decrypting font file: %s"%linked)
                    linkeddata = fontdecrypter.get_decrypted_font_data(linked)
                outputepub.writestr(linked,linkeddata)

            except Exception as e:
                print("Skipping linked file (%s)\nException: %s"%(linked,e))

            id = "a%d"%contentcount
            contentcount += 1
            manifest.appendChild(newTag(contentdom,"item",
                                        attrs={'id':id,
                                               'href':linked,
                                               'media-type':type}))

        contentxml = contentdom.toprettyxml(indent='   ') # ,encoding='utf-8'
        # tweak for brain damaged Nook STR.  Nook insists on name before content.
        contentxml = contentxml.replace('<meta content="coverimageid" name="cover"/>',
                                        '<meta name="cover" content="coverimageid"/>')
        outputepub.writestr("content.opf",contentxml)

        ## create toc.ncx file
        tocncxdom = getDOMImplementation().createDocument(None, "ncx", None)
        ncx = tocncxdom.documentElement
        ncx.setAttribute("version","2005-1")
        ncx.setAttribute("xmlns","http://www.daisy.org/z3986/2005/ncx/")
        head = tocncxdom.createElement("head")
        ncx.appendChild(head)
        head.appendChild(newTag(tocncxdom,"meta",
                                attrs={"name":"dtb:uid", "content":uniqueid}))
        depthnode = newTag(tocncxdom,"meta",
                                attrs={"name":"dtb:depth", "content":"1"})
        head.appendChild(depthnode)
        head.appendChild(newTag(tocncxdom,"meta",
                                attrs={"name":"dtb:totalPageCount", "content":"0"}))
        head.appendChild(newTag(tocncxdom,"meta",
                                attrs={"name":"dtb:maxPageNumber", "content":"0"}))

        docTitle = tocncxdom.createElement("docTitle")
        docTitle.appendChild(newTag(tocncxdom,"text",text=stripHTML(titleopt)))
        ncx.appendChild(docTitle)

        tocnavMap = tocncxdom.createElement("navMap")
        ncx.appendChild(tocnavMap)

        # come back to lines again for TOC because files only has files(gasp-shock!)
        count=1
        for line in self.split_lines:
            if line['include']:
                # if changed, use only changed values.
                if line['num'] in changedtocs:
                    line['toc'] = changedtocs[line['num']]
                # can have more than one toc entry.
                for title in line['toc']:
                    newnav = newTag(tocncxdom,"navPoint",
                                    {"id":"a%03d"%count,"playOrder":"%d" % count})
                    count += 1
                    tocnavMap.appendChild(newnav)
                    navlabel = newTag(tocncxdom,"navLabel")
                    newnav.appendChild(navlabel)
                    # For purposes of TOC titling & desc, use first book author
                    navlabel.appendChild(newTag(tocncxdom,"text",text=stripHTML(title)))
                    # Find the first 'spine' item's content for the title navpoint.
                    # Many epubs have the first chapter as first navpoint, so we can't just
                    # copy that anymore.
                    if line['anchor'] and line['href']+"#"+line['anchor'] in self.filecache.anchors:
                        src = self.filecache.anchors[line['href']+"#"+line['anchor']]
                        #print("toc from anchors(%s#%s)(%s)"%(line['href'],line['anchor'],src))
                    else:
                        #print("toc from href(%s)"%line['href'])
                        src = line['href']
                    newnav.appendChild(newTag(tocncxdom,"content",
                                              {"src":src}))

        outputepub.writestr("toc.ncx",tocncxdom.toprettyxml(indent='   ',encoding='utf-8'))

        if coverjpgpath:
            # write, not write string.  Pulling from file.
            outputepub.write(coverjpgpath,"cover.jpg")

            outputepub.writestr("cover.xhtml",'''
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"><head><title>Cover</title><style type="text/css" title="override_css">
@page {padding: 0pt; margin:0pt}
body { text-align: center; padding:0pt; margin: 0pt; }
div { margin: 0pt; padding: 0pt; }
</style></head><body><div>
<img src="cover.jpg" alt="cover"/>
</div></body></html>
''')

	# declares all the files created by Windows.  otherwise, when
        # it runs in appengine, windows unzips the files as 000 perms.
        for zf in outputepub.filelist:
            zf.create_system = 0
        outputepub.close()

class FileCache:

    def __init__(self,manifest_items={}):
        self.manifest_items = manifest_items
        self.oldnew = {}
        self.newold = {}
        self.anchors = {}
        self.linkedfiles = set()

        ## always include font files for embedded fonts
        for key, value in six.iteritems(self.manifest_items):
            # print("manifest:%s %s"%(key,value))
            if key.startswith('i:') and value[1] in ('application/vnd.ms-opentype',
                                                     'application/x-font-ttf',
                                                     'application/x-font-truetype',
                                                     'application/font-sfnt'):
                self.add_linked_file(value[0])

    def add_linked_file(self, href):
        href = normpath(unquote(href)) # fix %20 & /../
        if ("h:"+href) in self.manifest_items:
            type = self.manifest_items["h:"+href][1]
        else:
            type = 'unknown'
        self.linkedfiles.add((href,type))

    def add_content_file(self, href, filedata):

        changedname = False
        if href not in self.oldnew:
            self.oldnew[href]=[]
            newfile = href
        else:
            changedname = True
            newfile = "%s%d-%s"%(get_path_part(href),
                                 len(self.oldnew[href]),
                                 get_file_part(href))

        self.oldnew[href].append(newfile)
        self.newold[newfile]=href
        #print("newfile:%s"%newfile)

        soup = BeautifulSoup(filedata,'html5lib')
        #print("soup head:%s"%soup.find('head'))

        # same name?  Don't need to worry about changing links to anchors
        for a in soup.findAll(): # not just 'a', any tag.
            #print("a:%s"%a)
            if a.has_attr('id'):
                self.anchors[href+'#'+a['id']]=newfile+'#'+a['id']

        for img in soup.findAll('img'):
            if img.has_attr('src'):
                src=img['src']
            if img.has_attr('xlink:href'):
                src=img['xlink:href']
            self.add_linked_file(get_path_part(href)+src)

        # from baen epub.
        # <image width="462" height="616" xlink:href="cover.jpeg"/>
        for img in soup.findAll('image'):
            if img.has_attr('src'):
                src=img['src']
            if img.has_attr('xlink:href'):
                src=img['xlink:href']
            self.add_linked_file(get_path_part(href)+src)

        # link href="0.css" type="text/css"
        for style in soup.findAll('link',{'type':'text/css'}):
            #print("link:%s"%style)
            if style.has_attr('href'):
                self.add_linked_file(get_path_part(href)+style['href'])

        return newfile

def splitHtml(data,tagid,before=False):
    soup = BeautifulSoup(data,'html5lib')
    #print("splitHtml.soup head:%s"%soup.find('head'))

    splitpoint = soup.find(id=tagid)

    #print("splitpoint:%s"%splitpoint)

    if splitpoint == None:
        return data

    if before:
        # remove all next siblings.
        for n in splitpoint.findNextSiblings():
            n.extract()

        parent = splitpoint.parent
        while parent and parent.name != 'body':
            for n in parent.findNextSiblings():
                n.extract()
            parent = parent.parent

        splitpoint.extract()
    else:
        # remove all prev siblings.
        for n in splitpoint.findPreviousSiblings():
            n.extract()

        parent = splitpoint.parent
        while parent and parent.name != 'body':
            for n in parent.findPreviousSiblings():
                n.extract()
            parent = parent.parent

    return re.sub(r'( *\r?\n)+','\r\n',unicode(soup))

def get_path_part(n):
    relpath = os.path.dirname(n)
    if( len(relpath) > 0 ):
        relpath=relpath+"/"
    return relpath

def get_file_part(n):
    return os.path.basename(n)

## Utility method for creating new tags.
def newTag(dom,name,attrs=None,text=None):
    tag = dom.createElement(name)
    if( attrs is not None ):
        for attr in attrs.keys():
            tag.setAttribute(attr,attrs[attr])
    if( text is not None ):
        tag.appendChild(dom.createTextNode(text))
    return tag

def main(argv,usage=None):

    from optparse import OptionParser

    if not usage:
        # read in args, anything starting with -- will be treated as --<varible>=<value>
        usage = 'usage: python %prog'

    parser = OptionParser(usage+''' [options] <input epub> [line numbers...]

Giving an epub without line numbers will return a list of line numbers: the
possible split points in the input file. Calling with line numbers will
generate an epub with each of the "lines" given included.''')

    parser.add_option("-o", "--output", dest="outputopt", default="split.epub",
                      help="Set OUTPUT file, Default: split.epub", metavar="OUTPUT")
    parser.add_option("--output-dir", dest="outputdiropt",
                      help="Set OUTPUT directory, Default: presend working directory")
    parser.add_option('--split-by-section',
                      action='store_true', dest='split_by_section',
                      help='Create a new epub from each of the listed line sections instead of one containing all.  Splits all sections if no lines numbers are given. Each split will be named <number>-<output name> and placed in the output-dir.  Sections without a Table of Contents entry will be included with the preceding section(s)', )
    parser.add_option("-t", "--title", dest="titleopt", default=None,
                      help="Use TITLE as the metadata title.  Default: '<original epub title> Split' or ToC entry with --split-by-section", metavar="TITLE")
    parser.add_option("-d", "--description", dest="descopt", default=None,
                      help="Use DESC as the metadata description.  Default: 'Split from <epub title> by <author>'.", metavar="DESC")
    parser.add_option("-a", "--author",
                      action="append", dest="authoropts", default=[],
                      help="Use AUTHOR as a metadata author, multiple authors may be given, Default: <All authors from original epub>", metavar="AUTHOR")
    parser.add_option("-g", "--tag",
                      action="append", dest="tagopts", default=[],
                      help="Include TAG as dc:subject tag, multiple tags may be given, Default: None", metavar="TAG")
    parser.add_option("-l", "--language",
                      action="append", dest="languageopts", default=[],
                      help="Include LANG as dc:language tag, multiple languages may be given, Default: en", metavar="LANG")
    parser.add_option("-c", "--cover", dest="coveropt", default=None,
                      help="Path to a jpg to use as cover image.", metavar="COVER")

    (options, args) = parser.parse_args(argv)

    ## Add .epub if not already there.
    if not options.outputopt.lower().endswith(".epub"):
        options.outputopt=options.outputopt+".epub"

    if not options.languageopts:
        options.languageopts = ['en']

    if not args:
        parser.print_help()
        return

    epubO = SplitEpub(args[0])

    lines = epubO.get_split_lines()

    if options.split_by_section:
        if len(args) > 1:
            section_lines = args[1:]
        else:
            section_lines = range(len(lines))

        splitslist = []
        sectionlist = []
        title=None
        for lineno in section_lines:
            toclist = lines[int(lineno)]['toc']
            if sectionlist and not toclist:
                sectionlist.append(lineno)
            else:
                ## take title from (first) ToC if available, else titleopt (_ Split internally if None)
                title = (toclist[0] if toclist else options.titleopt)
                print("title: %s"%title)
                sectionlist=[lineno]
                splitslist.append((sectionlist,title))
        if sectionlist:
            splitslist.append((sectionlist,title))
        # print(splitslist)

        filecount = 1
        for sectionlist, title in splitslist:
            if title is None:
                filename = f"{filecount:04d}-none.epub"
            else:
                safe_title = sanitize_filename(title)
                filename = f"{filecount:04d}-{safe_title}.epub"
            
            if options.outputdiropt:
                # Ensure the output directory exists
                os.makedirs(options.outputdiropt, exist_ok=True)
                outputfile = os.path.join(options.outputdiropt, filename)
            else:
                outputfile = filename
            
            print("output file: " + outputfile)
            epubO.write_split_epub(outputfile, sectionlist, authoropts=options.authoropts, 
                                titleopt=title, descopt=options.descopt, 
                                tags=options.tagopts, languages=options.languageopts, 
                                coverjpgpath=options.coveropt)
            filecount+=1
        return
    elif len(args) == 1:
        count = 0
        showlist=['toc','guide','anchor','id','href']
        for line in lines:
            print("\nLine Number: %d"%count)
            for s in showlist:
                if s in line and line[s]:
                    print("\t%s: %s"%(s,line[s]))
            count += 1
        return

    if len(args) > 1:
        outputfile = options.outputopt
        if options.outputdiropt:
            outputfile = os.path.join(options.outputdiropt,outputfile)
        print("output file: "+outputfile)
        epubO.write_split_epub(outputfile,
                               args[1:],
                               authoropts=options.authoropts,
                               titleopt=options.titleopt,
                               descopt=options.descopt,
                               tags=options.tagopts,
                               languages=options.languageopts,
                               coverjpgpath=options.coveropt)

        return

if __name__ == "__main__":
    main(sys.argv[1:])


# encoding= utf-8
from __future__ import division, absolute_import, with_statement, print_function
import requests


def download_file(url, file_path, params=None, proxies=None, request_session=None, cookies=None):
    """
    proxies = {
      "http": "http://10.10.1.10:3128",
      "https": "http://10.10.1.10:1080",
    }
    """
    if not request_session:
        request_session = requests.session()
    r = request_session.get(url, params=params, stream=True, proxies=proxies, cookies=cookies)
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(1024):
            if chunk:
                f.write(chunk)
                f.flush()


def cidr2netmask(cidr):
    if cidr < 0 or cidr > 32:
        raise ValueError('CIDR should be in range [0, 32].')
    bin_ip = '1' * cidr + '0' * (32 - cidr)
    return bin2ip(bin_ip)


def netmask2cidr(netmask):
    mask_arr = netmask.split('.')
    return len(''.join(list(map(lambda part: bin(int(part))[2:].zfill(8), mask_arr))).rstrip('0'))


def ip2bin(ip):
        return ''.join(list(map(lambda part: bin(int(part))[2:].zfill(8), ip.split('.'))))


def bin2ip(bin_ip):
    segment = [bin_ip[i: i + 8] for i in range(0, 32, 8)]
    return '.'.join(str(int(s, 2)) for s in segment)


def get_content_type_by_ext(ext, df='application/octet-stream'):
    m = {
        ".123": "application/vnd.lotus-1-2-3",  # Lotus 1-2-3
        ".3dml": "text/vnd.in3d.3dml",  # In3D - 3DML
        ".3g2": "video/3gpp2",  # 3GP2
        ".3gp": "video/3gpp",  # 3GP
        ".7z": "application/x-7z-compressed",  # 7-Zip
        ".aab": "application/x-authorware-bin",  # Adobe (Macropedia) Authorware - Binary File
        ".aac": "audio/x-aac",  # Advanced Audio Coding (AAC)
        ".aam": "application/x-authorware-map",  # Adobe (Macropedia) Authorware - Map
        ".aas": "application/x-authorware-seg",  # Adobe (Macropedia) Authorware - Segment File
        ".abw": "application/x-abiword",  # AbiWord
        ".ac": "application/pkix-attr-cert",  # Attribute Certificate
        ".acc": "application/vnd.americandynamics.acc",  # Active Content Compression
        ".ace": "application/x-ace-compressed",  # Ace Archive
        ".acu": "application/vnd.acucobol",  # ACU Cobol
        ".adp": "audio/adpcm",  # Adaptive differential pulse-code modulation
        ".aep": "application/vnd.audiograph",  # Audiograph
        ".afp": "application/vnd.ibm.modcap",  # MO:DCA-P
        ".ahead": "application/vnd.ahead.space",  # Ahead AIR Application
        ".ai": "application/postscript",  # PostScript
        ".aif": "audio/x-aiff",  # Audio Interchange File Format
        ".air": "application/vnd.adobe.air-application-installer-package+zip",  # Adobe AIR Application
        ".ait": "application/vnd.dvb.ait",  # Digital Video Broadcasting
        ".ami": "application/vnd.amiga.ami",  # AmigaDE
        ".apk": "application/vnd.android.package-archive",  # Android Package Archive
        ".application": "application/x-ms-application",  # Microsoft ClickOnce
        ".apr": "application/vnd.lotus-approach",  # Lotus Approach
        ".asf": "video/x-ms-asf",  # Microsoft Advanced Systems Format (ASF)
        ".aso": "application/vnd.accpac.simply.aso",  # Simply Accounting
        ".atc": "application/vnd.acucorp",  # ACU Cobol
        ".atom": "application/atom+xml",  # Atom Syndication Format
        ".atomcat": "application/atomcat+xml",  # Atom Publishing Protocol
        ".atomsvc": "application/atomsvc+xml",  # Atom Publishing Protocol Service Document
        ".atx": "application/vnd.antix.game-component",  # Antix Game Player
        ".au": "audio/basic",  # Sun Audio - Au file format
        ".avi": "video/x-msvideo",  # Audio Video Interleave (AVI)
        ".aw": "application/applixware",  # Applixware
        ".azf": "application/vnd.airzip.filesecure.azf",  # AirZip FileSECURE
        ".azs": "application/vnd.airzip.filesecure.azs",  # AirZip FileSECURE
        ".azw": "application/vnd.amazon.ebook",  # Amazon Kindle eBook format
        ".bcpio": "application/x-bcpio",  # Binary CPIO Archive
        ".bdf": "application/x-font-bdf",  # Glyph Bitmap Distribution Format
        ".bdm": "application/vnd.syncml.dm+wbxml",  # SyncML - Device Management
        ".bed": "application/vnd.realvnc.bed",  # RealVNC
        ".bh2": "application/vnd.fujitsu.oasysprs",  # Fujitsu Oasys
        ".bin": "application/octet-stream",  # Binary Data
        ".bmi": "application/vnd.bmi",  # BMI Drawing Data Interchange
        ".bmp": "image/bmp",  # Bitmap Image File
        ".box": "application/vnd.previewsystems.box",  # Preview Systems ZipLock/VBox
        ".btif": "image/prs.btif",  # BTIF
        ".bz": "application/x-bzip",  # Bzip Archive
        ".bz2": "application/x-bzip2",  # Bzip2 Archive
        ".c": "text/x-c",  # C Source File
        ".c11amc": "application/vnd.cluetrust.cartomobile-config",  # ClueTrust CartoMobile - Config
        ".c11amz": "application/vnd.cluetrust.cartomobile-config-pkg",  # ClueTrust CartoMobile - Config Package
        ".c4g": "application/vnd.clonk.c4group",  # Clonk Game
        ".cab": "application/vnd.ms-cab-compressed",  # Microsoft Cabinet File
        ".car": "application/vnd.curl.car",  # CURL Applet
        ".cat": "application/vnd.ms-pki.seccat",  # Microsoft Trust UI Provider - Security Catalog
        ".ccxml": "application/ccxml+xml,",  # Voice Browser Call Control
        ".cdbcmsg": "application/vnd.contact.cmsg",  # CIM Database
        ".cdkey": "application/vnd.mediastation.cdkey",  # MediaRemote
        ".cdmia": "application/cdmi-capability",  # Cloud Data Management Interface (CDMI) - Capability
        ".cdmic": "application/cdmi-container",  # Cloud Data Management Interface (CDMI) - Contaimer
        ".cdmid": "application/cdmi-domain",  # Cloud Data Management Interface (CDMI) - Domain
        ".cdmio": "application/cdmi-object",  # Cloud Data Management Interface (CDMI) - Object
        ".cdmiq": "application/cdmi-queue",  # Cloud Data Management Interface (CDMI) - Queue
        ".cdx": "chemical/x-cdx",  # ChemDraw eXchange file
        ".cdxml": "application/vnd.chemdraw+xml",  # CambridgeSoft Chem Draw
        ".cdy": "application/vnd.cinderella",  # Interactive Geometry Software Cinderella
        ".cer": "application/pkix-cert",  # Internet Public Key Infrastructure - Certificate
        ".cgm": "image/cgm",  # Computer Graphics Metafile
        ".chat": "application/x-chat",  # pIRCh
        ".chm": "application/vnd.ms-htmlhelp",  # Microsoft Html Help File
        ".chrt": "application/vnd.kde.kchart",  # KDE KOffice Office Suite - KChart
        ".cif": "chemical/x-cif",  # Crystallographic Interchange Format
        ".cii": "application/vnd.anser-web-certificate-issue-initiation",  # ANSER-WEB Terminal Client - Certificate Issue
        ".cil": "application/vnd.ms-artgalry",  # Microsoft Artgalry
        ".cla": "application/vnd.claymore",  # Claymore Data Files
        ".class": "application/java-vm",  # Java Bytecode File
        ".clkk": "application/vnd.crick.clicker.keyboard",  # CrickSoftware - Clicker - Keyboard
        ".clkp": "application/vnd.crick.clicker.palette",  # CrickSoftware - Clicker - Palette
        ".clkt": "application/vnd.crick.clicker.template",  # CrickSoftware - Clicker - Template
        ".clkw": "application/vnd.crick.clicker.wordbank",  # CrickSoftware - Clicker - Wordbank
        ".clkx": "application/vnd.crick.clicker",  # CrickSoftware - Clicker
        ".clp": "application/x-msclip",  # Microsoft Clipboard Clip
        ".cmc": "application/vnd.cosmocaller",  # CosmoCaller
        ".cmdf": "chemical/x-cmdf",  # CrystalMaker Data Format
        ".cml": "chemical/x-cml",  # Chemical Markup Language
        ".cmp": "application/vnd.yellowriver-custom-menu",  # CustomMenu
        ".cmx": "image/x-cmx",  # Corel Metafile Exchange (CMX)
        ".cod": "application/vnd.rim.cod",  # Blackberry COD File
        ".cpio": "application/x-cpio",  # CPIO Archive
        ".cpt": "application/mac-compactpro",  # Compact Pro
        ".crd": "application/x-mscardfile",  # Microsoft Information Card
        ".crl": "application/pkix-crl",  # Internet Public Key Infrastructure - Certificate Revocation Lists
        ".cryptonote": "application/vnd.rig.cryptonote",  # CryptoNote
        ".csh": "application/x-csh",  # C Shell Script
        ".csml": "chemical/x-csml",  # Chemical Style Markup Language
        ".csp": "application/vnd.commonspace",  # Sixth Floor Media - CommonSpace
        ".css": "text/css",  # Cascading Style Sheets (CSS)
        ".csv": "text/csv",  # Comma-Seperated Values
        ".cu": "application/cu-seeme",  # CU-SeeMe
        ".curl": "text/vnd.curl",  # Curl - Applet
        ".cww": "application/prs.cww",  # CU-Writer
        ".dae": "model/vnd.collada+xml",  # COLLADA
        ".daf": "application/vnd.mobius.daf",  # Mobius Management Systems - UniversalArchive
        ".davmount": "application/davmount+xml",  # Web Distributed Authoring and Versioning
        ".dcurl": "text/vnd.curl.dcurl",  # Curl - Detached Applet
        ".dd2": "application/vnd.oma.dd2+xml",  # OMA Download Agents
        ".ddd": "application/vnd.fujixerox.ddd",  # Fujitsu - Xerox 2D CAD Data
        ".deb": "application/x-debian-package",  # Debian Package
        ".der": "application/x-x509-ca-cert",  # X.509 Certificate
        ".dfac": "application/vnd.dreamfactory",  # DreamFactory
        ".dir": "application/x-director",  # Adobe Shockwave Player
        ".dis": "application/vnd.mobius.dis",  # Mobius Management Systems - Distribution Database
        ".djvu": "image/vnd.djvu",  # DjVu
        ".dna": "application/vnd.dna",  # New Moon Liftoff/DNA
        ".doc": "application/msword",  # Microsoft Word
        ".docm": "application/vnd.ms-word.document.macroenabled.12",  # Micosoft Word - Macro-Enabled Document
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # Microsoft Office - OOXML - Word Document
        ".dotm": "application/vnd.ms-word.template.macroenabled.12",  # Micosoft Word - Macro-Enabled Template
        ".dotx": "application/vnd.openxmlformats-officedocument.wordprocessingml.template",  # Microsoft Office - OOXML - Word Document Template
        ".dp": "application/vnd.osgi.dp",  # OSGi Deployment Package
        ".dpg": "application/vnd.dpgraph",  # DPGraph
        ".dra": "audio/vnd.dra",  # DRA Audio
        ".dsc": "text/prs.lines.tag",  # PRS Lines Tag
        ".dssc": "application/dssc+der",  # Data Structure for the Security Suitability of Cryptographic Algorithms
        ".dtb": "application/x-dtbook+xml",  # Digital Talking Book
        ".dtd": "application/xml-dtd",  # Document Type Definition
        ".dts": "audio/vnd.dts",  # DTS Audio
        ".dtshd": "audio/vnd.dts.hd",  # DTS High Definition Audio
        ".dvi": "application/x-dvi",  # Device Independent File Format (DVI)
        ".dwf": "model/vnd.dwf",  # Autodesk Design Web Format (DWF)
        ".dwg": "image/vnd.dwg",  # DWG Drawing
        ".dxf": "image/vnd.dxf",  # AutoCAD DXF
        ".dxp": "application/vnd.spotfire.dxp",  # TIBCO Spotfire
        ".ecelp4800": "audio/vnd.nuera.ecelp4800",  # Nuera ECELP 4800
        ".ecelp7470": "audio/vnd.nuera.ecelp7470",  # Nuera ECELP 7470
        ".ecelp9600": "audio/vnd.nuera.ecelp9600",  # Nuera ECELP 9600
        ".edm": "application/vnd.novadigm.edm",  # Novadigm's RADIA and EDM products
        ".edx": "application/vnd.novadigm.edx",  # Novadigm's RADIA and EDM products
        ".efif": "application/vnd.picsel",  # Pcsel eFIF File
        ".ei6": "application/vnd.pg.osasli",  # Proprietary P&G Standard Reporting System
        ".eml": "message/rfc822",  # Email Message
        ".emma": "application/emma+xml",  # Extensible MultiModal Annotation
        ".eol": "audio/vnd.digital-winds",  # Digital Winds Music
        ".eot": "application/vnd.ms-fontobject",  # Microsoft Embedded OpenType
        ".epub": "application/epub+zip",  # Electronic Publication
        ".es": "application/ecmascript",  # ECMAScript
        ".es3": "application/vnd.eszigno3+xml",  # MICROSEC e-Szign¢
        ".esf": "application/vnd.epson.esf",  # QUASS Stream Player
        ".etx": "text/x-setext",  # Setext
        ".exe": "application/x-msdownload",  # Microsoft Application
        ".exi": "application/exi",  # Efficient XML Interchange
        ".ext": "application/vnd.novadigm.ext",  # Novadigm's RADIA and EDM products
        ".ez2": "application/vnd.ezpix-album",  # EZPix Secure Photo Album
        ".ez3": "application/vnd.ezpix-package",  # EZPix Secure Photo Album
        ".f": "text/x-fortran",  # Fortran Source File
        ".f4v": "video/x-f4v",  # Flash Video
        ".fbs": "image/vnd.fastbidsheet",  # FastBid Sheet
        ".fcs": "application/vnd.isac.fcs",  # International Society for Advancement of Cytometry
        ".fdf": "application/vnd.fdf",  # Forms Data Format
        ".fe_launch": "application/vnd.denovo.fcselayout-link",  # FCS Express Layout Link
        ".fg5": "application/vnd.fujitsu.oasysgp",  # Fujitsu Oasys
        ".fh": "image/x-freehand",  # FreeHand MX
        ".fig": "application/x-xfig",  # Xfig
        ".fli": "video/x-fli",  # FLI/FLC Animation Format
        ".flo": "application/vnd.micrografx.flo",  # Micrografx
        ".flv": "video/x-flv",  # Flash Video
        ".flw": "application/vnd.kde.kivio",  # KDE KOffice Office Suite - Kivio
        ".flx": "text/vnd.fmi.flexstor",  # FLEXSTOR
        ".fly": "text/vnd.fly",  # mod_fly / fly.cgi
        ".fm": "application/vnd.framemaker",  # FrameMaker Normal Format
        ".fnc": "application/vnd.frogans.fnc",  # Frogans Player
        ".fpx": "image/vnd.fpx",  # FlashPix
        ".fsc": "application/vnd.fsc.weblaunch",  # Friendly Software Corporation
        ".fst": "image/vnd.fst",  # FAST Search & Transfer ASA
        ".ftc": "application/vnd.fluxtime.clip",  # FluxTime Clip
        ".fti": "application/vnd.anser-web-funds-transfer-initiation",  # ANSER-WEB Terminal Client - Web Funds Transfer
        ".fvt": "video/vnd.fvt",  # FAST Search & Transfer ASA
        ".fxp": "application/vnd.adobe.fxp",  # Adobe Flex Project
        ".fzs": "application/vnd.fuzzysheet",  # FuzzySheet
        ".g2w": "application/vnd.geoplan",  # GeoplanW
        ".g3": "image/g3fax",  # G3 Fax Image
        ".g3w": "application/vnd.geospace",  # GeospacW
        ".gac": "application/vnd.groove-account",  # Groove - Account
        ".gdl": "model/vnd.gdl",  # Geometric Description Language (GDL)
        ".geo": "application/vnd.dynageo",  # DynaGeo
        ".gex": "application/vnd.geometry-explorer",  # GeoMetry Explorer
        ".ggb": "application/vnd.geogebra.file",  # GeoGebra
        ".ggt": "application/vnd.geogebra.tool",  # GeoGebra
        ".ghf": "application/vnd.groove-help",  # Groove - Help
        ".gif": "image/gif",  # Graphics Interchange Format
        ".gim": "application/vnd.groove-identity-message",  # Groove - Identity Message
        ".gmx": "application/vnd.gmx",  # GameMaker ActiveX
        ".gnumeric": "application/x-gnumeric",  # Gnumeric
        ".gph": "application/vnd.flographit",  # NpGraphIt
        ".gqf": "application/vnd.grafeq",  # GrafEq
        ".gram": "application/srgs",  # Speech Recognition Grammar Specification
        ".grv": "application/vnd.groove-injector",  # Groove - Injector
        ".grxml": "application/srgs+xml",  # Speech Recognition Grammar Specification - XML
        ".gsf": "application/x-font-ghostscript",  # Ghostscript Font
        ".gtar": "application/x-gtar",  # GNU Tar Files
        ".gtm": "application/vnd.groove-tool-message",  # Groove - Tool Message
        ".gtw": "model/vnd.gtw",  # Gen-Trix Studio
        ".gv": "text/vnd.graphviz",  # Graphviz
        ".gxt": "application/vnd.geonext",  # GEONExT and JSXGraph
        ".h261": "video/h261",  # H.261
        ".h263": "video/h263",  # H.263
        ".h264": "video/h264",  # H.264
        ".hal": "application/vnd.hal+xml",  # Hypertext Application Language
        ".hbci": "application/vnd.hbci",  # Homebanking Computer Interface (HBCI)
        ".hdf": "application/x-hdf",  # Hierarchical Data Format
        ".hlp": "application/winhlp",  # WinHelp
        ".hpgl": "application/vnd.hp-hpgl",  # HP-GL/2 and HP RTL
        ".hpid": "application/vnd.hp-hpid",  # Hewlett Packard Instant Delivery
        ".hps": "application/vnd.hp-hps",  # Hewlett-Packard's WebPrintSmart
        ".hqx": "application/mac-binhex40",  # Macintosh BinHex 4.0
        ".htke": "application/vnd.kenameaapp",  # Kenamea App
        ".html": "text/html",  # HyperText Markup Language (HTML)
        ".hvd": "application/vnd.yamaha.hv-dic",  # HV Voice Dictionary
        ".hvp": "application/vnd.yamaha.hv-voice",  # HV Voice Parameter
        ".hvs": "application/vnd.yamaha.hv-script",  # HV Script
        ".i2g": "application/vnd.intergeo",  # Interactive Geometry Software
        ".icc": "application/vnd.iccprofile",  # ICC profile
        ".ice": "x-conference/x-cooltalk",  # CoolTalk
        ".ico": "image/x-icon",  # Icon Image
        ".ics": "text/calendar",  # iCalendar
        ".ief": "image/ief",  # Image Exchange Format
        ".ifm": "application/vnd.shana.informed.formdata",  # Shana Informed Filler
        ".igl": "application/vnd.igloader",  # igLoader
        ".igm": "application/vnd.insors.igm",  # IOCOM Visimeet
        ".igs": "model/iges",  # Initial Graphics Exchange Specification (IGES)
        ".igx": "application/vnd.micrografx.igx",  # Micrografx iGrafx Professional
        ".iif": "application/vnd.shana.informed.interchange",  # Shana Informed Filler
        ".imp": "application/vnd.accpac.simply.imp",  # Simply Accounting - Data Import
        ".ims": "application/vnd.ms-ims",  # Microsoft Class Server
        ".ipfix": "application/ipfix",  # Internet Protocol Flow Information Export
        ".ipk": "application/vnd.shana.informed.package",  # Shana Informed Filler
        ".irm": "application/vnd.ibm.rights-management",  # IBM DB2 Rights Manager
        ".irp": "application/vnd.irepository.package+xml",  # iRepository / Lucidoc Editor
        ".itp": "application/vnd.shana.informed.formtemplate",  # Shana Informed Filler
        ".ivp": "application/vnd.immervision-ivp",  # ImmerVision PURE Players
        ".ivu": "application/vnd.immervision-ivu",  # ImmerVision PURE Players
        ".jad": "text/vnd.sun.j2me.app-descriptor",  # J2ME App Descriptor
        ".jam": "application/vnd.jam",  # Lightspeed Audio Lab
        ".jar": "application/java-archive",  # Java Archive
        ".java": "text/x-java-source,java",  # Java Source File
        ".jisp": "application/vnd.jisp",  # RhymBox
        ".jlt": "application/vnd.hp-jlyt",  # HP Indigo Digital Press - Job Layout Languate
        ".jnlp": "application/x-java-jnlp-file",  # Java Network Launching Protocol
        ".joda": "application/vnd.joost.joda-archive",  # Joda Archive
        ".jpeg": "image/jpeg",  # JPEG Image
        ".jpg": "image/jpeg",  # JPEG Image
        ".jpgv": "video/jpeg",  # JPGVideo
        ".jpm": "video/jpm",  # JPEG 2000 Compound Image File Format
        ".js": "application/javascript",  # JavaScript
        ".json": "application/json",  # JavaScript Object Notation (JSON)
        ".karbon": "application/vnd.kde.karbon",  # KDE KOffice Office Suite - Karbon
        ".kfo": "application/vnd.kde.kformula",  # KDE KOffice Office Suite - Kformula
        ".kia": "application/vnd.kidspiration",  # Kidspiration
        ".kml": "application/vnd.google-earth.kml+xml",  # Google Earth - KML
        ".kmz": "application/vnd.google-earth.kmz",  # Google Earth - Zipped KML
        ".kne": "application/vnd.kinar",  # Kinar Applications
        ".kon": "application/vnd.kde.kontour",  # KDE KOffice Office Suite - Kontour
        ".kpr": "application/vnd.kde.kpresenter",  # KDE KOffice Office Suite - Kpresenter
        ".ksp": "application/vnd.kde.kspread",  # KDE KOffice Office Suite - Kspread
        ".ktx": "image/ktx",  # OpenGL Textures (KTX)
        ".ktz": "application/vnd.kahootz",  # Kahootz
        ".kwd": "application/vnd.kde.kword",  # KDE KOffice Office Suite - Kword
        ".lasxml": "application/vnd.las.las+xml",  # Laser App Enterprise
        ".latex": "application/x-latex",  # LaTeX
        ".lbd": "application/vnd.llamagraphics.life-balance.desktop",  # Life Balance - Desktop Edition
        ".lbe": "application/vnd.llamagraphics.life-balance.exchange+xml",  # Life Balance - Exchange Format
        ".les": "application/vnd.hhe.lesson-player",  # Archipelago Lesson Player
        ".link66": "application/vnd.route66.link66+xml",  # ROUTE 66 Location Based Services
        ".lrm": "application/vnd.ms-lrm",  # Microsoft Learning Resource Module
        ".ltf": "application/vnd.frogans.ltf",  # Frogans Player
        ".lvp": "audio/vnd.lucent.voice",  # Lucent Voice
        ".lwp": "application/vnd.lotus-wordpro",  # Lotus Wordpro
        ".m21": "application/mp21",  # MPEG-21
        ".m3u": "audio/x-mpegurl",  # M3U (Multimedia Playlist)
        ".m3u8": "application/vnd.apple.mpegurl",  # Multimedia Playlist Unicode
        ".m4v": "video/x-m4v",  # M4v
        ".ma": "application/mathematica",  # Mathematica Notebooks
        ".mads": "application/mads+xml",  # Metadata Authority Description Schema
        ".mag": "application/vnd.ecowin.chart",  # EcoWin Chart
        ".mathml": "application/mathml+xml",  # Mathematical Markup Language
        ".mbk": "application/vnd.mobius.mbk",  # Mobius Management Systems - Basket file
        ".mbox": "application/mbox",  # Mbox database files
        ".mc1": "application/vnd.medcalcdata",  # MedCalc
        ".mcd": "application/vnd.mcd",  # Micro CADAM Helix D&D
        ".mcurl": "text/vnd.curl.mcurl",  # Curl - Manifest File
        ".mdb": "application/x-msaccess",  # Microsoft Access
        ".mdi": "image/vnd.ms-modi",  # Microsoft Document Imaging Format
        ".meta4": "application/metalink4+xml",  # Metalink
        ".mets": "application/mets+xml",  # Metadata Encoding and Transmission Standard
        ".mfm": "application/vnd.mfmp",  # Melody Format for Mobile Platform
        ".mgp": "application/vnd.osgeo.mapguide.package",  # MapGuide DBXML
        ".mgz": "application/vnd.proteus.magazine",  # EFI Proteus
        ".mid": "audio/midi",  # MIDI - Musical Instrument Digital Interface
        ".mif": "application/vnd.mif",  # FrameMaker Interchange Format
        ".mj2": "video/mj2",  # Motion JPEG 2000
        ".mlp": "application/vnd.dolby.mlp",  # Dolby Meridian Lossless Packing
        ".mmd": "application/vnd.chipnuts.karaoke-mmd",  # Karaoke on Chipnuts Chipsets
        ".mmf": "application/vnd.smaf",  # SMAF File
        ".mmr": "image/vnd.fujixerox.edmics-mmr",  # EDMICS 2000
        ".mny": "application/x-msmoney",  # Microsoft Money
        ".mods": "application/mods+xml",  # Metadata Object Description Schema
        ".movie": "video/x-sgi-movie",  # SGI Movie
        ".mp4": "application/mp4",  # MPEG4
        # ".mp4": "video/mp4",  # MPEG-4 Video
        ".mp4a": "audio/mp4",  # MPEG-4 Audio
        ".mpc": "application/vnd.mophun.certificate",  # Mophun Certificate
        ".mpeg": "video/mpeg",  # MPEG Video
        ".mpga": "audio/mpeg",  # MPEG Audio
        ".mpkg": "application/vnd.apple.installer+xml",  # Apple Installer Package
        ".mpm": "application/vnd.blueice.multipass",  # Blueice Research Multipass
        ".mpn": "application/vnd.mophun.application",  # Mophun VM
        ".mpp": "application/vnd.ms-project",  # Microsoft Project
        ".mpy": "application/vnd.ibm.minipay",  # MiniPay
        ".mqy": "application/vnd.mobius.mqy",  # Mobius Management Systems - Query File
        ".mrc": "application/marc",  # MARC Formats
        ".mrcx": "application/marcxml+xml",  # MARC21 XML Schema
        ".mscml": "application/mediaservercontrol+xml",  # Media Server Control Markup Language
        ".mseq": "application/vnd.mseq",  # 3GPP MSEQ File
        ".msf": "application/vnd.epson.msf",  # QUASS Stream Player
        ".msh": "model/mesh",  # Mesh Data Type
        ".msl": "application/vnd.mobius.msl",  # Mobius Management Systems - Script Language
        ".msty": "application/vnd.muvee.style",  # Muvee Automatic Video Editing
        ".mts": "model/vnd.mts",  # Virtue MTS
        ".mus": "application/vnd.musician",  # MUsical Score Interpreted Code Invented for the ASCII designation of Notation
        ".musicxml": "application/vnd.recordare.musicxml+xml",  # Recordare Applications
        ".mvb": "application/x-msmediaview",  # Microsoft MediaView
        ".mwf": "application/vnd.mfer",  # Medical Waveform Encoding Format
        ".mxf": "application/mxf",  # Material Exchange Format
        ".mxl": "application/vnd.recordare.musicxml",  # Recordare Applications
        ".mxml": "application/xv+xml",  # MXML
        ".mxs": "application/vnd.triscape.mxs",  # Triscape Map Explorer
        ".mxu": "video/vnd.mpegurl",  # MPEG Url
        ".n-gage": "application/vnd.nokia.n-gage.symbian.install",  # N-Gage Game Installer
        ".n3": "text/n3",  # Notation3
        ".nbp": "application/vnd.wolfram.player",  # Mathematica Notebook Player
        ".nc": "application/x-netcdf",  # Network Common Data Form (NetCDF)
        ".ncx": "application/x-dtbncx+xml",  # Navigation Control file for XML (for ePub)
        ".ngdat": "application/vnd.nokia.n-gage.data",  # N-Gage Game Data
        ".nlu": "application/vnd.neurolanguage.nlu",  # neuroLanguage
        ".nml": "application/vnd.enliven",  # Enliven Viewer
        ".nnd": "application/vnd.noblenet-directory",  # NobleNet Directory
        ".nns": "application/vnd.noblenet-sealer",  # NobleNet Sealer
        ".nnw": "application/vnd.noblenet-web",  # NobleNet Web
        ".npx": "image/vnd.net-fpx",  # FlashPix
        ".nsf": "application/vnd.lotus-notes",  # Lotus Notes
        ".oa2": "application/vnd.fujitsu.oasys2",  # Fujitsu Oasys
        ".oa3": "application/vnd.fujitsu.oasys3",  # Fujitsu Oasys
        ".oas": "application/vnd.fujitsu.oasys",  # Fujitsu Oasys
        ".obd": "application/x-msbinder",  # Microsoft Office Binder
        ".oda": "application/oda",  # Office Document Architecture
        ".odb": "application/vnd.oasis.opendocument.database",  # OpenDocument Database
        ".odc": "application/vnd.oasis.opendocument.chart",  # OpenDocument Chart
        ".odf": "application/vnd.oasis.opendocument.formula",  # OpenDocument Formula
        ".odft": "application/vnd.oasis.opendocument.formula-template",  # OpenDocument Formula Template
        ".odg": "application/vnd.oasis.opendocument.graphics",  # OpenDocument Graphics
        ".odi": "application/vnd.oasis.opendocument.image",  # OpenDocument Image
        ".odm": "application/vnd.oasis.opendocument.text-master",  # OpenDocument Text Master
        ".odp": "application/vnd.oasis.opendocument.presentation",  # OpenDocument Presentation
        ".ods": "application/vnd.oasis.opendocument.spreadsheet",  # OpenDocument Spreadsheet
        ".odt": "application/vnd.oasis.opendocument.text",  # OpenDocument Text
        ".oga": "audio/ogg",  # Ogg Audio
        ".ogv": "video/ogg",  # Ogg Video
        ".ogx": "application/ogg",  # Ogg
        ".onetoc": "application/onenote",  # Microsoft OneNote
        ".opf": "application/oebps-package+xml",  # Open eBook Publication Structure
        ".org": "application/vnd.lotus-organizer",  # Lotus Organizer
        ".osf": "application/vnd.yamaha.openscoreformat",  # Open Score Format
        ".osfpvg": "application/vnd.yamaha.openscoreformat.osfpvg+xml",  # OSFPVG
        ".otc": "application/vnd.oasis.opendocument.chart-template",  # OpenDocument Chart Template
        ".otf": "application/x-font-otf",  # OpenType Font File
        ".otg": "application/vnd.oasis.opendocument.graphics-template",  # OpenDocument Graphics Template
        ".oth": "application/vnd.oasis.opendocument.text-web",  # Open Document Text Web
        ".oti": "application/vnd.oasis.opendocument.image-template",  # OpenDocument Image Template
        ".otp": "application/vnd.oasis.opendocument.presentation-template",  # OpenDocument Presentation Template
        ".ots": "application/vnd.oasis.opendocument.spreadsheet-template",  # OpenDocument Spreadsheet Template
        ".ott": "application/vnd.oasis.opendocument.text-template",  # OpenDocument Text Template
        ".oxt": "application/vnd.openofficeorg.extension",  # Open Office Extension
        ".p": "text/x-pascal",  # Pascal Source File
        ".p10": "application/pkcs10",  # PKCS #10 - Certification Request Standard
        ".p12": "application/x-pkcs12",  # PKCS #12 - Personal Information Exchange Syntax Standard
        ".p7b": "application/x-pkcs7-certificates",  # PKCS #7 - Cryptographic Message Syntax Standard (Certificates)
        ".p7m": "application/pkcs7-mime",  # PKCS #7 - Cryptographic Message Syntax Standard
        ".p7r": "application/x-pkcs7-certreqresp",  # PKCS #7 - Cryptographic Message Syntax Standard (Certificate Request Response)
        ".p7s": "application/pkcs7-signature",  # PKCS #7 - Cryptographic Message Syntax Standard
        ".p8": "application/pkcs8",  # PKCS #8 - Private-Key Information Syntax Standard
        ".par": "text/plain-bas",  # BAS Partitur Format
        ".paw": "application/vnd.pawaafile",  # PawaaFILE
        ".pbd": "application/vnd.powerbuilder6",  # PowerBuilder
        ".pbm": "image/x-portable-bitmap",  # Portable Bitmap Format
        ".pcf": "application/x-font-pcf",  # Portable Compiled Format
        ".pcl": "application/vnd.hp-pcl",  # HP Printer Command Language
        ".pclxl": "application/vnd.hp-pclxl",  # PCL 6 Enhanced (Formely PCL XL)
        ".pcurl": "application/vnd.curl.pcurl",  # CURL Applet
        ".pcx": "image/x-pcx",  # PCX Image
        ".pdb": "application/vnd.palm",  # PalmOS Data
        ".pdf": "application/pdf",  # Adobe Portable Document Format
        ".pfa": "application/x-font-type1",  # PostScript Fonts
        ".pfr": "application/font-tdpfr",  # Portable Font Resource
        ".pgm": "image/x-portable-graymap",  # Portable Graymap Format
        ".pgn": "application/x-chess-pgn",  # Portable Game Notation (Chess Games)
        ".pgp": "application/pgp-signature",  # Pretty Good Privacy - Signature
        ".pic": "image/x-pict",  # PICT Image
        ".pki": "application/pkixcmp",  # Internet Public Key Infrastructure - Certificate Management Protocole
        ".pkipath": "application/pkix-pkipath",  # Internet Public Key Infrastructure - Certification Path
        ".plb": "application/vnd.3gpp.pic-bw-large",  # 3rd Generation Partnership Project - Pic Large
        ".plc": "application/vnd.mobius.plc",  # Mobius Management Systems - Policy Definition Language File
        ".plf": "application/vnd.pocketlearn",  # PocketLearn Viewers
        ".pls": "application/pls+xml",  # Pronunciation Lexicon Specification
        ".pml": "application/vnd.ctc-posml",  # PosML
        ".png": "image/png",  # Portable Network Graphics (PNG)
        ".pnm": "image/x-portable-anymap",  # Portable Anymap Image
        ".portpkg": "application/vnd.macports.portpkg",  # MacPorts Port System
        ".potm": "application/vnd.ms-powerpoint.template.macroenabled.12",  # Micosoft PowerPoint - Macro-Enabled Template File
        ".potx": "application/vnd.openxmlformats-officedocument.presentationml.template",  # Microsoft Office - OOXML - Presentation Template
        ".ppam": "application/vnd.ms-powerpoint.addin.macroenabled.12",  # Microsoft PowerPoint - Add-in file
        ".ppd": "application/vnd.cups-ppd",  # Adobe PostScript Printer Description File Format
        ".ppm": "image/x-portable-pixmap",  # Portable Pixmap Format
        ".ppsm": "application/vnd.ms-powerpoint.slideshow.macroenabled.12",  # Microsoft PowerPoint - Macro-Enabled Slide Show File
        ".ppsx": "application/vnd.openxmlformats-officedocument.presentationml.slideshow",  # Microsoft Office - OOXML - Presentation (Slideshow)
        ".ppt": "application/vnd.ms-powerpoint",  # Microsoft PowerPoint
        ".pptm": "application/vnd.ms-powerpoint.presentation.macroenabled.12",  # Microsoft PowerPoint - Macro-Enabled Presentation File
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # Microsoft Office - OOXML - Presentation
        ".prc": "application/x-mobipocket-ebook",  # Mobipocket
        ".pre": "application/vnd.lotus-freelance",  # Lotus Freelance
        ".prf": "application/pics-rules",  # PICSRules
        ".psb": "application/vnd.3gpp.pic-bw-small",  # 3rd Generation Partnership Project - Pic Small
        ".psd": "image/vnd.adobe.photoshop",  # Photoshop Document
        ".psf": "application/x-font-linux-psf",  # PSF Fonts
        ".pskcxml": "application/pskc+xml",  # Portable Symmetric Key Container
        ".ptid": "application/vnd.pvi.ptid1",  # Princeton Video Image
        ".pub": "application/x-mspublisher",  # Microsoft Publisher
        ".pvb": "application/vnd.3gpp.pic-bw-var",  # 3rd Generation Partnership Project - Pic Var
        ".pwn": "application/vnd.3m.post-it-notes",  # 3M Post It Notes
        ".pya": "audio/vnd.ms-playready.media.pya",  # Microsoft PlayReady Ecosystem
        ".pyv": "video/vnd.ms-playready.media.pyv",  # Microsoft PlayReady Ecosystem Video
        ".qam": "application/vnd.epson.quickanime",  # QuickAnime Player
        ".qbo": "application/vnd.intu.qbo",  # Open Financial Exchange
        ".qfx": "application/vnd.intu.qfx",  # Quicken
        ".qps": "application/vnd.publishare-delta-tree",  # PubliShare Objects
        ".qt": "video/quicktime",  # Quicktime Video
        ".qxd": "application/vnd.quark.quarkxpress",  # QuarkXpress
        ".ram": "audio/x-pn-realaudio",  # Real Audio Sound
        ".rar": "application/x-rar-compressed",  # RAR Archive
        ".ras": "image/x-cmu-raster",  # CMU Image
        ".rcprofile": "application/vnd.ipunplugged.rcprofile",  # IP Unplugged Roaming Client
        ".rdf": "application/rdf+xml",  # Resource Description Framework
        ".rdz": "application/vnd.data-vision.rdz",  # RemoteDocs R-Viewer
        ".rep": "application/vnd.businessobjects",  # BusinessObjects
        ".res": "application/x-dtbresource+xml",  # Digital Talking Book - Resource File
        ".rgb": "image/x-rgb",  # Silicon Graphics RGB Bitmap
        ".rif": "application/reginfo+xml",  # IMS Networks
        ".rip": "audio/vnd.rip",  # Hit'n'Mix
        ".rl": "application/resource-lists+xml",  # XML Resource Lists
        ".rlc": "image/vnd.fujixerox.edmics-rlc",  # EDMICS 2000
        ".rld": "application/resource-lists-diff+xml",  # XML Resource Lists Diff
        ".rm": "application/vnd.rn-realmedia",  # RealMedia
        ".rmp": "audio/x-pn-realaudio-plugin",  # Real Audio Sound
        ".rms": "application/vnd.jcp.javame.midlet-rms",  # Mobile Information Device Profile
        ".rnc": "application/relax-ng-compact-syntax",  # Relax NG Compact Syntax
        ".rp9": "application/vnd.cloanto.rp9",  # RetroPlatform Player
        ".rpss": "application/vnd.nokia.radio-presets",  # Nokia Radio Application - Preset
        ".rpst": "application/vnd.nokia.radio-preset",  # Nokia Radio Application - Preset
        ".rq": "application/sparql-query",  # SPARQL - Query
        ".rs": "application/rls-services+xml",  # XML Resource Lists
        ".rsd": "application/rsd+xml",  # Really Simple Discovery
        ".rss": "application/rss+xml",  # RSS - Really Simple Syndication
        ".rtf": "application/rtf",  # Rich Text Format
        ".rtx": "text/richtext",  # Rich Text Format (RTF)
        ".s": "text/x-asm",  # Assembler Source File
        ".saf": "application/vnd.yamaha.smaf-audio",  # SMAF Audio
        ".sbml": "application/sbml+xml",  # Systems Biology Markup Language
        ".sc": "application/vnd.ibm.secure-container",  # IBM Electronic Media Management System - Secure Container
        ".scd": "application/x-msschedule",  # Microsoft Schedule+
        ".scm": "application/vnd.lotus-screencam",  # Lotus Screencam
        ".scq": "application/scvp-cv-request",  # Server-Based Certificate Validation Protocol - Validation Request
        ".scs": "application/scvp-cv-response",  # Server-Based Certificate Validation Protocol - Validation Response
        ".scurl": "text/vnd.curl.scurl",  # Curl - Source Code
        ".sda": "application/vnd.stardivision.draw",  # StarOffice - Draw
        ".sdc": "application/vnd.stardivision.calc",  # StarOffice - Calc
        ".sdd": "application/vnd.stardivision.impress",  # StarOffice - Impress
        ".sdkm": "application/vnd.solent.sdkm+xml",  # SudokuMagic
        ".sdp": "application/sdp",  # Session Description Protocol
        ".sdw": "application/vnd.stardivision.writer",  # StarOffice - Writer
        ".see": "application/vnd.seemail",  # SeeMail
        ".seed": "application/vnd.fdsn.seed",  # Digital Siesmograph Networks - SEED Datafiles
        ".sema": "application/vnd.sema",  # Secured eMail
        ".semd": "application/vnd.semd",  # Secured eMail
        ".semf": "application/vnd.semf",  # Secured eMail
        ".ser": "application/java-serialized-object",  # Java Serialized Object
        ".setpay": "application/set-payment-initiation",  # Secure Electronic Transaction - Payment
        ".setreg": "application/set-registration-initiation",  # Secure Electronic Transaction - Registration
        ".sfd-hdstx": "application/vnd.hydrostatix.sof-data",  # Hydrostatix Master Suite
        ".sfs": "application/vnd.spotfire.sfs",  # TIBCO Spotfire
        ".sgl": "application/vnd.stardivision.writer-global",  # StarOffice - Writer (Global)
        ".sgml": "text/sgml",  # Standard Generalized Markup Language (SGML)
        ".sh": "application/x-sh",  # Bourne Shell Script
        ".shar": "application/x-shar",  # Shell Archive
        ".shf": "application/shf+xml",  # S Hexdump Format
        ".sis": "application/vnd.symbian.install",  # Symbian Install Package
        ".sit": "application/x-stuffit",  # Stuffit Archive
        ".sitx": "application/x-stuffitx",  # Stuffit Archive
        ".skp": "application/vnd.koan",  # SSEYO Koan Play File
        ".sldm": "application/vnd.ms-powerpoint.slide.macroenabled.12",  # Microsoft PowerPoint - Macro-Enabled Open XML Slide
        ".sldx": "application/vnd.openxmlformats-officedocument.presentationml.slide",  # Microsoft Office - OOXML - Presentation (Slide)
        ".slt": "application/vnd.epson.salt",  # SimpleAnimeLite Player
        ".sm": "application/vnd.stepmania.stepchart",  # StepMania
        ".smf": "application/vnd.stardivision.math",  # StarOffice - Math
        ".smi": "application/smil+xml",  # Synchronized Multimedia Integration Language
        ".snf": "application/x-font-snf",  # Server Normal Format
        ".spf": "application/vnd.yamaha.smaf-phrase",  # SMAF Phrase
        ".spl": "application/x-futuresplash",  # FutureSplash Animator
        ".spot": "text/vnd.in3d.spot",  # In3D - 3DML
        ".spp": "application/scvp-vp-response",  # Server-Based Certificate Validation Protocol - Validation Policies - Response
        ".spq": "application/scvp-vp-request",  # Server-Based Certificate Validation Protocol - Validation Policies - Request
        ".src": "application/x-wais-source",  # WAIS Source
        ".sru": "application/sru+xml",  # Search/Retrieve via URL Response Format
        ".srx": "application/sparql-results+xml",  # SPARQL - Results
        ".sse": "application/vnd.kodak-descriptor",  # Kodak Storyshare
        ".ssf": "application/vnd.epson.ssf",  # QUASS Stream Player
        ".ssml": "application/ssml+xml",  # Speech Synthesis Markup Language
        ".st": "application/vnd.sailingtracker.track",  # SailingTracker
        ".stc": "application/vnd.sun.xml.calc.template",  # OpenOffice - Calc Template (Spreadsheet)
        ".std": "application/vnd.sun.xml.draw.template",  # OpenOffice - Draw Template (Graphics)
        ".stf": "application/vnd.wt.stf",  # Worldtalk
        ".sti": "application/vnd.sun.xml.impress.template",  # OpenOffice - Impress Template (Presentation)
        ".stk": "application/hyperstudio",  # Hyperstudio
        ".stl": "application/vnd.ms-pki.stl",  # Microsoft Trust UI Provider - Certificate Trust Link
        ".str": "application/vnd.pg.format",  # Proprietary P&G Standard Reporting System
        ".stw": "application/vnd.sun.xml.writer.template",  # OpenOffice - Writer Template (Text - HTML)
        ".sub": "image/vnd.dvb.subtitle",  # Close Captioning - Subtitle
        ".sus": "application/vnd.sus-calendar",  # ScheduleUs
        ".sv4cpio": "application/x-sv4cpio",  # System V Release 4 CPIO Archive
        ".sv4crc": "application/x-sv4crc",  # System V Release 4 CPIO Checksum Data
        ".svc": "application/vnd.dvb.service",  # Digital Video Broadcasting
        ".svd": "application/vnd.svd",  # SourceView Document
        ".svg": "image/svg+xml",  # Scalable Vector Graphics (SVG)
        ".swf": "application/x-shockwave-flash",  # Adobe Flash
        ".swi": "application/vnd.aristanetworks.swi",  # Arista Networks Software Image
        ".sxc": "application/vnd.sun.xml.calc",  # OpenOffice - Calc (Spreadsheet)
        ".sxd": "application/vnd.sun.xml.draw",  # OpenOffice - Draw (Graphics)
        ".sxg": "application/vnd.sun.xml.writer.global",  # OpenOffice - Writer (Text - HTML)
        ".sxi": "application/vnd.sun.xml.impress",  # OpenOffice - Impress (Presentation)
        ".sxm": "application/vnd.sun.xml.math",  # OpenOffice - Math (Formula)
        ".sxw": "application/vnd.sun.xml.writer",  # OpenOffice - Writer (Text - HTML)
        ".t": "text/troff",  # troff
        ".tao": "application/vnd.tao.intent-module-archive",  # Tao Intent
        ".tar": "application/x-tar",  # Tar File (Tape Archive)
        ".tcap": "application/vnd.3gpp2.tcap",  # 3rd Generation Partnership Project - Transaction Capabilities Application Part
        ".tcl": "application/x-tcl",  # Tcl Script
        ".teacher": "application/vnd.smart.teacher",  # SMART Technologies Apps
        ".tei": "application/tei+xml",  # Text Encoding and Interchange
        ".tex": "application/x-tex",  # TeX
        ".texinfo": "application/x-texinfo",  # GNU Texinfo Document
        ".tfi": "application/thraud+xml",  # Sharing Transaction Fraud Data
        ".tfm": "application/x-tex-tfm",  # TeX Font Metric
        ".thmx": "application/vnd.ms-officetheme",  # Microsoft Office System Release Theme
        ".tiff": "image/tiff",  # Tagged Image File Format
        ".tmo": "application/vnd.tmobile-livetv",  # MobileTV
        ".torrent": "application/x-bittorrent",  # BitTorrent
        ".tpl": "application/vnd.groove-tool-template",  # Groove - Tool Template
        ".tpt": "application/vnd.trid.tpt",  # TRI Systems Config
        ".tra": "application/vnd.trueapp",  # True BASIC
        ".trm": "application/x-msterminal",  # Microsoft Windows Terminal Services
        ".tsd": "application/timestamped-data",  # Time Stamped Data Envelope
        ".tsv": "text/tab-separated-values",  # Tab Seperated Values
        ".ttf": "application/x-font-ttf",  # TrueType Font
        ".ttl": "text/turtle",  # Turtle (Terse RDF Triple Language)
        ".twd": "application/vnd.simtech-mindmapper",  # SimTech MindMapper
        ".txd": "application/vnd.genomatix.tuxedo",  # Genomatix Tuxedo Framework
        ".txf": "application/vnd.mobius.txf",  # Mobius Management Systems - Topic Index File
        ".txt": "text/plain",  # Text File
        ".ufd": "application/vnd.ufdl",  # Universal Forms Description Language
        ".umj": "application/vnd.umajin",  # UMAJIN
        ".unityweb": "application/vnd.unity",  # Unity 3d
        ".uoml": "application/vnd.uoml+xml",  # Unique Object Markup Language
        ".uri": "text/uri-list",  # URI Resolution Services
        ".ustar": "application/x-ustar",  # Ustar (Uniform Standard Tape Archive)
        ".utz": "application/vnd.uiq.theme",  # User Interface Quartz - Theme (Symbian)
        ".uu": "text/x-uuencode",  # UUEncode
        ".uva": "audio/vnd.dece.audio",  # DECE Audio
        ".uvh": "video/vnd.dece.hd",  # DECE High Definition Video
        ".uvi": "image/vnd.dece.graphic",  # DECE Graphic
        ".uvm": "video/vnd.dece.mobile",  # DECE Mobile Video
        ".uvp": "video/vnd.dece.pd",  # DECE PD Video
        ".uvs": "video/vnd.dece.sd",  # DECE SD Video
        ".uvu": "video/vnd.uvvu.mp4",  # DECE MP4
        ".uvv": "video/vnd.dece.video",  # DECE Video
        ".vcd": "application/x-cdlink",  # Video CD
        ".vcf": "text/x-vcard",  # vCard
        ".vcg": "application/vnd.groove-vcard",  # Groove - Vcard
        ".vcs": "text/x-vcalendar",  # vCalendar
        ".vcx": "application/vnd.vcx",  # VirtualCatalog
        ".vis": "application/vnd.visionary",  # Visionary
        ".viv": "video/vnd.vivo",  # Vivo
        ".vsd": "application/vnd.visio",  # Microsoft Visio
        ".vsf": "application/vnd.vsf",  # Viewport+
        ".vtu": "model/vnd.vtu",  # Virtue VTU
        ".vxml": "application/voicexml+xml",  # VoiceXML
        ".wad": "application/x-doom",  # Doom Video Game
        ".wav": "audio/x-wav",  # Waveform Audio File Format (WAV)
        ".wax": "audio/x-ms-wax",  # Microsoft Windows Media Audio Redirector
        ".wbmp": "image/vnd.wap.wbmp",  # WAP Bitamp (WBMP)
        ".wbs": "application/vnd.criticaltools.wbs+xml",  # Critical Tools - PERT Chart EXPERT
        ".wbxml": "application/vnd.wap.wbxml",  # WAP Binary XML (WBXML)
        ".weba": "audio/webm",  # Open Web Media Project - Audio
        ".webm": "video/webm",  # Open Web Media Project - Video
        ".webp": "image/webp",  # WebP Image
        ".wg": "application/vnd.pmi.widget",  # Qualcomm's Plaza Mobile Internet
        ".wgt": "application/widget",  # Widget Packaging and XML Configuration
        ".wm": "video/x-ms-wm",  # Microsoft Windows Media
        ".wma": "audio/x-ms-wma",  # Microsoft Windows Media Audio
        ".wmd": "application/x-ms-wmd",  # Microsoft Windows Media Player Download Package
        ".wmf": "application/x-msmetafile",  # Microsoft Windows Metafile
        ".wml": "text/vnd.wap.wml",  # Wireless Markup Language (WML)
        ".wmlc": "application/vnd.wap.wmlc",  # Compiled Wireless Markup Language (WMLC)
        ".wmls": "text/vnd.wap.wmlscript",  # Wireless Markup Language Script (WMLScript)
        ".wmlsc": "application/vnd.wap.wmlscriptc",  # WMLScript
        ".wmv": "video/x-ms-wmv",  # Microsoft Windows Media Video
        ".wmx": "video/x-ms-wmx",  # Microsoft Windows Media Audio/Video Playlist
        ".wmz": "application/x-ms-wmz",  # Microsoft Windows Media Player Skin Package
        ".woff": "application/x-font-woff",  # Web Open Font Format
        ".wpd": "application/vnd.wordperfect",  # Wordperfect
        ".wpl": "application/vnd.ms-wpl",  # Microsoft Windows Media Player Playlist
        ".wps": "application/vnd.ms-works",  # Microsoft Works
        ".wqd": "application/vnd.wqd",  # SundaHus WQ
        ".wri": "application/x-mswrite",  # Microsoft Wordpad
        ".wrl": "model/vrml",  # Virtual Reality Modeling Language
        ".wsdl": "application/wsdl+xml",  # WSDL - Web Services Description Language
        ".wspolicy": "application/wspolicy+xml",  # Web Services Policy
        ".wtb": "application/vnd.webturbo",  # WebTurbo
        ".wvx": "video/x-ms-wvx",  # Microsoft Windows Media Video Playlist
        ".x3d": "application/vnd.hzn-3d-crossword",  # 3D Crossword Plugin
        ".xap": "application/x-silverlight-app",  # Microsoft Silverlight
        ".xar": "application/vnd.xara",  # CorelXARA
        ".xbap": "application/x-ms-xbap",  # Microsoft XAML Browser Application
        ".xbd": "application/vnd.fujixerox.docuworks.binder",  # Fujitsu - Xerox DocuWorks Binder
        ".xbm": "image/x-xbitmap",  # X BitMap
        ".xdf": "application/xcap-diff+xml",  # XML Configuration Access Protocol - XCAP Diff
        ".xdm": "application/vnd.syncml.dm+xml",  # SyncML - Device Management
        ".xdp": "application/vnd.adobe.xdp+xml",  # Adobe XML Data Package
        ".xdssc": "application/dssc+xml",  # Data Structure for the Security Suitability of Cryptographic Algorithms
        ".xdw": "application/vnd.fujixerox.docuworks",  # Fujitsu - Xerox DocuWorks
        ".xenc": "application/xenc+xml",  # XML Encryption Syntax and Processing
        ".xer": "application/patch-ops-error+xml",  # XML Patch Framework
        ".xfdf": "application/vnd.adobe.xfdf",  # Adobe XML Forms Data Format
        ".xfdl": "application/vnd.xfdl",  # Extensible Forms Description Language
        ".xhtml": "application/xhtml+xml",  # XHTML - The Extensible HyperText Markup Language
        ".xif": "image/vnd.xiff",  # eXtended Image File Format (XIFF)
        ".xlam": "application/vnd.ms-excel.addin.macroenabled.12",  # Microsoft Excel - Add-In File
        ".xls": "application/vnd.ms-excel",  # Microsoft Excel
        ".xlsb": "application/vnd.ms-excel.sheet.binary.macroenabled.12",  # Microsoft Excel - Binary Workbook
        ".xlsm": "application/vnd.ms-excel.sheet.macroenabled.12",  # Microsoft Excel - Macro-Enabled Workbook
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # Microsoft Office - OOXML - Spreadsheet
        ".xltm": "application/vnd.ms-excel.template.macroenabled.12",  # Microsoft Excel - Macro-Enabled Template File
        ".xltx": "application/vnd.openxmlformats-officedocument.spreadsheetml.template",  # Microsoft Office - OOXML - Spreadsheet Teplate
        ".xml": "application/xml",  # XML - Extensible Markup Language
        ".xo": "application/vnd.olpc-sugar",  # Sugar Linux Application Bundle
        ".xop": "application/xop+xml",  # XML-Binary Optimized Packaging
        ".xpi": "application/x-xpinstall",  # XPInstall - Mozilla
        ".xpm": "image/x-xpixmap",  # X PixMap
        ".xpr": "application/vnd.is-xpr",  # Express by Infoseek
        ".xps": "application/vnd.ms-xpsdocument",  # Microsoft XML Paper Specification
        ".xpw": "application/vnd.intercon.formnet",  # Intercon FormNet
        ".xslt": "application/xslt+xml",  # XML Transformations
        ".xsm": "application/vnd.syncml+xml",  # SyncML
        ".xspf": "application/xspf+xml",  # XSPF - XML Shareable Playlist Format
        ".xul": "application/vnd.mozilla.xul+xml",  # XUL - XML User Interface Language
        ".xwd": "image/x-xwindowdump",  # X Window Dump
        ".xyz": "chemical/x-xyz",  # XYZ File Format
        ".yaml": "text/yaml",  # YAML Ain't Markup Language / Yet Another Markup Language
        ".yang": "application/yang",  # YANG Data Modeling Language
        ".yin": "application/yin+xml",  # YIN (YANG - XML)
        ".zaz": "application/vnd.zzazz.deck+xml",  # Zzazz Deck
        ".zip": "application/zip",  # Zip Archive
        ".zir": "application/vnd.zul",  # Z.U.L. Geometry
        ".zmm": "application/vnd.handheld-entertainment+xml"  # ZVUE Media Manager
    }
    return m.get(ext, df)

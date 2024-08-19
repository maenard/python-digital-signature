import sys
import datetime
from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12

from endesive import pdf

# import logging
# logging.basicConfig(level=logging.DEBUG)
#

def main(x, x1, y, y1, pdfimage, p12signature, password, flname, page, reason=''):    
    # from endesive import pdf
    print("File: ", flname)
    date = datetime.datetime.utcnow()
    date = date.strftime('%B %d, %Y')

    #offset = 100
    #x1 += offset
    #y1 -= offset * 1
    #y += (offset * 0.25)

    dct = {
        "aligned": 0,
        "sigflags": 3,
        "sigflagsft": 132,
        "sigpage": page,
        "auto_sigfield": True,
        #"sigandcertify": False,
        "signaturebox": (x, x1, y, y1),
        "signform": False,
        "sigfield": "Signature",

        # Text will be in the default font
        # Fields in the list display will be included in the text listing
        # Icon and background can both be set to images by having their
        #   value be a path to a file or a PIL Image object
        # If background is a list it is considered to be an opaque RGB colour
        # Outline is the colour used to draw both the border and the text
        "signature_appearance": {
            'background': [0.75, 0.8, 0.95],
            'icon': pdfimage,
            'outline': [0.2, 0.3, 0.5],
            'border': 2,
            'labels': True,
            'display': 'CN,DN,date,contact,reason,location'.split(','),
            },

        "contact": "mak@trisoft.com.pl",
        "location": "Szczecin",
        "signingdate": date,
        "reason": reason,
        "password": password,
    }

    # dct = {
    #     "aligned": 0,
    #     "sigflags": 3,
    #     "sigflagsft": 132,
    #     "sigpage": page, # change this for per page implementation
    #     "sigbutton": True,
    #     "sigfield": "Signature1",
    #     "auto_sigfield": True,
    #     "sigandcertify": False,
    #     "signform": False,
    #     "signaturebox": (x, x1, y, y1),
    #     #"signature_appearance": {
    #     #    'outline': [0.01, 0.02, 0.02],
    #     #    'icon': pdfimage,
    #     #    'labels': True,
    #     #    'display': 'CN,date,reason'.split(','),
    #     #},
    #
    #     "signature_manual": [
    #         #                R     G     B
    #         #['fill_colour', 0.95, 0.95, 0.95],
    #
    #         #            *[bounding box]
    #         #['rect_fill', 0, 0, 270, 18],
    #
    #         #                  R    G    B
    #         #['stroke_colour', 0.8, 0.8, 0.8],
    #
    #         #        inset
    #         #['border', 2],
    #
    #         #          key  *[bounding box]  distort centred
    #         #['image', 'sig0', 10, 30, 100, 60,  False, True],
    #         ['image', 'sig0', 20, -30, 120, 80,  False, True], # NOTE: This coordinates is used for normal pdfs? ambot unsay tawag :)
    #
    #         #         font     fs 
    #         ['font', 'default', 12],
    #         #               R  G  B
    #         ['fill_colour', 0, 0, 0],
    #
    #         ##            text
    #         [
    #             'text_box', '',
    #             # font  *[bounding box], fs, wrap, align, baseline
    #             'default', -10, -25, 100, 60, 10, True, 'centred', 'top'
    #         ],
    #     ],
    #     #   key: name used in image directives
    #     # value: PIL Image object or path to image file
    #     "manual_images": {'sig0': pdfimage},
    #     #   key: name used in font directives
    #     # value: path to TTF Font file
    #     "manual_fonts": {},
    #
    #     "contact": "",
    #     "location": "",
    #     "signingdate": date,
    #     "reason": reason,
    #     "password": password,
    # }

    bs = b''
    with open(p12signature, "rb") as fp:
        p12 = pkcs12.load_key_and_certificates(
            fp.read(), bs+password.encode('utf-8'), backends.default_backend()
        )
    #print(p12[0], p12[1], p12[2])
    print(f"Signed page: {page}")
    
    #if len(sys.argv) > 1:
    fname = flname

    print("File Path: ", fname)
    datau = open(fname, "rb").read()
    datas = pdf.cms.sign(datau, dct, p12[0], p12[1], p12[2], "sha256")
    fname = fname.replace(".pdf", "-signed-cms.pdf")
    with open(fname, "wb") as fp:
        fp.write(datau)
        fp.write(datas)

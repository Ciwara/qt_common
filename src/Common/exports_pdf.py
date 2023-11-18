#!usr/bin/env python
# -*- coding= UTF-8 -*-
# maintainer: Fadiga

from __future__ import absolute_import, division, print_function, unicode_literals

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.platypus.tables import Table, TableStyle

# from num2words import num2words
from .ui.util import openFile

# setup the empty canvas
# from io import FileIO as file
# from pyPdf import PdfFileWriter, PdfFileReader
# from PyPDF2 import PdfFileWriter, PdfFileReader
# from datetime import datetime


def export_dynamic_data(dict_data):
    date = dict_data.get("date")
    data = dict_data.get("data")
    headers = dict_data.get("headers")
    file_name = "{}.pdf".format(dict_data.get("file_name"))
    title = str(dict_data.get("title"))

    style_sheet = getSampleStyleSheet()
    styleN = ParagraphStyle(style_sheet["Normal"])

    el = []
    # htable = headers
    hdata = [(title, "", "", ""), (date, "", "", "")]
    htable = Table(hdata)
    htable.hAlign = "LEFT"

    ldata = []
    ldata.append(headers)
    #
    for r in data:
        row_table = []
        for elr in r:
            row_table.append(Paragraph("{}".format(elr), styleN))
        ldata.append(row_table)

    btable = Table(ldata)
    # btable = Table(ldata, colWidths=[(inch) for i in range(1, len(ldata) + 1)])
    # btable = Table(ldata)
    btable.hAlign = "LEFT"
    btable.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#C0C0C0")),
                (
                    "GRID",
                    (0, 1),
                    (-1, -1),
                    0.01 * inch,
                    (
                        0,
                        0,
                        0,
                    ),
                ),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    el.append(htable)
    el.append(btable)

    doc = SimpleDocTemplate(file_name, pagesize=A4)
    doc.build(el)
    openFile(file_name)

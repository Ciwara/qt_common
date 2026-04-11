#!usr/bin/env python
# -*- coding= UTF-8 -*-
# maintainer: Fadiga


import os
from datetime import datetime

import xlsxwriter

from .cstatic import CConstants
from .models import Organization
from .ui.util import openFile

style_org = {
    "align": "center",
    "valign": "vcenter",
    "font_size": 26,
    "border": 1,
    "font_color": "blue",
    "bold": True,
}

style_title = {
    "border": 1,
}
style_value = {"border": 0}
style_label = {"border": 0}
style_headers = {"border": 1}


# def align_style(val):
#     try:
#         int(val)
#         return int_align
#     except ValueError:
#         return str_align
#     except TypeError:
#         return "ERROR"
#     else:
#         return 0


def export_dynamic_data(dict_data):
    """
    - Export params
    dict = {
        'file_name': "prod",
        'data' : [1, 3, ...],
        'headers': ["ff", "kkk", "ooo"],
        'sheet': "Les produits",
        'extend_rows': [(row1, col1, val), (row2, col2, val), ]
        'widths': [col, ..]
        'date': object date
        'format_money': ['D:D',]

    }
    - Principe
    write((nbre ligne - 1), nbre colonne, "contenu", style(optionnel).
    merge_range((nbre ligne - 1), (nbre ligne - 1) + nbre de ligne à merger, (nbre de colonne - 1), (nbre de colonne - 1) + nbre
    de colonne à merger, u"contenu", style(optionnel)).
    """
    organization = Organization.get(id=1)

    file_name = "{}.xlsx".format(dict_data.get("file_name"))
    headers = dict_data.get("headers")
    sheet_name = str(dict_data.get("sheet"))
    title = str(dict_data.get("title"))
    data = dict_data.get("data")
    widths = dict_data.get("widths")
    date_ = str(dict_data.get("date"))
    extend_rows = dict_data.get("extend_rows")
    others = dict_data.get("others")
    footers = dict_data.get("footers")
    exclude_row = dict_data.get("exclude_row")
    format_money = dict_data.get("format_money")

    dict_alph = {
        1: "A",
        2: "C",
        3: "D",
        4: "E",
        5: "F",
        6: "G",
        7: "H",
        8: "I",
    }

    if date_ == "None":
        date_ = datetime.now()

    workbook = xlsxwriter.Workbook(file_name, {"default_date_format": "dd/mm/yy"})
    worksheet = workbook.add_worksheet(sheet_name)
    # worksheet.fit_num_pages = 1
    # worksheet.set_h_pagebreaks([4])

    date_format = workbook.add_format({"num_format": "d-mmm-yy"})
    format1 = workbook.add_format()
    format1.set_num_format("0.000")
    money = workbook.add_format({"num_format": "#,## "})
    style_def = workbook.add_format({})
    rowx = 1
    end_colx = len(headers) - 1
    # APP_LOGO pointe déjà vers img_media/logo.* (cstatic) — ne pas refaire join(img_media, APP_LOGO).
    if CConstants.APP_LOGO:
        worksheet.insert_image(
            "A1:B2",
            CConstants.APP_LOGO,
            {"x_offset": 1.5, "y_offset": 0.5},
        )
        rowx += 6
    else:
        worksheet.merge_range(
            "A{}:E{}".format(rowx, rowx),
            organization.name_orga,
            workbook.add_format(style_org),
        )
        rowx += 1
        worksheet.merge_range(
            "A{}:E{}".format(rowx, rowx),
            "Adresse : {}".format(organization.adress_org),
            style_def,
        )
        rowx += 1
        worksheet.merge_range(
            "A{}:B{}".format(rowx, rowx), "BP : {}".format(organization.bp), style_def
        )
        worksheet.merge_range(
            "{}{}:{}{}".format(
                dict_alph.get(end_colx - 1), rowx, dict_alph.get(end_colx), rowx
            ),
            "E-mail : {}".format(organization.email_org),
            style_def,
        )
        rowx += 1
        worksheet.merge_range(
            "A{}:{}{}".format(rowx, dict_alph.get(end_colx - 1), rowx),
            "Tel : {}".format(organization.phone),
            style_def,
        )
        rowx += 2
    for col in widths:
        w = 120 / len(headers)
        worksheet.set_column(col, col, w)
    columns = [({"header": item}) for item in headers]
    end_row_table = len(data) + rowx + 3
    if format_money:
        for col_str in format_money:
            worksheet.set_column(col_str, 18, money)
    rowx += 1
    worksheet.merge_range(
        "D{}:{}{}".format(rowx, dict_alph.get(end_colx), rowx), date_, date_format
    )
    rowx += 2
    worksheet.add_table(
        "A{}:{}{}".format(rowx, dict_alph.get(end_colx), end_row_table),
        {"autofilter": 0, "data": data, "columns": columns},
    )
    rowx = end_row_table
    # rowx += 1
    if extend_rows:
        for elt in extend_rows:
            col, val = elt
            worksheet.write(rowx, col, val, money)
        rowx += 1
    if footers:
        rowx += 1
        for s_col, e_col, val in footers:
            worksheet.merge_range(
                "{}{}:{}{}".format(s_col, rowx, e_col, rowx),
                val,
                workbook.add_format(style_label),
            )
            rowx += 1
        rowx += 1
    # others : le dict peut contenir d'anciennes refs Excel (A10:C10) — elles chevauchent
    # add_table. On écrit chaque texte sous le tableau sur la ligne courante.
    if others:
        rowx += 1
        for _pos, _pos2, val in others:
            if val is None or str(val).strip() == "":
                continue
            worksheet.merge_range(
                rowx,
                0,
                rowx,
                end_colx,
                str(val),
                workbook.add_format(style_label),
            )
            rowx += 1
    try:
        workbook.close()
        # workbook.save(file_name)
        openFile(file_name)
    except Exception as e:
        print(e)


def xexport_dynamic_data(dict_data):
    from openpyxl import Workbook
    from openpyxl.worksheet.table import Table, TableStyleInfo

    wb = Workbook()
    ws = wb.active

    organization = Organization.get(id=1)

    file_name = "{}.xlsx".format(dict_data.get("file_name"))
    headers = dict_data.get("headers")
    sheet_name = str(dict_data.get("sheet"))
    title = str(dict_data.get("title"))
    data = dict_data.get("data")
    widths = dict_data.get("widths")
    date_ = str(dict_data.get("date"))
    extend_rows = dict_data.get("extend_rows")
    others = dict_data.get("others")
    footers = dict_data.get("footers")
    exclude_row = dict_data.get("exclude_row")
    format_money = dict_data.get("format_money")

    # add column headings. NB. these must be strings
    ws.append(headers)
    for row in data:
        print(row)
        ws.append(row)

    dict_alph = {
        1: "A",
        2: "C",
        3: "D",
        4: "E",
        5: "F",
        6: "G",
        7: "H",
        8: "I",
    }
    REF = "A1:{}{}".format(dict_alph.get(len(headers)), len(data) + 1)
    print(REF)
    tab = Table(displayName="Table1", ref=REF)

    # Add a default style with striped rows and banded columns
    style = TableStyleInfo(
        name="TableStyleMedium9",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=True,
    )
    tab.tableStyleInfo = style
    ws.add_table(tab)
    wb.save(file_name)

    try:
        wb.close()
        openFile(file_name)
    except Exception as e:
        print(e)


# def long_cel(val):
#     list_char = []
#     while len(val) > 20:
#         c = True
#         print(len(val))
#         list_char.append(val[:20])
#         val = val[20:]
#     list_char.append(val)
#     print(list_char, "val")
#     return list_char

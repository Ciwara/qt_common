#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Autor: Fadiga

from __future__ import absolute_import, division, print_function, unicode_literals

from .models import Settings, Version


class AdminFixture(object):
    LIST_CREAT = [Version(number=1), Settings()]

    def create_all_or_pass(self):
        print("---- Init fixture -----")

        for f in self.LIST_CREAT:
            try:
                f.save()
            except Exception as e:
                print(e)

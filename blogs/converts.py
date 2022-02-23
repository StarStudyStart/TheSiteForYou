# /bin/bash/python3
# -*- coding:utf8 -*-
# @Time: 2022/1/14 23:31

class FilterConverts:
    regex = 'tag|category|archive'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return '%s' % value

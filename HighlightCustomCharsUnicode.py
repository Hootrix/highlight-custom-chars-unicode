#!/usr/bin/python
# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import json
import cgi,re

class HighlightCustomCharsUnicode(sublime_plugin.EventListener): 
    def on_activated(self, view):
        self.get_settings()
        self.view = view
        self.phantom_set = sublime.PhantomSet(view)
        # highlight custom characters
        self.highlight()

    def get_settings(self):
        settings = sublime.load_settings('HighlightCustomCharsUnicode.sublime-settings')

        self.highlight_color = settings.get('highlight_color') or 'purplish'
        self.regex_chars_list = settings.get('chars_regex')
        self.highlight_text = settings.get('highlight_text')

        if isinstance(self.regex_chars_list, list):
            self.regex_chars_list = ''.join(self.regex_chars_list)

        if self.regex_chars_list is None:
            self.regex_chars_list = ''

        # for some reason the sublime.IGNORECASE -flag did not work so lets
        # duplicate the chars as lower and upper :(
        # self.regex_chars_list = self.regex_chars_list.upper()
        

    def on_modified_async(self, view):
        self.highlight()

    def highlight(self):
        if self.view.settings().get('terminus_view'):
            return
        phantoms = []
        # 默认的宽度字符正则
        default_chars = u'\u200B-\u200F\uFEFF\u00AD\u2060\u202A-\u202E'
        if not self.regex_chars_list:
            self.regex_chars_list = default_chars
        find_chars = '['+self.regex_chars_list+']'
        # search the view
        for char_pos in self.view.find_all(find_chars):

            # 读取字符所在行的位置范围
            line_range_pos = self.view.lines(char_pos)
            pos = char_pos
            if line_range_pos:
                line_range_pos = line_range_pos[0]
                # line_range_pos.a 表示行首位置
                # line_range_pos.b 表示行尾位置
                if line_range_pos.a == pos.a and line_range_pos.b != pos.b: #or line_range_pos.b == pos.b:
                    pos = sublime.Region(pos.a+1, pos.b+1)
            char_unicode_str = json.dumps([self.view.substr(char_pos)], ensure_ascii=True)
            char_unicode_str = re.sub(r'^\["(.*)"\]$',r'\1',char_unicode_str)
            char_unicode_str = re.sub(r'^\\u','',char_unicode_str)
            char = char_unicode_str
            # char = char_unicode_str.lstrip('["').rstrip('"]').lstrip(r'\u')
            char_unicode_str = cgi.escape(self.highlight_text.replace(r'{$char}',char)) 
            phantoms.append(sublime.Phantom(pos, '<span style="color: var(--%s);">%s</span>' % (self.highlight_color,char_unicode_str), sublime.LAYOUT_INLINE))

        # 高亮显示查找到的字符unicode编码
        self.phantom_set.update(phantoms)

"""
dnscraper
Copyright (C) 2018 Thomas Leyh <thomas.leyh@mailbox.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import lxml.html as lhtml


def get_html_element_from_string(html: str):
    return lhtml.fragment_fromstring(html)


def remove_elements_with_class(class_name: str, html_element: lhtml.Element):
    class_elements = html_element.find_class(class_name)
    for element in class_elements:
        element.getparent().remove(element)
    return html_element


def remove_author_and_date(html_element: lhtml.Element):
    author_and_date_element = html_element.find("i")
    html_element.remove(author_and_date_element)
    return html_element

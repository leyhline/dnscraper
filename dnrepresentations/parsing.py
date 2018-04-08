from datetime import datetime
import re
import lxml.html as lhtml


class ForumPost:
    _re_author_and_date = re.compile(r"""Geschrieben von (.*) am (.*) um (.*):""")
    
    def __init__(self, element: lhtml.Element):
        self.element = element
        self.author_and_date_element = None
        
    def parse_author_and_date(self):
        if self.author_and_date_element is None:
            self.author_and_date_element = self.element.find("i")
        author_and_date_string = self.author_and_date_element.text_content()
        match = self._re_author_and_date.match(author_and_date_string)
        self.author, date, time = match.groups()
        self.datetime = datetime.strptime(date + " " + time, "%d.%m.%Y %H:%M")
        
    def clean(self):
        if self.author_and_date_element is None:
            self.author_and_date_element = self.element.find("i")
        self.element.remove(self.author_and_date_element)
        self._remove_class("quote")
        self._remove_class("quotecontent")
        
    def _remove_class(self, class_name: str):
        class_elements = self.element.find_class(class_name)
        for element in class_elements:
            element.getparent().remove(element)
    
    @property
    def xml(self):
        return lhtml.etree.tostring(self.element)
    
    @property
    def content(self):
        return self.element.text_content()
    

def construct_cleaned_post(element: lhtml.Element) -> ForumPost:
    """Automatically construct, parse and clean a ForumPost."""
    post = ForumPost(element)
    post.parse_author_and_date()
    post.clean()
    return post


class ForumThread:
    _re_title = re.compile(r"""(.*) - Komplett | """)
    
    def __init__(self, filename_url_or_file):
        self.path = filename_url_or_file
        self.posts = []
        self.title = ""
        
    def parse(self):
        etree = lhtml.parse(self.path)
        root = etree.getroot()
        title = root.head.find("title")
        match = self._re_title.match(title.text)
        self.title = match.group(1)
        post_elements = root.cssselect("html > body > div.normalfont")
        for element in post_elements:
            post = construct_cleaned_post(element)
            self.posts.append(post)

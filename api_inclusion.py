import re, requests
from bs4 import BeautifulSoup
from urlparse import urlparse
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

import sys
reload(sys)
sys.setdefaultencoding('utf8')

#API_INCLUDE_TAG = re.compile(r'\[!\[[\w ]+\]\(https:\/\/www.mbed.com\/embed\/\?type=library\)\]\([\w:/.-]+\)')
API_INCLUDE_TAG = re.compile(r'\[!\[[\w ]+\]\(https:\/\/www.mbed.com\/embed\/\?type=library[\w:/.&=-]*\)\]\([\w:/.&=-]+\)')


class ApiInclusionPreprocessor(Preprocessor):
    #modal_id = 0 # Each modal in the document needs a unique id

    # def get_import_button(self, url):
    #     v2_url = self.get_v2_import_url(url)
    #     v3_url = url
    #     button = (
    #         '<a href="#" data-reveal-id="chooseIDEModal-API-%s" style="float:right; color:white;" class="button">Import into IDE</a>'
    #         '<div id="chooseIDEModal-API-%s" class="reveal-modal" data-reveal aria-labelledby="modalTitle" aria-hidden="true" role="dialog">'
    #         '    <h2 id="modalTitle">Choose mbed IDE to import into</h2>'
    #         '    <a href="%s" class="button" target="_blank">mbed Studio</a>'
    #         '    <a href="%s" class="button" target="_blank">mbed classic</a>'
    #         '    <a class="close-reveal-modal" aria-label="Close">&#215;</a>'
    #         '</div>' % (self.modal_id, self.modal_id, v3_url, v2_url)
    #     )
    #     self.modal_id += 1
    #     return button

    def get_v2_import_url(self, url):
        '''
        button 1: https://docs.mbed.com/docs/mbed-drivers-api/en/latest/api/classmbed_1_1DigitalOut.html
        button 2: https://developer.mbed.org/users/mbed_official/code/mbed/docs/082adc85693f/
        https://developer.mbed.org/compiler/#import:/users/mbed_official/code/mbed/builds/082adc85693f;mode:lib
        '''
        parsed_url = urlparse(url)
        if 'developer.mbed.' in parsed_url.netloc:
            path = parsed_url.path.split('/')
            user = path[2]
            project = path[4]
            build = path[6]
            import_url = 'https://developer.mbed.org/compiler/#import:/users/%s/code/%s/builds/%s;mode:lib' % (user, project, build)
            return import_url
        elif 'docs.mbed.' in parsed_url.netloc:
            return ''
        else:
            return ''

    def get_import_button(self, url):
        import_url = self.get_v2_import_url(url)
        if import_url:
            return '<a href="%s" style="float:right; color:white;" class="button" target="_blank">Import library</a>' % import_url
        return ''

    def fix_link(self, api_url, filename):
        '''
        Doxygen generates relative urls. Need to create absolute urls for links.
        '''
        api_docs_url, _ = api_url.rsplit('/', 1)
        return api_docs_url + '/' + filename

    def get_api_snippet(self, url, soup):
        filename = url.split('/')[-1]
        api_snippets = []
        if filename.startswith('class'):
            api_snippets = soup.find_all('table', class_="memberdecls")  #returns all of the valid sections
            if not api_snippets:
                api_snippets = soup.find('div', class_="fragment")
                api_snippets = [str(api_snippets).encode('utf-8')]
            else:
                for snippet in api_snippets:
                    for tr in snippet.find_all('tr', class_=re.compile('separator')):
                        tr.extract()
                    for a in snippet.find_all('a', class_='el'):
                        a['href'] = self.fix_link(url, a['href'])
                        a['target'] = '_blank'
                    for img in snippet.find_all('img'):
                        img['src'] = self.fix_link(url, img['src'])

            api_snippet = ""
            for snippet in api_snippets:
                api_snippet = api_snippet + str(snippet).encode('utf-8')
        elif filename.find("source.html") != -1:
            soup = soup.find('div', class_="fragment")
            for span in soup.findAll('span', class_='lineno'):
                span.extract()
            api_snippet = str(soup).encode('utf-8')
            api_snippet = '<pre> <code class="cpp hljs">' + api_snippet + '</code> </pre>'
        return api_snippet

    def build_api_block(self, url):
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            soup = BeautifulSoup(response.text)
            try:
                title = soup.find('div', class_='title').contents[0] # Standard doxygen page
            except AttributeError: # mbed Doxygen page
                htmltitle = soup.find('div', class_='headertitle')
                #if h1 in htmltitle:
                title = htmltitle.h1.string
                #else:
                #    title = ""
            filename = url.split('/')[-1]
            api_header = '<div class="api-header"><a href=%s target="_blank"><i class="fa fa-folder-o"></i> <b class="filename">%s</b></a>' % (url, title) + self.get_import_button(url) + '</div>'
            api_block = '<div class="api-include-block">' + api_header + self.get_api_snippet(url, soup) + '</div>'

            return api_block.replace('\n', ' ').replace('\r', '')

    def run(self, lines):
        new_lines = []
        prev_line = ''
        for line in lines:
            m = API_INCLUDE_TAG.match(line)
            if m:
                urls = re.findall(r'\([\w:/.?=-]+\)', m.group())
                api_url = urls[1][1:-1]
                api_block = self.build_api_block(api_url)
                if api_block:
                    new_lines.append(api_block)
            else:
                new_lines.append(line)
            prev_line = line
        return new_lines


class Inclusion(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('api_inclusion', ApiInclusionPreprocessor(md), '>normalize_whitespace')


def makeExtension(*args, **kwargs):
    return Inclusion(*args, **kwargs)

from django import template
register = template.Library()
from django.utils.html import format_html

@register.simple_tag
def countpage(cupage, sumpage):
    startpage = cupage - 2
    endpage = cupage + 2
    while(startpage < 1):
        startpage += 1
        endpage += 1
    while(endpage > sumpage):
        endpage -= 1
        if(startpage > 1):
            startpage -= 1
    pagestr = ''
    for i in range(startpage, endpage+1):
        if(i == cupage):
            pagestr = pagestr + '<li class="paginate_button active" aria-controls="dataTables-example" tabindex="0"><a href="?page=%s">%s</a></li>'%(i, i)
        else:
            pagestr = pagestr + '<li class="paginate_button" aria-controls="dataTables-example" tabindex="0"><a href="?page=%s">%s</a></li>' % (i, i)
    return format_html(pagestr)
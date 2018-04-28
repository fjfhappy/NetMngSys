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


htmlstr = ""
def dodrawtree(treelist):
    global htmlstr
    htmlstr += '<li>'
    htmlstr += '<span>%s</span>' % treelist[0][0]
    if(treelist[0][1] == 0):
        htmlstr += '<em style="color: #F00">SNMP错误，推测连至网关</em>'
    elif (treelist[0][1] == 2):
        htmlstr += '<em style="color: #F00">计算信息不足，推测连至网关</em>'
    if(len(treelist) > 0):
        htmlstr += '<ul>'
        for i in range(1, len(treelist)):
            dodrawtree(treelist[i])
        htmlstr += '</ul>'
    htmlstr += '</li>'



@register.simple_tag
def drawtree(treelist):
    global htmlstr
    dodrawtree(treelist)
    return format_html(htmlstr)
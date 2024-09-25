
import markdown
from weasyprint import HTML


def textToPDF(markdown_text: str, outputFileName="output.pdf"):
    html_content = markdown.markdown(markdown_text)

    html = HTML(string=html_content)

    pdfFileName = outputFileName

    html.write_pdf(pdfFileName)

    return pdfFileName

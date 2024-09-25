
from markdown_pdf import MarkdownPdf, Section


def text_to_pdf(markdown_text: str, output_filename: str = "output.pdf"):
    pdf = MarkdownPdf()
    pdf.add_section(Section(markdown_text, toc=False))
    pdf.save(output_filename)
    return output_filename

from docling.document_converter import DocumentConverter

source = "./ragtest/cd/666.pdf"  # document per local path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())

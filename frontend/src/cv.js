// Reads a CV in the browser. Nothing is uploaded: the file never leaves the visitor's computer.
// The PDF and Word readers are loaded only when someone actually adds a CV, to keep the page fast.

export async function readCv(file) {
  const name = file.name.toLowerCase()
  const buffer = await file.arrayBuffer()

  if (name.endsWith('.pdf')) {
    const pdfjs = await import('pdfjs-dist')
    const workerUrl = (await import('pdfjs-dist/build/pdf.worker.min.mjs?url')).default
    pdfjs.GlobalWorkerOptions.workerSrc = workerUrl
    const doc = await pdfjs.getDocument({ data: buffer }).promise
    const pages = []
    for (let i = 1; i <= doc.numPages; i++) {
      const content = await (await doc.getPage(i)).getTextContent()
      pages.push(content.items.map((item) => item.str).join(' '))
    }
    return pages.join('\n')
  }

  if (name.endsWith('.docx')) {
    const mammoth = (await import('mammoth/mammoth.browser.js')).default
    const result = await mammoth.extractRawText({ arrayBuffer: buffer })
    return result.value
  }

  if (name.endsWith('.txt') || name.endsWith('.md')) {
    return new TextDecoder().decode(buffer)
  }

  throw new Error('Please use a PDF, a Word (.docx) file, or paste the text.')
}

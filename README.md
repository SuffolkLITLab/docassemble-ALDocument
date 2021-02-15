# docassemble.ALDocument

A package to help manage docassemble interviews that assemble multiple documents.

ALDocument is a single object that represents a document with a "preview"
version (perhaps without a signature) and a "final" version, as well as an
addendum, which is often needed for PDF forms.

The ALAddendumFieldDict object is an ordered dict that stores a collection of field names, together with a
character/item limit. The ALDocument uses this list to automatically include
an addendum when it is needed. One addendum template can easily be shared
across multiple documents that your interview assembles.

ALDocumentBundle is an object that can represent a list of ALDocuments in
a structured order. One interview may mix and match the same templates into
multiple "bundles". E.g., one set of cover instructions might be sent to the 
user and one to the court. Bundles also handle ALDocuments that are "enabled" or
"disabled". You may allow the user to control which documents are assembled 
manually, or the interview logic might control which documents ultimately are
assembled. The ALDocumentBundle will handle assembling just the "enabled"
documents. Bundles can be nested for convenience.

ALDocumentBundle.download_buttons_html() generates a table with download/view
buttons for the generated document, a slightly neater format than the 
docassemble default when there is a larger list of documents.

This package is deprecated; the functionality has been migrated to 
https://github.com/SuffolkLITLab/docassemble-AssemblyLine

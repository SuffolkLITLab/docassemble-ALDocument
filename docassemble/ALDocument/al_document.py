from docassemble.base.util import DADict, DAList, DAObject, DAFile, DAFileCollection, DAFileList, pdf_concatenate

class ALAddendum(DAObject):
  pass

class ALDocument(DADict):
  """
  An opinionated collection of typically three attachment blocks:
  1. The final version of a document, at typical key "final"
  2. The preview version of a document, at typical key "preview"
  2.5 Any alternate versions of the document, at any key other than 'addendum'
  3. An addendum of a document, at mandatory key "addendum"
  
  Each form that an interview generates will get its own ALDocument object.
  
  This should really relate to one canonical document in different states. Not multiple
  unrelated output documents that might get delivered together, except the addendum.
  
  The "addendum" key will typically be handled in a generic object block.
  Multiple documents can use the same addendum template, with just the case caption
  varying.
  
  The "filename" attribute will be used to name PDFs.
  
  The "enabled" attribute is used to control whether this form is used in this run
  of the interview.
  
  The optional "need_addendum" attribute controls whether the addendum is needed for this
  run of the interview. It will not be triggered if it is not defined (e.g., for a docx file,
  this is never needed).
  """
  def init(self, *pargs, **kwargs):
    super(ALDocument, self).init(*pargs, **kwargs)
 
  def as_pdf(self, key='final'):
    return pdf_concatenate(self.as_list(), filename=self.filename)

  def as_list(self, key='final'):
    if hasattr(self, 'need_addendum') and self.need_addendum:
      return [self[key], self['addendum']]
    else:
      return [self[key]]

class ALDocumentBundle(DAList):
  """
  Object representing a bundle of ALDocuments in a specific order. Used when
  it is helpful to deliver a single, printable collection of multiple templates to an enduser.
  You may use multiple bundles when each bundle gets used by the end user in different forums
  or at different times. E.g., one goes to the opposing party, one only to the court (such as
  impounded address or fee waiver).
  
  A bundle can contain nested bundles in the `templates` list.
  
  E.g., main_form, optional_motion1, optional_motion2
  
  required attribute: filename
  optional attribute: enabled
  required attribute: templates: a list of ALDocuments or ALBundles
  """
  def init(self, *pargs, **kwargs):
    super(ALDocumentBundle, self).init(*pargs, **kwargs)
    self.auto_gather=False
    self.gathered=True
    # self.initializeAttribute('templates', ALBundleList)
    
  def as_pdf(self, key='final'):
    return pdf_concatenate(self.as_flat_list(key=key), filename=self.filename)
  
  def as_flat_list(self, key='final'):
    """
    Returns the nested bundle as a single flat list.
    """
    # Iterate through the list of self.templates
    # If this is a simple document node, check if this individual template is enabled.
    # Otherwise, call the bundle's as_list() method to show all enabled templates.
    # Unpack the list of documents at each step so this can be concatenated into a single list
    flat_list = []
    for document in self:
      if isinstance(document, ALDocumentBundle):
        flat_list.extend(document.as_list(key=key))
      elif document.enabled: # base case
        flat_list.extend(document.as_list(key=key))
                         
    return flat_list
 
  def as_pdf_list(self, key='final'):
    """
    Returns the nested bundles as a list of PDFs that is only one level deep.
    """
    return [document.as_pdf(key=key) for document in self.templates]
    
class ALDocumentBundleDict(DADict):
  """
  A dictionary with named bundles of ALDocuments.
  In the assembly line, we expect to find two predetermined bundles:
  court_bundle and user_bundle.
  
  It may be helpful in some circumstances to have a "bundle" of bundles. E.g.,
  you may want to present the user multiple combinations of documents for
  different scenarios.
  """
  def init(self, *pargs, **kwargs):
    super(ALBundleList, self).init(*pargs, **kwargs)
    self.auto_gather=False
    self.gathered=True
    self.object_type = ALBundle
    if not hasattr(self, 'gathered'):
      self.gathered = True
    if not hasattr(self, 'auto_gather'):
      self.auto_gather=False

  def preview(format='PDF', bundle='user_bundle'):
    """
    Create a copy of the document as a single PDF that is suitable for a preview version of the 
    document (before signature is added).
    """
    return self[bundle].as_pdf(key='preview', format=format)
  
  def as_attachment(format='PDF', bundle='court_bundle'):
    """
    Return a list of PDF-ified documents, suitable to make an attachment to send_mail.
    """
    return self[bundle].as_pdf_list(key='final')
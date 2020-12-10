from docassemble.base.util import DADict, DAList, DAObject, DAFile, DAFileCollection, DAFileList, defined, value, pdf_concatenate, DAOrderedDict

class ALAddendumField(DAObject):
  """
  Required attributes:
    - field_name->str represents the name of a docassemble variable
    - field_style->"list"|"table"|"string" (optional: defaults to "string")
    - overflow_trigger->int
  Optional:    
    - headers->dict(attribute: display label for table)
  """
  def init(self, *pargs, **kwargs):
    super(ALAddendumField, self).init(*pargs, **kwargs)

  def overflow_value(self):
    """
    Try to return just the portion of the variable (list-like object or string)
    that exceeds the overflow trigger. Otherwise, return empty string.
    """
    try:
      if len(self.value_if_defined()) > self.overflow_trigger:
        return self.value_if_defined()[self.overflow_trigger:]
      else:
        return ""
    except:
      return ""

  def safe_value(self):
    """
    Try to return just the portion of the variable
    that is _shorter than_ the overflow trigger. Otherwise, return empty string.
    """
    try:
      if len(self.value_if_defined()) > self.overflow_trigger:
        return self.value_if_defined()[:self.overflow_trigger]
      else:
        return self.value_if_defined()
    except:
      return ""
    
    
  def value_if_defined(self):
    """
    Return the value of the field if it is defined, otherwise return an empty string.
    """
    if defined(self.field_name):
      return value(self.field_name)
    return ""
  
  def __str__(self):
    return str(self.value_if_defined())
    
  def columns(self):
    """
    Return a list of the columns in this object.
    """
    if hasattr(self, headers):
      return self.headers
    else:
      return [] # TODO

class ALAddendumFieldDict(DAOrderedDict):
  """
  optional:
    - style: if set to "overflow_only" will only display the overflow text
  """
  def init(self, *pargs, **kwargs):
    super(ALAddendumFieldDict, self).init(*pargs, **kwargs)  
    self.object_type = ALAddendumField
    self.auto_gather=False
    if not hasattr(self, 'style'):
      self.style = 'overflow_only'
    if hasattr(self, 'data'):
      self.from_list(data)
      del self.data      
  
  def from_list(self, data):
    for entry in data:
      new_field = self.initializeObject(entry['field_name'], ALAddendumField)
      new_field.field_name = entry['field_name']
      new_field.overflow_trigger = entry['overflow_trigger']
      
  def defined_fields(self, style='overflow_only'):
    """
    Return a filtered list of just the defined fields.
    If the "style" is set to overflow_only, only return the overflow values.
    """
    if style == 'overflow_only':
      return [field for field in self.elements.values() if defined(field.field_name) and len(field.overflow_value())]
    else:
      return [field for field in self.elements.values() if defined(field.field_name)]
    
  #def defined_sections(self):
  #  if self.style == 'overflow_only':    
  #    return [section for section in self.elements if len(section.defined_fields(style=self.style))]
  
class ALDocument(DADict):
  """
  An opinionated collection of typically three attachment blocks:
  1. The final version of a document, at typical key "final"
  2. The preview version of a document, at typical key "preview"
  3. An addendum of a document, at the attribute `addendum`
  
  Each form that an interview generates will get its own ALDocument object.
  
  This should really relate to one canonical document in different states. Not multiple
  unrelated output documents that might get delivered together, except the addendum.
  
  The "addendum" attribute will typically be handled in a generic object block.
  Multiple documents can use the same addendum template, with just the case caption
  varying.
  
  Required attributes:
    - filename: name used for output PDF
    - enabled
    - has_addendum: set to False if the document never has overflow, so docassemble does not 
                    seek the optional "need_addendum" attribute
  
  Optional attribute:
    - addendum: an attachment block
    - addendum_fields
  
  """
  def init(self, *pargs, **kwargs):
    super(ALDocument, self).init(*pargs, **kwargs)
    self.initializeAttribute('overflow_fields',ALAddendumFieldDict)
 
  def as_pdf(self, key='final'):
    return pdf_concatenate(self.as_list(key=key), filename=self.filename)

  def as_list(self, key='final'):
    if self.has_addendum and self.need_addendum:
      return [self[key], self.addendum]
    else:
      return [self[key]]

class ALDocumentBundle(DAList):
  """
  DAList of ALDocuments or nested ALDocumentBundles.
  
  Use case: providing a list of documents in a specific order.
  Example:
    - Cover page
    - Main motion form
    - Notice of Interpreter Request
 
  E.g., you may bundle documents one way for the court, one way for the user, one way for the
  opposing party. ALDocuments can separately be "enabled" or "disabled" for a particular run, which
  will affect their inclusion in all bundles.
  
  A bundle can be returned as one PDF or as a list of documents. If the list contains nested
  bundles, each nested bundle can similarly be returned as a combined PDF or a list of documents.
  
  required attributes: 
    - filename
  optional attribute: enabled
  """
  def init(self, *pargs, **kwargs):
    super(ALDocumentBundle, self).init(*pargs, **kwargs)
    self.auto_gather=False
    self.gathered=True
    # self.initializeAttribute('templates', ALBundleList)
    
  def as_pdf(self, key='final'):
    return pdf_concatenate(self.as_flat_list(key=key), filename=self.filename)
  
  def preview(self):
    return self.as_pdf(key='preview')
  
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
    return [document.as_pdf(key=key) for document in self]
  
  def as_html(self, key='final'):
    pass
    
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
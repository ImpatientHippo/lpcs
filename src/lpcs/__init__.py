
from arpeggio import (
  Optional, ZeroOrMore, OneOrMore, ParserPython, EOF,
  PTNodeVisitor, visit_parse_tree
)
from arpeggio import RegExMatch as _

### Grammar
def save_file():   return header, "\n", ZeroOrMore(line), EOF
def line():        return assignment, _(r"\s*\n") 

def header():      return '#3:2'
def assignment():  return var_name, _(r"\s+"), lpc_value
def var_name():    return _("[a-zA-Z_][a-zA-Z0-9_]*")
def lpc_value():   return [ number , str_literal, array, mapping, struct, lwobject, closure, ref ]
def space():       return _(r"\s")

def ref():         return "<", _(r"[0-9]+"), ">", Optional(anchor)
def anchor():      return "=", lpc_value

def array():       return "({" , ZeroOrMore( lpc_value, "," ), "})"
def mapping():     return "([", ZeroOrMore( entry, "," ), "])"
def entry():       return lpc_value, ":", lpc_value, ZeroOrMore( ";", lpc_value )
def struct():      return "(<", str_literal, ",", ZeroOrMore( lpc_value, "," ), ">)"
def lwobject():    return "(*", str_literal, ",", ZeroOrMore( lpc_value, "," ), "*)"
def number():      return _(r"-?\d+(\.\d+)?([eE]-?\d+)?")
def str_literal(): return '"', _(r'([^"\\\n]|\\.)*'), '"'
def closure():     return "#'", var_name

### Analysis
class SaveFile(PTNodeVisitor):

  refs = {}

  def visit_number(self,node,children):
    if "." in node.value or "e" in node.value or "E" in node.value:
      return float(node.value)
    return int(node.value)

  def visit_str_literal(self,node,children):
    return unescape(children[0])

  def visit_closure(self,node,children):
    return "#'"+children[0]

  def visit_array(self,node,children):
    return [ c for c in children ]

  def visit_lpc_value(self,node,children):
    return children[0]

  def visit_entry(self,node,children):
    return children

  def visit_mapping(self,node,children):
    return { c[0]: c[1:] for c in children }

  def visit_assignment(self,node,children):
    return [ children[0], children[2] ]

  def visit_struct(self,node,children):
    return Struct( children )

  def visit_lwobject(self,node,children):
    return LWObject( children )

  def visit_save_file(self,node,children):
    return { a[0]: a[1] for a in children }

  def visit_line(self,node,children):
    return children[0]

  def visit_anchor(self,node,children):
    return children[0]

  def visit_ref(self,node,children):
    if len(children)>1:
      self.refs[children[0]] = children[1]
      return children[1]
    return Ref(self,children[0])

class Ref:
  """
    Wrapper for a reference inside a save_file.
  """
  def __init__(self,context:SaveFile,key:str):
    self.context = context
    self.key = key

  def deref(self) -> any:
    return self.context.refs[self.key]

  def __lpc_dump__(self) -> str:
    return _lpc_dumps_value( self.deref() )

class Struct:
  """
    Wrapper class for LPC Structs.
    Members are
    * params list of arguments, starting with the description string
  """
  def __init__(self,params:[str]):
    self.params = [ p for p in params ]

  def __lpc_dump__(self) -> str:
    return "(<" + "".join([ _lpc_dumps_value(e)+"," for e in self.params ]) + ">)"

  def __len__( self ) -> int:
    return len(self.params)

  def __getitem__( self, idx: int ) -> any:
    return self.params[idx]

  def __setitem__( self, idx: int, value: any ) -> None:
    self.params[ idx ] = value

class LWObject:
  """
    Wrapper class for LPC Lightweight Objects.
    Members are
    * params list of arguments, starting with the description string
  """
  def __init__(self,params:[str]):
    self.params = [ p for p in params ]

  def __lpc_dump__(self) -> str:
    return "(*" + "".join([ _lpc_dumps_value(e)+"," for e in self.params ]) + "*)"

  def __len__( self ) -> int:
    return len(self.params)

  def __getitem__( self, idx: int ) -> any:
    return self.params[idx]

  def __setitem__( self, idx: int, value: any ) -> None:
    self.params[ idx ] = value


def lpc_loads( data: str ) -> any:
  """
    Transform string content of a savefile into pythonic
    datastructure. Note that mappings end up as dicts with
    an array as value, because mappsings my have more than
    one value.
  """
  return visit_parse_tree( parser.parse(data), SaveFile() )

def _dump_map_entry( e ):
  return ";".join([ _lpc_dumps_value(v) for v in e ])

def _lpc_dumps_value( value ):
  t = type(value)
  if t in [ int ,float ]:
    return str(value)
  if t is str:
    return '"'+escape(str(value))+'"'
  if t is list:
    return "({" + "".join([ _lpc_dumps_value(e)+"," for e in value ]) + "})"
  if t is dict:
    return "([" + "".join([ f'"{k}":{_dump_map_entry(v)},' for k,v in value.items() ]) + "])"
  if hasattr(value,"__lpc_dump__"):
    return value.__lpc_dump__()
  raise ValueError( f"unexpected type {t}" )

def lpc_dumps( data: any ) -> str:
  """
    Create String content of a savefile for data.
  """
  text = "#3:2\n"
  for name,value in data.items():
    text += name + " " + _lpc_dumps_value(value) + "\n"
  return text

def lpc_load( file:str ) -> str:
  """
    Loads savefile and returns datastructure.
  """
  with open(file,"r") as f:
    return lpc_loads( f.read() )

def lpc_dump( file: str, data:any ) -> None:
  """
    Saves Datastructure from data to file.
  """
  with open(file,"w") as f:
    f.write(lpc_dumps(data))

def unescape( text: str ) -> str:
  """
    Simple Version of escaping special chars in strings.
    handles \n, \ and " only.
  """
  res = ""
  esc = False
  for c in text:
    if esc:
      if c=="n":
        res += "\n"
      elif c=='"':
        res += '"'
      else:
        res += c
      esc = False
    elif c=="\\":
      esc = True
    else:
      res += c
  if esc:
    raise ValueError( "String ends with incomplete \\" )
  return res
  
def escape( text: str ) -> str:
  """
    Simple Version of escaping special chars in strings.
    handles \n, \ and " only.
  """
  return text.replace( "\\", "\\\\" ).replace( "\n", "\\n" ).replace( "\"", "\\\"" )

parser = ParserPython(save_file,skipws=False)


/* Generated By:JavaCC: Do not edit this line. DDSParser.java */
package dods.dap.parser;
import java.util.Stack;
import dods.dap.*;

public class DDSParser implements DDSParserConstants {
  /* $Id: DDSParser.java,v 1.27 2002/06/05 20:44:51 jimg Exp $ */
  private DDS dds;
  private BaseTypeFactory factory;  // used to construct new types
  private Stack ctor;        // stack for ctor types
  private BaseType current;
  private int part;          // part is defined in each type which uses it
  private String id;

  private static final String noDDSMsg =
"The descriptor object returned from the dataset was null\n" +
"Check that the URL is correct.";

    /** Add the variable pointed to by CURRENT to either the topmost ctor
	object on the stack CTOR or to the dataset variable table TABLE if
	CTOR is empty. If it exists, the current ctor object is poped off the
	stack and assigned to CURRENT.

	NB: the ctor stack is popped for lists and arrays because they are
	ctors which contain only a single variable. For other ctor types,
	several varaiables may be members and the parse rule (see
	`declaration' above) determines when to pop the stack. */
    private void addEntry() {
        if (!ctor.empty()) {  // must be parsing a ctor type
            if (ctor.peek() instanceof DVector) {
                DVector top = (DVector)(ctor.peek());
                top.addVariable(current);
                current = (BaseType)(ctor.pop());
            }
            else if (ctor.peek() instanceof DConstructor) {
                DConstructor top = (DConstructor)(ctor.peek());
                if (top instanceof DGrid)
                    top.addVariable(current, part);
                else
                    top.addVariable(current);
            }
        }
        else {
            dds.addVariable(current);
        }
    }

    /** A helper function to throw a common exception */
    private void throwBad(String s1) throws BadSemanticsException {
        throw new BadSemanticsException("In the dataset descriptor object:\n"
                               + "`" + s1 + "' is not a valid declaration.");
    }

    /** A helper function to throw a common exception */
    private void throwBad(String s1, String s2) throws BadSemanticsException {
        throw new BadSemanticsException("In the dataset descriptor object:\n"
                      + "`" + s1 + " " + s2 + "' is not a valid declaration");
    }

    /** A helper function to check semantics and add a DDS entry */
    private void checkAdd(String s1) throws BadSemanticsException {
        try {
            current.checkSemantics();
            addEntry();
        }
        catch (BadSemanticsException e) {
            throwBad(s1);
        }
    }

    /** A helper function to check semantics and add a DDS entry */
    private void checkAdd(String s1, String s2) throws BadSemanticsException {
        try {
            current.checkSemantics();
            addEntry();
        }
        catch (BadSemanticsException e) {
            throwBad(s1, s2);
        }
    }

    /** A helper to check if the word matches a given keyword. 
	@param keyword The lower case to test against.
	@param word Does this match keyword? (Case folded to lower.) */
    private boolean isKeyword(String word, String keyword) {
        return keyword.equalsIgnoreCase(word);
    }

  final public void Dataset(DDS dds, BaseTypeFactory factory) throws ParseException, DDSException {
    this.dds = dds;
    this.factory = factory;
    this.ctor = new Stack();
    switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
    case DATASET:
      jj_consume_token(DATASET);
      jj_consume_token(21);
      Declarations();
      jj_consume_token(22);
      Name();
      jj_consume_token(23);
      break;
    default:
      jj_la1[0] = jj_gen;
      error(noDDSMsg);
    }
  }

  final public void Declarations() throws ParseException, DDSException {
    label_1:
    while (true) {
      switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
      case LIST:
      case SEQUENCE:
      case STRUCTURE:
      case GRID:
      case BYTE:
      case INT16:
      case UINT16:
      case INT32:
      case UINT32:
      case FLOAT32:
      case FLOAT64:
      case STRING:
      case URL:
        ;
        break;
      default:
        jj_la1[1] = jj_gen;
        break label_1;
      }
      Declaration();
    }
  }

  final public void Declaration() throws ParseException, DDSException {
    String s1, s2;
    switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
    case LIST:
      s1 = List();
      s2 = NonListDecl();
        checkAdd(s1, s2);
      break;
    case SEQUENCE:
    case STRUCTURE:
    case GRID:
    case BYTE:
    case INT16:
    case UINT16:
    case INT32:
    case UINT32:
    case FLOAT32:
    case FLOAT64:
    case STRING:
    case URL:
      NonListDecl();
      break;
    default:
      jj_la1[2] = jj_gen;
      jj_consume_token(-1);
      throw new ParseException();
    }
  }

// This non-terminal is here only to keep types like `List List Int32' from
// parsing. DODS does not allow Lists of Lists. Those types make translation
// to/from arrays too hard.
  final public String NonListDecl() throws ParseException, DDSException {
    String s1=null, s2=null;
    Token t;
    try {
      switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
      case BYTE:
      case INT16:
      case UINT16:
      case INT32:
      case UINT32:
      case FLOAT32:
      case FLOAT64:
      case STRING:
      case URL:
        s1 = BaseType();
        s2 = Var();
        jj_consume_token(23);
             checkAdd(s1, s2);
             {if (true) return s2;}
        break;
      case STRUCTURE:
        Structure();
        jj_consume_token(21);
        Declarations();
        jj_consume_token(22);
             current = (BaseType)ctor.pop();
        s1 = Var();
        jj_consume_token(23);
             checkAdd(s1);
             {if (true) return s1;}
        break;
      case SEQUENCE:
        Sequence();
        jj_consume_token(21);
        Declarations();
        jj_consume_token(22);
             current = (BaseType)ctor.pop();
        s1 = Var();
        jj_consume_token(23);
             checkAdd(s1);
             {if (true) return s1;}
        break;
      case GRID:
        Grid();
        jj_consume_token(21);
        t = jj_consume_token(WORD);
        jj_consume_token(24);
             if (isKeyword(t.image, "array"))
                 part = DGrid.ARRAY;
             else
                 error("\nParse error: Expected the keyword \"Array:\"\n"
                       + "but found: " + t.image + " instead.");
        Declaration();
        t = jj_consume_token(WORD);
        jj_consume_token(24);
             if (isKeyword(t.image, "maps"))
                 part = DGrid.MAPS;
             else
                 error("\nParse error: Expected the keyword \"Maps:\"\n"
                       + "but found: " + t.image + " instead.");
        Declarations();
        jj_consume_token(22);
             current = (BaseType)ctor.pop();
        s1 = Var();
        jj_consume_token(23);
             checkAdd(s1);
             {if (true) return s1;}
        break;
      default:
        jj_la1[3] = jj_gen;
        jj_consume_token(-1);
        throw new ParseException();
      }
    } catch (ParseException e) {
        error("\nParse Error on token: " + s1 + "\n"
              + "In the dataset descriptor object:\n"
              + "Expected a variable declaration (e.g., Int32 i;).");
    }
    throw new Error("Missing return statement in function");
  }

  final public String List() throws ParseException {
    Token t;
    t = jj_consume_token(LIST);
        ctor.push(factory.newDList());
        {if (true) return t.image;}
    throw new Error("Missing return statement in function");
  }

  final public String Structure() throws ParseException {
    Token t;
    t = jj_consume_token(STRUCTURE);
        ctor.push(factory.newDStructure());
        {if (true) return t.image;}
    throw new Error("Missing return statement in function");
  }

  final public String Sequence() throws ParseException {
    Token t;
    t = jj_consume_token(SEQUENCE);
        ctor.push(factory.newDSequence());
        {if (true) return t.image;}
    throw new Error("Missing return statement in function");
  }

  final public String Grid() throws ParseException {
    Token t;
    t = jj_consume_token(GRID);
        ctor.push(factory.newDGrid());
        {if (true) return t.image;}
    throw new Error("Missing return statement in function");
  }

  final public String BaseType() throws ParseException {
    Token t;
    switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
    case BYTE:
      t = jj_consume_token(BYTE);
        current = factory.newDByte();
        {if (true) return t.image;}
      break;
    case INT16:
      t = jj_consume_token(INT16);
        current = factory.newDInt16();
        {if (true) return t.image;}
      break;
    case UINT16:
      t = jj_consume_token(UINT16);
        current = factory.newDUInt16();
        {if (true) return t.image;}
      break;
    case INT32:
      t = jj_consume_token(INT32);
        current = factory.newDInt32();
        {if (true) return t.image;}
      break;
    case UINT32:
      t = jj_consume_token(UINT32);
        current = factory.newDUInt32();
        {if (true) return t.image;}
      break;
    case FLOAT32:
      t = jj_consume_token(FLOAT32);
        current = factory.newDFloat32();
        {if (true) return t.image;}
      break;
    case FLOAT64:
      t = jj_consume_token(FLOAT64);
        current = factory.newDFloat64();
        {if (true) return t.image;}
      break;
    case STRING:
      t = jj_consume_token(STRING);
        current = factory.newDString();
        {if (true) return t.image;}
      break;
    case URL:
      t = jj_consume_token(URL);
        current = factory.newDURL();
        {if (true) return t.image;}
      break;
    default:
      jj_la1[4] = jj_gen;
      jj_consume_token(-1);
      throw new ParseException();
    }
    throw new Error("Missing return statement in function");
  }

// What's going on here!? A variable's name can be either a WORD or one of
// the previously reserved words Byte, Int16, et cetera. This allows datasets
// with truly bizarre variable names to be served by DODS. 5/22/2002 jhrg
  final public String Var() throws ParseException, DDSException {
    Token t;
    switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
    case WORD:
      t = jj_consume_token(WORD);
                    current.setName(t.image);
      label_2:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[5] = jj_gen;
          break label_2;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case BYTE:
      t = jj_consume_token(BYTE);
                    current.setName(t.image);
      label_3:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[6] = jj_gen;
          break label_3;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case INT16:
      t = jj_consume_token(INT16);
                    current.setName(t.image);
      label_4:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[7] = jj_gen;
          break label_4;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case UINT16:
      t = jj_consume_token(UINT16);
                    current.setName(t.image);
      label_5:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[8] = jj_gen;
          break label_5;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case INT32:
      t = jj_consume_token(INT32);
                    current.setName(t.image);
      label_6:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[9] = jj_gen;
          break label_6;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case UINT32:
      t = jj_consume_token(UINT32);
                    current.setName(t.image);
      label_7:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[10] = jj_gen;
          break label_7;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case FLOAT32:
      t = jj_consume_token(FLOAT32);
                    current.setName(t.image);
      label_8:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[11] = jj_gen;
          break label_8;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case FLOAT64:
      t = jj_consume_token(FLOAT64);
                    current.setName(t.image);
      label_9:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[12] = jj_gen;
          break label_9;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case STRING:
      t = jj_consume_token(STRING);
                    current.setName(t.image);
      label_10:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[13] = jj_gen;
          break label_10;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case URL:
      t = jj_consume_token(URL);
                    current.setName(t.image);
      label_11:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[14] = jj_gen;
          break label_11;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case STRUCTURE:
      t = jj_consume_token(STRUCTURE);
                    current.setName(t.image);
      label_12:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[15] = jj_gen;
          break label_12;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case SEQUENCE:
      t = jj_consume_token(SEQUENCE);
                    current.setName(t.image);
      label_13:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[16] = jj_gen;
          break label_13;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case GRID:
      t = jj_consume_token(GRID);
                    current.setName(t.image);
      label_14:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[17] = jj_gen;
          break label_14;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    case LIST:
      t = jj_consume_token(LIST);
                    current.setName(t.image);
      label_15:
      while (true) {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          ;
          break;
        default:
          jj_la1[18] = jj_gen;
          break label_15;
        }
        ArrayDecl();
      }
                    {if (true) return t.image;}
      break;
    default:
      jj_la1[19] = jj_gen;
      jj_consume_token(-1);
      throw new ParseException();
    }
    throw new Error("Missing return statement in function");
  }

  final public void ArrayDecl() throws ParseException, DDSException {
    Token t= new Token();
    try {
      if (jj_2_1(3)) {
        jj_consume_token(25);
        t = jj_consume_token(WORD);
        jj_consume_token(26);
             if (current instanceof DArray) {
                 ((DArray)current).appendDim(Integer.parseInt(t.image));
             } else {
                 DArray a = factory.newDArray();
                 a.addVariable(current);
                 a.appendDim(Integer.parseInt(t.image));
                 current = a;
             }
      } else {
        switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
        case 25:
          jj_consume_token(25);
          t = jj_consume_token(WORD);
             id = t.image;
          jj_consume_token(27);
          t = jj_consume_token(WORD);
             if (current instanceof DArray) {
                 ((DArray)current).appendDim(Integer.parseInt(t.image), id);
             } else {
                 DArray a = factory.newDArray();
                 a.addVariable(current);
                 a.appendDim(Integer.parseInt(t.image), id);
                 current = a;
             }
          jj_consume_token(26);
          break;
        default:
          jj_la1[20] = jj_gen;
          jj_consume_token(-1);
          throw new ParseException();
        }
      }
    } catch (NumberFormatException e) {
        error("\nThe index: " + t.image + " is not an integer value.\n"
              + "Index values must be integers.");
    } catch (ParseException e) {
        error("\nThere was a problem parsing the DDS:\n"+
              "Expected an array subscript, but didn't find it\n\n" +
              "The offending line contains the characters: "+t.image+"\n\n"+
              "ParseException Message: \n" + e.getMessage() +"\n");
    }
  }

  final public void Name() throws ParseException, DDSException {
    Token t;
    try {
      switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
      case WORD:
        t = jj_consume_token(WORD);
                           dds.setName(t.image);
        break;
      case BYTE:
        t = jj_consume_token(BYTE);
                           dds.setName(t.image);
        break;
      case INT16:
        t = jj_consume_token(INT16);
                           dds.setName(t.image);
        break;
      case UINT16:
        t = jj_consume_token(UINT16);
                           dds.setName(t.image);
        break;
      case INT32:
        t = jj_consume_token(INT32);
                           dds.setName(t.image);
        break;
      case UINT32:
        t = jj_consume_token(UINT32);
                           dds.setName(t.image);
        break;
      case FLOAT32:
        t = jj_consume_token(FLOAT32);
                           dds.setName(t.image);
        break;
      case FLOAT64:
        t = jj_consume_token(FLOAT64);
                           dds.setName(t.image);
        break;
      case STRING:
        t = jj_consume_token(STRING);
                           dds.setName(t.image);
        break;
      case URL:
        t = jj_consume_token(URL);
                           dds.setName(t.image);
        break;
      case STRUCTURE:
        t = jj_consume_token(STRUCTURE);
                           dds.setName(t.image);
        break;
      case SEQUENCE:
        t = jj_consume_token(SEQUENCE);
                           dds.setName(t.image);
        break;
      case GRID:
        t = jj_consume_token(GRID);
                           dds.setName(t.image);
        break;
      case LIST:
        t = jj_consume_token(LIST);
                           dds.setName(t.image);
        break;
      default:
        jj_la1[21] = jj_gen;
        jj_consume_token(-1);
        throw new ParseException();
      }
    } catch (ParseException e) {
        error("Error parsing the dataset name.\n" +
              "The name may be missing or may contain an illegal character.");
    }
  }

  void error(String msg) throws ParseException, DDSException {
    throw new DDSException(DODSException.UNKNOWN_ERROR, msg);
  }

  final private boolean jj_2_1(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_1();
    jj_save(0, xla);
    return retval;
  }

  final private boolean jj_3_1() {
    if (jj_scan_token(25)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_scan_token(WORD)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_scan_token(26)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  public DDSParserTokenManager token_source;
  SimpleCharStream jj_input_stream;
  public Token token, jj_nt;
  private int jj_ntk;
  private Token jj_scanpos, jj_lastpos;
  private int jj_la;
  public boolean lookingAhead = false;
  private boolean jj_semLA;
  private int jj_gen;
  final private int[] jj_la1 = new int[22];
  final private int[] jj_la1_0 = {0x40,0xfff80,0xfff80,0xfff00,0xff800,0x2000000,0x2000000,0x2000000,0x2000000,0x2000000,0x2000000,0x2000000,0x2000000,0x2000000,0x2000000,0x2000000,0x2000000,0x2000000,0x2000000,0x1fff80,0x2000000,0x1fff80,};
  final private JJCalls[] jj_2_rtns = new JJCalls[1];
  private boolean jj_rescan = false;
  private int jj_gc = 0;

  public DDSParser(java.io.InputStream stream) {
    jj_input_stream = new SimpleCharStream(stream, 1, 1);
    token_source = new DDSParserTokenManager(jj_input_stream);
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 22; i++) jj_la1[i] = -1;
    for (int i = 0; i < jj_2_rtns.length; i++) jj_2_rtns[i] = new JJCalls();
  }

  public void ReInit(java.io.InputStream stream) {
    jj_input_stream.ReInit(stream, 1, 1);
    token_source.ReInit(jj_input_stream);
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 22; i++) jj_la1[i] = -1;
    for (int i = 0; i < jj_2_rtns.length; i++) jj_2_rtns[i] = new JJCalls();
  }

  public DDSParser(java.io.Reader stream) {
    jj_input_stream = new SimpleCharStream(stream, 1, 1);
    token_source = new DDSParserTokenManager(jj_input_stream);
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 22; i++) jj_la1[i] = -1;
    for (int i = 0; i < jj_2_rtns.length; i++) jj_2_rtns[i] = new JJCalls();
  }

  public void ReInit(java.io.Reader stream) {
    jj_input_stream.ReInit(stream, 1, 1);
    token_source.ReInit(jj_input_stream);
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 22; i++) jj_la1[i] = -1;
    for (int i = 0; i < jj_2_rtns.length; i++) jj_2_rtns[i] = new JJCalls();
  }

  public DDSParser(DDSParserTokenManager tm) {
    token_source = tm;
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 22; i++) jj_la1[i] = -1;
    for (int i = 0; i < jj_2_rtns.length; i++) jj_2_rtns[i] = new JJCalls();
  }

  public void ReInit(DDSParserTokenManager tm) {
    token_source = tm;
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 22; i++) jj_la1[i] = -1;
    for (int i = 0; i < jj_2_rtns.length; i++) jj_2_rtns[i] = new JJCalls();
  }

  final private Token jj_consume_token(int kind) throws ParseException {
    Token oldToken;
    if ((oldToken = token).next != null) token = token.next;
    else token = token.next = token_source.getNextToken();
    jj_ntk = -1;
    if (token.kind == kind) {
      jj_gen++;
      if (++jj_gc > 100) {
        jj_gc = 0;
        for (int i = 0; i < jj_2_rtns.length; i++) {
          JJCalls c = jj_2_rtns[i];
          while (c != null) {
            if (c.gen < jj_gen) c.first = null;
            c = c.next;
          }
        }
      }
      return token;
    }
    token = oldToken;
    jj_kind = kind;
    throw generateParseException();
  }

  final private boolean jj_scan_token(int kind) {
    if (jj_scanpos == jj_lastpos) {
      jj_la--;
      if (jj_scanpos.next == null) {
        jj_lastpos = jj_scanpos = jj_scanpos.next = token_source.getNextToken();
      } else {
        jj_lastpos = jj_scanpos = jj_scanpos.next;
      }
    } else {
      jj_scanpos = jj_scanpos.next;
    }
    if (jj_rescan) {
      int i = 0; Token tok = token;
      while (tok != null && tok != jj_scanpos) { i++; tok = tok.next; }
      if (tok != null) jj_add_error_token(kind, i);
    }
    return (jj_scanpos.kind != kind);
  }

  final public Token getNextToken() {
    if (token.next != null) token = token.next;
    else token = token.next = token_source.getNextToken();
    jj_ntk = -1;
    jj_gen++;
    return token;
  }

  final public Token getToken(int index) {
    Token t = lookingAhead ? jj_scanpos : token;
    for (int i = 0; i < index; i++) {
      if (t.next != null) t = t.next;
      else t = t.next = token_source.getNextToken();
    }
    return t;
  }

  final private int jj_ntk() {
    if ((jj_nt=token.next) == null)
      return (jj_ntk = (token.next=token_source.getNextToken()).kind);
    else
      return (jj_ntk = jj_nt.kind);
  }

  private java.util.Vector jj_expentries = new java.util.Vector();
  private int[] jj_expentry;
  private int jj_kind = -1;
  private int[] jj_lasttokens = new int[100];
  private int jj_endpos;

  private void jj_add_error_token(int kind, int pos) {
    if (pos >= 100) return;
    if (pos == jj_endpos + 1) {
      jj_lasttokens[jj_endpos++] = kind;
    } else if (jj_endpos != 0) {
      jj_expentry = new int[jj_endpos];
      for (int i = 0; i < jj_endpos; i++) {
        jj_expentry[i] = jj_lasttokens[i];
      }
      boolean exists = false;
      for (java.util.Enumeration enum = jj_expentries.elements(); enum.hasMoreElements();) {
        int[] oldentry = (int[])(enum.nextElement());
        if (oldentry.length == jj_expentry.length) {
          exists = true;
          for (int i = 0; i < jj_expentry.length; i++) {
            if (oldentry[i] != jj_expentry[i]) {
              exists = false;
              break;
            }
          }
          if (exists) break;
        }
      }
      if (!exists) jj_expentries.addElement(jj_expentry);
      if (pos != 0) jj_lasttokens[(jj_endpos = pos) - 1] = kind;
    }
  }

  final public ParseException generateParseException() {
    jj_expentries.removeAllElements();
    boolean[] la1tokens = new boolean[28];
    for (int i = 0; i < 28; i++) {
      la1tokens[i] = false;
    }
    if (jj_kind >= 0) {
      la1tokens[jj_kind] = true;
      jj_kind = -1;
    }
    for (int i = 0; i < 22; i++) {
      if (jj_la1[i] == jj_gen) {
        for (int j = 0; j < 32; j++) {
          if ((jj_la1_0[i] & (1<<j)) != 0) {
            la1tokens[j] = true;
          }
        }
      }
    }
    for (int i = 0; i < 28; i++) {
      if (la1tokens[i]) {
        jj_expentry = new int[1];
        jj_expentry[0] = i;
        jj_expentries.addElement(jj_expentry);
      }
    }
    jj_endpos = 0;
    jj_rescan_token();
    jj_add_error_token(0, 0);
    int[][] exptokseq = new int[jj_expentries.size()][];
    for (int i = 0; i < jj_expentries.size(); i++) {
      exptokseq[i] = (int[])jj_expentries.elementAt(i);
    }
    return new ParseException(token, exptokseq, tokenImage);
  }

  final public void enable_tracing() {
  }

  final public void disable_tracing() {
  }

  final private void jj_rescan_token() {
    jj_rescan = true;
    for (int i = 0; i < 1; i++) {
      JJCalls p = jj_2_rtns[i];
      do {
        if (p.gen > jj_gen) {
          jj_la = p.arg; jj_lastpos = jj_scanpos = p.first;
          switch (i) {
            case 0: jj_3_1(); break;
          }
        }
        p = p.next;
      } while (p != null);
    }
    jj_rescan = false;
  }

  final private void jj_save(int index, int xla) {
    JJCalls p = jj_2_rtns[index];
    while (p.gen > jj_gen) {
      if (p.next == null) { p = p.next = new JJCalls(); break; }
      p = p.next;
    }
    p.gen = jj_gen + xla - jj_la; p.first = token; p.arg = xla;
  }

  static final class JJCalls {
    int gen;
    Token first;
    int arg;
    JJCalls next;
  }

}

/* Generated By:JavaCC: Do not edit this line. DASParser.java */
package dods.dap.parser;

import java.util.Stack;
import dods.dap.*;

public class DASParser implements DASParserConstants {
    /* $Id: DASParser.java,v 1.28 2002/06/05 20:44:51 jimg Exp $ */
    private DAS das;
    private Stack stack;
    private String name;
    private int type;

    private static final String attrTupleMsg =
    "Error: Expected an attribute type. Such as Byte, Int32, String, et c.\n"
    + "followed by a name and value.\n";

    private static final String noDASMsg =
    "The attribute object returned from the dataset was null\n"
    + "Check that the URL is correct.";

    /** Return the topmost AttributeTable on the stack. */
    private final AttributeTable topOfStack() {
        return (AttributeTable)stack.peek();
    }

    /** Is the stack empty? */
    private final boolean isStackEmpty() {
        return stack.isEmpty();
    }

    /** Return the rightmost component of name (separated by '.'). */
    private final String attrName(String name) {
        int i = name.lastIndexOf(".");
        if (i==-1)
            return name;
        else
            return name.substring(i+1);
    }

  final public void Attributes(DAS das) throws ParseException, DASException {
    this.das = das;
    this.stack = new Stack();
    try {
      switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
      case ATTR:
        label_1:
        while (true) {
          Attribute();
          switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
          case ATTR:
            ;
            break;
          default:
            jj_la1[0] = jj_gen;
            break label_1;
          }
        }
        break;
      default:
        jj_la1[1] = jj_gen;
        error(noDASMsg);
      }
    } catch (TokenMgrError e) {
        error("Error parsing the Attribute object:\n"
              + e.getMessage() + "\n");
    } catch (ParseException e) {
        error("Error parsing the Attribute object:\n"
              + e.getMessage() + "\n");
    }
  }

  final public void Attribute() throws ParseException, DASException {
    jj_consume_token(ATTR);
    jj_consume_token(19);
    AttrList();
    jj_consume_token(20);
  }

  final public void AttrList() throws ParseException, DASException {
    label_2:
    while (true) {
      switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
      case ATTR:
      case ALIAS:
      case BYTE:
      case INT16:
      case UINT16:
      case INT32:
      case UINT32:
      case FLOAT32:
      case FLOAT64:
      case STRING:
      case URL:
      case WORD:
        ;
        break;
      default:
        jj_la1[2] = jj_gen;
        break label_2;
      }
      AttrTuple();
    }
  }

  final public void AttrTuple() throws ParseException, DASException {
    Token t = new Token();
    try {
      if (jj_2_1(2)) {
        Alias();
      } else if (jj_2_2(2)) {
        jj_consume_token(BYTE);
                                 type = Attribute.BYTE;
        t = Name();
                    name = t.image;
        Bytes();
        label_3:
        while (true) {
          switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
          case 21:
            ;
            break;
          default:
            jj_la1[3] = jj_gen;
            break label_3;
          }
          jj_consume_token(21);
          Bytes();
        }
        jj_consume_token(22);
      } else if (jj_2_3(2)) {
        jj_consume_token(INT16);
                                  type = Attribute.INT16;
        t = Name();
                    name = t.image;
        Ints();
        label_4:
        while (true) {
          switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
          case 21:
            ;
            break;
          default:
            jj_la1[4] = jj_gen;
            break label_4;
          }
          jj_consume_token(21);
          Ints();
        }
        jj_consume_token(22);
      } else if (jj_2_4(2)) {
        jj_consume_token(UINT16);
                                   type = Attribute.UINT16;
        t = Name();
                    name = t.image;
        Ints();
        label_5:
        while (true) {
          switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
          case 21:
            ;
            break;
          default:
            jj_la1[5] = jj_gen;
            break label_5;
          }
          jj_consume_token(21);
          Ints();
        }
        jj_consume_token(22);
      } else if (jj_2_5(2)) {
        jj_consume_token(INT32);
                                  type = Attribute.INT32;
        t = Name();
                    name = t.image;
        Ints();
        label_6:
        while (true) {
          switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
          case 21:
            ;
            break;
          default:
            jj_la1[6] = jj_gen;
            break label_6;
          }
          jj_consume_token(21);
          Ints();
        }
        jj_consume_token(22);
      } else if (jj_2_6(2)) {
        jj_consume_token(UINT32);
                                   type = Attribute.UINT32;
        t = Name();
                    name = t.image;
        Ints();
        label_7:
        while (true) {
          switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
          case 21:
            ;
            break;
          default:
            jj_la1[7] = jj_gen;
            break label_7;
          }
          jj_consume_token(21);
          Ints();
        }
        jj_consume_token(22);
      } else if (jj_2_7(2)) {
        jj_consume_token(FLOAT32);
                                    type = Attribute.FLOAT32;
        t = Name();
                    name = t.image;
        Floats();
        label_8:
        while (true) {
          switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
          case 21:
            ;
            break;
          default:
            jj_la1[8] = jj_gen;
            break label_8;
          }
          jj_consume_token(21);
          Floats();
        }
        jj_consume_token(22);
      } else if (jj_2_8(2)) {
        jj_consume_token(FLOAT64);
                                    type = Attribute.FLOAT64;
        t = Name();
                    name = t.image;
        Floats();
        label_9:
        while (true) {
          switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
          case 21:
            ;
            break;
          default:
            jj_la1[9] = jj_gen;
            break label_9;
          }
          jj_consume_token(21);
          Floats();
        }
        jj_consume_token(22);
      } else if (jj_2_9(2)) {
        jj_consume_token(STRING);
                                   type = Attribute.STRING;
        t = Name();
                    name = t.image;
        Strs();
        label_10:
        while (true) {
          switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
          case 21:
            ;
            break;
          default:
            jj_la1[10] = jj_gen;
            break label_10;
          }
          jj_consume_token(21);
          Strs();
        }
        jj_consume_token(22);
      } else if (jj_2_10(2)) {
        jj_consume_token(URL);
                                type = Attribute.URL;
        t = Name();
                    name = t.image;
        Urls();
        label_11:
        while (true) {
          switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
          case 21:
            ;
            break;
          default:
            jj_la1[11] = jj_gen;
            break label_11;
          }
          jj_consume_token(21);
          Urls();
        }
        jj_consume_token(22);
      } else if (jj_2_11(2)) {
        t = Name();
             AttributeTable at;
             if (isStackEmpty()) {
                 at = das.getAttributeTable(t.image);
                 if (at == null) {
                     at = new AttributeTable(t.image);
                     das.addAttributeTable(t.image, at);
                 }
             } else {
                 Attribute a = topOfStack().getAttribute(t.image);
                 if (a == null) {
                     at = topOfStack().appendContainer(t.image);
                 } else {
                     at = a.getContainer();
                 }
             }
             stack.push(at);
        jj_consume_token(19);
        AttrList();
                stack.pop();
        jj_consume_token(20);
      } else {
        jj_consume_token(-1);
        throw new ParseException();
      }
    } catch (ParseException e) {
        error(attrTupleMsg + "\n"
              + "The offending line contained the token: '" + t + "'\n"
              + "ParseException Message: '" + e.getMessage() + "'\n");
    }
  }

  final public void Bytes() throws ParseException, DASException {
    Token t;
    t = jj_consume_token(WORD);
        addAttribute(type, name, t.image);
  }

  final public void Ints() throws ParseException, DASException {
    Token t;
    t = jj_consume_token(WORD);
        addAttribute(type, name, t.image);
  }

  final public void Floats() throws ParseException, DASException {
    Token t;
    t = jj_consume_token(WORD);
        addAttribute(type, name, t.image);
  }

  final public void Strs() throws ParseException, DASException {
    Token t;
    try {
      switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
      case WORD:
        t = jj_consume_token(WORD);
            addAttribute(type, name, t.image);
        break;
      case STR:
        t = jj_consume_token(STR);
            addAttribute(type, name, t.image);
        break;
      default:
        jj_la1[12] = jj_gen;
        jj_consume_token(-1);
        throw new ParseException();
      }
    } catch (TokenMgrError e) {
        // If we get an exception thrown inside a quoted string then assume
        // that the scanner has found EOF before the token (STR) ended (i.e.
        // we have an unterminated double quote on our hands). 5/29/2002 jhrg
        error("Unterminated quote: " + e.getMessage() + ")");
    }
  }

  final public void Urls() throws ParseException, DASException {
    Strs();
  }

  final public void Alias() throws ParseException, DASException {
    Token t;
    String alias = "";
    String attr = "";
    try {
      jj_consume_token(ALIAS);
      t = jj_consume_token(WORD);
                           alias = t.image;
      t = jj_consume_token(WORD);
            attr = t.image;
            if (isStackEmpty()) {
                AttributeTable at = das.getAttributeTable(attr);
                // Note: this won't show up as an Alias when printing the DAS!
                das.addAttributeTable(alias, at);
            }
            else {
                topOfStack().addAlias(alias, attr);
            }
      jj_consume_token(22);
    } catch (NoSuchAttributeException e) {
        error("Error: The attribute " + attr + " does not exist.");
    } catch (AttributeExistsException e) {
        error("Error: The alias " + alias + " already exists in this DAS.");
    }
  }

  final public Token Name() throws ParseException, DASException {
    Token t;
    switch ((jj_ntk==-1)?jj_ntk():jj_ntk) {
    case WORD:
      t = jj_consume_token(WORD);
               {if (true) return t;}
      break;
    case ATTR:
      t = jj_consume_token(ATTR);
                 {if (true) return t;}
      break;
    case ALIAS:
      t = jj_consume_token(ALIAS);
                  {if (true) return t;}
      break;
    case BYTE:
      t = jj_consume_token(BYTE);
                 {if (true) return t;}
      break;
    case INT16:
      t = jj_consume_token(INT16);
                  {if (true) return t;}
      break;
    case UINT16:
      t = jj_consume_token(UINT16);
                   {if (true) return t;}
      break;
    case INT32:
      t = jj_consume_token(INT32);
                  {if (true) return t;}
      break;
    case UINT32:
      t = jj_consume_token(UINT32);
                   {if (true) return t;}
      break;
    case FLOAT32:
      t = jj_consume_token(FLOAT32);
                    {if (true) return t;}
      break;
    case FLOAT64:
      t = jj_consume_token(FLOAT64);
                    {if (true) return t;}
      break;
    case STRING:
      t = jj_consume_token(STRING);
                   {if (true) return t;}
      break;
    case URL:
      t = jj_consume_token(URL);
                {if (true) return t;}
      break;
    default:
      jj_la1[13] = jj_gen;
      jj_consume_token(-1);
      throw new ParseException();
    }
    throw new Error("Missing return statement in function");
  }

  void error(String msg) throws ParseException, DASException {
    throw new DASException(DODSException.MALFORMED_EXPR,msg);
  }

  void addAttribute(int type, String name, String value) throws ParseException, DASException {
    try {
        if (isStackEmpty()) {
            String msg = "Whoa! Attribute table stack empty when adding `"
                + name +".'";
            error(msg);
        }

        // appendAttribute throws a variety of DASExceptions if the attribute
        // tuple is bad. This includes throwing AttribtueBadValueException if
        // the value is bad (see the private method dispatchCheckValue()).
        // 5/23/2002 jhrg
        //System.err.println("Calling appendAttribute (name, type, value): "
        //		   + name + ", " + type + ", " + value);
        topOfStack().appendAttribute(name, type, value);
    }
    // If the attribute value is bad (the exception thrown by
    // dispatchCheckValue() above) then add this attribute as a 'Bad
    // Attribute.'
    catch (AttributeBadValueException e) {
        // System.err.println("Caught an AttributeBadValueException");
        String msg = "`" + value + "' is not " + aOrAn(getTypeName(type))
            + " " + getTypeName(type) + " value.";
        addBadAttribute(topOfStack().getName(), type, name, value, msg);
    }
  }

  void addBadAttribute(String container_name, int type, String name, String value,
                String msg) throws ParseException, DASException {
    String errorContainerName = container_name + "_dods_errors";

    // First, if this bad value is already in a *_dods_errors container,
    // then just add it. This can happen when the server side processes a DAS
    // and then hands it off to a client which does the same. The false value
    // for arg four below supresses checking the value of the attribute
    // (since we know it's bad and don't want the exception to be generated
    // again). 
    if (topOfStack().getName().equals(errorContainerName)) {
        topOfStack().appendAttribute(name, type, value, false);
    }
    // Otherwise, make a new container. Call it <attr's name>_errors. If that
    // container already exists, use it. Add the attribute. Add the error
    // string to an attribute in the container called `<name_explanation.'.
    else {
        // Does the error container alreay exist? 
        AttributeTable errorContainer = null;
        Attribute a = topOfStack().getAttribute(errorContainerName);
        if (a != null)
            errorContainer = a.getContainer(); // get value as container
        else
            errorContainer = topOfStack().appendContainer(errorContainerName);

        // Arg four == false --> supress type/value checking.
        errorContainer.appendAttribute(name, type, value, false);
        errorContainer.appendAttribute(name + "_explanation",
                                       dods.dap.Attribute.STRING,
                                       "\"" + msg + "\"");
    }
  }

  String aOrAn(String subject) throws ParseException {
    String vowels = "aeiouAEIOUyY";
    if (vowels.indexOf(subject.charAt(1)) >= 0)
        return "an";
    else
        return "a";
  }

  String getTypeName(int type) throws ParseException {
    switch(type) {
    case Attribute.CONTAINER: return "Container";
    case Attribute.BYTE: return "Byte";
    case Attribute.INT16: return "Int16";
    case Attribute.UINT16: return "UInt16";
    case Attribute.INT32: return "Int32";
    case Attribute.UINT32: return "UInt32";
    case Attribute.FLOAT32: return "Float32";
    case Attribute.FLOAT64: return "Float64";
    case Attribute.STRING: return "String";
    case Attribute.URL: return "Url";
    default: return "";
    }
  }

  final private boolean jj_2_1(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_1();
    jj_save(0, xla);
    return retval;
  }

  final private boolean jj_2_2(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_2();
    jj_save(1, xla);
    return retval;
  }

  final private boolean jj_2_3(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_3();
    jj_save(2, xla);
    return retval;
  }

  final private boolean jj_2_4(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_4();
    jj_save(3, xla);
    return retval;
  }

  final private boolean jj_2_5(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_5();
    jj_save(4, xla);
    return retval;
  }

  final private boolean jj_2_6(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_6();
    jj_save(5, xla);
    return retval;
  }

  final private boolean jj_2_7(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_7();
    jj_save(6, xla);
    return retval;
  }

  final private boolean jj_2_8(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_8();
    jj_save(7, xla);
    return retval;
  }

  final private boolean jj_2_9(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_9();
    jj_save(8, xla);
    return retval;
  }

  final private boolean jj_2_10(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_10();
    jj_save(9, xla);
    return retval;
  }

  final private boolean jj_2_11(int xla) {
    jj_la = xla; jj_lastpos = jj_scanpos = token;
    boolean retval = !jj_3_11();
    jj_save(10, xla);
    return retval;
  }

  final private boolean jj_3R_13() {
    Token xsp;
    xsp = jj_scanpos;
    if (jj_3R_14()) {
    jj_scanpos = xsp;
    if (jj_3R_15()) {
    jj_scanpos = xsp;
    if (jj_3R_16()) {
    jj_scanpos = xsp;
    if (jj_3R_17()) {
    jj_scanpos = xsp;
    if (jj_3R_18()) {
    jj_scanpos = xsp;
    if (jj_3R_19()) {
    jj_scanpos = xsp;
    if (jj_3R_20()) {
    jj_scanpos = xsp;
    if (jj_3R_21()) {
    jj_scanpos = xsp;
    if (jj_3R_22()) {
    jj_scanpos = xsp;
    if (jj_3R_23()) {
    jj_scanpos = xsp;
    if (jj_3R_24()) {
    jj_scanpos = xsp;
    if (jj_3R_25()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    } else if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    } else if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    } else if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    } else if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    } else if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    } else if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    } else if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    } else if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    } else if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    } else if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    } else if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_14() {
    if (jj_scan_token(WORD)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3_7() {
    if (jj_scan_token(FLOAT32)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_3R_13()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3_6() {
    if (jj_scan_token(UINT32)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_3R_13()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3_5() {
    if (jj_scan_token(INT32)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_3R_13()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3_4() {
    if (jj_scan_token(UINT16)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_3R_13()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3_3() {
    if (jj_scan_token(INT16)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_3R_13()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3_2() {
    if (jj_scan_token(BYTE)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_3R_13()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3_1() {
    if (jj_3R_12()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_12() {
    if (jj_scan_token(ALIAS)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_scan_token(WORD)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3_11() {
    if (jj_3R_13()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_scan_token(19)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_25() {
    if (jj_scan_token(URL)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_24() {
    if (jj_scan_token(STRING)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_23() {
    if (jj_scan_token(FLOAT64)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3_10() {
    if (jj_scan_token(URL)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_3R_13()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_22() {
    if (jj_scan_token(FLOAT32)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_21() {
    if (jj_scan_token(UINT32)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_20() {
    if (jj_scan_token(INT32)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_19() {
    if (jj_scan_token(UINT16)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3_9() {
    if (jj_scan_token(STRING)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_3R_13()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_18() {
    if (jj_scan_token(INT16)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_17() {
    if (jj_scan_token(BYTE)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_16() {
    if (jj_scan_token(ALIAS)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3_8() {
    if (jj_scan_token(FLOAT64)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    if (jj_3R_13()) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  final private boolean jj_3R_15() {
    if (jj_scan_token(ATTR)) return true;
    if (jj_la == 0 && jj_scanpos == jj_lastpos) return false;
    return false;
  }

  public DASParserTokenManager token_source;
  SimpleCharStream jj_input_stream;
  public Token token, jj_nt;
  private int jj_ntk;
  private Token jj_scanpos, jj_lastpos;
  private int jj_la;
  public boolean lookingAhead = false;
  private boolean jj_semLA;
  private int jj_gen;
  final private int[] jj_la1 = new int[14];
  final private int[] jj_la1_0 = {0x40,0x40,0x3ffc0,0x200000,0x200000,0x200000,0x200000,0x200000,0x200000,0x200000,0x200000,0x200000,0x60000,0x3ffc0,};
  final private JJCalls[] jj_2_rtns = new JJCalls[11];
  private boolean jj_rescan = false;
  private int jj_gc = 0;

  public DASParser(java.io.InputStream stream) {
    jj_input_stream = new SimpleCharStream(stream, 1, 1);
    token_source = new DASParserTokenManager(jj_input_stream);
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 14; i++) jj_la1[i] = -1;
    for (int i = 0; i < jj_2_rtns.length; i++) jj_2_rtns[i] = new JJCalls();
  }

  public void ReInit(java.io.InputStream stream) {
    jj_input_stream.ReInit(stream, 1, 1);
    token_source.ReInit(jj_input_stream);
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 14; i++) jj_la1[i] = -1;
    for (int i = 0; i < jj_2_rtns.length; i++) jj_2_rtns[i] = new JJCalls();
  }

  public DASParser(java.io.Reader stream) {
    jj_input_stream = new SimpleCharStream(stream, 1, 1);
    token_source = new DASParserTokenManager(jj_input_stream);
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 14; i++) jj_la1[i] = -1;
    for (int i = 0; i < jj_2_rtns.length; i++) jj_2_rtns[i] = new JJCalls();
  }

  public void ReInit(java.io.Reader stream) {
    jj_input_stream.ReInit(stream, 1, 1);
    token_source.ReInit(jj_input_stream);
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 14; i++) jj_la1[i] = -1;
    for (int i = 0; i < jj_2_rtns.length; i++) jj_2_rtns[i] = new JJCalls();
  }

  public DASParser(DASParserTokenManager tm) {
    token_source = tm;
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 14; i++) jj_la1[i] = -1;
    for (int i = 0; i < jj_2_rtns.length; i++) jj_2_rtns[i] = new JJCalls();
  }

  public void ReInit(DASParserTokenManager tm) {
    token_source = tm;
    token = new Token();
    jj_ntk = -1;
    jj_gen = 0;
    for (int i = 0; i < 14; i++) jj_la1[i] = -1;
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
    boolean[] la1tokens = new boolean[23];
    for (int i = 0; i < 23; i++) {
      la1tokens[i] = false;
    }
    if (jj_kind >= 0) {
      la1tokens[jj_kind] = true;
      jj_kind = -1;
    }
    for (int i = 0; i < 14; i++) {
      if (jj_la1[i] == jj_gen) {
        for (int j = 0; j < 32; j++) {
          if ((jj_la1_0[i] & (1<<j)) != 0) {
            la1tokens[j] = true;
          }
        }
      }
    }
    for (int i = 0; i < 23; i++) {
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
    for (int i = 0; i < 11; i++) {
      JJCalls p = jj_2_rtns[i];
      do {
        if (p.gen > jj_gen) {
          jj_la = p.arg; jj_lastpos = jj_scanpos = p.first;
          switch (i) {
            case 0: jj_3_1(); break;
            case 1: jj_3_2(); break;
            case 2: jj_3_3(); break;
            case 3: jj_3_4(); break;
            case 4: jj_3_5(); break;
            case 5: jj_3_6(); break;
            case 6: jj_3_7(); break;
            case 7: jj_3_8(); break;
            case 8: jj_3_9(); break;
            case 9: jj_3_10(); break;
            case 10: jj_3_11(); break;
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

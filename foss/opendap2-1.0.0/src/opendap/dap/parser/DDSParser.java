package opendap.dap.parser;

import java.io.InputStream;

public class DDSParser extends DapParser
{
    public DDSParser(InputStream stream)
	throws ParseException
    {
	super(stream);
    }
}

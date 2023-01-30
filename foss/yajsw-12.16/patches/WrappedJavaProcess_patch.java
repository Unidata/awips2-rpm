--- ../../yajsw-12.16_unmodified/src/yajsw/src/main/java/org/rzo/yajsw/wrapper/WrappedJavaProcess.java	2021-04-19 16:10:42.000000000 -0400
+++ ../src/yajsw/src/main/java/org/rzo/yajsw/wrapper/WrappedJavaProcess.java	2021-08-20 10:20:00.521108046 -0400
@@ -25,6 +25,7 @@
 import java.util.ArrayList;
 import java.util.Collection;
 import java.util.Collections;
+import java.util.HashMap;
 import java.util.Iterator;
 import java.util.List;
 import java.util.Map;
@@ -37,7 +38,9 @@
 import java.util.logging.Level;
 import java.util.regex.Matcher;
 import java.util.regex.Pattern;
+import java.util.stream.Collectors;
 
+import org.apache.commons.lang3.StringUtils;
 import org.rzo.yajsw.Constants;
 import org.rzo.yajsw.app.WrapperMainServiceWin;
 import org.rzo.yajsw.boot.WrapperLoader;
@@ -55,6 +58,31 @@
  */
 public class WrappedJavaProcess extends AbstractWrappedProcess
 {
+	/*
+	 *  bkowal 
+ 	 *  Constants used to set and determine the order of jvm parameters. 
+ 	 */
+	private static final String LAST_KEYWORD = "LAST";
+
+	private static final String _PERIOD_SEPARATOR_ = ".";
+
+	/*
+	 * bkowal - define the parameter order parameter name
+	 */
+	private static final String ORDER_PATTERN = "wrapper.jvm.parameter.order";
+
+	private static final String NUMERIC_ORDER_PATTERN = ORDER_PATTERN
+		 + _PERIOD_SEPARATOR_ + "([1-9][0-9]*)";
+
+	private static final Pattern numericOrderPattern = Pattern
+		.compile(NUMERIC_ORDER_PATTERN);
+
+	private static final String LAST_ORDER_PATTERN = ORDER_PATTERN
+		+ _PERIOD_SEPARATOR_ + LAST_KEYWORD;
+
+	private static final Pattern lastOrderPattern = Pattern
+		.compile(LAST_ORDER_PATTERN);
+	/* End of Constants. */	
 
 	/** The _key. */
 	String _key;
@@ -141,11 +169,19 @@
 		List jvmOptions = jvmOptions();
 		List wrapperOptions = wrapperOptions();
 		String mainClass = getMainClass();
-		List command = new ArrayList();
+		List<String> command = new ArrayList<>();
 		command.add(java);
 		command.addAll(jvmOptions);
 		command.addAll(wrapperOptions);
 		command.add(mainClass);
+		/*
+		 * bkowal 
+ 		 * Filter any empty Strings out of the command list.
+		 */
+		command = command.stream()
+			.filter((c) -> StringUtils.isNotBlank(c))
+			.collect(Collectors.toList());
+
 		String[] arrCmd = new String[command.size()];
 		for (int i = 0; i < arrCmd.length; i++)
 			arrCmd[i] = (String) command.get(i);
@@ -238,7 +274,7 @@
 	private List jvmOptions()
 	{
 		ArrayList result = new ArrayList();
-		result.add("-classpath");
+		// bkowal the placement of classpath in the command is now configurable.
 		StringBuffer sb = new StringBuffer();
 		sb.append(WrapperLoader.getWrapperAppJar().trim());
 		StringBuilder appCp = getAppClassPath(
@@ -252,7 +288,10 @@
 		String cp = sb.toString();
 		if (cp.contains(" ") && Platform.isWindows())
 			cp = "\"" + cp + "\"";
-		result.add(checkValue(cp));
+		/*
+		 * bkowal Save the classpath instead of adding it immediately
+ 		 */
+		cp = checkValue(cp);
 		boolean hasXrs = false;
 		boolean hasXmx = false;
 		boolean hasXms = false;
@@ -263,6 +302,11 @@
 			String value = _config.getString(key);
 			if (value == null)
 				continue;
+			// bkowal exclude jvm parameters that could not be resolved.
+ 			if (value.contains("?unresolved?")) {
+				getWrapperLogger().warning("JVM Parameter: '" + key + "' COULD NOT BE RESOLVED!!!");
+				continue;
+			}
 			result.add(checkQuotes(checkValue(value)));
 			hasXrs |= value.contains("-Xrs");
 			hasXmx |= value.contains("-Xmx");
@@ -367,7 +411,12 @@
 		if (port != -1)
 		{
 			result.add("-Xdebug");
-			result.add("-Xrunjdwp:transport=dt_socket,server=y,suspend=y,address="
+			/*
+			 * Updated by bkowal on 12/10/2014. changed suspend=y => suspend=n;
+ 			 * the wrapper will continue process startup even if there is not a remote debugger
+ 			 * connected to the client when suspend is disabled.
+ 			 */
+			result.add("-Xrunjdwp:transport=dt_socket,server=y,suspend=n,address="
 					+ port);
 		}
 		String preMainScript = _config.getString("wrapper.app.pre_main.script",
@@ -402,7 +451,146 @@
 		 * (!result.contains("-Dcom.sun.management.jmxremote"))
 		 * result.add("-Dcom.sun.management.jmxremote");
 		 */
-		return result;
+		return orderParameters(result, cp);
+	}
+
+	/*
+	 * bkowal
+	 * Added orderParameters method
+  	 */
+	private List orderParameters(List parameters, String classpath)
+	{
+		Map<String, String> orderedParametersMap = new HashMap<>();
+
+		/*
+		 * bkowal - loop through the parameters and re-arrange the parameters
+		 * in the specified order.
+  		 */
+		for (Iterator<String> it = _config.getKeys("wrapper.jvm.parameter.order"); it.hasNext();)
+		{
+			String paramOrderKey = it.next();
+			
+			Matcher numericMatcher =
+				numericOrderPattern.matcher(paramOrderKey);
+			Matcher lastMatcher =
+				lastOrderPattern.matcher(paramOrderKey);
+
+			String index = null;
+			/* determine the order parameter type */
+			if (numericMatcher.matches())
+			{
+				index = numericMatcher.group(1);
+			}
+			if (lastMatcher.matches())
+			{
+				index = LAST_KEYWORD;
+			}
+
+			if (index == null)
+			{
+				getWrapperLogger().warning("Invalid Parameter Order Specifier: '" +
+				paramOrderKey + "'; SKIPPING!!!");
+				continue;
+			}
+
+			String parameter = _config.getString(paramOrderKey);
+			orderedParametersMap.put(index, parameter);
+		}
+
+		/* Determine the total number of ordered parameters. */
+		int numberOrdered = orderedParametersMap.size();
+		/* Ensure that there are actually parameters that we will be ordering. */
+		if (numberOrdered <= 0 || numberOrdered > parameters.size())
+		{
+			// Respect the original YAJSW JVM parameter order.
+			parameters.add(0, "-classpath");
+			parameters.add(1, classpath);
+			return parameters;
+		}
+
+		String lastParameter = null;
+		int classpathIndex = -1;
+		if (orderedParametersMap.containsKey(LAST_KEYWORD))
+		{
+			numberOrdered -= 1;
+			// extract and save off the "LAST" parameter
+			String parameter = orderedParametersMap.get(LAST_KEYWORD);
+			if (parameter.equals("-classpath"))
+			{
+				// the end of the list.
+				classpathIndex = parameters.size() - 1;
+			}
+			else
+			{
+				lastParameter = lookupParameter(parameters, parameter);
+				// remove the parameter from the list.
+			}
+		}
+
+		/* loop through the parameters that will need to be ordered.*/
+		for (int i = 1; i <= numberOrdered; i++)
+		{
+			String parameter =
+				orderedParametersMap.get(Integer.toString(i));
+			if (parameter == null)
+			{
+				continue;
+			}
+
+			if (parameter.equals("-classpath"))
+			{
+				classpathIndex = i - 1;
+				continue;
+			}
+			String orderedParameter =
+				lookupParameter(parameters, parameter);
+			if (orderedParameter == null)
+			{
+				continue;
+			}
+			// remove the parameter from the list.
+			parameters.remove(orderedParameter);
+			// add the parameter at the requested location.
+			parameters.add(i - 1, orderedParameter);
+		}
+
+		if (lastParameter != null)
+		{
+			parameters.add(lastParameter);
+		}
+
+		if (classpathIndex > 0)
+		{
+			parameters.add(classpathIndex, "-classpath");
+			parameters.add(classpathIndex + 1, classpath);
+		}
+		else
+		{
+			// Respect the original YAJSW JVM parameter order.
+			parameters.add(0, "-classpath");
+			parameters.add(1, classpath);
+		}
+
+		return parameters;
+	}
+
+	/*
+	 * bkowal
+ 	 * Added lookupParameter method
+ 	 */
+	private String lookupParameter(List parameters, String parameter)
+	{
+		for (Object _parameter : parameters)
+		{
+			if (_parameter.toString().contains(parameter))
+			{
+				return _parameter.toString();
+			}
+		}
+
+		getWrapperLogger().warning("Parameter Not Found: '" +
+			parameter + "'; UNABLE TO ADD TO ORDERED PARAMETERS!!!");
+		return null;
 	}
 
 	// avoid -Dkey="somequotedstring"withnonequoted
@@ -482,6 +670,41 @@
 
 		}
 
+		/*
+		 * bkowal - recursively search the directories specified 
+		 * using the wrapper.search.java.classpath jvm parameter and add entries
+ 		 * to the classpath.
+ 		 */
+		final String[] jarPattern = new String[] { "jar" };
+		List<String> containingDirectories = new ArrayList<>();
+		for (Iterator<String> it = _config.getKeys("wrapper.search.java.classpath"); it.hasNext();)
+		{
+			String key = it.next();
+			String location = _config.getString(key);
+
+			File locationDirectory = new File(location);
+			if (locationDirectory.exists() == false ||
+				locationDirectory.isDirectory() == false)
+			{
+				getWrapperLogger().warning(location +
+					" either does not exist or is not a directory; skipping!");
+				continue;
+			}
+			Iterator<?> foundFilesIterator =
+				org.apache.commons.io.FileUtils.iterateFiles(locationDirectory, jarPattern, true);
+			while (foundFilesIterator.hasNext())
+			{
+				File foundFile = (File) foundFilesIterator.next();
+				String containingDirectory = org.apache.commons.io.FilenameUtils
+					.getFullPath(foundFile.getAbsolutePath());
+				if (containingDirectories.contains(containingDirectory) == false) {
+					containingDirectories.add(containingDirectory);
+					sb.append(PATHSEP);
+					sb.append(containingDirectory + "*");
+				}
+			}
+		}
+
 		return sb;
 	}
 

--- ../../yajsw-12.16_unmodified/src/yajsw/src/main/java/org/rzo/yajsw/wrapper/AbstractWrappedProcess.java	2021-04-19 16:10:42.000000000 -0400
+++ ../src/yajsw/src/main/java/org/rzo/yajsw/wrapper/AbstractWrappedProcess.java	2021-08-12 14:40:13.233209957 -0400
@@ -110,8 +110,6 @@
 import org.rzo.yajsw.util.Utils;
 import org.rzo.yajsw.util.VFSUtils;
 
-import sun.security.action.GetPropertyAction;
-
 import com.sun.jna.Platform;
 import com.sun.jna.PlatformEx;
 
@@ -239,9 +237,12 @@
 
 	volatile int _minAppLogLines = MIN_PROCESS_LINES_TO_LOG;
 
-	static final String lineSeparator = ((String) AccessController
-			.doPrivileged(new GetPropertyAction("line.separator")));
-
+	/*
+	 * lsingh
+	 * Replace deprecated lineSeparator call. Also, removed com.sun import at the top of this file.
+	 */
+	static final String lineSeparator = System.lineSeparator();
+	
 	public Configuration getConfiguration()
 	{
 		if (_config == null)
@@ -1296,8 +1297,14 @@
 			_controller.processStarted();
 			_totalRestartCount++;
 			postStart();
-			getWrapperLogger().info(
-					"started process with pid " + _osProcess.getPid());
+			/*
+ 			 * bkowal
+  			 * Suppress extraneous output unless debug is enabled.
+			 */
+			if (_debug > 0) {
+				getWrapperLogger().info(
+						"started process with pid " + _osProcess.getPid());
+			}
 			if (pipeStreams())
 			{
 
@@ -2330,9 +2337,15 @@
 				Constants.DEFAULT_JVM_EXIT_TIMEOUT) * 1000;
 		if (shutdownWaitTime > Integer.MAX_VALUE)
 			shutdownWaitTime = Integer.MAX_VALUE;
-		getWrapperLogger().info(
-				"stopping process with pid/timeout " + _osProcess.getPid()
-						+ " " + shutdownWaitTime);
+		/*
+		 * bkowal
+ 		 * Suppress extraneous output unless debug is enabled.
+ 		 */
+		if(_debug > 0) {
+			getWrapperLogger().info(
+					"stopping process with pid/timeout " + _osProcess.getPid()
+							+ " " + shutdownWaitTime);
+		}
 
 		stopController((int) shutdownWaitTime, _stopReason);
 		stopOsProcess((int) shutdownWaitTime);
@@ -2431,9 +2444,14 @@
 		}
 		_osProcess.destroy();
 
-		// if (_debug > 0)
-		getWrapperLogger().info(
-				"process exit code: " + _osProcess.getExitCode());
+		/*
+		 * bkowal
+ 		 * Suppress extraneous output unless debug is enabled.
+ 		 */
+		if(_debug > 0) {
+			getWrapperLogger().info(
+					"process exit code: " + _osProcess.getExitCode());
+		}
 	}
 
 	private long getRemainStopWaitTime()
@@ -3224,163 +3242,182 @@
 					{
 						((MissingTriggerAction) it.next()).start();
 					}
-				while ((line = br.readLine()) != null)
+				while (true)
 				{
-					if (AbstractWrappedProcess.this._osProcess == null
-							|| _pid == AbstractWrappedProcess.this._osProcess
-									.getPid())
-					{
-						if (_debug > 2)
-							getWrapperLogger().info(
-									"process not running, terminating gobler "
-											+ _name);
-						break;
-					}
+					/*
+					 * D. Friedman  2017-06-20  DR 20038 -- Handle OutOfMemoryError due to long lines.
+ 					 */
+					try{
+						line = br.readLine();
+						if (line == null) {
+							break;
+						}
+						if (AbstractWrappedProcess.this._osProcess == null
+								|| _pid == AbstractWrappedProcess.this._osProcess
+										.getPid())
+						{
+							if (_debug > 2)
+								getWrapperLogger().info(
+										"process not running, terminating gobler "
+												+ _name);
+							break;
+						}
 
-					if (_drain)
-					{
-						// System.out.println("drainBuffer.write "+line);
-						_drainBuffer.write(line);
-					}
-					if (k > _minAppLogLines)
-						_goblerLog.finest(line);
-					else
-					{
+						if (_drain)
+						{
+							// System.out.println("drainBuffer.write "+line);
+							_drainBuffer.write(line);
+						}
+						/*
+						 * bkowal
+ 						 * Allow all lines to be logged by the wrapper.
+ 						 */
 						_goblerLog.info(line);
 						k++;
-					}
-
-					if (_actionTriggers != null)
-						for (int i = 0; i < _actionTriggers.length; i++)
+						/*
+						if (k > _minAppLogLines)
+							_goblerLog.finest(line);
+						else
 						{
-							if (line.contains(_actionTriggers[i]))
+							_goblerLog.info(line);
+							k++;
+						}
+						*/
+						if (_actionTriggers != null)
+							for (int i = 0; i < _actionTriggers.length; i++)
 							{
-								Object obj = _actions.get(_actionTriggers[i]);
-								if (obj instanceof TriggerAction)
+								if (line.contains(_actionTriggers[i]))
 								{
-									TriggerAction action = (TriggerAction) obj;
-									if (enabledTriggerDebug.contains(action
-											.getId()))
+									Object obj = _actions.get(_actionTriggers[i]);
+									if (obj instanceof TriggerAction)
 									{
-										getWrapperLogger().info(
-												"Trigger found: "
-														+ _actionTriggers[i]
-														+ " in line: " + line);
-									}
-									action.execute(new String(line));
-								}
-								else if (obj instanceof Collection)
-								{
-									Collection c = (Collection) obj;
-									for (Iterator it = c.iterator(); it
-											.hasNext();)
-									{
-										TriggerAction action = (TriggerAction) it
-												.next();
+										TriggerAction action = (TriggerAction) obj;
 										if (enabledTriggerDebug.contains(action
 												.getId()))
 										{
 											getWrapperLogger().info(
-													"Trigger found: " + action
-															+ " in line: "
-															+ line);
+													"Trigger found: "
+															+ _actionTriggers[i]
+															+ " in line: " + line);
 										}
 										action.execute(new String(line));
 									}
+										else if (obj instanceof Collection)
+									{
+									Collection c = (Collection) obj;
+									for (Iterator it = c.iterator(); it
+											.hasNext();)
+										{
+											TriggerAction action = (TriggerAction) it
+													.next();
+											if (enabledTriggerDebug.contains(action
+													.getId()))
+											{
+												getWrapperLogger().info(
+														"Trigger found: " + action
+																+ " in line: "
+																+ line);
+											}
+											action.execute(new String(line));
+										}
+									}
+									break;
 								}
-								break;
 							}
-						}
 
-					if (_actionTriggersRegex != null)
-						for (int i = 0; i < _actionTriggersRegex.length; i++)
-						{
-							if (_actionTriggersRegex[i].matches(line))
+						if (_actionTriggersRegex != null)
+							for (int i = 0; i < _actionTriggersRegex.length; i++)
 							{
-								Object obj = (TriggerAction) _actionsRegex
-										.get(_actionTriggersRegex[i].getRegEx());
-								if (obj instanceof TriggerAction)
+								if (_actionTriggersRegex[i].matches(line))
 								{
-									TriggerAction action = (TriggerAction) obj;
-									if (enabledTriggerDebug.contains(action
-											.getId()))
+									Object obj = (TriggerAction) _actionsRegex
+											.get(_actionTriggersRegex[i].getRegEx());
+									if (obj instanceof TriggerAction)
 									{
-										getWrapperLogger()
-												.info("Trigger found: "
-														+ _actionTriggersRegex[i]
-														+ " in line: " + line);
-									}
-									action.execute(new String(line));
-								}
-								else if (obj instanceof Collection)
-								{
-									Collection c = (Collection) obj;
-									for (Iterator it = c.iterator(); it
-											.hasNext();)
-									{
-										TriggerAction action = (TriggerAction) it
-												.next();
+										TriggerAction action = (TriggerAction) obj;
 										if (enabledTriggerDebug.contains(action
 												.getId()))
 										{
 											getWrapperLogger()
 													.info("Trigger found: "
 															+ _actionTriggersRegex[i]
-															+ " in line: "
-															+ line);
+															+ " in line: " + line);
 										}
 										action.execute(new String(line));
 									}
+									else if (obj instanceof Collection)
+									{
+										Collection c = (Collection) obj;
+										for (Iterator it = c.iterator(); it
+												.hasNext();)
+										{
+											TriggerAction action = (TriggerAction) it
+													.next();
+											if (enabledTriggerDebug.contains(action
+													.getId()))
+											{
+												getWrapperLogger()
+														.info("Trigger found: "
+																+ _actionTriggersRegex[i]
+																+ " in line: "
+																+ line);
+											}
+											action.execute(new String(line));
+										}
+									}
+									break;
 								}
-								break;
 							}
-						}
 
-					if (_missingActionTriggers != null)
-						for (int i = 0; i < _missingActionTriggers.length; i++)
-						{
-							if ("".equals(_missingActionTriggers[i])
-									|| line.contains(_missingActionTriggers[i]))
+						if (_missingActionTriggers != null)
+							for (int i = 0; i < _missingActionTriggers.length; i++)
 							{
-								Object obj = (TriggerAction) _missingActions
-										.get(_missingActionTriggers[i]);
-								if (obj instanceof TriggerAction)
+								if ("".equals(_missingActionTriggers[i])
+										|| line.contains(_missingActionTriggers[i]))
 								{
-									TriggerAction action = (TriggerAction) obj;
-									if (enabledTriggerDebug.contains(action
-											.getId()))
-										getWrapperLogger()
-												.info("found missing trigger : "
-														+ _missingActionTriggers[i]);
-									action.execute(new String(line));
+									Object obj = (TriggerAction) _missingActions
+											.get(_missingActionTriggers[i]);
+									if (obj instanceof TriggerAction)
+									{
+										TriggerAction action = (TriggerAction) obj;
+										if (enabledTriggerDebug.contains(action
+												.getId()))
+											getWrapperLogger()
+													.info("found missing trigger : "
+															+ _missingActionTriggers[i]);
+										action.execute(new String(line));
+									}
+									// break;
 								}
-								// break;
 							}
-						}
 
-					if (_missingActionTriggersRegex != null)
-						for (int i = 0; i < _missingActionTriggersRegex.length; i++)
-						{
-							if (_missingActionTriggersRegex[i].matches(line))
+						if (_missingActionTriggersRegex != null)
+							for (int i = 0; i < _missingActionTriggersRegex.length; i++)
 							{
-								Object obj = (TriggerAction) _missingActionsRegex
-										.get(_missingActionTriggersRegex[i]
-												.getRegEx());
-								if (obj instanceof TriggerAction)
+								if (_missingActionTriggersRegex[i].matches(line))
 								{
-									TriggerAction action = (TriggerAction) obj;
-									if (enabledTriggerDebug.contains(action
-											.getId()))
-										getWrapperLogger()
-												.info("found missing trigger : "
-														+ _missingActionTriggersRegex[i]);
-									action.execute(new String(line));
+									Object obj = (TriggerAction) _missingActionsRegex
+											.get(_missingActionTriggersRegex[i]
+													.getRegEx());
+									if (obj instanceof TriggerAction)
+									{
+										TriggerAction action = (TriggerAction) obj;
+										if (enabledTriggerDebug.contains(action
+												.getId()))
+											getWrapperLogger()
+													.info("found missing trigger : "
+															+ _missingActionTriggersRegex[i]);
+										action.execute(new String(line));
+									}
+									// break;
 								}
-								// break;
 							}
-						}
 
-					Thread.yield();
+						Thread.yield();
+					} catch (OutOfMemoryError e) {
+						_goblerLog.warning("Caught OutOfMemoryError while reading line");
+						br = new BufferedReader(isr);
+					}
 				}
 			}
 			catch (Exception ioe)

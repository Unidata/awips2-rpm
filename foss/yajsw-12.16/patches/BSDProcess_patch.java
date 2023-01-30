--- ../../yajsw-12.16_unmodified/src/yajsw/src/main/java/org/rzo/yajsw/os/posix/bsd/BSDProcess.java	2021-04-19 16:10:42.000000000 -0400
+++ ../src/yajsw/src/main/java/org/rzo/yajsw/os/posix/bsd/BSDProcess.java	2021-08-12 14:38:16.732326391 -0400
@@ -20,9 +20,11 @@
 import java.io.IOException;
 import java.io.InputStreamReader;
 import java.net.URI;
+import java.nio.file.Paths;
 import java.util.ArrayList;
 import java.util.List;
 
+import org.apache.commons.lang3.BooleanUtils;
 import org.rzo.yajsw.boot.WrapperLoader;
 import org.rzo.yajsw.io.CyclicBufferFileInputStream;
 import org.rzo.yajsw.io.CyclicBufferFilePrintStream;
@@ -38,6 +40,8 @@
 {
 	java.lang.Process _process;
 
+	private static final String ENV_JAVA_HOME = "JAVA_HOME";
+
 	@Override
 	public String getStdInName()
 	{
@@ -161,7 +165,12 @@
 				}
 				_terminated = true;
 				_exitCode = p.exitValue();
-				System.out.println("exit code bsd process " + _exitCode);
+				/*
+ 				 * bkowal Suppress extraneous output unless debug is enabled
+ 				 */
+				if (_debug) {
+					System.out.println("exit code bsd process " + _exitCode);
+				}
 				BSDProcess.this.setTerminated(true);
 			}
 
@@ -226,7 +235,12 @@
 				System.out.println("error setting affinity");
 		}
 
-		System.out.println("started process " + _pid);
+		/*
+		 * bkowal Suppress extraneous output unless debug is enabled
+ 		 */
+		if(_debug) {
+			System.out.println("started process " + _pid);
+		}
 
 		return true;
 	}
@@ -265,25 +279,34 @@
 		return null;
 	}
 
+	/*
+	 * bkowal Updated the method to determine which Java should be used.
+	 */
 	private String getCurrentJava()
 	{
-		int myPid = OperatingSystem.instance().processManagerInstance()
-				.currentProcessId();
-		Process myProcess = OperatingSystem.instance().processManagerInstance()
-				.getProcess(myPid);
-		String cmd = myProcess.getCommand();
-		String jvm = null;
-		if (cmd.startsWith("\""))
-			jvm = cmd.substring(0, cmd.indexOf("\" ") + 1);
-		else
-		{
-			int firstSpace = cmd.indexOf(" ");
-			if (firstSpace > -1)
-				jvm = cmd.substring(0, firstSpace);
-			else
-				jvm = cmd;
+		Boolean system_java = BooleanUtils.toBoolean(getEnvironmentAsMap().get("use.system.java"));
+		if (system_java || System.getenv(ENV_JAVA_HOME) == null) {
+			int myPid = OperatingSystem.instance().processManagerInstance()
+					.currentProcessId();
+			Process myProcess = OperatingSystem.instance().processManagerInstance()
+					.getProcess(myPid);
+			String cmd = myProcess.getCommand();
+			String jvm = null;
+			if (cmd.startsWith("\"")){
+				jvm = cmd.substring(0, cmd.indexOf("\" ") + 1);
+			}else
+			{
+				int firstSpace = cmd.indexOf(" ");
+				if (firstSpace > -1){
+					jvm = cmd.substring(0, cmd.indexOf(" "));
+				}else{
+					jvm = cmd;
+				}
+			}
+			return jvm;
 		}
-		return jvm;
+
+		return Paths.get(System.getenv(ENV_JAVA_HOME)).resolve("bin").resolve("java").toString();		
 	}
 
 	public String getCommandInternal()

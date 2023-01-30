--- ../../yajsw-12.16_unmodified/src/yajsw/src/main/java/org/rzo/yajsw/WrapperExe.java	2021-04-19 16:10:42.000000000 -0400
+++ ../src/yajsw/src/main/java/org/rzo/yajsw/WrapperExe.java	2021-08-11 13:17:58.342972501 -0400
@@ -107,9 +107,13 @@
 	 */
 	public static void main(String[] args)
 	{
-		System.out.println("YAJSW: " + YajswVersion.YAJSW_VERSION);
-		System.out.println("OS   : " + YajswVersion.OS_VERSION);
-		System.out.println("JVM  : " + YajswVersion.JAVA_VERSION);
+	        /*
+                 * bkowal
+                 * Suppress extraneous output.
+                 */
+                // System.out.println("YAJSW: " + YajswVersion.YAJSW_VERSION);
+		// System.out.println("OS   : " + YajswVersion.OS_VERSION);
+		// System.out.println("JVM  : " + YajswVersion.JAVA_VERSION);
 		String wrapperJar = WrapperLoader.getWrapperJar();
 		String homeDir = new File(wrapperJar).getParent();
 		if (!OperatingSystem.instance().setWorkingDir(homeDir))

--- ../../yajsw-12.16_unmodified/src/yajsw/src/main/java/org/rzo/yajsw/os/posix/bsd/AppStarter.java	2021-04-19 16:10:42.000000000 -0400
+++ ../src/yajsw/src/main/java/org/rzo/yajsw/os/posix/bsd/AppStarter.java	2021-08-11 14:47:11.647041815 -0400
@@ -46,8 +46,10 @@
 		// detach from parent
 		CLibrary.INSTANCE.umask(0);
 		CLibrary.INSTANCE.setsid();
-
-		System.out.println("calling exec");
+		/*
+		 * bkowal Suppress extraneous output.
+ 		 */
+		//System.out.println("calling exec");
 		// close streams ?
 		if (!isPipeStreams())
 		{

--- ../../yajsw-12.16_unmodified/src/yajsw/src/main/java/org/rzo/yajsw/app/WrapperManagerImpl.java	2021-04-19 16:10:42.000000000 -0400
+++ ../src/yajsw/src/main/java/org/rzo/yajsw/app/WrapperManagerImpl.java	2021-08-12 14:35:34.378307892 -0400
@@ -247,9 +247,12 @@
 		 * (InterruptedException e1) { // TODO Auto-generated catch block
 		 * e1.printStackTrace(); }
 		 */
-		System.out.println("YAJSW: " + YajswVersion.YAJSW_VERSION);
-		System.out.println("OS   : " + YajswVersion.OS_VERSION);
-		System.out.println("JVM  : " + YajswVersion.JAVA_VERSION);
+                 /*
+                  * bkowal Suppress extraneous output.
+                  */
+		//System.out.println("YAJSW: " + YajswVersion.YAJSW_VERSION);
+		//System.out.println("OS   : " + YajswVersion.OS_VERSION);
+		//System.out.println("JVM  : " + YajswVersion.JAVA_VERSION);
 		// set commons logging for vfs -> avoid using default java logger
 		ClassLoader currentClassLoader = Thread.currentThread()
 				.getContextClassLoader();
@@ -653,11 +656,16 @@
 				{
 					minorGCBeanX = gcBean;
 				}
-				else if (gcBean.getName().toLowerCase().contains("scavenge"))
+				/*
+				 * D. Friedman  2017-02-10  DR 19670 -- Recognize G1 GC beans
+ 				 */
+				else if (gcBean.getName().toLowerCase().contains("scavenge")
+					|| gcBean.getName().equals("G1 Young Generation"))
 				{
 					minorGCBeanX = gcBean;
 				}
-				else if (gcBean.getName().toLowerCase().contains("marksweep"))
+				else if (gcBean.getName().toLowerCase().contains("marksweep")
+					|| gcBean.getName().equals("G1 Old Generation"))
 				{
 					fullGCBeanX = gcBean;
 				}
@@ -1222,6 +1230,9 @@
 								{
 									if (minorGCDuration == -1)
 										getGCData();
+									/*
+									 * D. Friedman  2017-02-10  DR 19670 -- Do not send null value
+									 */
 									future = _session
 											.writeAndFlush(new Message(
 													Constants.WRAPPER_MSG_PING,
@@ -1231,7 +1242,7 @@
 															+ ";"
 															+ fullGCDuration
 															+ ";"
-															+ lastUsedHeap));
+															+ (lastUsedHeap != null ? lastUsedHeap : -1)));
 									currentPercentHeap = -1;
 									minorGCDuration = -1;
 									fullGCDuration = -1;
@@ -1409,7 +1420,12 @@
 			if (msg.getCode() == Constants.WRAPPER_MSG_STOP)
 				try
 				{
-					System.out.println("wrapper manager received "+msg);
+					/*
+ 					 * bkowal Suppress extraneous output unless debug is enabled
+   					 */ 
+					if (_debug > 0) {
+						System.out.println("wrapper manager received "+msg);
+					}
 					_stopping = true;
 
 					if (session != null)

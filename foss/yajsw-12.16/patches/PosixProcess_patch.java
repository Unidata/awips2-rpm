--- ../../yajsw-12.16_unmodified/src/yajsw/src/main/java/org/rzo/yajsw/os/posix/PosixProcess.java	2021-04-19 16:10:42.000000000 -0400
+++ ../src/yajsw/src/main/java/org/rzo/yajsw/os/posix/PosixProcess.java	2021-08-11 14:34:29.141230328 -0400
@@ -805,7 +805,12 @@
 			return false;
 		if (_arrCmd == null) {
 			_arrCmd = _cmd.split(" ");
-			log("exec: " + _cmd);
+			/*
+			 * bkowal Suppress extraneous output unless debug is enabled.
+	 		 */
+			if (_debug) {
+				log("exec: " + _cmd);
+			}
 		} else {
 			String cmd = "";
 			for (String c : _arrCmd) {
@@ -816,8 +821,12 @@
 					cmd += c + " ";
 				}
 			}
-			// if (_debug)
-			log("exec:" + cmd);
+			/*
+			 * bkowal Suppress extraneous output unless debug is enabled.
+			 */
+			if (_debug) {
+				log("exec:" + cmd);
+			}
 		}
 		//
 		if (stdout == -1) {
@@ -867,7 +876,12 @@
 		if ((pid = CLibrary.INSTANCE.fork()) == 0) {
 			if (_umask != -1)
 				umask(_umask);
-			System.out.println("fork 0");
+			/*
+ 			 * bkowal Suppress extraneous output unless debug is enabled.
+ 			 */
+			if (_debug) {
+				System.out.println("fork 0");
+			}
 
 			// closeDescriptors();
 
@@ -875,8 +889,12 @@
 			if (getWorkingDir() != null)
 				if (CLibrary.INSTANCE.chdir(getWorkingDir()) != 0)
 					log("could not set working dir");
-
-			System.out.println("fork 1");
+			/*
+			 * bkowal Suppress extraneous output unless debug is enabled.
+			 */
+                        if (_debug) {
+				System.out.println("fork 1");
+			}
 
 			// set priority
 			if (_priority == PRIORITY_BELOW_NORMAL) {
@@ -894,7 +912,12 @@
 			}
 			if (getUser() != null)
 				switchUser(getUser(), getPassword());
-			System.out.println("fork 2");
+				/*
+				 * bkowal Suppress extraneous output unless debug is enabled.
+				 */
+				if (_debug) {
+					System.out.println("fork 2");
+				}
 
 			// try
 			// {
@@ -1044,7 +1067,10 @@
 				int r = 0;
 				while (r != _pid && r != -1) {
 					r = CLibrary.INSTANCE.waitpid(_pid, status, 0);
-					if (_logger != null)
+					/*
+					 * bkowal Suppress extraneous output unless debug is enabled.
+ 					 */
+					if (_logger != null && _debug)
 						_logger.info("waitpid " + r + " " + status.getValue());
 				}
 				if (r == _pid) {
@@ -1058,7 +1084,10 @@
 					//	_exitCode = 0;
 						_exitSignal = WTERMSIG(code);
 				}
-				if (_logger != null)
+				/*
+				 * bkowal Suppress extraneous output unless debug is enabled.
+				 */
+				if (_logger != null && _debug)
 					_logger.info("exit code posix process: "
 							+ status.getValue() + " application(status/signal): " + _exitCode+"/"+_exitSignal);
 				_terminated = true;
@@ -1066,7 +1095,10 @@
 
 		});
 
-		if (_logger != null)
+		/*
+		 * bkowal Suppress extraneous output unless debug is enabled.
+		 */
+		if (_logger != null && _debug)
 			_logger.info("started process " + _pid);
 	}
 

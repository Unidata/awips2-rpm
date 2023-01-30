--- ../../yajsw-12.16_unmodified/src/yajsw/src/main/java/org/rzo/yajsw/script/AbstractScript.java	2021-04-19 16:10:42.000000000 -0400
+++ ../src/yajsw/src/main/java/org/rzo/yajsw/script/AbstractScript.java	2021-08-12 13:03:37.112747533 -0400
@@ -113,56 +113,34 @@
 					+ " : too many concurrent invocations -> abort execution");
 			return;
 		}
-		Object result = null;
-		log("executeWithTimeout script: " + _name);
-
-		Timeout timerTimeout = TIMER.newTimeout(new TimerTask()
-		{
-
-			public void run(Timeout arg0) throws Exception
-			{
-				log("script "+_name+" timed out -> interrupt");
-				try
-				{
-					interrupt();
-				}
-				catch (Throwable e)
-				{
-
-				}
-			}
-
-		}, _timeout, TimeUnit.MILLISECONDS);
-		_timerTimeout.set(timerTimeout);
-		_future = EXECUTOR.submit(new Callable<Object>()
+		/* Changed by rjpeter Aug 07, 2014.
+		 * 
+		 * Ensures that the main shutdown thread of YAJSW will wait for the
+		 * script to run and finish.
+		 */
+		 _future = EXECUTOR.submit(new Callable<Object>()
 		{
 			public Object call()
 			{
-				log("executing script: " + _name);
-				Object result = execute(line);
-				if (_timerTimeout.get() != null)
-					_timerTimeout.get().cancel();
-				_timerTimeout.set(null);
-				_remainingConcInvocations.incrementAndGet();
-				log("executed script: " + _name + " "
-						+ result);
-				return result;
+				return execute(line);
 			}
 		});
-		Thread.yield();
+		// wait for script to finish
 		try {
-			 result = _future.get(_timeout, TimeUnit.MILLISECONDS);
-		} catch (InterruptedException e) {
-			// TODO Auto-generated catch block
-			e.printStackTrace();
-		} catch (ExecutionException e) {
-			// TODO Auto-generated catch block
-			e.printStackTrace();
+			_future.get(_timeout, TimeUnit.MILLISECONDS);
 		} catch (TimeoutException e) {
-			// TODO Auto-generated catch block
-			e.printStackTrace();
+			log("Script " + _name + " took too long -> interrupt");
+			try {
+				interrupt();
+			} catch (Throwable t) {
+				log("Interrupt of script " + _name + " has failed: "
+					+ e.getLocalizedMessage() + "!");
+			}
+		} catch (Exception e) {
+			 log("Script " + _name + " failed to complete: " +
+				e.getLocalizedMessage() + "!");
 		}
-		log("script done: "+result);
+		Thread.yield();
 	}
 
 	private boolean checkRemainConc()

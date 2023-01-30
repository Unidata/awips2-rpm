/*******************************************************************************
 * Copyright  2015 rzorzorzo@users.sf.net
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *******************************************************************************/

package org.rzo.yajsw.script;

import java.io.InputStream;
import java.util.concurrent.Callable;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

import org.rzo.yajsw.os.OperatingSystem;
import org.rzo.yajsw.util.DaemonThreadFactory;
import org.rzo.yajsw.wrapper.WrappedProcess;

import io.netty.util.Timeout;
import io.netty.util.TimerTask;

// TODO: Auto-generated Javadoc
/**
 * The Class ShellScript.
 */
public class ShellScript extends AbstractScript
{
	String[] _cmd;
	AtomicReference<Process> p = new AtomicReference();
	protected static final Executor executor = Executors
			.newCachedThreadPool(new DaemonThreadFactory("yajsw.shellscript"));

	/**
	 * Instantiates a new shell script.
	 * 
	 * @param script
	 *            the script
	 * @param timeout
	 */
	public ShellScript(String script, String id, WrappedProcess process,
			String[] args, int timeout, int maxConcInvocations)
	{
		super(script, id, process, args, timeout,
				maxConcInvocations);
		if (script.endsWith(".sh"))
			_cmd = new String[]{"/bin/sh"};
		if (script.endsWith("bat"))
			_cmd = new String[]{"cmd", "/c"};
	}

	/*
_pro	 * 
	 * @see org.rzo.yajsw.script.AbstractScript#execute(java.lang.String,
	 * java.lang.String, java.lang.String, java.lang.String, java.lang.String,
	 * java.lang.String, java.lang.Object)
	 */
	public Object execute(String line)
	{
		//log("shellscript execute "+getScript());
		String id = _id;
		String state = _process != null ? _process.getStringState() : "?";
		String count = _process != null ? "" + _process.getRestartCount() : "?";
		String pid = _process != null ? "" + _process.getAppPid() : "?";
		String exitCode = _process != null ? "" + _process.getExitCode() : "?";
		String[] cmd = _cmd == null ? new String[7] : new String[_cmd.length+7];
		int i=0;
		if (_cmd != null)
		for (i=0; i<_cmd.length; i++)
			cmd[i] = _cmd[i];
		cmd[i] = getScript();
		cmd[i+1] = id;
		cmd[i+2] = state;
		cmd[i+3] = count;
		cmd[i+4] = pid;
		cmd[i+5] = exitCode;
		cmd[i+6] = line == null ? "?" : line;
		String ccmd = "";
		for (String x:cmd)
			ccmd += x+" ";
		try
		{
			String result = osCommand(cmd, _timeout);
			return result;
		}
		catch (Exception ex)
		{
			ex.printStackTrace();
		}
		return null;
	}

	@Override
	public void interrupt()
	{
		if (p.get() != null)
			p.get().destroy();
		p.set(null);
		if (_future != null)
			_future.cancel(true);
	}

	void log(String msg)
	{
		if (_process != null && _process.getInternalWrapperLogger() != null)
			_process.getInternalWrapperLogger().info(msg);
		else
			System.out.println(msg);
	}
	
	void log (Exception e)
	{
		if (_process != null && _process.getInternalWrapperLogger() != null)
			_process.getInternalWrapperLogger().warn(e);
		else
			e.printStackTrace();
		
	}
	
	public String osCommand(String[] cmd, long timeout)
	{
		try
		{
			p.set(Runtime.getRuntime().exec(cmd));
			FutureTask<String> future = new FutureTask(new Callable()
			{

				public String call() throws Exception
				{
					StringBuffer result = new StringBuffer();
					InputStream in = p.get().getInputStream();
					InputStream err = p.get().getErrorStream();
					int x;
					int y;
					while ((x = in.read()) != -1)
						result.append((char) x);
					while ((y = err.read()) != -1)
						result.append((char) y);

					return result.toString();
				}
			});
			executor.execute(future);
			String result = future.get(timeout, TimeUnit.MILLISECONDS);
			return result;

		}
		catch (Exception e)
		{
			log("Error executing \"" + getScript() + "\": " + e);
			log(e);
			interrupt();
		}
		return null;
	}



}

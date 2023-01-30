package org.rzo.yajsw.config;

import java.util.Map;

public interface YajswConfigurationInterpolator
{
	public Object interpolate(Object name);

	public Object getBinding();

	public Map<? extends String, ? extends String> getFromBinding();

	public Map<String, String> getUsedEnvVars();

}

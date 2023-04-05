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

package org.rzo.yajsw.io;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.util.Arrays;

// TODO: Auto-generated Javadoc
/**
 * The Class CyclicBufferFilePrintStream.
 */
public class CyclicBufferFilePrintStream extends PrintStream
{

	/** The length. */
	public static int length = 1024 * 200;

	/**
	 * New output stream.
	 * 
	 * @param raf
	 *            the raf
	 * 
	 * @return the output stream
	 * 
	 * @throws IOException
	 *             Signals that an I/O exception has occurred.
	 */
	public static OutputStream newOutputStream(final RandomAccessFile raf)
			throws IOException
	{
		return new OutputStream()
		{
			ByteBuffer buf = raf.getChannel().map(
					FileChannel.MapMode.READ_WRITE, 5, length - 5);
			ByteBuffer posBuf = raf.getChannel().map(
					FileChannel.MapMode.READ_WRITE, 1, 4);
			ByteBuffer lockBuf = raf.getChannel().map(
					FileChannel.MapMode.READ_WRITE, 0, 1);

			// RandomAccessFile _raf = raf;

			@Override
			public synchronized void close() throws IOException
			{
				super.close();
				raf.close();
			}

			private void lock()
			{
				lockBuf.position(0);
				lockBuf.put((byte) 1);
			}

			private void unlock()
			{
				lockBuf.position(0);
				lockBuf.put((byte) 0);
			}

			private void setPosition(int pos)
			{
				posBuf.position(0);
				posBuf.putInt(pos);
			}

			@Override
			public synchronized void write(int b) throws IOException
			{
				lock();
				if (buf.remaining() == 0)
				{
					buf.position(0);
					// System.out.println("buffer overwrite");
				}
				buf.put((byte) b);
				setPosition(buf.position());
				unlock();
			}

			@Override
			public synchronized void write(byte[] bytes, int off, int len)
					throws IOException
			{
				lock();
				int toWrite = buf.remaining() > len ? len : buf.remaining();
				// System.out.println("write "+buf.position() +
				// " "+len+" "+buf.remaining());
				buf.put(bytes, off, toWrite);

				if (toWrite != len)
				{
					// System.out.println("buffer overwrite");
					buf.position(0);
					buf.put(bytes, off + toWrite, len - toWrite);
				}
				setPosition(buf.position());
				unlock();
			}
		};
	}

	/**
	 * Instantiates a new cyclic buffer file print stream.
	 * 
	 * @param file
	 *            the file
	 * 
	 * @throws IOException
	 *             Signals that an I/O exception has occurred.
	 */
	public CyclicBufferFilePrintStream(File file) throws IOException
	{
		super(newOutputStream(new RandomAccessFile(file, "rw")));
	}

	/**
	 * The main method.
	 * 
	 * @param args
	 *            the arguments
	 */
	public static void main(String[] args)
	{
		try
		{
			CyclicBufferFilePrintStream writer = new CyclicBufferFilePrintStream(
					new File("test.dat"));
			for (int i = 0; i < 10000000; i++)
			{
				char[] bytes = new char[1024 - ("" + System.currentTimeMillis())
						.length() - 1];
				Arrays.fill(bytes, ("" + (i % 10)).charAt(0));
				String s = "" + System.currentTimeMillis() + ":"
						+ new String(bytes);
				writer.println(s);
				System.out.println(s);
				if (i % 2 == 0)
					try
					{
						Thread.sleep(500);
					}
					catch (InterruptedException e)
					{
						e.printStackTrace();
						Thread.currentThread().interrupt();
					}
			}
		}
		catch (IOException e)
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}
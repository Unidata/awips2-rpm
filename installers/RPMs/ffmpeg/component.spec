%define _ffmpeg_version 5.0-static
%define _ffmpeg_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II FFMPEG Spec File
#

Name: awips2-ffmpeg
Summary: AWIPS II ffmpeg Distribution
Version: 5.0
Release: 1%{?dist}
Group: AWIPSII
BuildRoot: /tmp
BuildArch: x86_64
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
Packager: %{_build_site}

AutoReq: no
Provides: awips2-ffmpeg

%description
AWIPS II FFMPEG Distribution - Contains AWIPS II FFMPEG Binary.

%prep
# Ensure that a "buildroot" has been specified.
if [ "%{_build_root}" = "" ]
then
    echo "ERROR: A BuildRoot has not been specified."
    echo "FATAL: Unable to Continue ... Terminating."
    exit 1
fi

if [ -d %{_build_root} ]
then
    rm --recursive --force %{_build_root}
fi
if [ -d %{_ffmpeg_build_loc} ]; then
    rm --recursive --force %{_ffmpeg_build_loc}
fi
mkdir --parents %{_ffmpeg_build_loc}
if [ $? -ne 0 ]; then
    exit 1
fi

%install
_ffmpeg_destination=%{_build_root}/usr/bin/
_ffmpeg_dir=%{_baseline_workspace}/foss/ffmpeg-%{_ffmpeg_version}
_ffmpeg_file=ffmpeg-%{_ffmpeg_version}.tar.gz

cp ${_ffmpeg_dir}/${_ffmpeg_file} %{_ffmpeg_build_loc}
cd %{_ffmpeg_build_loc}
tar --extract --file ${_ffmpeg_file}
mkdir --parents ${_ffmpeg_destination}
cp ffmpeg-%{_ffmpeg_version}/ffmpeg ${_ffmpeg_destination}

%clean
rm --recursive --force ${RPM_BUILD_ROOT}
rm --recursive --force %{_ffmpeg_build_loc}

%files
%defattr(755,root,root,755)
/usr/bin/ffmpeg

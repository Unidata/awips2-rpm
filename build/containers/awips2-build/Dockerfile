#
# AWIPS II build container
# 
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    Apr 20, 2021  8437      tgurney      Initial creation
#    Jun  4, 2021  8437      tgurney      Change volume mounts
#    Jun 10, 2021  8437      tgurney      Combine Dockerfiles into one.
#                                         Move user and group creation to
#                                         a script executed at run time.
#                                         Run the build as non-root user
#    Jun 21, 2021  8543      tgurney      Add PostgreSQL 12
#    Jun 30, 2021  8437      tgurney      Add a fixed sync_workspace.sh.
#                                         Remove CentOS 8 workarounds
#    Jul 14, 2021  8437      tgurney      Add python3-tkinter
#    Jul 26, 2021  8437      tgurney      Move certificate install to the end
#    Jul 28, 2021  8437      tgurney      Change CentOS 8 to Rocky 8
#    Aug 04, 2021  8599      dgilling     Enable python38 modules to make 
#                                         additional packages from Code Ready
#                                         Builder repo available,
#                                         Add pyparsing.
#    Aug 05, 2021  8598      dgilling     Add more-itertools.
#    Aug 25, 2021  8437      tgurney      Add /install dir and creatrepo pkg
#    Sep 02, 2021  8623      dgilling     Add PyYAML.
#    Sep 16, 2021  8563      tgurney      Add tcl-devel.i686
#    Oct 28, 2021  8464      dgilling     Add i686 packages for libelf-devel, 
#                                         libxml2-devel.
#    Dec 17, 2021  8404      njensen      Add rehost scripts
#    Oct 12, 2022  8063      dgilling     Remove RHEL numpy and scipy packages.
#                                         add python38-packaging.
#    Mar 01, 2023  9047      dgilling     Upgrade to python 3.9.
#    Mar 08, 2023  9070      tgurney      Add libtiff-devel
#                                         (PROJ 8.x build dependency)
#    Mar 15, 2023  9034      tgurney      Add libqhull_r
#                                         (PostGIS 3 runtime dependency)
#    May 18, 2023 2033895    tgurney      Add gdbm, gdbm-devel (for rehost)
#    May 26, 2023 2034250    tgurney      Upgrade to python 3.11
#    Jun  2, 2023 2034252    tgurney      Remove python chardet package, not used anymore
#    Jun  7, 2023 2034280    dgilling     Add package ninja-build, a dependency for 
#                                         meson.

ARG img
FROM $img

# Allowed values are:
# rhel8
# rocky8
ARG os

# Install CA certificates
# This will allow us to download packages through the Raytheon corporate
# proxy
COPY ./image-data/certs /root/certs
RUN /root/certs/install_certs.sh

# Enable CodeReady Builder repo to get certain devel packages that are not
# available in the main repos in el8
RUN \
yum install -y yum-utils && \
if [[ "$os" == "rocky8" ]]; then \
    yum-config-manager --enable powertools \
    && yum clean all && rm --recursive --force /var/cache/yum; \
elif [[ "$os" == "rhel8" ]]; then \
    yum-config-manager --enable codeready-builder-for-rhel-8-x86_64-rpms \
    && yum clean all && rm --recursive --force /var/cache/yum; \
fi

# Install Python
RUN \
    yum install -y \
      python3.11 \
      python3.11-devel \
      python3.11-idna \
      python3.11-packaging \
      python3.11-pip \
      python3.11-pybind11 \
      python3.11-pyparsing \
      python3.11-pyyaml \
      python3.11-requests \
      python3.11-setuptools \
      python3.11-six \
      python3.11-tkinter \
      python3.11-urllib3 \
      python3.11-wheel \
    && yum -y clean all && rm --recursive --force /var/cache/yum

# 64-bit packages
RUN \ 
yum -y install \
# Must-have packages, mostly based on the CentOS Developer Tools package group
# plus a few other necessary packages
  autoconf \
  automake \
  binutils \
  bison \
  byacc \
  bzip2 \
  ca-certificates \
  cpp \
  createrepo \
  cscope \
  ctags \
  curl \
  diffstat \
  elfutils \
  findutils \
  flex \
  gcc \
  gcc-c++ \
  gcc-gfortran \
  gettext \
  git \
  glibc-common \
  glibc-devel \
  gzip \
  hostname \
  intltool \
  less \
  libstdc++-devel \
  libtool \
  make \
  ninja-build \
  patch \
  patchutils \
  perl \
  pkgconfig \
  readline \
  redhat-rpm-config \
  rpm-build \
  rpm-sign \
  rsync \
  subversion \
  sudo \
  swig \
  systemtap \
  unzip \
  vim \
  zip \
# Put any "BuildRequires" dependencies of your packages here.
# For packages that are part of the build environment in SetupEnvironment.sh,
# also put the "Requires" dependencies here.
  blas \
  blas-devel \
  bzip2-devel \
  boost \
  boost-devel \
  cairo \
  cairo-devel \
  cairo-gobject-devel \
  cmake \
  cyrus-sasl \
  cyrus-sasl-devel \
  cyrus-sasl-md5 \
  cyrus-sasl-plain \
  freetype \
  freetype-devel \
  glib2 \
  glib2-devel \
  gobject-introspection \
  gobject-introspection-devel \
  gtk3 \
  imake \
  initscripts \
  jasper-devel \
  jasper-libs \
  java-11-openjdk-devel \
  ksh \
  lapack \
  lapack-devel \
  libcurl-devel \
  libffi \
  libffi-devel \
  libgfortran \
  libicu-devel \
  libjpeg-turbo \
  libjpeg-turbo-devel \
  libpng \
  libpng-devel \
  libqhull \
  libqhull_r \
  libselinux-devel \
  libtiff-devel \
  libtirpc-devel \
  libuuid \
  libuuid-devel \
  libxml2 \
  libxml2-devel \
  libxslt \
  libxslt-devel \
  libX11-devel \
  libXt-devel \
  libyaml \
  libyaml-devel \
  lua \
  lua-devel \
  lua-libs \
  lzo-devel \
  maven \
  motif-devel \
  nspr \
  nspr-devel \
  nss \
  nss-devel \
  openldap-devel \
  openssh-clients \
  openssl \
  openssl-devel \
  pcre-devel \
  pcre2-devel \
  qhull-devel \
  readline-devel \
  rpcgen \
  sqlite-devel \
  tcl \
  tcl-devel \
  tcsh \
  tk \
  tk-devel \
  xorg-x11-server-Xvfb \
  xz-devel \
  zlib \
  zlib-devel \
# Other necessary stuff found through testing.
# Someday someone should figure out and document why each of these packages is
# needed. It could be that some are not needed at all.
# - ghostscript and poppler for additional matplotlib features
  chkconfig \
  ghostscript \
  poppler-devel \
  poppler-utils \
  ruby \
  && yum -y clean all && rm --recursive --force /var/cache/yum

# i686 packages are installed separately because yum fails otherwise
RUN yum -y install \
  boost.i686 \
  boost-devel.i686 \
  bzip2-devel.i686 \
  cyrus-sasl-devel.i686 \
  expat-devel.i686 \
  elfutils-libelf-devel.i686 \
  glibc.i686 \
  gdbm.i686 \
  gdbm-devel.i686 \
  glibc-devel.i686 \
  jasper-devel.i686 \
  keyutils-libs-devel.i686 \
  krb5-devel.i686 \
  libcom_err-devel.i686 \
  libcurl.i686 \
  libcurl-devel.i686 \
  libecpg-devel.i686 \
  libgcc.i686 \
  libgfortran.i686 \
  libICE-devel.i686 \
  libicu-devel.i686 \
  libjpeg-turbo-devel.i686 \
  libpgtypes.i686 \
  libpq-devel.i686 \
  libquadmath-devel.i686 \
  libSM-devel.i686 \
  libstdc++.i686 \
  libstdc++-devel.i686 \
  libtirpc-devel.i686 \
  libuuid.i686 \
  libuuid-devel.i686 \
  libX11-devel.i686 \
  libXt-devel.i686 \
  libxml2-devel.i686 \
  motif-devel.i686 \
  nspr.i686 \
  nspr-devel.i686 \
  nss.i686 \
  nss-devel.i686 \
  openldap-devel.i686 \
  openssl-devel.i686 \
  pcre2-devel.i686 \
  tcl.i686 \
  tcl-devel.i686 \
  tk.i686 \
  tk-devel.i686 \
  zlib-devel.i686 \
  && yum -y clean all && rm --recursive --force /var/cache/yum

RUN \
  yum module install -y \
      postgresql:12/client \
      postgresql:12/server \
  && yum install -y \
      libpq-12.5-1.el8_3.x86_64 \
      libpq-devel-12.5-1.el8_3.x86_64 \
      libpq-devel-12.5-1.el8_3.i686 \
      libpgtypes.i686 \
      libecpg-devel.i686 \
      postgresql-server-devel \
  # ghostscript-devel renamed to libgs-devel
  && yum install -y libgs-devel \
  && yum -y clean all && rm -rf /var/cache/yum

# Install any temporary packages you may need here
# RUN yum install -y my-package

# Create work directories and mount points
RUN mkdir /build && \
  mkdir /awips2 && \
  mkdir /install && \
  mkdir --parents /home/build/workspace && \
  mkdir --parents /home/build/git && \
  mkdir --parents /home/build/home-data && \
  ln --symbolic ../git /home/build/workspace/git

RUN mkdir --parents /root/scripts
COPY ./image-data/scripts/sync_workspace.sh /home/build/sync_workspace.sh
COPY ./image-data/scripts/run_build.sh /home/build/run_build.sh
COPY ./image-data/scripts/run_rehost_build.sh /home/build/run_rehost_build.sh
COPY ./image-data/scripts/run.sh /root/scripts/run.sh
COPY ./image-data/scripts/initialize.sh /root/scripts/initialize.sh
COPY ./image-data/scripts/run_rehost.sh /root/scripts/run_rehost.sh
RUN chmod +x /root/scripts/run.sh
RUN chmod +x /root/scripts/initialize.sh
RUN chmod +x /home/build/run_build.sh

WORKDIR /home/build/
CMD ["/bin/bash"]

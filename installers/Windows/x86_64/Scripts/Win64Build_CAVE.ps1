#
# Build entry point for 64 Bit Windows CAVE Installer.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- ------------------------------------------------------
# Mar 11, 2015  4221     dlovely     Migration from AWIPS2_baseline plus added INNO Support
# Jun 26, 2015  4295     dlovely     Removed AlertViz
# Jul 08, 2015  4295     dlovley     Added some more error checking
#
#
# Jenkins Master/Slave Settings: 
# Under the Node Properties specify "Tool Locations" for Java and Git
#   Java = C:\Program Files\Raytheon\AWIPS II\Java
#   Git = C:\Program Files (x86)\Git\cmd\git.exe
#
# Jenkins Build Settings:
# Set Jenkins to clone AWIPS2_build to the workspace and change to the correct branch.
#   When using SSH for GIT id_rsa and known_hosts need to be manually placed in:
#     C:\Windows\SysWOW64\config\systemprofile\.ssh\
#   So the build can use these keys when running as a System Service.
#
# String Parameters passed in per build:
#   BUILD_FILE = Windows-14.4.1-Build-1
#   BUILD_VERSION = 14.4.1
#
# Windows Power Shell Build Script
#===============================================================================================================
# # Required:
# Set-Variable -name JENKINS_BUILD_VERSION -value $ENV:BUILD_VERSION
# Set-Variable -name JENKINS_BUILD_FILE -value $ENV:BUILD_FILE
# Set-Variable -name JENKINS_BUILD_JAVA_JDK_LOC -value $ENV:JAVA_HOME 
# Set-Variable -name JENKINS_WORKSAPCE_DIR -value $ENV:WORKSPACE
#
# # Only use one of the following sets:
# # (Manual) Using this you must manually place the initial Zip file in WORKSPACE\START\
# #Set-Variable -name JENKINS_BUILD_NO_SSH -value "true"
# #OR
# # (Automated) Using these settings, Jenkins will get the zip file and push the installer to a remote server.
# Set-Variable -name JENKINS_BUILD_SSH_SERVER_GET -value "jenkins@halfmaen:/home/jenkins/staging/win32-nightly"
# Set-Variable -name JENKINS_BUILD_SSH_SERVER_PUT -value "root@awipscm:/var/www/html/thinclient/x64"
# Set-Variable -name JENKINS_BUILD_PRIVATE_KEY_LOC -value "C:\SSHKeys\Private.ppk"
#
# # Set the path for the build script
# $buildScript = Join-Path $JENKINS_WORKSAPCE_DIR "Installers\Windows\x86_64\Scripts\Win64Build_CAVE.ps1"
#
# # Start the build.
# . $buildScript
# if ($? -ne $true) { EXIT 1; }
#
# EXIT 0
#===============================================================================================================
#

function Get-ScriptDirectory
{
    $Invocation = (Get-Variable MyInvocation -Scope 1).Value
    Split-Path $Invocation.MyCommand.Path
}

Set-Variable -name A2_WORKSPACE_DIR -value "C:\Build"
if ( "${JENKINS_WORKSAPCE_DIR}" -ne "" ) { 
  Set-Variable -name A2_WORKSPACE_DIR -value ${JENKINS_WORKSAPCE_DIR} 
  $environmentScript = Join-Path ${A2_WORKSPACE_DIR} "installers\Windows\x86_64\Scripts\environment.ps1"
} else {
  $environmentScript = Join-Path (Get-ScriptDirectory) environment.ps1
}

. $environmentScript

# Clean up old installers.
Remove-Item -ErrorAction SilentlyContinue -force "${A2_WORKSPACE_DIR}\AWIPS II CAVE *.exe"

# Only remove old zip files and download the current one if configured in Jenkins.
if ( "${JENKINS_BUILD_NO_SSH}" -eq "" ) { 
  # Create the Start Directory
  $startDirectory = Split-Path ${A2_START_DIR} -leaf
  $startDirectoryContainer = Split-Path ${A2_START_DIR} -parent
  if ( Test-Path ${A2_START_DIR} ) {
      Remove-Item -recurse -force ${A2_START_DIR}
      if ($? -ne $true) { EXIT 1; }
  }
  New-Item -path $startDirectoryContainer -name $startDirectory -type directory | Out-Null
  if ($? -ne $true) { EXIT 1; }

  # Retrieve the zip file
  & "${PSCP_EXE_DIR}\pscp.exe" -i ${SSH_PRIVATE_KEY} ${SSH_SERVER_GET}/CAVE-${AWIPS2_VERSION}-${JENKINS_BUILD_FILE}.zip ${A2_START_DIR}
  if ($? -ne $true) { EXIT 1; }
}

# Get the name of the zip file.
$zipFile = Get-ChildItem ${A2_START_DIR} -filter "*.zip" -name

# Extract CAVE.
. ${A2_SCRIPTS_DIR}\prepare.ps1 "$zipFile"
if ($? -ne $true) { EXIT 1; }

# Extract the Inno setup zip.
pushd .
cd ${A2_TOOLS_DIR}

if ( Test-Path ${INNO_EXE_DIR} ) {
    Remove-Item -recurse -force ${INNO_EXE_DIR}
    if ($? -ne $true) { EXIT 1; }
}

& "$JAVA_JDK_DIR\bin\jar.exe" xvf ${INNO_ZIP_FILE}
if ( $? -ne $true ) {
    echo "FATAL: Failed to unzip ${INNO_ZIP_FILE}".
    EXIT 1
}
popd

# Compile the INNO Setup
& "${INNO_EXE_DIR}\ISCC.exe" /DVERSION=${AWIPS2_VERSION} /DOUTPUT_DIR=${A2_WORKSPACE_DIR} /DSOURCE_DIR=${A2_PREPARE_CAVE_DIR} `
                             /DLICENSE_DIR=${INNO_LIC_DIR} /DBUILD_FILE=${JENKINS_BUILD_FILE} ${A2_SCRIPTS_DIR}\Script.iss
if ($? -ne $true) { EXIT 1; }

# Only upload the current installer if configured in Jenkins.
if ( "${JENKINS_BUILD_NO_SSH}" -eq "" ) { 
  # Upload the Setup
  & "${PSCP_EXE_DIR}\pscp.exe" -i ${SSH_PRIVATE_KEY} ${A2_WORKSPACE_DIR}\*.exe ${SSH_SERVER_PUT}/${AWIPS2_VERSION}
  if ($? -ne $true) { EXIT 1; }
}

;
; SCRIPT HISTORY
;
; Date          Ticket#  Engineer    Description
; ------------- -------- ----------- ----------------------------
; Mar 11, 2015  4221     dlovely     Initial creation
; Feb 15, 2016  4343     dlovely     Updated for 16.1.1
; Feb 16, 2016  5015     dlovely     Updated for 16.2.1
; Feb 24, 2016  5333     dlovely     Updated Java to 1.8u74
; May 04, 2016  5333     dlovely     Updated Java to 1.8u77; Simplified config
; May 16, 2016  5582     dlovely     Upgraded Jep to 3.5.2
; Jun 10, 2016  5582     dlovely     Upgraded Jep to 3.5.3
;

; Configuration for this installer:
#define AWIPSVersion "16.4.1.1"
#define JavaVersion "8.0.77"
#define PythonVersion "2.7.10"

[Setup]
AppId=51618112-45E0-4E45-A5D7-104E0A46C5DF

AppName=AWIPS II Runtime Environment x64 
AppVersion={#AWIPSVersion}
AppVerName=AWIPS II Runtime Environment {#AWIPSVersion} x64 
AppCopyright=Copyright © {#GetDateTimeString('yyyy', '', '')} Raytheon
AppPublisher=Raytheon
AppPublisherURL=http://www.raytheon.com

VersionInfoVersion={#AWIPSVersion}

DefaultDirName={pf}\Raytheon\AWIPS II
DefaultGroupName=AWIPS II

OutputDir=C:\Setup\Installer
OutputBaseFilename=AWIPS II Runtime Environment {#AWIPSVersion} x64 

Compression=lzma
SolidCompression=yes

ShowLanguageDialog=no

ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

SourceDir=C:\Setup\Program\
LicenseFile=C:\Setup\License.txt

[Languages]
Name: english; MessagesFile: compiler:Default.isl

[Components]
Name: java; Description: "AWIPS II Java Files"; Types: full custom
Name: python; Description: "AWIPS II Python Files"; Types: full custom

[Files]
Source: FOSS_licenses.zip; DestDir: {app}; Flags: ignoreversion 64bit
Source: Master_Rights_File.pdf; DestDir: {app}; Flags: ignoreversion 64bit
Source: Java\*; DestDir: {app}\Java; Components: java; Flags: ignoreversion recursesubdirs 64bit
Source: Python\*; DestDir: {app}\Python; Components: python; Flags: ignoreversion recursesubdirs 64bit

[Icons]
Name: {group}\{cm:UninstallProgram,AWIPS II Runtime Environment x64}; Filename: {uninstallexe}

[Registry]  
Root: HKLM64; Subkey: "Software\Raytheon"; Flags: uninsdeletekeyifempty

Root: HKLM64; Subkey: "Software\Raytheon\Runtime Environment"; ValueType: string; ValueName: "Name"; ValueData: "AWIPS II Runtime Environment x64"; Flags: uninsdeletekey

Root: HKLM64; Subkey: "Software\Raytheon\Runtime Environment\AWIPS II Java"; ValueType: string; ValueName: "JavaInstallDirectory"; ValueData: "{app}\Java"; Components: java; Flags: uninsdeletekey
Root: HKLM64; Subkey: "Software\Raytheon\Runtime Environment\AWIPS II Java"; ValueType: string; ValueName: "JavaJdkDirectory"; ValueData: "{app}\Java"; Components: java; Flags: uninsdeletekey
Root: HKLM64; Subkey: "Software\Raytheon\Runtime Environment\AWIPS II Java"; ValueType: string; ValueName: "JavaJreDirectory"; ValueData: "{app}\Java\jre"; Components: java; Flags: uninsdeletekey
Root: HKLM64; Subkey: "Software\Raytheon\Runtime Environment\AWIPS II Java"; ValueType: string; ValueName: "JavaVersion"; ValueData: {#JavaVersion}; Components: java; Flags: uninsdeletekey

Root: HKLM64; Subkey: "Software\Raytheon\Runtime Environment\AWIPS II Python"; ValueType: string; ValueName: "PythonInstallDirectory"; ValueData: "{app}\Python"; Components: python; Flags: uninsdeletekey
Root: HKLM64; Subkey: "Software\Raytheon\Runtime Environment\AWIPS II Python"; ValueType: string; ValueName: "PythonVersion"; ValueData: {#PythonVersion}; Components: python; Flags: uninsdeletekey

[UninstallDelete]
Type: filesandordirs; Name: {app}\FOSS_licenses.zip
Type: filesandordirs; Name: {app}\Master_Rights_File.pdf
Type: filesandordirs; Name: {app}\Java\*; Components: java
Type: filesandordirs; Name: {app}\Python\*; Components: python
Type: dirifempty; Name: {app}

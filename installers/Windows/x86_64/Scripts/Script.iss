;
; Build script for 64 Bit CAVE. This script uses the following parameters passed in 
; from the command line. Noted by the {#*} notation in this script.
;
; VERSION=${AWIPS2_VERSION}
; OUTPUT_DIR=${A2_WORKSPACE_DIR}
; SOURCE_DIR=${A2_PREPARE_CAVE_DIR}
; LICENSE_DIR=${INNO_LIC_DIR}
; BUILD_FILE=${JENKINS_BUILD_FILE}
;
; SCRIPT HISTORY
;
; Date          Ticket#  Engineer    Description
; ------------- -------- ----------- -----------------------------
; Mar 11, 2015  4221     dlovely     Initial creation
; Apr 13, 2015  4382     dlovely     Updates bat file with Java/Python Locations
; May 21, 2015  4295     dlovely     Removed permission change on etc directory
; Jun 25, 2015  4295     dlovely     Removed Alertviz from installer
; Jun 30, 2015  4295     dlovely     Removed Cave.bat, Added env vars to registry
; Jul 08, 2015  4295     dlovely     Added function to clear Windows icon cache
; Aug 03, 2015  4694     dlovely     Logback will now add user.home to LOGDIR
;

[Setup]
; Unique Application GUID. This does not change version to version.
AppId=BCB286A6-F633-4767-B673-17213F3F8390

AppName=AWIPS II CAVE
AppVersion={#VERSION}
AppVerName=AWIPS II CAVE {#VERSION}
AppCopyright=Copyright © 2015 Raytheon
AppPublisher=Raytheon
AppPublisherURL=http://www.raytheon.com

; Do not warn that the dir exist since A2RE will always install first
DirExistsWarning=no

; Start Menu Info
DefaultDirName={pf}\Raytheon\AWIPS II
DefaultGroupName=AWIPS II

; Output file location and name
OutputDir={#OUTPUT_DIR}
OutputBaseFilename=AWIPS II CAVE {#BUILD_FILE} x64

Compression=lzma
SolidCompression=yes

ShowLanguageDialog=no

ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Source directory defines where the applications are.
; This is passed in from the build system.
SourceDir={#SOURCE_DIR}
LicenseFile={#LICENSE_DIR}\License.txt

; Reload the environment
ChangesEnvironment=yes

[Languages]
Name: english; MessagesFile: compiler:Default.isl

[Components]
; Option to install CAVE - Requires check for A2RE to be installed
Name: cave; Description: "AWIPS II CAVE Files"; Types: full custom; Check: InitializeSetup

[Tasks]
; Create the desktop icons
Name: desktopicon; Description: {cm:CreateDesktopIcon}; GroupDescription: {cm:AdditionalIcons}; Flags: checkedonce

[Files]
; Location for CAVE Application files
Source: CAVE\*; DestDir: {app}\CAVE; Components: cave; Flags: ignoreversion recursesubdirs 64bit; Excludes: "cave.exe"
Source: CAVE\cave.exe; DestDir: {app}\CAVE; Components: cave; Flags: ignoreversion 64bit; AfterInstall: RefreshIcons

[Icons]
; Icons for CAVE
Name: {commondesktop}\AWIPS II CAVE; Filename: {app}\Cave\cave.exe; Parameters: "-component thinclient"; Tasks: desktopicon; WorkingDir: {app}\Cave; Comment: "AWIPS II CAVE"; Components: cave; IconFilename: {app}\CAVE\cave.exe
Name: {group}\AWIPS II CAVE; Filename: {app}\Cave\cave.exe; Parameters: "-component thinclient"; WorkingDir: {app}\Cave; Comment: "AWIPS II CAVE"; Components: cave; IconFilename: {app}\CAVE\cave.exe
; Uninstaller Icon - Start Menu Only. 
Name: {group}\{cm:UninstallProgram,AWIPS II CAVE}; Filename: {uninstallexe}

[UninstallDelete]
Type: filesandordirs; Name: {app}\CAVE\*; Components: cave
; Only delete the Application directory if empty since A2RE would still be installed.
Type: dirifempty; Name: {app}

[Registry]
; Add the LOGDIR env variable. 
Root: HKLM64; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "LOGDIR"; ValueData: "caveData\logs"; Flags: uninsdeletevalue

; Modify the sytem path, this will check each addition to see if it is already in the path before adding.
Root: HKLM64; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{code:GetPythonDir};{olddata}"; Check: AddToPath(ExpandConstant('{code:GetPythonDir}'))
Root: HKLM64; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{code:GetPythonDir}\DLLs;{olddata}"; Check: AddToPath(ExpandConstant('{code:GetPythonDir}\DLLs'))
Root: HKLM64; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{code:GetPythonDir}\Lib\site-packages\jep;{olddata}"; Check: AddToPath(ExpandConstant('{code:GetPythonDir}\Lib\site-packages\jep'))
Root: HKLM64; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{code:GetJavaDir}\bin;{olddata}"; Check: AddToPath(ExpandConstant('{code:GetJavaDir}\bin'))
Root: HKLM64; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{app}\Cave\lib;{olddata}"; Check: AddToPath(ExpandConstant('{app}\Cave\lib'))

; Add the PythonPath env variable. 
Root: HKLM64; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "PythonPath"; ValueData: "{app}\Cave\lib"; Flags: uninsdeletevalue
Root: HKLM64; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "PythonPath"; ValueData: "{code:GetPythonDir}\Lib\lib-tk;{olddata}"; Flags: uninsdeletevalue
Root: HKLM64; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "PythonPath"; ValueData: "{code:GetPythonDir}\DLLs;{olddata}"; Flags: uninsdeletevalue
Root: HKLM64; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "PythonPath"; ValueData: "{code:GetPythonDir}\Lib;{olddata}"; Flags: uninsdeletevalue
Root: HKLM64; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "PythonPath"; ValueData: "{code:GetPythonDir};{olddata}"; Flags: uninsdeletevalue
    
[Code]
// Function to check to see if the A2RE was installed. Checks the registry key
// HKLM:Software\Raytheon\Runtime Environment. This is run during install time.
function InitializeSetup: Boolean;
begin
  Result := True;
  if not RegKeyExists(HKLM64, 'Software\Raytheon\Runtime Environment') then
  begin
    Result := False;
    MsgBox('The AWIPS II Runtime Environment (x64) must be installed before AWIPS II CAVE can be installed.', mbError, MB_OK);
  end;
end;

// Function to return the current A2RE Java JRE Directory key.
function GetJavaDir(Param: String): String;
var
    JavaDir : String;
begin
    Result := 'C:\Program Files\Raytheon\AWIPS II\Java\jre';
    if RegQueryStringValue(HKLM64, 'Software\Raytheon\Runtime Environment\AWIPS II Java', 'JavaJreDirectory', JavaDir) then
    begin
        Result := JavaDir;
    end;
end;

// Function to return the current A2RE Python Directory key.
function GetPythonDir(Param: String): String;
var
    PythonDir : String;
begin
    Result := 'C:\Program Files\Raytheon\AWIPS II\Python';
    if RegQueryStringValue(HKLM64, 'Software\Raytheon\Runtime Environment\AWIPS II Python', 'PythonInstallDirectory', PythonDir) then
    begin
        Result := PythonDir;
    end;
end;

// Function to check if a string is currently in the system PATH.
function AddToPath(AddingPath: String): Boolean;
var
    Path: String;
begin
    Result := True;
    if RegQueryStringValue(HKLM64,'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', Path) then
    begin
      Result := Pos(';' + UpperCase(AddingPath) + ';', ';' + UpperCase(Path) + ';') = 0;
    end;
end;

// Clear the Windows Icon cache due to an icon change in Cave.exe
procedure RefreshIcons;
var
    ResultCode: Integer;
begin
    Exec('ie4uinit.exe', '-ClearIconCache', '', SW_HIDE, ewWaitUntilTerminated, ResultCode)
end;


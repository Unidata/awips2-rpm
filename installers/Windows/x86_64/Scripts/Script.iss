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

[Languages]
Name: english; MessagesFile: compiler:Default.isl

[Components]
; Option to install CAVE - Requires check for A2RE to be installed
Name: cave; Description: "AWIPS II CAVE Files"; Types: full custom; Check: InitializeSetup
; Option to install AlertViz - Requires check for A2RE to be installed
Name: alertviz; Description: "AWIPS II AlertViz Files"; Types: full custom; Check: InitializeSetup 

[Tasks]
; Create the desktop icons
Name: desktopicon; Description: {cm:CreateDesktopIcon}; GroupDescription: {cm:AdditionalIcons}; Flags: checkedonce

[Files]
; Location for CAVE Application files
Source: CAVE\*; DestDir: {app}\CAVE; Components: cave; Flags: ignoreversion recursesubdirs 64bit; Excludes: "cave.bat"
Source: CAVE\cave.bat; DestDir: {app}\CAVE; Components: cave; Flags: ignoreversion 64bit; AfterInstall: ChangeBatPaths(ExpandConstant('{app}\Cave\cave.bat'))
; Location for AlertViz Application files
Source: AlertViz\*; DestDir: {app}\AlertViz; Components: alertviz; Flags: ignoreversion recursesubdirs 64bit; Excludes: "alertviz.bat"
Source: AlertViz\alertviz.bat; DestDir: {app}\AlertViz; Components: alertviz; Flags: ignoreversion 64bit; AfterInstall: ChangeBatPaths(ExpandConstant('{app}\AlertViz\alertviz.bat'))
  
[Icons]
; Icons for CAVE
Name: {commondesktop}\AWIPS II CAVE; Filename: {app}\Cave\cave.bat; Parameters: "-component thinclient"; Tasks: desktopicon; WorkingDir: {app}\Cave; Comment: "AWIPS II CAVE"; Components: cave; IconFilename: {app}\CAVE\cave.exe
Name: {group}\AWIPS II CAVE; Filename: {app}\Cave\cave.bat; Parameters: "-component thinclient"; WorkingDir: {app}\Cave; Comment: "AWIPS II CAVE"; Components: cave; IconFilename: {app}\CAVE\cave.exe
; Icons for AlertViz
Name: {commondesktop}\AWIPS II AlertViz; Filename: {app}\AlertViz\alertviz.bat; Parameters: "-component thinalertviz"; Tasks: desktopicon; WorkingDir: {app}\AlertViz; Comment: "AWIPS II AlertViz"; Components: alertviz; IconFilename: {app}\AlertViz\alertviz.exe
Name: {group}\AWIPS II AlertViz; Filename: {app}\AlertViz\alertviz.bat; Parameters: "-component thinalertviz"; WorkingDir: {app}\AlertViz; Comment: "AWIPS II AlertViz"; Components: alertviz; IconFilename: {app}\AlertViz\alertviz.exe
; Uninstaller Icon - Start Menu Only. 
Name: {group}\{cm:UninstallProgram,AWIPS II CAVE}; Filename: {uninstallexe}

[Dirs]
; Change only the etc directory to allow modifications
Name: "{app}\Cave\etc"; Permissions: everyone-modify

[UninstallDelete]
Type: filesandordirs; Name: {app}\CAVE\*; Components: cave
Type: filesandordirs; Name: {app}\AlertViz\*; Components: alertviz 
; Only delete the Application directory if empty since A2RE would still be installed.
Type: dirifempty; Name: {app}

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

// Checkes the registry for the Java and Python paths and updates the bat file with the locations. 
procedure ChangeBatPaths (FileName: String);
var
    FileData: String;
    V: string;
begin
    LoadStringFromFile(FileName, FileData);
    RegQueryStringValue(HKLM64, 'Software\Raytheon\Runtime Environment\AWIPS II Java', 'JavaJreDirectory', V)
    StringChange(FileData, 'SET JavaJreDirectory=C:\Program Files\Raytheon\AWIPS II\Java\jre7', 'SET JavaJreDirectory=' + V + '');
    RegQueryStringValue(HKLM64, 'Software\Raytheon\Runtime Environment\AWIPS II Python', 'PythonInstallDirectory', V)
    StringChange(FileData, 'SET PythonInstallDirectory=C:\Program Files\Raytheon\AWIPS II\Python', 'SET PythonInstallDirectory=' + V + '');
    SaveStringToFile(FileName, FileData, False);
end;

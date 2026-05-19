; installer.iss — Inno Setup 6 script for the Worldographer Annotation Editor
;
; Prerequisites:
;   1. Run PyInstaller first to build dist\WorldographerEditor\
;      (see worldographer_editor.spec)
;   2. Install Inno Setup 6 from https://jrsoftware.org/isinfo.php
;   3. Open this file in the Inno Setup IDE and click Build → Compile
;      (or run: iscc installer.iss from the command line)
;
; Output:
;   installer_output\WorldographerEditor_Setup_1.0.0.exe
;
; The installer:
;   - Copies all files from dist\WorldographerEditor\ to Program Files
;   - Creates a Start Menu shortcut and an optional Desktop shortcut
;   - Creates an uninstaller entry in "Apps & features"
;   - Requires no Python, no PySide6, no external libraries on the target PC

#define AppName      "Worldographer Annotation Editor"
#define AppVersion   "1.0.0"
#define AppPublisher "Your Name"
#define AppExeName   "WorldographerEditor.exe"
#define AppURL       "https://github.com/yourname/worldographer-editor"
; Path to the PyInstaller output folder (relative to this .iss file)
#define DistDir      "dist\WorldographerEditor"

[Setup]
; Unique GUID — regenerate with Tools > Generate GUID if you fork the project
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\WorldographerEditor
DefaultGroupName={#AppName}
AllowNoIcons=yes
; Output settings
OutputDir=installer_output
OutputBaseFilename=WorldographerEditor_Setup_{#AppVersion}
; Compression
Compression=lzma2/max
SolidCompression=yes
; Require elevation only if installing to Program Files (recommended)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Minimum Windows version: Windows 10 (needed for PySide6 6.x)
MinVersion=10.0
; Architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Wizard appearance
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copy everything from the PyInstaller dist folder
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcut
Name: "{group}\{#AppName}";          Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
; Optional Desktop shortcut
Name: "{autodesktop}\{#AppName}";    Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; Offer to launch immediately after install
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up the recent-files cache that the app creates in its own folder
Type: files; Name: "{app}\.worldographer_recent.json"

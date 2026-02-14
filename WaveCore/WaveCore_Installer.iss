; Script de Inno Setup para WaveCore v1.0.0
; Desarrollado por Antigravity para Luis Alberto Gómez

[Setup]
AppId={{C6E253A3-84B1-4A2D-BA3C-9A8D6E1F2031}
AppName=WaveCore Audio Library
AppVersion=1.0.0
AppPublisher=Luis Alberto Gómez
DefaultDirName={autopf}\WaveCore
DefaultGroupName=WaveCore
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=WaveCore_Setup_v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
SetupIconFile=d:\WaveCore\WaveCore\src\resources\icons\WaveCore.ico
UninstallDisplayIcon={app}\WaveCore.exe

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "d:\WaveCore\WaveCore\dist\WaveCore.exe"; DestDir: "{app}"; Flags: ignoreversion
; Nota: Al usar --onefile en PyInstaller, solo necesitamos el .exe principal.

[Icons]
Name: "{group}\WaveCore"; Filename: "{app}\WaveCore.exe"
Name: "{group}\{cm:UninstallProgram,WaveCore}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\WaveCore"; Filename: "{app}\WaveCore.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WaveCore.exe"; Description: "{cm:LaunchProgram,WaveCore}"; Flags: nowait postinstall skipifsilent

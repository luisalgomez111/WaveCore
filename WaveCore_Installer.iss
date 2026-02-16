; WaveCore v2.0.0 Installer Script
; Optimized for Windows 10/11

#define AppName "WaveCore"
#define AppVersion "2.0.0"
#define AppPublisher "WaveCore Project"
#define AppURL "https://wave-core.vercel.app/"
#define AppExeName "WaveCore.exe"
#define AppId "{{A7B6C8D9-E0F1-4G2H-8I3J-K4L5M6N7O8P9}"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
; Icons
SetupIconFile=WaveCore\src\resources\icons\WaveCore.ico
UninstallDisplayIcon={app}\{#AppExeName}
; Output
OutputDir=Output
OutputBaseFilename=WaveCore_Setup_v2.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: resources are already bundled in the --onefile EXE, but keeping this as reference if needed.

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

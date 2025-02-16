[Setup]
AppName=TempoCamara
AppVersion=1.0
DefaultDirName={pf}\TempoCamara
OutputDir=.\Installer
OutputBaseFilename=Instalador_TempoCamara
Compression=lzma
SolidCompression=yes

[Files]
; Executável principal
Source: "C:\Users\Usuario\Desktop\codigo\dist\TempoCamara.exe"; DestDir: "{app}"
; Pasta de recursos
Source: "C:\Users\Usuario\Desktop\codigo\assets\*"; DestDir: "{app}\assets"; Flags: recursesubdirs
; Arquivos de dados/configuração
Source: "C:\Users\Usuario\Desktop\codigo\config.ini"; DestDir: "{app}"
Source: "C:\Users\Usuario\Desktop\codigo\config.json"; DestDir: "{app}"
Source: "C:\Users\Usuario\Desktop\codigo\database.db"; DestDir: "{app}"
Source: "C:\Users\Usuario\Desktop\codigo\private_key.pem"; DestDir: "{app}"
Source: "C:\Users\Usuario\Desktop\codigo\public_key.pem"; DestDir: "{app}"
Source: "C:\Users\Usuario\Desktop\codigo\serial.txt"; DestDir: "{app}"

[Icons]
Name: "{commonprograms}\TempoCamara"; Filename: "{app}\TempoCamara.exe"
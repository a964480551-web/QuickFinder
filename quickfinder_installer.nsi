Unicode True
!include "MUI2.nsh"

!define APP_NAME "QuickFinder"
!define APP_VERSION "2.1.0"
!define APP_EXE "QuickFinder.exe"
!define APP_ID "QuickFinder"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "release\installer-nsis\QuickFinder_Setup_${APP_VERSION}.exe"
InstallDir "$LOCALAPPDATA\Programs\${APP_NAME}"
InstallDirRegKey HKCU "Software\${APP_ID}" "InstallDir"
RequestExecutionLevel user

Icon "quickfinder.ico"
UninstallIcon "quickfinder.ico"
BrandingText "QuickFinder · Open Source"
ShowInstDetails show
ShowUninstDetails show

VIProductVersion "2.1.0.0"
VIAddVersionKey /LANG=2052 "ProductName" "QuickFinder"
VIAddVersionKey /LANG=2052 "FileDescription" "QuickFinder 安装程序"
VIAddVersionKey /LANG=2052 "FileVersion" "2.1.0"
VIAddVersionKey /LANG=2052 "ProductVersion" "2.1.0"
VIAddVersionKey /LANG=2052 "LegalCopyright" "Copyright © 2026 QuickFinder contributors"

!define MUI_ABORTWARNING
!define MUI_ICON "quickfinder.ico"
!define MUI_UNICON "quickfinder.ico"
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "启动 QuickFinder"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "SimpChinese"

Section "QuickFinder（必需）" SEC_MAIN
  SectionIn RO
  SetOutPath "$INSTDIR"
  File /r "release\dist-onedir\QuickFinder\*.*"

  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\${APP_ID}" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "DisplayName" "QuickFinder"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "DisplayIcon" "$INSTDIR\${APP_EXE}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}" "NoRepair" 1

  CreateDirectory "$SMPROGRAMS\QuickFinder"
  CreateShortcut "$SMPROGRAMS\QuickFinder\QuickFinder.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\QuickFinder\卸载 QuickFinder.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

Section /o "桌面快捷方式" SEC_DESKTOP
  CreateShortcut "$DESKTOP\QuickFinder.lnk" "$INSTDIR\${APP_EXE}"
SectionEnd

LangString DESC_SEC_MAIN ${LANG_SIMPCHINESE} "安装 QuickFinder 主程序和运行所需组件。"
LangString DESC_SEC_DESKTOP ${LANG_SIMPCHINESE} "在桌面创建 QuickFinder 快捷方式。"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_MAIN} $(DESC_SEC_MAIN)
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_DESKTOP} $(DESC_SEC_DESKTOP)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section "Uninstall"
  Delete "$DESKTOP\QuickFinder.lnk"
  Delete "$SMPROGRAMS\QuickFinder\QuickFinder.lnk"
  Delete "$SMPROGRAMS\QuickFinder\卸载 QuickFinder.lnk"
  RMDir "$SMPROGRAMS\QuickFinder"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}"
  DeleteRegKey HKCU "Software\${APP_ID}"
SectionEnd

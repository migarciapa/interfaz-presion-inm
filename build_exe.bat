:: EMPAQUETADO DE PROYECTO CON PYINSTALLER

:: Borrado de carpetas de builds anteriores
rmdir /s /q build
rmdir /s /q dist

python -m PyInstaller --noconfirm --onefile --windowed ^
    --name=INMpress ^
    --icon=app/resources/app_icon.ico ^
    --add-data "app/resources;app/resources" ^
    app/main.py
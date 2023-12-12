打包命令
pyinstaller -F --add-data="venv;venv" --add-data="templates;templates" --add-data="videoFrameExtraction.py;." --add-data="reloadImage.py;." --add-data="imageHash.py;." videoFrameExtractionFile.py
打包命令
pyinstaller -F --add-data="venv;venv" --add-data="templates;templates" --add-data="videoFrameExtraction.py;." --add-data="reloadImage.py;." --add-data="imageHash.py;." videoFrameExtractionFile.py
（1）--add-data="venv;venv"
    需要打包进exe文件的文件夹
（2）--add-data="videoFrameExtraction.py;."
    需要打包进exe文件的py依赖文件
（3）最后的 videoFrameExtractionFile.py
    需要打包进exe文件的主main入口py文件

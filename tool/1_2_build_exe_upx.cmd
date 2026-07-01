PyInstaller ^
-w -F ^
--icon="ZenFileSorter.ico" ^
--clean --noconfirm ^
--optimize=2 ^
--upx-dir="D:\soft\upx-5.2.0-win64" ^
--disable-windowed-traceback ^
--version-file="version_info.txt" ^
--exclude-module=tkinter.test ^
--exclude-module=unittest ^
--exclude-module=test ^
--exclude-module=email ^
--exclude-module=html ^
--exclude-module=xmlrpc ^
--exclude-module=multiprocessing ^
--exclude-module=asyncio ^
--exclude-module=sqlite3 ^
--exclude-module=ssl ^
--exclude-module=ctypes.test ^
--exclude-module=pydoc ^
--exclude-module=distutils ^
--name="媒体文件分类管理工具v2.2" ^
"..\zen_file_sorter.pyw"
pause
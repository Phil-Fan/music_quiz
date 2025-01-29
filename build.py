import os
import shutil
import PyInstaller.__main__

# 确保build目录存在
if not os.path.exists('build'):
    os.makedirs('build')

# 运行PyInstaller
PyInstaller.__main__.run([
    'build_config.spec',
    '--distpath=build',
    '--workpath=build/temp',
    '--clean'
])

# 复制必要的文件夹到构建目录
dist_dir = os.path.join('build', 'MusicQuiz')
if not os.path.exists(dist_dir):
    os.makedirs(dist_dir)

# 复制songs文件夹（如果存在）
if os.path.exists('songs'):
    shutil.copytree('songs', os.path.join(dist_dir, 'songs'), dirs_exist_ok=True)

# 创建result文件夹
result_dir = os.path.join(dist_dir, 'result')
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

print("构建完成！程序已生成到 build/MusicQuiz 目录下") 
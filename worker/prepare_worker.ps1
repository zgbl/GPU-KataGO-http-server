# prepare_worker.ps1
# 在 Windows 10 机器运行，用于同步最新的后端代码到 worker 文件夹

$BackendDir = "d:\Codes\blackricegobackend2"
$WorkerDir = "d:\Codes\GPU-KataGO-http-server-master\GPU-KataGO-http-server-master\worker"

Write-Host "Syncing files to $WorkerDir..."

# 创建目录
New-Item -ItemType Directory -Force -Path "$WorkerDir\lib"
New-Item -ItemType Directory -Force -Path "$WorkerDir\models"
New-Item -ItemType Directory -Force -Path "$WorkerDir\scripts"

# 复制文件
Copy-Item -Path "$BackendDir\lib\*" -Destination "$WorkerDir\lib\" -Recurse -Force
Copy-Item -Path "$BackendDir\models\*" -Destination "$WorkerDir\models\" -Recurse -Force
Copy-Item -Path "$BackendDir\scripts\*" -Destination "$WorkerDir\scripts\" -Recurse -Force
Copy-Item -Path "$BackendDir\package.json" -Destination "$WorkerDir\" -Force

Write-Host "Done! You can now run 'docker-compose build' in the worker folder."

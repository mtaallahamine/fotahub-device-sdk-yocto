@echo off
setlocal

docker volume create yocto-factory-data
docker run ^
  --name yocto-factory ^
  --interactive --tty --rm ^
  --volume yocto-factory-data:/build/yocto ^
  --volume %~dp0:/project ^
  fotahub/yocto-factory:2021.1.0 ^
  %*
  
endlocal

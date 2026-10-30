# B1 + IMX219 + mediad 0.17.1 摄像头启动修复

仅适用于已验证的 B1 / Linux `6.1.84-10-rk2410-nocsf`、media0 IMX219 拓扑及 mediad 固定 1080p 传感器模式。不要直接用于其他相机或任意 Armbian 镜像。

两个故障需要一起处理：ISP 与传感器尺寸不一致会低帧率、花屏；3A 在旧尺寸下初始化后，即使尺寸一致、达到 30 fps，画面仍可能有彩色条纹。必须先配置整个 1080p 媒体链路，再初始化 rkaiq，最后启动 mediad。

## 安装（在主板上执行）

先备份同名已有文件。操作会短暂停止视频服务。首次安装不需要修改系统原有 service 文件，也不需要修改 overlay。

```sh
sudo systemctl stop mediad rkaiq_3A
sudo install -m 755 microduck-camera-isp-1080 /usr/local/sbin/
sudo mkdir -p /etc/systemd/system/rkaiq_3A.service.d /etc/systemd/system/mediad.service.d
sudo install -m 644 20-b1-camera-mode.conf /etc/systemd/system/rkaiq_3A.service.d/
sudo install -m 644 20-b1-isp-size.conf /etc/systemd/system/mediad.service.d/
sudo systemctl daemon-reload
sudo systemctl start mediad
```

`rkaiq_3A` 的 ExecStartPre 在图像处理初始化前设置传感器、DPHY、CSI、ISP 的格式和裁剪；mediad 显式依赖 3A。准备脚本最多等待约 10 秒让媒体图出现，失败会阻止服务继续启动并留下日志。

## 检查

```sh
systemctl --no-pager status rkaiq_3A mediad
cat /run/mediad/camera.json
robotctl frame --output /tmp/check.uyvy
```

需要下载并目视检查实际图像，不能只凭 fps 判定画质。当前 raw frame 元数据为 1280×720 UYVY，显示旋转为 90°，可用 FFmpeg 转换：

```sh
ffmpeg -f rawvideo -pixel_format uyvy422 -video_size 1280x720 \
  -i check.uyvy -frames:v 1 -vf transpose=1 check.jpg
```

本修复不解决另行发现的 WebRTC 编码插件兼容性问题。抓图成功不等同网页视频验收通过。

## 撤销

停止 mediad 和 rkaiq_3A，将本次安装的两个 drop-in 文件及准备脚本移出对应安装目录（恢复之前备份的同名文件，如有），执行 `sudo systemctl daemon-reload` 后重启主板。无需改动机器人运动配置。

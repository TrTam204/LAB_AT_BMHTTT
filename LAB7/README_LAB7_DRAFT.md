# LAB 7 – pfSense Web Protection

## Mục tiêu
Dùng pfSense ngăn client bypass proxy; Ubuntu WEB-PROXY chạy E2Guardian :8080 → Squid :3128; ClamAV quét tải HTTP; DMZ-WEB phục vụ các hostname `*.lab7.test`.

## Môi trường dự kiến
- pfSense LAN `10.6.0.1`, DMZ `172.16.6.1`
- DC01/DNS `10.6.0.10`; Client-A `10.6.0.21`; Client-B `10.6.0.22`
- WEB-PROXY Ubuntu Server 24.04 `10.6.0.30/24`, gateway `10.6.0.1`, DNS `10.6.0.10`
- DMZ-WEB `172.16.6.10`

## Trình tự cấu hình
1. Kiểm tra VM LAB 6, mạng, DNS; tạo snapshot `LAB7_START`.
2. Tạo Ubuntu WEB-PROXY (2 GB RAM, 2 vCPU, 20 GB disk), gắn Internal Network `lab6-lan`.
3. Dùng script `03_WEB_PROXY/install_lab7_proxy.sh` trong tài nguyên giảng viên; kiểm tra nội dung script trước khi chạy. Áp dụng các file hướng dẫn thay đổi cấu hình E2Guardian/Squid, không chép đè mù quáng.
4. Kiểm tra `sudo systemctl status squid e2guardian clamav-daemon` và `sudo ss -lntp | grep -E ':(8080|3128)'`. Squid chỉ nghe localhost.
5. Tại DMZ-WEB, kiểm tra rồi chạy `01_DMZ_WEB/setup_lab7_dmz_web.sh`; trên DC01 dùng `02_DNS/Add-LAB7-DNS.ps1` hoặc tạo thủ công bản ghi A trỏ `172.16.6.10`.
6. Trên client kiểm tra `nslookup normal.lab7.test 10.6.0.10`; cấu hình browser HTTP proxy `10.6.0.30:8080`.
7. Trên pfSense tạo alias `LAB7_CLIENTS`, `LAB7_PROXY`, `WEB_PORTS`, `MAIL_PORTS`; đặt pass DNS và proxy trước block direct web, cho proxy đi web/DMZ, kiểm tra rule mặc định và state cũ.
8. Áp dụng lists: hard block, warning/bypass 300 giây, allow; kiểm tra `normal`, `china`, `jobs`, `weapons`, `education`, `streaming`, `blockedgame`.
9. Tạo time-window 60 phút cho entertainment/games (không phải quota tích lũy); kiểm thử trong/ngoài khung.
10. Kiểm tra EICAR qua HTTP, ClamAV và log. Chỉ ghi đạt size limit nếu thử file 100 MB và 110 MB cho kết quả đúng. HTTPS inspection là phần mở rộng chỉ trong máy LAB.

## Kiểm tra và log
```bash
sudo systemctl status squid e2guardian clamav-daemon
sudo tail -n 50 /var/log/e2guardian/access.log
sudo tail -n 50 /var/log/squid/access.log
sudo journalctl -u clamav-daemon -n 50 --no-pager
```
Firewall log: pfSense → Status → System Logs → Firewall.

## Lỗi đã gặp và cách xử lý
*Chưa thực hiện lab — bổ sung đúng lỗi thực tế sau khi chạy.*

| Lỗi thực tế | Nguyên nhân xác nhận | Cách xử lý / kiểm tra lại |
|---|---|---|
| [Chưa có] | [Chưa có] | [Chưa có] |

## Ghi chú
README này là bản chuẩn bị, không xác nhận các chức năng đã chạy thành công. Không nộp private key CA.

## Nguyễn Hồ Trường Tam_11CNPM2_MSSV 1150080156
## Lap4: 
# Báo cáo LAB 4: Khảo sát và Đánh giá Bề mặt mạng bằng Nmap

- **Họ tên:** Nguyễn Hồ Trường Tam
- **MSSV:** [Điền MSSV của bạn]
- **Tên lab:** LAB 4 - Khảo sát và Đánh giá bề mặt mạng bằng Nmap
- **Phiên bản môi trường:** VirtualBox mới nhất, Nmap, Kali Linux 2026.2, Windows Host 10/11.
- **Cách dựng môi trường:** Sử dụng mạng VirtualBox Host-Only (192.168.56.0/24). Máy quét Kali Linux (192.168.56.10) và máy mục tiêu Metasploitable 2 (192.168.56.101).
- **Các tình huống đã thực hiện:**
  - Host Discovery toàn dải mạng /24 để nhận diện máy đang hoạt động.
  - Quét trạng thái cổng với các cờ -sT, -sS, -sF, -sX, -sN, -sA.
  - Định danh dịch vụ (-sV) và xác định hệ điều hành (-O).
  - Khởi chạy script NSE dò tìm lỗ hổng SMB (smb-os-discovery, smb-vuln-ms17-010).
- **Kết quả:** PASS (Môi trường quét hoạt động ổn định, xuất đầy đủ log và minh chứng báo cáo kỹ thuật đúng hạn).
- **Lỗi gặp phải & Cách khắc phục:** 
  - *Lỗi:* Trong quá trình lấy file máy ảo về bị treo tiến trình giải nén ở quyền admin thư mục Windows.
  - *Khắc phục:* Đổi đường dẫn giải nén ra thư mục ngoài và sử dụng công cụ 7-Zip/WinRAR thay cho trình nén mặc định của Windows. Cấu hình lại đúng Adapter 1 thành Host-Only.
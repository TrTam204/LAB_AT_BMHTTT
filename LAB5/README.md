## Nguyễn Hồ Trường Tam_11CNPM2_MSSV 1150080156
# BÁO CÁO LAB: CẤU HÌNH TƯỜNG LỬA PFSENSE
# link video: https://youtu.be/VNAbaU2CN_E?si=-yRjbO7pXUpJqzC_
- **Tên lab**: Thiết lập mô hình Firewall pfSense (Lab 5)
- **Phiên bản môi trường**: 
  - Ảo hóa: Oracle VirtualBox (hoặc VMware)
  - pfSense: CE 2.7.2-RELEASE (amd64)
  - Hệ điều hành máy ảo: Windows Server 2019/2022, Ubuntu Server 22.04 LTS

## Cách dựng môi trường
1. Import/Tạo máy ảo pfSense cấu hình 3 card mạng (WAN: Bridged, LAN: Host-only 10.0.0.0/8, DMZ: Internal Network 172.16.0.0/16).
2. Tạo máy Domain Controller (10.0.0.2) đóng vai trò máy tính người dùng trong LAN.
3. Tạo máy DMZ-Web (172.16.0.2) cho vùng máy chủ và LAN-Test (10.0.0.3) cho các bài test cô lập host.
4. Thực hiện tắt các rule mặc định (Default allow LAN to any) để thiết lập state quản lý thủ công.

## Các tình huống đã thực hiện & Kết quả
- **Tình huống 1 (Chặn ICMP, mở Web/DNS)**: Đã cấu hình và test Ping thất bại, truy cập Web thành công. -> **Kết quả: PASS**
- **Tình huống 2 (Chỉ cho DC ra Internet, host khác bị chặn)**: DC kết nối mạng thành công, máy Ubuntu LAN-Test không ra mạng được. -> **Kết quả: PASS**
- **Tình huống 3 (Cô lập DMZ khỏi LAN)**: Máy chủ DMZ ra được Internet nhưng không thể Ping ngược vào máy DC trong LAN. -> **Kết quả: PASS**

## Lỗi gặp phải và cách khắc phục
- **Lỗi**: Khi vừa tạo rule chặn hoặc đổi rule, cấu hình cũ dường như vẫn hoạt động và không có tác dụng ngay.
- **Cách khắc phục**: Firewall pfSense là stateful firewall. Cần phải Reset State Table (`Diagnostics > States > Reset States`) sau mỗi lần đổi rule và ngắt kết nối ping cũ (`Ctrl + C`) để các gói tin mới đi qua rule mới kiểm tra.
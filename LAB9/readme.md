# README – BÁO CÁO THỰC HÀNH LAB 9 (GÓI LAB 10): REMOTE DNS CACHE POISONING

## 1. Thông tin sinh viên và bài thực hành

* **Họ và tên:** Nguyễn Hồ Trường Tâm
* **Mã số sinh viên (MSSV):** 1150080156
* **Lớp học phần:** 11CNPM2
* **Môn học:** Thực hành An toàn và Bảo mật Hệ thống Thông tin
* **Tên bài thực hành:** Lab 9 (Gói tài nguyên LAB 10) – Remote DNS Cache Poisoning / Kaminsky trong môi trường pfSense cô lập

## 2. Môi trường triển khai

Hệ thống được triển khai trong môi trường mạng ảo hóa cô lập trên [Oracle VirtualBox](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/networkingdetails.html) kết hợp tường lửa [Netgate pfSense](https://docs.netgate.com/pfsense/en/latest/interfaces/configure.html) và dịch vụ phân giải tên miền [ISC BIND 9.18](https://bind9.readthedocs.io/en/v9.18.50/), sử dụng tên miền thử nghiệm nội bộ `example.lab10.test` theo chuẩn [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606).

| Máy ảo (VM) | Vai trò trong bài Lab | Mạng nội bộ (Internal Network) | Địa chỉ IP / Gateway | Trạng thái vận hành 
| :--- | :--- | :--- | :--- | :--- |
| **`pfSense_Tam`** | Firewall / Router phân tách mạng | `dns-lab` (`em4`) & `attack-net` (`em5`) | `10.9.0.1/24` & `10.10.0.1/24` | Bật (`1024 MB RAM`) |
| **`web-proxy-tam`** | `DNS-SERVER` (BIND9 & Lab Resolver) | `dns-lab` | `10.9.0.10/24` (GW `10.9.0.1`) | Bật (`1024 MB RAM`) |
| **`kali-tam`** | `ATTACKER` (Evil DNS & Fake Web) | `attack-net` (`Promiscuous: Deny`) | `10.10.0.200/24` (GW `10.10.0.1`) | Bật (`1280 MB RAM`) |
| **`APP-TEST`** | `AUTH-DNS` & Race Relay | `lab6-dmz` | `172.16.6.20/24` (UDP `53/5300`) | Tắt (Phân tích qua mã nguồn) |
| **`VICTIM`** | Máy trạm DNS Client | `dns-lab` | `10.9.0.100/24` (DNS `10.9.0.10`) | Tắt (Kiểm thử trực tiếp trên Resolver) |

## 3. Các bước cơ bản dựng và thực hiện bài Lab

1. **Phân đoạn mạng và cô lập Attacker trên pfSense:**
   * Tạo Snapshot dự phòng `LAB10_START_FROM_LAB9` trên VirtualBox và thêm card mạng nội bộ `attack-net` cho `pfSense_Tam`.
   * Khởi tạo interface `ATTACKNET` (`10.10.0.1/24`, không gán Upstream Gateway) và thiết lập bộ Firewall Rules cô lập trên hai tab `ATTACKNET` và `DNSLAB` (chỉ mở cổng DNS `53` và cổng mô phỏng `5300`, chặn toàn bộ truy cập sang `LAN 10.6.0.0/24`, `MGMT 192.168.56.0/24` và `WAN`).
2. **Chuyển máy Attacker sang mạng riêng và kiểm chứng không thể Sniff:**
   * Chuyển card mạng của `kali-tam` khỏi `dns-lab` sang `attack-net`, khóa `Promiscuous Mode = Deny` và đặt IP tĩnh `10.10.0.200/24` (Gateway `10.10.0.1`).
   * Dùng `tcpdump` trên `kali-tam` để xác nhận máy tấn công bắt được `0 packets` khi `DNS-SERVER` truy vấn, chứng minh tính chất tấn công từ xa (Remote / Off-path).
3. **Cấu hình Baseline BIND9 và chạy thành phần mô phỏng tấn công:**
   * Trên `web-proxy-tam` (`10.9.0.10/24`), nạp cấu hình `named.conf.options.baseline` và `named.conf.local.baseline` (chỉ cho phép đệ quy trong dải `10.9.0.0/24`, bật `dnssec-validation auto` kèm `validate-except` cho `example.lab10.test`).
   * Tạm dừng BIND9, khởi chạy `vuln_resolver_lab10.py` lắng nghe tại `10.9.0.10:53` với cổng nguồn cố định `UDP 33333`; đồng thời bật `evil_dns_lab10.py` (`10.10.0.200:53`) và trang web mô phỏng `fake_index.html` (`10.10.0.200:80`) trên `kali-tam`.
4. **Khôi phục BIND9 và áp dụng Hardening:**
   * Dừng resolver mô phỏng, khởi động lại dịch vụ BIND 9.18 (`named`) trên `10.9.0.10`.
   * Kiểm chứng `kali-tam` (`10.10.0.200`) bị từ chối truy vấn đệ quy (`status: REFUSED` nhờ `allow-recursion`) và quan sát BIND 9.18 ngẫu nhiên hóa cổng nguồn UDP (`Source-Port Randomization`) thay vì cố định ở cổng `33333`.

## 4. Khó khăn và hạn chế gặp phải

* **Giới hạn dung lượng bộ nhớ vật lý (8 GB RAM):** Kịch bản đầy đủ của bài Lab yêu cầu vận hành đồng thời 5 máy ảo (`pfSense`, `DNS-SERVER`, `VICTIM`, `ATTACKER Kali`, và `AUTH-DNS/APP-TEST`). Trên máy tính cá nhân chỉ có 8 GB RAM (hệ điều hành Windows đã chiếm khoảng 3.5 GB RAM), việc bật cùng lúc 5 máy ảo gây tràn bộ nhớ và treo hệ thống ảo hóa.
* **Hướng khắc phục và phạm vi hoàn thành (~55% khối lượng):** Tối ưu hóa mô hình bằng cách chỉ bật đồng thời 3 máy ảo cốt lõi (`pfSense_Tam`, `web-proxy-tam`, `kali-tam` với tổng RAM ~3.2 GB). Toàn bộ phần phân đoạn mạng `ATTACKNET`, chứng minh không thể sniff `DNS-LAB`, dựng Resolver mô phỏng (`UDP 33333`), dựng Evil DNS/Fake Web và kiểm chứng Hardening trên BIND9 đều được thực hiện đầy đủ; riêng phần chạy đua gói tin trực tiếp qua `auth_dns_relay_lab10.py` trên máy thứ 4 và kiểm thử trình duyệt trên máy thứ 5 được phân tích thông qua mã nguồn và đối chiếu luồng gói tin trong báo cáo.
* **Xung đột cấu hình mạng khi chuyển vai máy ảo:** Khi chuyển `kali-tam` từ mạng `dns-lab` sang `attack-net`, dịch vụ `NetworkManager` có thể tự động xóa IP tĩnh vừa gán; đã xử lý triệt để bằng cách tắt quản lý tự động trên card `eth0` (`nmcli device set eth0 managed no`) trước khi đặt IP `10.10.0.200/24`.

# LAB 8 – Local DNS Attack: DNS Spoofing và Cache Poisoning trên pfSense

**Môn học:** An toàn và Bảo mật Hệ thống Thông tin

**Sinh viên thực hiện:** Nguyễn Hồ Trường Tâm

**MSSV:** 1150080156

**Lớp:** 11CNPM2

## 1. Tổng quan và Mục tiêu bài thực hành

Bài thực hành gốc của **SEED Labs (Local DNS Attack)** xây dựng 3 máy trong cùng mạng LAN gồm *DNS Server*, *User (Victim)* và *Attacker* nhằm quan sát kỹ thuật chuyển hướng tên miền cục bộ (DNS Pharming), giả mạo phản hồi DNS trực tiếp (Direct DNS Spoofing) và đầu độc bộ nhớ đệm DNS (DNS Cache Poisoning).

Trong phiên bản cập nhật năm 2026 của học phần (**tài liệu học phần LAB 8 / gói tài nguyên LAB 9**), bài thực hành giữ nguyên 3 nhiệm vụ cốt lõi của SEED Labs nhưng nâng cấp toàn bộ hệ thống lên **Ubuntu 24.04 LTS** và **Kali Linux**, đồng thời đặt chúng trong một phân đoạn mạng ảo riêng biệt (`DNS-LAB 10.9.0.0/24`) nằm phía sau tường lửa **pfSense**:

1. **Dựng máy chủ DNS-SERVER (`10.9.0.10`) chạy BIND9** làm máy chủ phân giải đệ quy/cache (Recursive/Caching Resolver) cho mạng `10.9.0.0/24` và Authoritative cho miền nội bộ `lab9.test`.

2. **Cấu hình Zone thuận (`lab9.test`), Zone nghịch (`9.10.in-addr.arpa`), Forward Zone (`external.lab9.test`)** và kiểm thử bằng `dig`, `nslookup`, `resolvectl`.

3. **Bắt và phân tích gói tin DNS bằng Wireshark/tcpdump** để hiểu cơ chế khớp các trường `Transaction ID (16-bit)`, `UDP Source/Destination Port` và `Query Name`.

4. **Thực hiện 3 kịch bản tấn công cốt lõi:**

   * **Task 1:** Chuyển hướng tên miền bằng tệp `/etc/hosts` cục bộ (*HOSTS-file Redirection*).

   * **Task 2:** Giả mạo phản hồi DNS trực tiếp tới máy nạn nhân (*Direct DNS Spoofing — `--mode victim`*).

   * **Task 3:** Đầu độc bộ nhớ đệm máy chủ BIND9 (*DNS Cache Poisoning — `--mode resolver`*).

5. **Khôi phục môi trường và thực nghiệm phòng thủ (Hardening):** Xóa cache độc hại, khôi phục cấu hình gốc, bật lại **DNS COOKIE**, chuyển **Promiscuous Mode** về `Deny`, và phân tích các giải pháp bảo vệ hạ tầng DNS (Network Segmentation, DNS Egress Control, DNSSEC).

## 2. Môi trường Phần mềm, Công cụ Hỗ trợ và Kiến trúc Mạng

### 2.1. Phần mềm ảo hóa và Hệ điều hành sử dụng

| Phần mềm / Công cụ | Phiên bản / Môi trường | Vai trò và chức năng hỗ trợ trong bài Lab | 
| ----- | ----- | ----- | 
| **Oracle VirtualBox** | VirtualBox 7.x | Nền tảng ảo hóa vận hành các máy ảo, cung cấp switch ảo `Internal Network (dns-lab)` và chế độ `Promiscuous Mode = Allow VMs` để mô phỏng tấn công sniffing/spoofing cùng LAN. | 
| **pfSense Firewall** | pfSense CE 2.7.x | Tường lửa trung tâm kế thừa từ LAB trước; bổ sung interface `OPT2 (DNSLAB - 10.9.0.1/24)` để định tuyến có kiểm soát sang `DMZ (172.16.6.0/24)` và cô lập hoàn toàn lưu lượng tấn công khỏi `LAN-DOMAIN (10.6.0.0/24)`, `MGMT (192.168.56.0/24)` và `WAN`. | 
| **Ubuntu Server 24.04 LTS** | Máy `DNS-SERVER` (`10.9.0.10`) | Chạy dịch vụ **ISC BIND 9 (`named`)** đóng vai trò DNS Authoritative cho `lab9.test` và Recursive/Caching Resolver cho mạng `10.9.0.0/24`. | 
| **Ubuntu 24.04 Desktop/Server** | Máy `VICTIM` (`10.9.0.100`) | Máy trạm người dùng sử dụng **Netplan** và **systemd-resolved (`resolvectl`)**, cấu hình DNS duy nhất về `10.9.0.10`. | 
| **Kali Linux 2026.x** | Máy `ATTACKER` (`10.9.0.200`) | Máy tấn công trang bị thư viện **Python3 Scapy** (chạy `dns_spoof_lab9.py`), **Wireshark / tcpdump** (bắt gói tin cổng UDP 53) và **Python HTTP Server** (phục vụ trang web giả mạo `fake_index.html` ở cổng 80). | 
| **Python 3 Authoritative Simulator** | Máy `APP-TEST` (`172.16.6.20`) | Chạy script `auth_dns_delayed.py` trên vùng DMZ, đóng vai trò máy chủ Authoritative DNS cho `external.lab9.test` với độ trễ phản hồi chủ đích `1.5 giây` để tái현 rõ cuộc đua gói tin (*DNS Race Condition*). | 
| **Nginx / Python HTTP Server** | Máy `DMZ-WEB` (`172.16.6.10`) | Máy chủ Web hợp lệ trong vùng DMZ, là đích thực sự của tên miền `www.lab9.test` và `www.external.lab9.test`. | 

### 2.2. Bảng quy hoạch địa chỉ IP và Card mạng VirtualBox

| Máy ảo (VM) | Card mạng khi thực hành | Địa chỉ IP / Subnet | Gateway | DNS Server | Ghi chú cấu hình đặc biệt | 
| ----- | ----- | ----- | ----- | ----- | ----- | 
| **pfSense** | Adapter 1: WAN (`NAT Network`)  Adapter 2: MGMT (`Host-Only`)  Adapter 3: LAN (`lab6-lan`)  Adapter 4: DMZ (`lab6-dmz`)  **Adapter 5: OPT2 (`dns-lab`)** | WAN: `192.168.250.x/24`  MGMT: `192.168.56.254/24`  LAN: `10.6.0.1/24`  DMZ: `172.16.6.1/24`  **DNSLAB: `10.9.0.1/24`** | WAN GW | \- | Không đặt Upstream Gateway trên interface `DNSLAB`; không bật DHCP trên `DNSLAB`. | 
| **DNS-SERVER** | Internal Network: `dns-lab` | `10.9.0.10/24` | `10.9.0.1` | `127.0.0.1` | Dùng thêm 1 card NAT tạm thời lúc cài `bind9 dnsutils`, sau đó **tắt card NAT**. | 
| **VICTIM** | Internal Network: `dns-lab` | `10.9.0.100/24` | `10.9.0.1` | `10.9.0.10` | Quản lý IP và DNS bằng `/etc/netplan/01-victim-dnslab.yaml`. | 
| **ATTACKER (Kali)** | Internal Network: `dns-lab` | `10.9.0.200/24` | `10.9.0.1` | `10.9.0.10` | **Bắt buộc đặt `Promiscuous Mode = Allow VMs`** trong lúc chạy Task 2 & Task 3. | 
| **APP-TEST / AUTH-DNS** | Internal Network: `lab6-dmz` | `172.16.6.20/24` | `172.16.6.1` | \- | Chạy `sudo python3 auth_dns_delayed.py --bind 172.16.6.20 --delay 1.5`. | 
| **DMZ-WEB** | Internal Network: `lab6-dmz` | `172.16.6.10/24` | `172.16.6.1` | \- | Chạy Web Server hợp lệ ở cổng TCP `80`. | 

### 2.3. Tối ưu hóa RAM khi chạy nhiều máy ảo trên máy thật (8 GB – 16 GB RAM)

* Để tránh tràn RAM hoặc giật lag khi bật đồng thời nhiều máy ảo:

  * Giữ RAM của **pfSense** ở mức `1024 MB – 1536 MB`.

  * Dùng **Ubuntu Server 24.04 (không giao diện GUI)** cho `DNS-SERVER` (`1024 MB – 1536 MB` RAM) và có thể dùng bản Server hoặc giao diện nhẹ cho `VICTIM` (`1536 MB – 2048 MB` RAM).

  * Hai địa chỉ `172.16.6.10` (DMZ-WEB) và `172.16.6.20` (APP-TEST/AUTH-DNS) trong vùng DMZ có thể được gán chung trên **cùng 1 máy ảo DMZ Linux** (bằng lệnh `sudo ip addr add 172.16.6.10/24 dev eth0` và `sudo ip addr add 172.16.6.20/24 dev eth0`), vừa chạy HTTP Server ở `172.16.6.10:80` vừa chạy `auth_dns_delayed.py` ở `172.16.6.20:53`, giúp tiết kiệm 1 máy ảo riêng biệt.

  * Không cần bật các máy của mạng cũ (`DC01`, `Win10 Client`, `WEB-PROXY` của Lab 6/7) vì nhánh `10.6.0.0/24` không tham gia vào bài tấn công này.

## 3. Các Bước Thực Hiện Chi Tiết Từng Giai Đoạn (Step-by-Step Guide)

### Bước 1: Kiểm tra toàn vẹn tài nguyên và tạo Snapshot dự phòng

1. Kiểm tra mã băm SHA256 của bộ tài nguyên giảng viên cung cấp (`LAB9_Resources`):

   ```
   cd LAB9_Resources
   sha256sum -c SHA256SUMS.txt
   
   ```

2. Tắt máy ảo `pfSense` và `Kali Linux`, vào **VirtualBox -> Snapshots -> Take** để tạo snapshot tên `LAB9_START_FROM_LAB8`.

### Bước 2: Cấu hình Interface `DNSLAB` và Firewall Rules trên pfSense

1. **Gắn thêm Adapter 5 cho pfSense:**

   * Mở **VirtualBox -> pfSense -> Settings -> Network -> Adapter 5**.

   * Tích chọn **Enable Network Adapter**.

   * **Attached to:** `Internal Network` | **Name:** `dns-lab` | Tích chọn **Cable Connected**.

2. **Gán Interface `DNSLAB` trên WebGUI pfSense (`https://192.168.56.254`):**

   * Vào **Interfaces -> Assignments**, tại dòng *Available network ports* chọn card mạng vừa thêm (ví dụ `em4`) và nhấn **+ Add**.

   * Nhấn vào tên interface mới (`OPT2`), tích **Enable interface**, đổi **Description** thành `DNSLAB`.

   * **IPv4 Configuration Type:** `Static IPv4`.

   * **IPv4 Address:** `10.9.0.1` / `24`.

   * **IPv4 Upstream Gateway:** Để mặc định `None` (*tuyệt đối không chọn gateway*).

   * Nhấn **Save -> Apply Changes**.

3. **Tạo 5 Firewall Rules cô lập trên tab `Firewall -> Rules -> DNSLAB`:** Tạo lần lượt 5 rules từ trên xuống dưới theo đúng bảng ma trận:

   * **Rule 1 (Pass):** Interface `DNSLAB` | Protocol `TCP/UDP` | Source `Single host or alias: 10.9.0.10` | Destination `Single host or alias: 172.16.6.20` | Destination Port `53 (DNS)` | Description: `Allow DNS-SERVER to AUTH-DNS`.

   * **Rule 2 (Pass):** Interface `DNSLAB` | Protocol `TCP` | Source `DNSLAB subnets (10.9.0.0/24)` | Destination `Single host or alias: 172.16.6.10` | Destination Port `80 (HTTP)` | Description: `Allow DNSLAB to Legitimate DMZ-WEB`.

   * **Rule 3 (Block + Log):** Interface `DNSLAB` | Protocol `Any` | Source `DNSLAB subnets` | Destination `Network: 10.6.0.0/24` (hoặc `LAN subnets`) | Tích chọn **Log packets** | Description: `Protect LAB8 LAN-DOMAIN`.

   * **Rule 4 (Block + Log):** Interface `DNSLAB` | Protocol `Any` | Source `DNSLAB subnets` | Destination `Network: 192.168.56.0/24` (hoặc `MGMT subnets`) | Tích chọn **Log packets** | Description: `Protect MGMT`.

   * **Rule 5 (Block + Log):** Interface `DNSLAB` | Protocol `Any` | Source `DNSLAB subnets` | Destination `Any` | Tích chọn **Log packets** | Description: `Default isolation for attack phase`.

   * Nhấn **Save -> Apply Changes**, sau đó vào **Diagnostics -> States -> Reset States** để xóa các phiên kết nối cũ.

### Bước 3: Dựng và cấu hình `DNS-SERVER` BIND9 (`10.9.0.10`)

1. **Cài đặt gói phần mềm (khi còn bật card NAT tạm thời):**

   ```
   sudo apt update
   sudo apt install -y bind9 dnsutils
   
   ```

   Sau khi cài xong, tắt card NAT của `DNS-SERVER`, chỉ giữ lại card `Internal Network: dns-lab` và đặt IP tĩnh `10.9.0.10/24`, gateway `10.9.0.1`.

2. **Sao lưu và cấu hình `/etc/bind/named.conf.options`:**

   ```
   sudo cp /etc/bind/named.conf.options /etc/bind/named.conf.options.bak
   sudo cp /etc/bind/named.conf.local /etc/bind/named.conf.local.bak
   
   ```

   Ghi nội dung chuẩn vào `/etc/bind/named.conf.options`:

   ```
   options {
       directory "/var/cache/bind";
       listen-on { 127.0.0.1; 10.9.0.10; };
       listen-on-v6 { none; };
       recursion yes;
       allow-query { 127.0.0.1; 10.9.0.0/24; };
       allow-recursion { 127.0.0.1; 10.9.0.0/24; };
       dnssec-validation auto;
       minimal-responses yes;
   };
   
   // LAB ONLY: Tắt DNS COOKIE riêng với AUTH-DNS 172.16.6.20 để tái lập bài spoofing on-path
   server 172.16.6.20 {
       send-cookie no;
   };
   
   ```

3. **Cấu hình `/etc/bind/named.conf.local`:**

   ```
   zone "lab9.test" {
       type master;
       file "/etc/bind/db.lab9.test";
   };
   
   zone "9.10.in-addr.arpa" {
       type master;
       file "/etc/bind/db.10.9.0";
   };
   
   zone "external.lab9.test" {
       type forward;
       forward only;
       forwarders { 172.16.6.20; };
   };
   
   ```

4. **Tạo file Zone thuận `/etc/bind/db.lab9.test`:**

   ```
   $TTL 300
   @   IN SOA ns.lab9.test. admin.lab9.test. (
           2026101101 ; serial
           300        ; refresh
           120        ; retry
           3600       ; expire
           60 )       ; negative cache TTL
   @       IN NS  ns.lab9.test.
   ns      IN A   10.9.0.10
   www     IN A   172.16.6.10
   portal  IN A   172.16.6.10
   
   ```

5. **Tạo file Zone nghịch `/etc/bind/db.10.9.0`:**

   ```
   $TTL 300
   @   IN SOA ns.lab9.test. admin.lab9.test. (
           2026101101 300 120 3600 60 )
   @       IN NS  ns.lab9.test.
   10      IN PTR ns.lab9.test.
   100     IN PTR victim.lab9.test.
   200     IN PTR attacker.lab9.test.
   
   ```

6. **Kiểm tra cú pháp, khởi động lại BIND9 và kiểm thử Local Zone:**

   ```
   sudo named-checkconf
   sudo named-checkzone lab9.test /etc/bind/db.lab9.test
   sudo named-checkzone 9.10.in-addr.arpa /etc/bind/db.10.9.0
   sudo systemctl restart bind9
   sudo ss -lunpt | grep :53
   dig @10.9.0.10 www.lab9.test A +short
   dig @10.9.0.10 -x 10.9.0.10 +short
   
   ```

### Bước 4: Cấu hình máy `VICTIM` (`10.9.0.100`) và `ATTACKER` Kali (`10.9.0.200`)

1. **Trên máy `VICTIM` (`10.9.0.100`):**

   * Kiểm tra tên card mạng bằng `ip -br link` (ví dụ `enp0s3` hoặc `ens33`).

   * Tạo file `/etc/netplan/01-victim-dnslab.yaml`:

     ```
     network:
       version: 2
       ethernets:
         enp0s3:
           dhcp4: no
           addresses: [10.9.0.100/24]
           routes:
             - to: default
               via: 10.9.0.1
           nameservers:
             addresses: [10.9.0.10]
     
     ```

   * Phân quyền chuẩn và áp dụng cấu hình:

     ```
     sudo chmod 600 /etc/netplan/01-victim-dnslab.yaml
     sudo netplan apply
     ip -br addr
     ip route
     resolvectl status
     resolvectl query www.lab9.test
     
     ```

2. **Trên máy `ATTACKER` Kali Linux (`10.9.0.200`):**

   * Khi còn bật card NAT, cài đặt đủ gói công cụ:

     ```
     sudo apt update && sudo apt install -y python3-scapy wireshark tcpdump
     
     ```

   * Tắt card NAT, chỉ bật card `Internal Network: dns-lab` với **`Promiscuous Mode = Allow VMs`**.

   * Gán IP tĩnh `10.9.0.200/24` và gateway `10.9.0.1` cho card `dns-lab` (ví dụ `eth0` hoặc `eth1`):

     ```
     sudo ip addr add 10.9.0.200/24 dev eth0
     sudo ip link set eth0 up
     sudo ip route replace default via 10.9.0.1 dev eth0
     
     ```

   * Khởi chạy Web Server giả mạo phục vụ trang `fake_index.html` tại cổng 80:

     ```
     mkdir -p ~/LAB9/fake_site
     cp fake_index.html ~/LAB9/fake_site/index.html
     sudo python3 -m http.server 80 --directory ~/LAB9/fake_site
     
     ```

### Bước 5: Khởi động `AUTH-DNS` (`172.16.6.20`), `DMZ-WEB` (`172.16.6.10`) và Kiểm tra Baseline

1. **Trên máy vùng DMZ (`172.16.6.10` và `172.16.6.20`):**

   * Đảm bảo Web Server hợp lệ đang chạy trên `172.16.6.10:80` (ví dụ hiển thị nội dung `"DMZ-WEB LEGITIMATE SERVER 172.16.6.10"`).

   * Khởi chạy Authoritative DNS mô phỏng có độ trễ 1.5 giây trên `172.16.6.20`:

     ```
     sudo python3 auth_dns_delayed.py --bind 172.16.6.20 --delay 1.5
     
     ```

2. **Kiểm tra Baseline từ `DNS-SERVER` và `VICTIM`:**

   * Trên `DNS-SERVER`: `sudo rndc flush`

   * Trên `VICTIM`:

     ```
     dig @10.9.0.10 www.external.lab9.test A +noall +answer
     curl http://www.external.lab9.test
     
     ```

   * **Yêu cầu bắt buộc:** Kết quả `dig` phải trả về `172.16.6.10` (sau khoảng 1.5 giây chờ) và `curl` trả về nội dung trang web hợp lệ của `DMZ-WEB`.

3. **Bắt gói tin Baseline trên Wireshark tại Kali:**

   * Mở Wireshark trên card mạng `dns-lab` của Kali, nhập filter: `dns.qry.name == "www.external.lab9.test"`.

   * Quan sát thấy Kali bắt được cả gói Query của `10.9.0.100 -> 10.9.0.10` và gói Forward Query của `10.9.0.10 -> 172.16.6.20`.

### Bước 6: Thực hiện Task 1 – Thay đổi tệp `/etc/hosts` (HOSTS-file Redirection)

1. Trên máy `VICTIM` (`10.9.0.100`), sao lưu và thêm bản ghi giả mạo vào `/etc/hosts`:

   ```
   sudo cp /etc/hosts /etc/hosts.lab9.bak
   echo "10.9.0.200   www.lab9.test" | sudo tee -a /etc/hosts
   
   ```

2. Kiểm tra hiệu ứng chuyển hướng và so sánh với `dig`:

   ```
   getent hosts www.lab9.test
   curl http://www.lab9.test
   dig @10.9.0.10 www.lab9.test A +short
   
   ```

   * `getent` và `curl` lập tức trỏ về `10.9.0.200` (hiển thị trang giả lập của Kali).

   * `dig @10.9.0.10` vẫn trả về `172.16.6.10` vì `dig` hỏi trực tiếp DNS server mà không đọc `/etc/hosts`.

3. **Khôi phục ngay sau khi chụp ảnh minh chứng Task 1:**

   ```
   sudo cp /etc/hosts.lab9.bak /etc/hosts
   sudo resolvectl flush-caches
   
   ```

### Bước 7: Thực hiện Task 2 – Giả mạo phản hồi DNS trực tiếp (Direct DNS Spoofing)

1. **Làm sạch cache trước khi thử nghiệm:**

   * Trên `DNS-SERVER`: `sudo rndc flush`

   * Trên `VICTIM`: `sudo resolvectl flush-caches`

2. **Trên `ATTACKER` Kali (`10.9.0.200`), mở một terminal mới và chạy script ở chế độ `victim`:**

   ```
   sudo python3 dns_spoof_lab9.py --mode victim --iface eth0
   
   ```

   *(Thay `eth0` bằng tên card mạng `dns-lab` thực tế trên Kali của bạn, kiểm tra bằng `ip -br addr`)*.

3. **Trên `VICTIM` (`10.9.0.100`), phát sinh truy vấn mới:**

   ```
   resolvectl query www.external.lab9.test
   curl http://www.external.lab9.test
   
   ```

4. **Quan sát kết quả:**

   * Terminal của Kali in ra: `[LAB9] forged victim response: www.external.lab9.test. -> 10.9.0.200; txid=...; dst=10.9.0.100:...`

   * Máy `VICTIM` nhận địa chỉ `10.9.0.200` và lệnh `curl` hiển thị nội dung trang giả mạo `LAB 9 - TRANG MÔ PHỎNG BỊ CHUYỂN HƯỚNG`.

   * Trên Wireshark, chụp lại màn hình thể hiện rõ gói `Forged response (A = 10.9.0.200)` đến ngay lập tức với cùng `Transaction ID` và `UDP client port`, trong khi gói `Legitimate response (A = 172.16.6.10)` đến trễ hơn 1.5 giây nên bị hệ điều hành bỏ qua.

### Bước 8: Thực hiện Task 3 – Đầu độc bộ nhớ đệm DNS (DNS Cache Poisoning)

1. **Xóa sạch cache và kiểm tra lại trạng thái trước khi tấn công:**

   * Dừng script Task 2 trên Kali (`Ctrl + C`).

   * Trên `DNS-SERVER`: `sudo rndc flush`

   * Trên `VICTIM`: `sudo resolvectl flush-caches`

2. **Trên `ATTACKER` Kali (`10.9.0.200`), khởi chạy script ở chế độ `resolver`:**

   ```
   sudo python3 dns_spoof_lab9.py --mode resolver --iface eth0
   
   ```

3. **Trên `VICTIM` (`10.9.0.100`), kích hoạt truy vấn để buộc `DNS-SERVER` phải hỏi `AUTH-DNS`:**

   ```
   sudo resolvectl flush-caches
   resolvectl query www.external.lab9.test
   curl http://www.external.lab9.test
   
   ```

4. **Kiểm chứng bộ nhớ đệm của `DNS-SERVER` đã bị đầu độc:**

   * Dừng hẳn script `dns_spoof_lab9.py` trên Kali (`Ctrl + C`).

   * Thử truy vấn lại từ `VICTIM` hoặc chạy `dig @10.9.0.10 www.external.lab9.test`: kết quả **vẫn trả về `10.9.0.200`** vì bản ghi giả đã nằm trong bộ nhớ đệm của BIND9 với TTL 120 giây.

   * Trên `DNS-SERVER` (`10.9.0.10`), xuất dữ liệu cache ra file và kiểm tra:

     ```
     sudo rndc dumpdb -cache
     sudo grep -A4 -B4 "www.external.lab9.test" /var/cache/bind/named_dump.db
     
     ```

     Chụp ảnh màn hình thấy rõ dòng `www.external.lab9.test. ... A 10.9.0.200` trong `/var/cache/bind/named_dump.db`.

### Bước 9: Khôi phục hệ thống và Thực hành Phòng thủ (Hardening)

1. **Khôi phục sạch bộ nhớ đệm:**

   * Dừng mọi tiến trình tấn công trên Kali.

   * Trên `DNS-SERVER`: `sudo rndc flush`

   * Trên `VICTIM`:

     ```
     sudo resolvectl flush-caches
     dig @10.9.0.10 www.external.lab9.test A +noall +answer
     
     ```

   * Xác nhận kết quả đã quay trở về `172.16.6.10` và chụp ảnh minh chứng khôi phục.

2. **Thực hiện bài tập phòng thủ:**

   * Mở `/etc/bind/named.conf.options` trên `DNS-SERVER`, xóa (hoặc đóng chú thích `//`) khối `server 172.16.6.20 { send-cookie no; };`, sau đó chạy `sudo systemctl restart bind9`.

   * Mở cài đặt **VirtualBox -> Kali Linux -> Settings -> Network**, đổi **Promiscuous Mode** từ `Allow VMs` về **`Deny`** và chụp ảnh minh chứng.

## 4. Danh Mục 22 Khung Chèn Ảnh Trong File Báo Cáo Word

Trong file báo cáo Word (`11CNPM2-Lab8_1150080156-NguyenHoTruongTam.docx`), 22 khung chờ chèn ảnh đã được đánh số và đặt tên gợi ý rõ ràng theo đúng thứ tự thực hiện (bao gồm đầy đủ 9 nhóm ảnh minh chứng bắt buộc ở Mục L.2 của đề bài):

| Mã khung trong Word | Tên file ảnh gợi ý | Nội dung cần chụp để chèn vào khung | Thuộc nhóm minh chứng bắt buộc | 
| ----- | ----- | ----- | ----- | 
| **ẢNH 01** | `H01_DanhSachVM_Snapshot.png` | Giao diện VirtualBox hiển thị các máy ảo và Snapshot `LAB9_START_FROM_LAB8`. | Chuẩn bị môi trường | 
| **ẢNH 02** | `H02_pfSense_DNSLAB_Interface.png` | Cấu hình Interface `DNSLAB` (`10.9.0.1/24`, không gateway) trên pfSense. | **Bắt buộc #1** (pfSense DNSLAB) | 
| **ẢNH 03** | `H03_pfSense_DNSLAB_Rules.png` | Bảng 5 Firewall Rules cô lập trên tab `Firewall > Rules > DNSLAB`. | **Bắt buộc #1** (Ruleset cô lập) | 
| **ẢNH 04** | `H04_VBox_Promiscuous_AllowVMs.png` | Card mạng `dns-lab` của Kali đặt `Promiscuous Mode = Allow VMs`. | Cấu hình mạng VM | 
| **ẢNH 05** | `H05_DNS_Server_IP_Status.png` | Lệnh `ip -br addr`, `ip route`, `systemctl status bind9` trên `DNS-SERVER` (`10.9.0.10`). | **Bắt buộc #2** (IP các máy) | 
| **ẢNH 06** | `H06_BIND9_Validate_Zone.png` | Lệnh `named-checkconf`, `named-checkzone` báo OK và `ss -lunpt | grep :53`. | **Bắt buộc #3** (Validate BIND9) | 
| **ẢNH 07** | `H07_BIND9_LocalZone_Dig.png` | Kết quả `dig @10.9.0.10 www.lab9.test` và `dig -x 10.9.0.10` trên `DNS-SERVER`. | Kiểm thử Local Zone | 
| **ẢNH 08** | `H08_Victim_Netplan_Resolvectl.png` | Lệnh `ip -br addr`, `resolvectl status` và `resolvectl query www.lab9.test` trên `VICTIM` (`10.9.0.100`). | **Bắt buộc #2** (IP các máy) | 
| **ẢNH 09** | `H09_Kali_IP_FakeWeb.png` | Lệnh `ip -br addr` (`10.9.0.200`) và chạy `python3 -m http.server 80` trên Kali. | **Bắt buộc #2** (IP các máy) | 
| **ẢNH 10** | `H10_AppTest_AuthDNS_Delayed.png` | Chạy `auth_dns_delayed.py --bind 172.16.6.20 --delay 1.5` trên `APP-TEST`. | Chuẩn bị Baseline | 
| **ẢNH 11** | `H11_Baseline_External_Success.png` | Kết quả `dig` và `curl http://www.external.lab9.test` trả về `172.16.6.10`. | **Bắt buộc #4** (Baseline `172.16.6.10`) | 
| **ẢNH 12** | `H12_Wireshark_Baseline_DNS.png` | Wireshark trên Kali bắt được luồng truy vấn DNS Baseline. | Quan sát gói tin | 
| **ẢNH 13** | `H13_Task1_Hosts_Redirect.png` | Task 1: `getent`/`curl` đi tới `10.9.0.200` trong khi `dig @10.9.0.10` vẫn trả `172.16.6.10`. | **Bắt buộc #5** (Task 1 HOSTS) | 
| **ẢNH 14** | `H14_Task1_Restore_Hosts.png` | Khôi phục `/etc/hosts` từ file `.bak` và xóa cache trên `VICTIM`. | Khôi phục sau Task 1 | 
| **ẢNH 15** | `H15_Task2_Kali_Spoof_Victim.png` | Task 2: Terminal Kali chạy `dns_spoof_lab9.py --mode victim` báo đã gửi gói forged. | **Bắt buộc #6** (Task 2 Spoofing) | 
| **ẢNH 16** | `H16_Task2_Victim_Result.png` | Task 2: `VICTIM` nhận `10.9.0.200` và hiển thị trang giả lập của Kali. | **Bắt buộc #6** (Task 2 Victim nhận `10.9.0.200`) | 
| **ẢNH 17** | `H17_Task2_Wireshark_Evidence.png` | Task 2: Wireshark có Query + Forged Response (`10.9.0.200`) + Legitimate Response (`172.16.6.10`), khớp TXID & UDP Port. | **Bắt buộc #6** (Wireshark Task 2) | 
| **ẢNH 18** | `H18_Task3_Kali_Spoof_Resolver.png` | Task 3: Terminal Kali chạy `dns_spoof_lab9.py --mode resolver` báo đã gửi gói forged tới `10.9.0.10`. | **Bắt buộc #7** (Task 3 Resolver) | 
| **ẢNH 19** | `H19_Task3_Victim_Poisoned.png` | Task 3: `VICTIM` truy vấn nhận `10.9.0.200` ngay cả khi đã dừng script trên Kali. | **Bắt buộc #7** (Task 3 Cache Poisoning) | 
| **ẢNH 20** | `H20_Task3_BIND9_CacheDump.png` | Task 3: Lệnh `rndc dumpdb -cache` và `grep` file `/var/cache/bind/named_dump.db` chứa `10.9.0.200`. | **Bắt buộc #7** (Cache chứa `10.9.0.200`) | 
| **ẢNH 21** | `H21_Restore_Clean_Cache.png` | Sau khi `rndc flush` và `resolvectl flush-caches`, kết quả phân giải trở về `172.16.6.10`. | **Bắt buộc #8** (Sau flush về `172.16.6.10`) | 
| **ẢNH 22** | `H22_Defense_Cookie_PromiscDeny.png` | Cài đặt VirtualBox của Kali đã trả `Promiscuous Mode` về `Deny` sau buổi lab. | **Bắt buộc #9** (Promiscuous Mode = Deny) | 

## 5. Phân Tích Các Khó Khăn Thường Gặp và Cách Khắc Phục (Troubleshooting)

Trong quá trình triển khai mô hình Lab 8 trên Ubuntu 24.04, Kali Linux và pfSense, dưới đây là 8 khó khăn kỹ thuật phổ biến nhất và cách xử lý triệt để:

### Khó khăn 1: Sửa `/etc/resolv.conf` trên Ubuntu 24.04 bị mất cấu hình hoặc `netplan apply` báo lỗi quyền

* **Nguyên nhân:** Ubuntu 24.04 sử dụng dịch vụ `systemd-resolved` quản lý tệp `/etc/resolv.conf` dưới dạng symbolic link động, nên mọi chỉnh sửa thủ công bằng `nano /etc/resolv.conf` đều bị ghi đè. Ngoài ra, Netplan trên Ubuntu 24.04 kiểm tra rất gắt quyền truy cập file `.yaml` và tên card mạng (`enp0s3` vs `eth0`).

* **Cách khắc phục:**

  * Chạy `ip -br link` để xem đúng tên card mạng thực tế trên máy `VICTIM`, sửa lại tên đó trong `/etc/netplan/01-victim-dnslab.yaml`.

  * Chạy `sudo chmod 600 /etc/netplan/01-victim-dnslab.yaml` để tránh cảnh báo `Permissions for /etc/netplan/... are too open`, sau đó chạy `sudo netplan apply`.

  * Kiểm tra lại bằng `resolvectl status` để chắc chắn dòng `Current DNS Server` chỉ hiển thị duy nhất `10.9.0.10`.

### Khó khăn 2: Quên tắt card NAT phụ làm sai lệch đường đi của truy vấn DNS

* **Nguyên nhân:** Trong lúc cài đặt `bind9`, `scapy`, `wireshark`, sinh viên bật thêm 1 card NAT trên các máy ảo. Nếu quên tắt card NAT khi bước vào pha thực hành, hệ điều hành sẽ tạo Default Route ưu tiên đi qua card NAT kèm theo DNS Server mặc định của VirtualBox NAT (`10.0.2.3`), khiến `VICTIM` không hỏi `10.9.0.10` hoặc gói tin không đi qua switch `dns-lab`.

* **Cách khắc phục:** Ngay sau khi `apt install` xong, tắt máy ảo (hoặc rút cáp ảo / tắt interface NAT bằng `sudo ip link set <nat_iface> down`) để mỗi máy trong `DNS-LAB` chỉ còn hoạt động duy nhất trên card `Internal Network: dns-lab`.

### Khó khăn 3: Kali Linux không bắt được gói tin DNS giữa `VICTIM` và `DNS-SERVER`

* **Nguyên nhân:** Mặc định VirtualBox đặt chế độ `Promiscuous Mode = Deny` trên card mạng ảo, khiến switch ảo `dns-lab` chỉ chuyển tiếp các khung tin Unicast tới đúng máy đích mà không cho phép Kali nghe lén. Hoặc sinh viên truyền sai tên card mạng vào tham số `--iface` (ví dụ gõ `--iface eth1` trong khi trên Kali card mạng là `eth0`).

* **Cách khắc phục:**

  * Vào **VirtualBox -> Kali -> Settings -> Network**, đổi **Promiscuous Mode** thành **`Allow VMs`**.

  * Trên Kali, gõ `ip -br addr` để xem chính xác tên card đang mang địa chỉ `10.9.0.200/24` và truyền đúng tên đó vào lệnh `sudo python3 dns_spoof_lab9.py --mode victim --iface <tên_card>`.

### Khó khăn 4: Chạy script giả mạo nhưng `VICTIM` vẫn luôn nhận kết quả thật `172.16.6.10`

* **Nguyên nhân:**

  1. Bản ghi `www.external.lab9.test -> 172.16.6.10` từ bước kiểm tra Baseline vẫn còn lưu trong bộ nhớ đệm của BIND9 (`10.9.0.10`) hoặc `systemd-resolved` (`10.9.0.100`), nên khi truy vấn lại hệ thống trả lời ngay từ cache mà không gửi gói tin ra mạng.

  2. Hoặc tiến trình `auth_dns_delayed.py` bên máy `APP-TEST` chưa đặt độ trễ đủ lớn.

* **Cách khắc phục:**

  * Luôn thực hiện cặp lệnh xóa cache trước mỗi lần thử nghiệm:

    * Trên `DNS-SERVER`: `sudo rndc flush`

    * Trên `VICTIM`: `sudo resolvectl flush-caches`

  * Nếu máy ảo chạy hơi chậm làm Kali phản hồi trễ, có thể tăng nhẹ tham số delay trên `APP-TEST` lên `2.0` giây: `sudo python3 auth_dns_delayed.py --bind 172.16.6.20 --delay 2.0`.

### Khó khăn 5: Task 2 thành công nhưng Task 3 (Cache Poisoning) không đầu độc được BIND9

* **Nguyên nhân:** Từ phiên bản BIND 9.10 trở lên (đặc biệt trên Ubuntu 24.04), cơ chế **DNS COOKIE (RFC 7873)** được bật mặc định. Nếu trong `/etc/bind/named.conf.options` thiếu khối cấu hình `server 172.16.6.20 { send-cookie no; };`, BIND9 sẽ kiểm tra Cookie hoặc xử lý chặt chẽ phản hồi không khớp tùy chọn EDNS.

* **Cách khắc phục:** Kiểm tra kỹ tệp `/etc/bind/named.conf.options` đã có đoạn `server 172.16.6.20 { send-cookie no; };` chưa, sau đó chạy `sudo named-checkconf && sudo systemctl restart bind9` và xóa cache trước khi chạy lại `--mode resolver`.

### Khó khăn 6: Cấu hình nhầm Upstream Gateway trên Interface `DNSLAB` của pfSense

* **Nguyên nhân:** Khi thêm interface `OPT2 (DNSLAB)` trên pfSense, nhiều bạn vô tình tạo thêm một Gateway trong mục *IPv4 Upstream Gateway*. Khi một interface có Upstream Gateway, pfSense coi đó là cổng WAN (Internet) thay vì mạng nội bộ (LAN), dẫn đến việc áp dụng NAT chiều ra và chặn hoặc làm hỏng định tuyến liên mạng giữa `DNSLAB (10.9.0.0/24)` và `DMZ (172.16.6.0/24)`.

* **Cách khắc phục:** Vào **Interfaces -> DNSLAB**, đảm bảo mục **IPv4 Upstream Gateway** được chọn là **`None`**, nhấn **Save -> Apply Changes**.

### Khó khăn 7: Không tìm thấy tệp `named_dump.db` khi kiểm tra bộ nhớ đệm BIND9 ở Task 3

* **Nguyên nhân:** Trên Ubuntu Server 24.04 với AppArmor được kích hoạt cho dịch vụ `named`, lệnh `sudo rndc dumpdb -cache` sẽ ghi tệp kết xuất vào thư mục làm việc mặc định được khai báo ở chỉ thị `directory` trong `/etc/bind/named.conf.options` (tức `/var/cache/bind/named_dump.db`).

* **Cách khắc phục:** Sau khi gõ `sudo rndc dumpdb -cache`, chờ 1 giây rồi chạy `sudo ls -la /var/cache/bind/` hoặc `sudo find /var/cache/bind -maxdepth 1 -type f -name "*dump*"` để xác nhận tệp `/var/cache/bind/named_dump.db`, sau đó dùng `sudo grep -A4 -B4 "www.external.lab9.test" /var/cache/bind/named_dump.db`.

### Khó khăn 8: Dịch vụ `systemd-resolved` chiếm cổng 53 trên máy `DNS-SERVER`

* **Nguyên nhân:** Trên một số bản cài đặt Ubuntu 24.04, dịch vụ `systemd-resolved` lắng nghe stub listener tại `127.0.0.53:53`. Nếu BIND9 cấu hình `listen-on { any; };` có thể xảy ra xung đột hoặc khi gõ lệnh `dig` không chỉ định `@10.9.0.10` sẽ hỏi nhầm stub cục bộ.

* **Cách khắc phục:** Giữ đúng chỉ thị `listen-on { 127.0.0.1; 10.9.0.10; };` trong `/etc/bind/named.conf.options` như tệp mẫu chuẩn của bài Lab và luôn chỉ định rõ `@10.9.0.10` khi chạy lệnh `dig @10.9.0.10 ...` trên máy chủ.
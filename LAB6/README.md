# LAB 6 – Cấu hình Firewall và chính sách truy cập trên pfSense

**Môn học:** An toàn bảo mật hệ thống thông tin  
**Sinh viên:** Nguyễn Hồ Trường Tam  
**MSSV:** 1150080156  
**Lớp:** 11CNPM2

## 1. Môi trường thực hiện

Sử dụng Oracle VirtualBox để triển khai hệ thống mạng LAB6.

Các máy ảo:
- `pfSense_Tam`: pfSense CE 2.7.2, RAM 1536 MB.
- `Win10_LAN_Tam`: Windows 10, làm máy Client.
- `kali-linux-2026.2`: Kali Linux, làm máy chủ website mô phỏng trong DMZ.

Do máy thật chỉ có 8 GB RAM nên các máy ảo được chạy luân phiên để hạn chế tình trạng giật, lag.

## 2. Cấu hình pfSense

### 2.1. Cấu hình card mạng VirtualBox

Vào VirtualBox → chọn `pfSense_Tam` → Settings → Network.

| Adapter | Attached to | Name / Vai trò |
|---|---|---|
| Adapter 1 | NAT Network | LAB6-WAN |
| Adapter 2 | Host-Only Adapter | MGMT |
| Adapter 3 | Internal Network | lab6-lan |
| Adapter 4 | Internal Network | lab6-dmz |

Bật **Enable Network Adapter** và **Virtual Cable Connected** cho cả 4 adapter.

### 2.2. Gán interface và địa chỉ IP

Khởi động pfSense, chọn `1) Assign Interfaces` để gán card mạng, sau đó chọn `2) Set interface(s) IP address` để cấu hình địa chỉ IPv4.

| Interface | Card | IPv4 |
|---|---|---|
| WAN | em0 | DHCP – 192.168.250.3/24 |
| MGMT | em1 | 192.168.56.254/24 |
| LAN | em2 | 10.6.0.1/24 |
| DMZ | em3 | 172.16.6.1/24 |

Truy cập giao diện quản trị bằng trình duyệt trên Windows thật:

`https://192.168.56.254`

### 2.3. Cấu hình Firewall Rule cho MGMT

Vào Firewall → Rules → MGMT → Add.

Thiết lập:
- Action: Pass
- Interface: MGMT
- Protocol: TCP
- Source: 192.168.56.1
- Destination: MGMT address
- Destination Port: 443 (HTTPS)

Nhấn Save → Apply Changes.

Rule này cho phép máy Windows thật truy cập WebGUI pfSense qua mạng quản trị.

## 3. Cấu hình Firewall Aliases

Vào Firewall → Aliases → Add.

Tạo các alias sau:

| Alias | Type | Giá trị |
|---|---|---|
| CLIENT_A | Host(s) | 10.6.0.21 |
| CLIENT_B | Host(s) | 10.6.0.22 |
| POLICY_CLIENTS | Host(s) | 10.6.0.21, 10.6.0.22 |
| GENERAL_SITE | Host(s) | 172.16.6.10 |
| JOB_SITE | Host(s) | 172.16.6.20 |
| SOCIAL_SITE | Host(s) | 172.16.6.30 |
| RESTRICTED_SITE | Host(s) | 172.16.6.40 |
| WEB_PORTS | Port(s) | 80, 443 |

Sau khi tạo xong, nhấn Apply Changes.

Các alias giúp quản lý địa chỉ IP và cổng dịch vụ mà không cần nhập lại trong từng firewall rule.

## 4. Cấu hình Schedule

Vào Firewall → Schedules → Add.

Tạo hai lịch:

| Schedule | Ngày | Thời gian |
|---|---|---|
| LUNCH_WINDOW | Thứ 2 – Thứ 6 | 11:30 – 13:00 |
| WORK_HOURS | Thứ 2 – Thứ 6 | 08:00 – 17:00 |

Nhấn Add Time → Save.

Schedule được sử dụng trong các rule cho phép truy cập theo thời gian. Khi lịch không hoạt động, rule Pass gắn với lịch sẽ không khớp.

## 5. Cấu hình Firewall Rules trên LAN

Vào Firewall → Rules → LAN → Add.

Các rule đã tạo trong quá trình thực hành:

| Rule | Action | Source | Destination | Port / Schedule |
|---|---|---|---|---|
| LAB6_BLOCK_A_JOB | Block | CLIENT_A | JOB_SITE | TCP/80 |
| LAB6_BLOCK_RESTRICTED | Block | POLICY_CLIENTS | RESTRICTED_SITE | TCP/80 |
| LAB6_ALLOW_B_SOCIAL_LUNCH | Pass | CLIENT_B | SOCIAL_SITE | TCP/80, LUNCH_WINDOW |
| LAB6_BLOCK_B_SOCIAL | Block | CLIENT_B | SOCIAL_SITE | TCP/80 |
| LAB6_ALLOW_GENERAL_SITE | Pass | POLICY_CLIENTS | GENERAL_SITE | TCP/80 |
| LAB6_ALLOW_WEB_WORKHOURS | Pass | POLICY_CLIENTS | Any | WEB_PORTS, WORK_HOURS |
| LAB6_BLOCK_OTHER_TRAFFIC | Block | POLICY_CLIENTS | Any | Any |

Đối với rule có Schedule, mở Advanced Options → Display Advanced để chọn lịch.

Bật Log packets cho các rule Block cần ghi nhận.

Sau khi tạo rule, nhấn Save → Apply Changes.

**Lưu ý:** pfSense áp dụng nguyên tắc first-match, kiểm tra rule từ trên xuống dưới. Rule Pass có Schedule phải nằm trên rule Block tương ứng. Trong ảnh ruleset cuối, một số rule còn sai thứ tự nên chưa thể xác nhận toàn bộ chính sách hoạt động như dự kiến.

Rule `LAN to Internet` cũ đã được vô hiệu hóa để tránh cho phép lưu lượng quá rộng.

## 6. Cấu hình Firewall Rule trên DMZ

Vào Firewall → Rules → DMZ → Add.

Thiết lập:

- Action: Block
- Interface: DMZ
- Address Family: IPv4
- Protocol: Any
- Source: DMZ subnets
- Destination: LAN subnets
- Log packets: Enable
- Description: LAB6_BLOCK_DMZ_TO_LAN

Nhấn Save → Apply Changes.

Mục đích là chặn các kết nối mới do máy trong DMZ chủ động gửi vào LAN.

## 7. Cấu hình Kali làm DMZ Web Server

### 7.1. Cấu hình mạng

Trong VirtualBox, thiết lập Adapter 1 của Kali:

- Attached to: Internal Network
- Name: lab6-dmz
- Virtual Cable Connected: Enable

Khởi động Kali, mở Terminal.

Kiểm tra card mạng bằng lệnh:

`ip -br addr`

Card mạng sử dụng là `eth0`.

### 7.2. Đặt địa chỉ IP

Thực hiện lần lượt:

`sudo ip addr add 172.16.6.10/24 dev eth0`

`sudo ip addr add 172.16.6.20/24 dev eth0`

`sudo ip addr add 172.16.6.30/24 dev eth0`

`sudo ip addr add 172.16.6.40/24 dev eth0`

Cấu hình gateway:

`sudo ip route replace default via 172.16.6.1 dev eth0`

Kiểm tra:

`ip -br addr`

Kết quả hiển thị đủ 4 địa chỉ IPv4 trên `eth0`.

### 7.3. Chạy Web Server bằng Python

Tạo thư mục:

`mkdir -p ~/lab6-web`

Tạo trang HTML:

`echo '<h1>LAB6 DMZ WEB - TEST SUCCESS</h1>' > ~/lab6-web/index.html`

Khởi động HTTP Server:

`sudo python3 -m http.server 80 --bind 0.0.0.0 --directory ~/lab6-web`

Mở Terminal thứ hai và kiểm tra:

`curl http://172.16.6.10`

`curl http://172.16.6.20`

`curl http://172.16.6.30`

`curl http://172.16.6.40`

Cả 4 địa chỉ trả về nội dung `LAB6 DMZ WEB - TEST SUCCESS`.

Đây là kết quả kiểm thử HTTP ngay trên Kali, chưa phải kết quả kiểm thử Firewall từ Client qua pfSense.

## 8. Cấu hình Windows 10 Client

Trong VirtualBox, chọn `Win10_LAN_Tam` → Settings → Network.

Thiết lập:
- Adapter 1: Internal Network
- Name: lab6-lan
- Virtual Cable Connected: Enable

Trong Windows 10, nhấn Win + R → nhập `ncpa.cpl`.

Chọn Ethernet → Properties → Internet Protocol Version 4 (TCP/IPv4).

Cấu hình:

| Thông số | Giá trị |
|---|---|
| IP Address | 10.6.0.21 |
| Subnet Mask | 255.255.255.0 |
| Default Gateway | 10.6.0.1 |
| Preferred DNS | 10.6.0.10 (dự kiến cho DC01) |

Mở CMD kiểm tra:

`ipconfig`

`ping 10.6.0.1`

`arp -a`

Sau đó mở PowerShell và chạy:

`Test-NetConnection 10.6.0.1 -Port 443`

Kết quả thực tế:

`TcpTestSucceeded : True`

Điều này xác nhận Windows 10 kết nối được TCP/443 tới pfSense LAN.

## 9. Các lỗi gặp phải và cách khắc phục

### Lỗi 1: Không truy cập được pfSense WebGUI

**Hiện tượng:** Trình duyệt truy cập `192.168.56.254` báo ERR_CONNECTION_TIMED_OUT.

**Nguyên nhân:** Chưa có Firewall Rule phù hợp trên MGMT.

**Cách xử lý:** Tạm thời vào pfSense Console → chọn Shell và dùng `pfctl -d` để tắt bộ lọc firewall trong quá trình khắc phục.

Sau khi truy cập được WebGUI, tạo rule MGMT cho phép TCP/443 từ `192.168.56.1`.

Bật lại firewall bằng `pfctl -e` và kiểm tra kết nối.

Không để firewall ở trạng thái disabled sau khi xử lý xong.

### Lỗi 2: Nhập sai tên Internal Network

**Hiện tượng:** Windows 10 không liên lạc được với pfSense LAN.

**Nguyên nhân:** Tên mạng `lab6_lan` và `lab6-lan` khác nhau.

**Cách xử lý:** Chỉnh Adapter của Windows 10 về đúng tên `lab6-lan`, giống Adapter 3 trên pfSense.

### Lỗi 3: Ping gateway không thành công

**Hiện tượng:** Chạy `ping 10.6.0.1` báo Request timed out.

**Nguyên nhân có thể:** Firewall đang chặn ICMP.

**Cách kiểm tra:** Dùng `arp -a`, sau đó kiểm thử TCP bằng PowerShell:

`Test-NetConnection 10.6.0.1 -Port 443`

**Kết quả:** `TcpTestSucceeded : True`, xác nhận kết nối TCP/443 hoạt động dù ICMP timeout.

### Lỗi 4: Không lưu được Firewall Rule DMZ

**Hiện tượng:**

`DMZ subnets is not a valid source IP address or alias`

`LAN subnets is not a valid destination IP address or alias`

**Nguyên nhân:** Nhập chữ `DMZ subnets` và `LAN subnets` vào ô Address or Alias.

**Cách xử lý:** Chọn trực tiếp `DMZ subnets` và `LAN subnets` trong danh sách Source/Destination thay vì nhập bằng tay.

Sau đó Save → Apply Changes thành công.

### Lỗi 5: Không tìm thấy Schedule trong Firewall Rule

**Hiện tượng:** Khi tạo rule không thấy trường Schedule.

**Nguyên nhân:** Schedule nằm trong phần Advanced Options.

**Cách xử lý:** Nhấn Display Advanced, tìm Schedule rồi chọn `LUNCH_WINDOW` hoặc `WORK_HOURS`.

### Lỗi 6: Firewall Rule sai thứ tự

**Hiện tượng:** Rule Block nằm trên rule Pass, làm chính sách cho phép theo lịch không được áp dụng như mong muốn.

**Nguyên nhân:** pfSense xử lý các rule theo thứ tự từ trên xuống dưới.

**Cách xử lý:** Sắp xếp rule đặc hiệu đúng thứ tự, đưa rule Pass có Schedule lên trước rule Block tương ứng, sau đó Save → Apply Changes.

Trong ảnh cuối vẫn còn một số rule sai vị trí; đây là vấn đề cấu hình chưa được xác nhận khắc phục hoàn toàn.

### Lỗi 7: Không chạy được Test-NetConnection

**Hiện tượng:**

`'Test-NetConnection' is not recognized as an internal or external command`

**Nguyên nhân:** Nhập lệnh PowerShell trong cửa sổ CMD.

**Cách xử lý:** Mở Windows PowerShell và thực hiện lại lệnh. Kết quả trả về `TcpTestSucceeded : True`.

### Lỗi 8: Máy bị lag do thiếu RAM

**Hiện tượng:** Máy thật chạy chậm khi bật pfSense, Windows 10 và Kali cùng lúc.

**Nguyên nhân:** Máy thật có 8 GB RAM, không đủ thoải mái để chạy đồng thời nhiều máy ảo và ứng dụng.

**Cách xử lý:**
- Giảm RAM pfSense xuống 1536 MB.
- Sử dụng Python HTTP Server thay vì cài thêm máy chủ mới.
- Chạy luân phiên Kali và Windows 10 khi có thể.
- Tắt các ứng dụng không cần thiết trên máy thật.

### Lỗi 9: Kali mất địa chỉ IP sau khi tắt máy

**Nguyên nhân:** Các địa chỉ được cấu hình bằng `ip addr add` là cấu hình tạm thời.

**Cách xử lý:** Chạy lại lệnh gán IP và khởi động lại Python HTTP Server sau khi bật Kali.

## 10. Sao lưu cấu hình pfSense

Vào Diagnostics → Backup & Restore.

Chọn:
- Backup area: All
- Skip RRD data: Enable

Nhấn Download configuration as XML.

File XML dùng để khôi phục cấu hình pfSense khi cần thiết. Không công khai file backup chưa được loại bỏ dữ liệu nhạy cảm.

**Phạm vi chưa triển khai:** Windows Server Active Directory, LDAP Authentication và Captive Portal. Các kết quả kiểm thử Allow/Block từ Windows 10 tới website DMZ, so sánh Block/Reject và Reset States cũng chưa được xác nhận thực tế.

---

**Kết thúc nội dung cấu hình và xử lý lỗi LAB6.**
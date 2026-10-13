# LAB 6 - Xác thực Active Directory và chính sách truy cập trên pfSense

> **Trạng thái: 
> **Nguồn yêu cầu:** `LAB6_pfSense_AD_Access_Policies_2026.pdf`
> **Báo cáo Word:** `11CNPM2-Lab6_1150080156-NguyenHoTruongTam.docx`

## 1. Mục tiêu

- pfSense CE 4 interface: WAN, MGMT, LAN, DMZ; topology tách riêng LAB5.
- Windows Server AD DS + DNS, domain `lab6.test`; LDAP `LAB6-AD` và test `sv_a`, `sv_b`.
- Captive Portal `LAB6_USERS` trên LAN dùng LDAP.
- Host/port Alias, Schedule và 7 kịch bản policy theo IP/port/time.
- Log, States, kiểm tra trước/sau; bàn giao báo cáo Word và `config.xml` từ pfSense.

**Giới hạn kỹ thuật:** tài khoản LDAP chỉ chứng minh xác thực; pfSense base firewall không dùng username AD làm Source rule trực tiếp. Kịch bản lọc site là mô phỏng bằng IP của DMZ, không phải Web Category Filtering thật.

## 2. Sơ đồ địa chỉ IP

| Thành phần | IP / Mạng | Ghi chú |
|---|---|---|
| WAN pfSense | DHCP từ `LAB6-WAN`, `192.168.250.0/24` | NAT Network, gateway `192.168.250.1` theo sơ đồ |
| MGMT pfSense | `192.168.56.254/24` | Host-Only; WebGUI |
| Host MGMT | `192.168.56.1/24` | Không gateway/DNS |
| LAN pfSense | `10.6.0.1/24` | Gateway clients |
| DC01 | `10.6.0.10/24` | GW `10.6.0.1`; DNS `10.6.0.10`; `lab6.test` |
| Client-A | `10.6.0.21/24` | GW `10.6.0.1`; DNS `10.6.0.10`; `sv_a` |
| Client-B | `10.6.0.22/24` | GW `10.6.0.1`; DNS `10.6.0.10`; `sv_b` |
| DMZ pfSense | `172.16.6.1/24` | Gateway DMZ |
| DMZ-WEB | `172.16.6.10/24`, IP phụ `.20`, `.30`, `.40` | Nginx / test sites |

## 3. Cấu trúc nộp bài

```text
LAB6/
├── README.md
├── 11CNPM2-Lab6_1150080156-NguyenHoTruongTam.docx
├── config.xml                
└── images/
    ├── 01_topology.png
    ├── ...
    └── 25_ruleset_summary.png
```

## 4. Các bước thực hiện theo tài liệu PDF

### B. Dựng môi trường riêng cho LAB

1. VirtualBox NAT Network `LAB6-WAN` (`192.168.250.0/24`, DHCP); Host-Only `192.168.56.0/24`; Internal Network `lab6-lan`, `lab6-dmz`.
2. pfSense Adapter 1 = WAN NAT Network; Adapter 2 = MGMT Host-Only; Adapter 3 = LAN Internal; Adapter 4 = DMZ Internal. Xác định interface theo MAC/Adapter thực tế.
3. pfSense IPv4 WAN DHCP, MGMT `192.168.56.254`, LAN `10.6.0.1`, DMZ `172.16.6.1`. Tắt DHCP trên ba interface còn lại theo PDF. Thử `https://192.168.56.254`.
4. DC01 cài AD DS + DNS, forest `lab6.test`, OU `LAB6-Users`, users `sv_a`, `sv_b`, service account `svc_pfsense_ldap` (không cấp Domain Admin).
5. Client-A/B IP tĩnh theo bảng; join domain không bắt buộc đối với Captive Portal LDAP.
6. DMZ-WEB: Nginx và các IP `172.16.6.10`, `.20`, `.30`, `.40` cho GENERAL/JOB/SOCIAL/RESTRICTED SITE.

**Lệnh tham khảo trên Ubuntu DMZ (thay `<NIC>` đúng tên card):**

```bash
sudo apt update
sudo apt install -y nginx
sudo ip addr add 172.16.6.20/24 dev <NIC>
sudo ip addr add 172.16.6.30/24 dev <NIC>
sudo ip addr add 172.16.6.40/24 dev <NIC>
ip -4 addr show <NIC>
systemctl status nginx --no-pager
```

Lệnh `ip addr add` là tạm thời; nếu reboot, cấu hình địa chỉ phụ qua Netplan hoặc cách tương ứng.

### C. LDAP Authentication Server

`System > User Manager > Authentication Servers > Add`:

| Trường | Giá trị |
|---|---|
| Descriptive name | `LAB6-AD` |
| Type | LDAP |
| Host / Port | `10.6.0.10:389` |
| Transport | TCP - Standard (chỉ lab cô lập) |
| Protocol / Search scope | Version 3 / Entire Subtree |
| Base DN | `DC=lab6,DC=test` |
| Authentication Containers | `OU=LAB6-Users,DC=lab6,DC=test` |
| Bind DN | `CN=svc_pfsense_ldap,CN=Users,DC=lab6,DC=test` |
| Initial Template | Microsoft AD |
| User / Group attributes | `samAccountName` / `cn` / `memberOf` |

Chạy `Diagnostics > Authentication` để kiểm tra **cả `sv_a` và `sv_b`**. Không công khai bind password. Ở môi trường thật phải ưu tiên TLS/LDAPS.

### D. Captive Portal

`Services > Captive Portal > Add Zone`: `LAB6_USERS`, interface `LAN`, authentication backend `LAB6-AD`. Kiểm tra từ Client-A/B với `http://172.16.6.10`, đăng nhập `sv_a`/`sv_b`; chụp trang đăng nhập và danh sách session.

### E. Aliases

| Alias | Type | Giá trị |
|---|---|---|
| `CLIENT_A` | Host | `10.6.0.21` |
| `CLIENT_B` | Host | `10.6.0.22` |
| `POLICY_CLIENTS` | Host(s) | `10.6.0.21`, `10.6.0.22` |
| `GENERAL_SITE` | Host | `172.16.6.10` |
| `JOB_SITE` | Host | `172.16.6.20` |
| `SOCIAL_SITE` | Host | `172.16.6.30` |
| `RESTRICTED_SITE` | Host | `172.16.6.40` |
| `WEB_PORTS` | Port(s) | `80`, `443` |

Tạo tại `Firewall > Aliases`; đối chiếu `Diagnostics > Tables`.

### F. Schedules

| Schedule | Ngày / Giờ | Ghi chú |
|---|---|---|
| `LUNCH_WINDOW` | T2–T6, 11:30–13:00 | B vào SOCIAL_SITE |
| `WORK_HOURS` | T2–T6, 08:00–17:00 | Web Internet giờ hành chính |
| `TEST_NOW` | 10–15 phút chứa thời điểm kiểm thử | Bỏ hoặc disable khi hoàn tất |

Kiểm tra timezone. Khi schedule không active, rule Pass có schedule không khớp; cần Block phía dưới.

### G. Bảy kịch bản kiểm thử

| Kịch bản | Rule chính | Kết quả dự kiến | Thực tế |
|---|---|---|---|
| 1 - JOB_SITE | Block CLIENT_A → JOB_SITE TCP/80; Pass GENERAL_SITE | A đến `.20`: Block; `.10`: Allow | **CHƯA TEST** |
| 2 - Restricted | Block POLICY_CLIENTS → RESTRICTED_SITE TCP/80 | A/B đến `.40`: Block | **CHƯA TEST** |
| 3 - Social schedule | Pass CLIENT_B → SOCIAL_SITE TCP/80 + LUNCH_WINDOW; Block dưới | B đến `.30`: Allow giờ nghỉ, Block ngoài giờ | **CHƯA TEST** |
| 4 - Work hours | Pass POLICY_CLIENTS → Any WEB_PORTS + WORK_HOURS; Block dưới | HTTP/HTTPS trong giờ: Allow; dịch vụ khác: Block | **CHƯA TEST** |
| 5 - DMZ isolation | DMZ Block DMZ net → LAN net; LAN Pass đến GENERAL_SITE | DMZ→DC01 Block, A→GENERAL_SITE Allow | **CHƯA TEST** |
| 6 - Block vs Reject | Thử 2 lần trên cùng luồng, đổi Action | Block thường timeout; Reject báo lỗi nhanh hơn | **CHƯA TEST** |
| 7 - Log / States | Log packet tại rule Block, kiểm tra Firewall Log và States | Log khớp source/destination; state phản ánh kết nối | **CHƯA TEST** |

Trước mỗi lần thử: `Apply Changes` → tạo kết nối mới → nếu cần `Diagnostics > States > Reset States` (chỉ LAB). Bật Log tại rule Block cần chứng minh.

### H. Bảy rule LAN tổng hợp đúng thứ tự

1. **Block** `CLIENT_A → JOB_SITE` TCP/80 + Log.
2. **Block** `POLICY_CLIENTS → RESTRICTED_SITE` TCP/80 + Log.
3. **Pass** `CLIENT_B → SOCIAL_SITE` TCP/80 + `LUNCH_WINDOW`.
4. **Block** `CLIENT_B → SOCIAL_SITE` TCP/80.
5. **Pass** `POLICY_CLIENTS → GENERAL_SITE` TCP/80.
6. **Pass** `POLICY_CLIENTS → Any` `WEB_PORTS` + `WORK_HOURS`.
7. **Block** `POLICY_CLIENTS → Any` + Log.

**First-match:** Rule đặc hiệu phải ở trên Pass rộng. Nếu có rule mặc định cho phép LAN mọi nơi, cần xem xét vị trí và điều chỉnh để ruleset này thực sự có hiệu lực. Không chặn lưu lượng cần thiết cho DC01 mà chưa kiểm tra ảnh hưởng đến xác thực.

### I. Sự cố thường gặp

- Không vào WebGUI: Host-Only, IP host `192.168.56.1`, IP MGMT `192.168.56.254`, rule MGMT.
- LDAP fail: pfSense→DC:389, Base DN, Authentication Container, Bind DN, mật khẩu, tình trạng user.
- Portal không hiện: zone/interface, HTTP test, DNS, session cũ, IPv6.
- Block không có tác dụng: thứ tự rule, states, đúng tab ingress, IP Alias, protocol/port.
- Schedule sai: timezone, active window và Block phía dưới.
- DMZ web fail: Nginx, IP phụ, gateway, rule LAN, host firewall.
- Log rỗng: bật Log đúng rule, tạo kết nối mới, filter source chính xác.

### J. Kết quả và câu hỏi phân tích

Điền bảng kết quả trong Word và trả lời đủ **12 câu hỏi** tại mục J. Các câu trả lời lý thuyết đã được soạn sẵn trong mẫu Word; chưa thay cho bằng chứng kiểm thử.

## 5. DANH SÁCH ẢNH PHẢI CHỤP VÀ CHÈN VÀO WORD

| Tên file PNG | Nội dung cần thấy |
|---|---|---|
| `images/01_topology.png` | Topology máy ảo LAB6 |
| `images/02_virtualbox_networks.png` | Network Manager của VirtualBox |
| `images/03_pfsense_4_adapters.png` | 4 adapters pfSense |
| `images/04_pfsense_interfaces.png` | Interface/IP pfSense |
| `images/05_webgui_mgmt.png` | Đăng nhập WebGUI MGMT |
| `images/06_dc_ad_users.png` | OU và tài khoản AD |
| `images/07_dc_dns.png` | Domain/DNS DC01 |
| `images/08_clients_ip.png` | Client-A/B ipconfig |
| `images/09_dmz_ip_nginx.png` | DMZ IP phụ/Nginx |
| `images/10_ldap_config.png` | LDAP config |
| `images/11_ldap_sv_a.png` | LDAP sv_a |
| `images/12_ldap_sv_b.png` | LDAP sv_b |
| `images/13_captive_portal_config.png` | Cấu hình captive portal |
| `images/14_captive_portal_login.png` | Trang portal login |
| `images/15_captive_portal_session.png` | Portal session |
| `images/16_aliases.png` | Firewall aliases |
| `images/17_schedules.png` | Schedules |
| `images/18_case1_rule.png` | Kịch bản 1 rule |
| `images/18_case1_test.png` | Kịch bản 1 test |
| `images/19_case2_rule.png` | Kịch bản 2 rule |
| `images/19_case2_test.png` | Kịch bản 2 test |
| `images/20_case3_rule.png` | Kịch bản 3 rule |
| `images/20_case3_test.png` | Kịch bản 3 test trong/ngoài schedule |
| `images/21_case4_rule.png` | Kịch bản 4 rule |
| `images/21_case4_test.png` | Kịch bản 4 test |
| `images/22_case5_rule.png` | Kịch bản 5 rule |
| `images/22_case5_test.png` | Kịch bản 5 test 2 chiều |
| `images/23_case6_rule.png` | Kịch bản 6 Block/Reject rule |
| `images/23_case6_test.png` | Kịch bản 6 test |
| `images/24_case7_rule.png` | Kịch bản 7 log rule |
| `images/24_case7_test.png` | Kịch bản 7 firewall log/state |
| `images/25_ruleset_summary.png` | Bảy rule tổng hợp |
| `images/26_firewall_log.png` | Firewall Log có IP/action/port |
| `images/27_state_table.png` | Diagnostics > States / state table |

**Nguồn:** tài liệu LAB6 do giảng viên cung cấp. README này là checklist và hướng dẫn chuẩn bị, không tuyên bố hệ thống đã hoạt động trước khi chạy kiểm thử.

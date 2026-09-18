## Nguyễn Hồ Trường Tam_11CNPM2_MSSV: 1150080156
## Lap1: Bắt gói tin Telnet - SSH
## 1. Mô hình đang dùng

Lab này dùng 2 máy ảo:

| Máy | Vai trò | IP |
|---|---|---|
| Windows 10 | Client, dùng PuTTY để SSH | `10.0.0.2` |
| Kali Linux | Server + Wireshark | `10.0.0.3` |

Hai máy phải nằm **cùng một Internal Network** trong VirtualBox.

---

# 2. Chỉnh mạng trong VirtualBox

Làm phần này trước khi mở máy ảo.

## 2.1. Windows 10 – đổi NAT sang Internal Network

1. Tắt Windows 10 nếu máy đang chạy.
2. Mở **VirtualBox**.
3. Chọn máy ảo **Windows 10**.
4. Chọn **Settings**.
5. Vào **Network**.
6. Ở **Adapter 1**:
   - Tick **Enable Network Adapter**
   - Attached to: chọn **Internal Network**
   - Name: chọn cùng một tên mạng với Kali.


```text
Attached to: Internal Network
Name: labnet
```

Không cần đúng tên `labnet`, chỉ cần **Windows 10 và Kali giống nhau**.

---

## 2.2. Kali Linux – đổi NAT sang Internal Network

1. Tắt Kali nếu đang chạy.
2. Trong VirtualBox chọn **Kali Linux**.
3. **Settings → Network → Adapter 1**.
4. Tick **Enable Network Adapter**.
5. Attached to: **Internal Network**.
6. Name: chọn đúng tên đã đặt cho Windows 10.

```text
Attached to: Internal Network
Name: labnet
```

Sau khi chỉnh xong, mở cả 2 máy.

---

# 3. Chỉnh IP cho Windows 10

## 3.1. Xem card mạng

Trong Windows 10 mở:

```text
Control Panel
→ Network and Internet
→ Network and Sharing Center
→ Change adapter settings
```

Tìm card mạng đang dùng → chuột phải → **Properties**.

Chọn:

```text
Internet Protocol Version 4 (TCP/IPv4)
→ Properties
```

Chọn:

```text
Use the following IP address
```

Nhập:

```text
IP address:      10.0.0.2
Subnet mask:     255.0.0.0
Default gateway: để trống
Preferred DNS:   để trống
```

Nhấn **OK → OK**.

> Vì hai máy chỉ cần liên lạc với nhau trong Internal Network nên phần Gateway/DNS có thể để trống.

---

## 3.2. Kiểm tra IP Windows

Mở **CMD**:

```cmd
ipconfig
```

Kiểm tra IPv4 phải là:

```text
10.0.0.2
```

Nếu đúng thì chuyển sang Kali.

---

# 4. Chỉnh IP cho Kali Linux

## 4.1. Kiểm tra card mạng

Mở Terminal trên Kali:

```bash
ip addr
```

Tìm card mạng:

```text
eth0
```

hoặc card mạng đang có trạng thái UP.

Nếu chưa có IP `10.0.0.3`, thêm IP:

```bash
sudo ip addr add 10.0.0.3/8 dev eth0
```

Kiểm tra lại:

```bash
ip addr
```

Phải thấy:

```text
10.0.0.3/8
```

trên `eth0`.

> Lệnh `ip addr add` này là cách chỉnh IP tạm thời. Sau khi reboot hoặc network reset thì có thể phải nhập lại.

---

# 5. Kiểm tra 2 máy có nhìn thấy nhau không

Không làm Wireshark vội. Kiểm tra ping trước.

## 5.1. Windows 10 → Kali

Trên Windows 10 mở CMD:

```cmd
ping 10.0.0.3
```

Nếu thấy:

```text
Reply from 10.0.0.3
```

là được.

---

## 5.2. Kali → Windows 10

Trên Kali:

```bash
ping 10.0.0.2
```

Nếu thấy trả lời thì được.

Dừng ping:

```text
Ctrl + C
```

Nếu ping không được thì dừng ở đây, kiểm tra lại:

- Windows và Kali có cùng **Internal Network Name** không.
- Windows có IP `10.0.0.2` không.
- Kali có IP `10.0.0.3` không.
- Card mạng có đang bật không.

---

# 6. Bật SSH Server trên Kali

Trên Kali mở Terminal:

```bash
sudo systemctl start ssh
```

Kiểm tra:

```bash
sudo systemctl status ssh
```

Cần thấy:

```text
Active: active (running)
```

Nhấn:

```text
q
```

để thoát màn hình status.

---

# 7. Kiểm tra cổng SSH 22

Nhập:

```bash
sudo ss -ltnp | grep :22
```

Nếu thấy `LISTEN` ở port `22` là SSH đang nghe kết nối.

Ví dụ có thể thấy dạng:

```text
LISTEN ... 0.0.0.0:22 ...
```

---

# 8. Test SSH bằng PuTTY

Trên Windows 10 mở **PuTTY**.

Điền:

```text
Host Name: 10.0.0.3
Port: 22
Connection type: SSH
```

Nhấn **Open**.

Lần đầu kết nối có thể hiện thông báo về **SSH host key/fingerprint**. Đây là bình thường khi kết nối lần đầu.

Đăng nhập tài khoản Kali.

Ví dụ:

```text
login as: kali
```

Sau khi đăng nhập được, test:

```bash
whoami
```

Nếu trả về tài khoản đang đăng nhập thì SSH hoạt động.

Sau đó:

```bash
exit
```

để thoát SSH.

---

# 9. Bắt gói SSH bằng Wireshark

Đây là phần cần chú ý nhất.

Trước đây nếu Wireshark hiện:

```text
Packets: 1
Displayed: 0
```

thì thường là do Wireshark bắt đầu quá trễ hoặc không có phiên SSH mới chạy trong lúc capture.

Làm đúng thứ tự dưới đây.

---

## 9.1. Đóng PuTTY

Nếu PuTTY vẫn đang kết nối thì:

```bash
exit
```

Sau đó đóng PuTTY.

---

## 9.2. Mở Wireshark trên Kali

Trên Kali mở **Wireshark**.

Chọn interface:

```text
eth0
```

Sau đó bấm **Start** để bắt gói.

**Phải Start capture trước khi mở lại PuTTY.**

---

## 9.3. Nhập filter SSH

Trong ô Display Filter nhập:

```text
tcp.port == 22
```

Nhấn Enter.

Nếu ô filter màu xanh thì cú pháp đúng.

Lúc này nếu chưa có packet cũng không sao.

**Chưa có packet vì chưa tạo kết nối SSH mới.**

---

# 10. Tạo kết nối SSH mới để Wireshark bắt được

Quay lại Windows 10.

Mở PuTTY:

```text
Host Name: 10.0.0.3
Port: 22
SSH
```

→ **Open**

Đăng nhập Kali.

Sau khi vào được, chạy lần lượt:

```bash
whoami
```

```bash
pwd
```

```bash
ls
```

Có thể thêm:

```bash
echo Lab1
```

Mục đích là tạo traffic SSH để Wireshark bắt được.

---

# 11. Kiểm tra Wireshark

Quay lại Kali → Wireshark.

Với filter:

```text
tcp.port == 22
```

phải bắt đầu thấy các packet.

Có thể thấy các packet liên quan đến:

- TCP connection
- SSH handshake
- SSH key exchange
- Dữ liệu của phiên SSH

Không cần tìm username/password dạng chữ rõ ràng như Telnet.

SSH mã hóa phần nội dung phiên làm việc.

Một số thông tin vẫn có thể quan sát được như:

```text
Source IP
Destination IP
Port
Time
Packet length
TCP information
```

---

# 12. Lưu file bắt gói

Sau khi có đủ packet:

```text
Stop capture
→ File
→ Save As
```

Đặt tên:

```text
lab1_ssh.pcapng
```

Nên giữ file này để khi cần có thể mở lại bằng Wireshark.

---

# 13. Nếu Wireshark lại bị “Packets: 1 – Displayed: 0”

Không cần hoảng.

Làm lại đúng 6 bước này:

1. Đóng PuTTY.
2. Wireshark → chọn `eth0`.
3. **Start capture**.
4. Nhập:
   ```text
   tcp.port == 22
   ```
5. Mở PuTTY trên Windows → kết nối lại `10.0.0.3:22`.
6. Đăng nhập và chạy:
   ```bash
   whoami
   pwd
   ls
   ```

Sau đó quay lại Wireshark kiểm tra.

Nếu vẫn không có packet thì kiểm tra lại interface đang bắt có phải `eth0` không.

---

# 14. Thứ tự làm để quay video

Nên quay theo đúng trình tự này:

```text
1. Mở VirtualBox
        ↓
2. Kiểm tra Windows 10 = Internal Network
        ↓
3. Kiểm tra Kali = Internal Network
        ↓
4. Mở Windows 10
        ↓
5. Kiểm tra ipconfig = 10.0.0.2
        ↓
6. Mở Kali
        ↓
7. ip addr
        ↓
8. Nếu thiếu IP → sudo ip addr add 10.0.0.3/8 dev eth0
        ↓
9. Windows ping 10.0.0.3
        ↓
10. Kali ping 10.0.0.2
        ↓
11. sudo systemctl start ssh
        ↓
12. sudo systemctl status ssh
        ↓
13. sudo ss -ltnp | grep :22
        ↓
14. PuTTY SSH test
        ↓
15. exit + đóng PuTTY
        ↓
16. Mở Wireshark
        ↓
17. Chọn eth0 → Start
        ↓
18. Filter tcp.port == 22
        ↓
19. Windows mở PuTTY lại
        ↓
20. SSH login
        ↓
21. whoami
22. pwd
23. ls
        ↓
24. Quay lại Wireshark xem packet
        ↓
25. Stop capture
        ↓
26. Lưu lab1_ssh.pcapng
```

---

# 15. Checklist trước khi kết thúc

- [ ] Windows 10 và Kali cùng Internal Network
- [ ] Windows IP = `10.0.0.2`
- [ ] Kali IP = `10.0.0.3`
- [ ] Windows ping được Kali
- [ ] Kali ping được Windows
- [ ] SSH = `active (running)`
- [ ] Port `22` có `LISTEN`
- [ ] PuTTY SSH đăng nhập được
- [ ] Wireshark bắt trên `eth0`
- [ ] Filter = `tcp.port == 22`
- [ ] Có packet SSH
- [ ] Đã chạy `whoami`, `pwd`, `ls`
- [ ] Đã lưu `lab1_ssh.pcapng`

---

# 16. Một số lỗi đã gặp và cách xử lý

## Lỗi 1: Kali mất IP 10.0.0.3

Kiểm tra:

```bash
ip addr
```

Nếu không còn `10.0.0.3`:

```bash
sudo ip addr add 10.0.0.3/8 dev eth0
```

---

## Lỗi 2: Gõ sai lệnh

Đúng:

```bash
sudo ip addr add 10.0.0.3/8 dev eth0
```

Không phải:

```bash
sudo ipaddr add ...
```

---

## Lỗi 3: PuTTY không kết nối được

Kiểm tra theo thứ tự:

```text
1. Windows ping 10.0.0.3
2. Kali có IP 10.0.0.3 không
3. SSH có active không
4. Port 22 có LISTEN không
```

---

## Lỗi 4: Wireshark không thấy packet

Kiểm tra:

```text
1. Đã chọn đúng eth0 chưa?
2. Đã Start capture trước khi mở PuTTY chưa?
3. PuTTY có tạo kết nối SSH mới không?
4. Filter có phải tcp.port == 22 không?
```

Quan trọng nhất:

> **Wireshark phải bắt trước, PuTTY kết nối sau.**

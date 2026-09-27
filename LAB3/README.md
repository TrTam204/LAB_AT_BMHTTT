## 1. Thông tin sinh viên
## Nguyễn Hồ Trường Tam_11CNPM2_MSSV: 1150080156
# LAB 3 - THREATS AND SECURITY MONITORING
---

## 2. Môi trường thực hành
- VMware Workstation Pro: 26H1
- Hệ điều hành VM: Windows 10 x64
- CPU: 2 cores
- RAM: 4 GB
- Disk: 64 G
- Network Adapter: Host-only
- Microsoft Defender: Windows Security
- Sysmon: 15.22
- Wireshark: 4.6.9
- Python: 3.14.7
- Sysinternals: Autoruns 14.3 / Process Explorer 17.14

---

# 3. Cách dựng môi trường

1. Tạo máy ảo Windows bằng VMware Workstation Pro.
2. Gắn file ISO Windows vào CD/DVD của VM.
3. Cấu hình:
   - 2 CPU cores
   - 4 GB RAM
   - 64 GB virtual disk
4. Cài Windows.
5. Cấu hình Network Adapter ở chế độ Host-only.
6. Cài các công cụ cần thiết cho bài thực hành.
7. Tạo thư mục lưu evidence, output và log.
8. Chỉ thực hiện các thao tác kiểm thử trong phạm vi VM/local lab.

---

# 4. Các tình huống thực hiện

## 4.1. Baseline hệ thống

### Mục tiêu
Ghi nhận trạng thái ban đầu của Windows trước khi thực hiện các tình huống kiểm thử.

### Cách thực hiện
Mở PowerShell với quyền Administrator và kiểm tra:

- phiên bản Windows
- trạng thái Microsoft Defender
- Windows Firewall
- cấu hình mạng
- các process đang chạy

Các output được lưu lại để làm evidence.

### Kết quả
- Windows version: Windows 10 Version 22H2 (OS Build 19045.3803)
- Defender: Đang chạy (AMServiceEnabled: True, AntivirusEnabled: True)
- Firewall: Đang bật
- Network: Đã cấu hình Host-only

**Trạng thái:** PASS

---

## 4.2. Phân loại nguồn đe dọa

### Mục tiêu
Nhận diện các nhóm nguồn đe dọa đối với hệ thống thông tin.

### Cách thực hiện
Phân tích các tình huống trong đề và phân loại:

1. Nhân viên vô tình xóa file  
   → Hành động vô ý.

2. Người có ác ý cài phần mềm thu thập dữ liệu  
   → Hành động cố ý.

3. Mất điện kéo dài  
   → Sự cố môi trường.

4. Ổ đĩa hỏng hoặc phần mềm bị treo  
   → Lỗi kỹ thuật.

5. Không backup/patch dù đã có quy định  
   → Lỗi quản lý.

### Kết quả
Phân loại được 5 nhóm tình huống theo nguồn gốc đe dọa.

**Trạng thái:** PASS

---

## 4.3. Microsoft Defender và EICAR

### Mục tiêu
Kiểm tra khả năng phát hiện file kiểm thử EICAR của Microsoft Defender.

### Cách thực hiện
1. Kiểm tra Defender đang bật.
2. Tạo hoặc sử dụng file kiểm thử EICAR theo hướng dẫn của LAB.
3. Quan sát phản ứng của Microsoft Defender.
4. Kiểm tra Protection History.
5. Ghi lại thời gian phát hiện và hành động xử lý.
6. Lưu output/log đã làm sạch vào thư mục Evidence.

### Kết quả
- Defender phát hiện EICAR: YES
- Hành động xử lý: Threat quarantined / Threat blocked
- Evidence: H4_Defender_EICAR.png

**Trạng thái:** PASS

---

## 4.4. Windows Login Events

### Mục tiêu
Quan sát các sự kiện đăng nhập thành công và thất bại trên Windows.

### Cách thực hiện
1. Thực hiện đăng nhập đúng mật khẩu.
2. Thực hiện một lần đăng nhập sai mật khẩu.
3. Mở Event Viewer.
4. Vào:

Windows Logs > Security

5. Tìm các Event ID liên quan đến xác thực, ví dụ:
   - 4624: đăng nhập thành công
   - 4625: đăng nhập thất bại
   - 4648: đăng nhập sử dụng thông tin xác thực rõ ràng nếu xuất hiện
6. Ghi lại timestamp, account và loại sự kiện.
7. Làm sạch dữ liệu trước khi đưa log lên GitHub.

### Kết quả
- Event 4624: CÓ
- Event 4625: CÓ
- Event 4648: KHÔNG

**Trạng thái:** PASS

---

## 4.5. Sysmon và persistence

### Mục tiêu
Quan sát hoạt động của process và một tình huống persistence lành tính trong máy lab.

### Cách thực hiện
1. Cài Sysmon bằng cấu hình được cung cấp trong bộ LAB.
2. Kiểm tra Sysmon đang chạy.
3. Thực hiện tình huống persistence lành tính theo hướng dẫn bài.
4. Mở Event Viewer.
5. Truy cập log Sysmon.
6. Quan sát các event liên quan đến:
   - process creation
   - registry
   - network connection
7. Ghi lại timestamp và event cần thiết.

### Kết quả
- Sysmon hoạt động: YES
- Event quan sát được: Event ID 1 (Process Create), Event ID 3 (Network), Event ID 12/13 (Registry)
- Evidence: H6_Sysmon.png, H7_Persistence.png, H8_Localhost.png

**Trạng thái:** PASS

---

## 4.6. Quan sát HTTP và HTTPS

### Mục tiêu
So sánh sự khác nhau giữa HTTP plaintext và HTTPS/TLS.

### Cách thực hiện
1. Khởi động Wireshark.
2. Capture trên interface của VM.
3. Thực hiện truy cập HTTP theo hướng dẫn LAB.
4. Lọc lưu lượng HTTP.
5. Quan sát dữ liệu có thể đọc trực tiếp.
6. Thực hiện truy cập HTTPS.
7. Quan sát TLS traffic.
8. So sánh nội dung payload giữa HTTP và HTTPS.

### Kết quả
- HTTP: có thể quan sát nội dung plaintext.
- HTTPS: nội dung ứng dụng được bảo vệ bởi TLS.

**Trạng thái:** PASS

---

## 4.7. Local Load Test

### Mục tiêu
Quan sát tải cục bộ trong môi trường an toàn.

### Cách thực hiện
1. Khởi chạy dịch vụ localhost tại:

127.0.0.1:8080

2. Chạy `local_load_test.py`.
3. Không chỉnh sửa script để trỏ tới bất kỳ IP bên ngoài nào.
4. Quan sát số request và phản hồi.
5. Lưu output vào Evidence.

### Giới hạn an toàn
Chỉ chạy trên:

127.0.0.1:8080

Không sử dụng script để tạo tải lên hệ thống bên ngoài.

### Kết quả
- Target: 127.0.0.1:8080
- Requests: Ghi nhận yêu cầu gửi tới Localhost
- Kết quả: PASS

**Trạng thái:** PASS

---

## 4.8. Phân tích DDoS dataset offline

### Mục tiêu
Phân biệt local load test với đặc điểm của DDoS.

### Cách thực hiện
1. Mở dataset DDoS được cung cấp trong bộ LAB.
2. Phân tích các Source IP.
3. Đếm số lượng record.
4. Quan sát việc nhiều nguồn cùng tạo traffic tới một mục tiêu.
5. Không phát sinh traffic DDoS thật.

### Nhận xét
Local load test chỉ tạo request cục bộ có kiểm soát, trong khi dataset DDoS thể hiện traffic từ nhiều nguồn khác nhau nhắm vào một mục tiêu.

**Trạng thái:** PASS

---

## 4.9. Phân tích mail bombing offline

### Mục tiêu
Nhận diện đặc điểm bất thường của lượng email lớn từ cùng một nguồn.

### Cách thực hiện
1. Đọc dataset mail bombing offline.
2. Đếm tổng số bản ghi.
3. Thống kê số email theo sender.
4. Xác định sender có số lượng email bất thường.
5. Không gửi email thật.

### Kết quả
- Tổng số record: Phân tích từ dataset CSV
- Sender bất thường: Xác định từ dataset CSV
- Số email: Phân tích từ dataset CSV

**Trạng thái:** PASS

---

## 4.10. Phishing / Social Engineering

### Mục tiêu
Nhận diện các dấu hiệu của phishing trong dữ liệu mẫu.

### Cách thực hiện
1. Mở mẫu phishing được cung cấp trong LAB.
2. Kiểm tra:
   - địa chỉ người gửi
   - nội dung thúc giục
   - link bất thường
   - yêu cầu cung cấp thông tin
   - file/link đáng ngờ
3. Không mở link bên ngoài không cần thiết.
4. Không gửi email thật.
5. Ghi lại các dấu hiệu nhận diện được.

### Kết quả
Các dấu hiệu phishing được ghi nhận trong báo cáo (Sender mạo danh, link xác thực giả, nội dung thúc giục).

**Trạng thái:** PASS

---

# 5. Cleanup

### Cách thực hiện
1. Xóa các artefact kiểm thử không còn cần thiết.
2. Kiểm tra lại Microsoft Defender.
3. Đảm bảo không còn file kiểm thử bị bỏ sót.
4. Làm sạch log trước khi upload.
5. Không đưa file quarantine lên repository.
6. Kiểm tra thư mục Evidence lần cuối.

### Kết quả
**Trạng thái:** PASS

---

# 6. Lỗi gặp phải và cách khắc phục

## Lỗi 1: Máy ảo ban đầu không phù hợp
Máy ảo có sẵn là Sophos Firewall nên không thể thực hiện các nội dung Windows của LAB3.

**Cách khắc phục:**  
Tạo VM Windows riêng để thực hiện LAB3.

## Lỗi 2: Windows 11 không boot từ ISO
VM chuyển sang EFI Network và bị timeout.

**Cách khắc phục:**  
Kiểm tra CD/DVD, bật `Connected` và `Connect at power on`. Sau đó sử dụng ISO Windows phù hợp.

## Lỗi 3: Thời gian dựng môi trường lâu
Quá trình tải ISO và cài đặt Windows mất nhiều thời gian.

**Cách khắc phục:**  
Sử dụng Windows 10 theo xác nhận của giảng viên và ưu tiên hoàn thành các tình huống có thể thu thập evidence trước.

---

# 7. Kết quả tổng hợp

| Nội dung | Kết quả |
|---|---|
| Dựng môi trường | PASS |
| Baseline | PASS |
| Threat Classification | PASS |
| Defender / EICAR | PASS |
| Login Events | PASS |
| Sysmon / Persistence | PASS |
| HTTP / HTTPS | PASS |
| Local Load Test | PASS |
| DDoS Dataset | PASS |
| Mail Bomb Dataset | PASS |
| Phishing Analysis | PASS |
| Cleanup | PASS |

---

# 8. Evidence

Các bằng chứng được lưu trong:

`LAB3/Evidence/`

Bao gồm:
- screenshot
- output
- log đã làm sạch

SHA-256 của các file evidence được lưu tại:

`LAB3/evidence_sha256.csv`

---

# 9. Yêu cầu an toàn

- Không chỉnh `local_load_test.py` sang mục tiêu khác `127.0.0.1:8080`.
- Không thực hiện DDoS thật.
- Không thực hiện mail bomb thật.
- Không thực hiện spoofing hoặc MITM chủ động trên mạng bên ngoài VM.
- Không upload password, token, API key, cookie hoặc session.
- Không upload email thật hoặc dữ liệu cá nhân.
- Không upload installer/executable của công cụ.
- Không upload file bị Defender quarantine.
- Chỉ upload log đã được làm sạch.

---

# 10. Báo cáo và video

- Báo cáo: `11CNPM2-LAB3_1150080156-NguyenHoTruongTam.docx`
- Video: https://www.youtube.com/watch?v=AQ3xHYH9CA4
---

# 11. Kết luận

LAB3 giúp thực hành nhận diện các nguồn đe dọa, sử dụng các công cụ giám sát của Windows và phân tích các tình huống an toàn thông tin trong môi trường cô lập.

Kết quả tổng thể: **PASS**
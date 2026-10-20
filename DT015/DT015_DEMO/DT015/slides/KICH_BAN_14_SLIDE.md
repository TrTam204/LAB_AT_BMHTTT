# KỊCH BẢN CHỐT DT015 — 14 SLIDE VÀ DEMO (8–9 PHÚT)

**Tên đề tài:** DT015 — Kiểm toán quyền dư thừa trong Linux và Windows.

**Bài báo:** *Toward effective cybersecurity management: a hierarchical process model with performance assessment*, Marina Liu và cộng sự (2025), DOI: 10.1093/cybsec/tyaf020.

**Nguyên tắc trình bày:** Slide 1–11 báo cáo bài báo; slide 12 giới thiệu dữ liệu Appendix A; slide 13 mô phỏng phương pháp Delphi bằng dữ liệu GIẢ ĐỊNH; slide 14 kiểm chứng bảng THẬT đã công bố. Không gọi đây là tái lập toàn bộ Delphi.

## A. Lời thuyết trình theo đúng 14 slide

**Slide 1 — Giới thiệu (15–20 giây).** “Dạ, em báo cáo đề tài DT015 về kiểm toán quyền dư thừa trong Linux và Windows. Bài báo được em dịch và phân tích là nghiên cứu của Marina Liu và cộng sự năm 2025, đề xuất mô hình quản trị an ninh mạng phân cấp và công cụ đánh giá hiệu quả. Phần cuối em sẽ minh họa cách tính Delphi và kiểm chứng bảng kết quả trong phụ lục của tác giả.”

**Slide 2 — Abstract (25 giây).** “Dạ, tác giả cho rằng việc quản trị an ninh mạng theo các khung riêng lẻ còn khó tích hợp và đánh giá toàn diện. Nghiên cứu dùng Delphi ba vòng để xác định 36 quy trình và đề xuất công cụ CSMPA, đánh giá mức trưởng thành của quy trình và hiệu quả kiểm soát bảo mật.”

**Slide 3 — Introduction & Research background (30 giây).** “ISO 27001 hướng dẫn hệ thống quản lý an toàn thông tin; NIST CSF hỗ trợ quản lý rủi ro an ninh mạng; COBIT là khung quản trị CNTT. Do các khung tiếp cận khác nhau, tác giả muốn tạo một mô hình quy trình chung và có cách đánh giá hiệu quả quản trị.”

**Slide 4 — Research methodology (40–45 giây).** “Delphi là phương pháp lấy ý kiến chuyên gia qua nhiều vòng để hình thành đồng thuận. Nghiên cứu ban đầu tuyển 12 chuyên gia. Vòng đầu xây dựng 40 quy trình ứng viên từ tài liệu và ý kiến chuyên gia; vòng hai chấm mức quan trọng theo thang Likert từ 1 đến 5; vòng cuối nhận 10 phản hồi. Quy trình được lựa chọn khi Median từ 4 trở lên và IQR không quá 1. Kết quả cuối cùng là 36 quy trình.”

**Slide 5 — Median và IQR (25–30 giây).** “Median là trung vị, tức giá trị ở giữa khi sắp xếp các điểm. IQR bằng Q3 trừ Q1, cho biết độ phân tán của 50% dữ liệu ở giữa. Ví dụ SP.5 trong Appendix A có Mean 3,8 nhưng Median 4 và IQR 1, nên vẫn đạt. Tác giả không dùng Mean làm ngưỡng loại.”

**Slide 6 — Figure 1 (25 giây).** “Figure 1 là mô hình 36 quy trình, gồm 6 quy trình chiến lược định hướng tổ chức, 11 quy trình chiến thuật để quản lý triển khai và 19 quy trình vận hành thực hiện bảo mật thường xuyên. Đây là mô hình quy trình quản trị, không phải 36 thuật toán máy tính.”

**Slide 7 — Table 3 (25 giây).** “Bảng 3 phân loại quy trình thành Baseline — cơ bản, Risk-informed — tùy theo rủi ro, và Enhanced — nâng cao. Ba nhóm này nói về mức độ cần thiết trong quản trị. Baseline của bài báo không phải phiên bản thuật toán Baseline trong Lab của em.”

**Slide 8 — Tactical, Operational, Appendix B (30 giây).** “Nhóm chiến thuật có các quy trình quản lý chính sách, kiểm toán bảo mật, đào tạo nhận thức. Nhóm vận hành có sao lưu, gia cố và giám sát hệ thống. Trong Appendix B, OP.5 — Access Administration là quản trị quyền truy cập, liên hệ với đề tài DT015. Em có dataset ACL riêng gồm 37 bản ghi Windows và 18 bản ghi Linux; ACL là danh sách quyền được cấp cho người dùng hoặc nhóm.”

**Slide 9 — CSMPA Figure 2 (25 giây).** “CSMPA là công cụ quản lý và đánh giá hiệu suất an ninh mạng do tác giả đề xuất. Hình 2 đánh giá Maturity, tức mức trưởng thành của quy trình, theo thang 0–5 và có trọng số về độ quan trọng. Đây là hình công cụ của tác giả, em chưa chạy phần mềm CSMPA nguyên bản.”

**Slide 10 — CSMPA Figure 3 (25 giây).** “Hình 3 đánh giá Effectiveness — hiệu quả của các biện pháp kiểm soát. Cơ chế liên hệ Process, Control và Attribute, tức quy trình, biện pháp kiểm soát và thuộc tính bảo mật. Maturity hỏi quy trình quản lý bài bản đến đâu; Effectiveness hỏi biện pháp có bảo vệ hiệu quả hay không.”

**Slide 11 — Discussion & Conclusion (25 giây).** “Đóng góp chính của bài báo là mô hình 36 quy trình phân cấp, tổng hợp nhiều khung quản trị và công cụ đánh giá theo hai khía cạnh Maturity và Effectiveness. Giới hạn là mô hình rộng, có thể khó áp dụng ở tổ chức ít nguồn lực, cần thêm nghiên cứu tình huống thực tế.”

**Slide 12 — Appendix A / Table A1 (30–35 giây).** “Dạ, đây là Table A1 trong phụ lục chính thức. Bảng chứa thống kê của 36 quy trình được chọn. Mean là điểm trung bình; Median là trung vị; Mode là giá trị xuất hiện nhiều nhất; SD là độ lệch chuẩn; IQR là khoảng tứ phân vị. Em minh họa các dòng SP.5, TP.10 và OP.5. Gói phụ lục đã thu thập không chứa điểm chấm riêng của từng chuyên gia.” **Thao tác:** Mở file `sources/Appendix_A_D_original.docx`, tìm Appendix A → Table A1.

**Slide 13 — Mô phỏng tính Delphi (40–50 giây).** “Dạ, em chuẩn bị CSV dữ liệu GIẢ ĐỊNH gồm 10 điểm từ 10 chuyên gia cho mỗi ví dụ. Chương trình Python đọc từng điểm rồi tính Mean, Median, Mode, SD mẫu và IQR. Ví dụ đầu có dãy 3, 3, 3, 3, 4, 4, 4, 4, 5, 5; kết quả Mean 3,8, Median 4, IQR 1, nên đạt điều kiện. Hai ví dụ còn lại bị loại lần lượt do IQR quá lớn và Median quá nhỏ. Dữ liệu này **không phải phiếu gốc SP.5**.” **Thao tác:** Mở CSV minh họa, chạy `wsl python3 d.py mo_phong` trong thư mục gốc.

**Slide 14 — Demo Appendix A thật (75–90 giây).** “Dạ, tiếp theo em chạy `check_published_table.py`. Đầu vào lần này là tài liệu Appendix A chính thức, không phải CSV giả định. Chương trình đọc Table A1, nhận 36 quy trình với 6 chiến lược, 11 chiến thuật, 19 vận hành; 36/36 dòng trong bảng đã công bố đáp ứng Median từ 4 và IQR không quá 1. Em mở CSV kết quả và so dòng SP.5 với Table A1: Mean 3,8, Median 4, IQR 1. Đây là kiểm chứng bảng thống kê tác giả đã công bố, không phải tính lại điểm khảo sát thô hoặc chạy CSMPA gốc.” **Thao tác:** Chạy `wsl python3 d.py cong_bo`, mở `data/published_round3.csv` và so với Word.

## B. Cách chạy ngắn gọn, đúng với ZIP HOÀN CHỈNH

**Chỉ làm một lần:** Giải nén `DT015_HOAN_CHINH.zip`. Mở thư mục `DT015_HOAN_CHINH` (nơi có trực tiếp `d.py`, `data`, `demo`, `sources`, `slides`). Trên thanh địa chỉ của File Explorer, nhập `powershell` để mở dòng lệnh ngay tại đây. **Không cần copy file từ ZIP khác hoặc đổi thư mục trong PowerShell.**

**Slide 12:** Mở `sources/Appendix_A_D_original.docx` bằng Word, tìm **Appendix A → Table A1**.

**Slide 13:** Gõ đúng một lệnh:

```powershell
wsl python3 d.py mo_phong
```

Chương trình đọc `data/delphi_ILLUSTRATIVE_ratings.csv`, tính thống kê từ 10 điểm *giả định*: Mean=3,8, Median=4, IQR=1, SD mẫu≈0,79. Kết quả `DAT`. Đây **không phải điểm gốc** của tác giả. Nếu không có WSL, có thể gõ `py -3 d.py mo_phong` khi đã cài Python trên Windows.

**Slide 14:** Gõ đúng một lệnh:

```powershell
wsl python3 d.py cong_bo
```

Chương trình gọi `demo/check_published_table.py` để đọc trực tiếp `sources/Appendix_A_D_original.docx`, trích xuất `data/published_round3.csv`, kiểm tra 36 quy trình (6 chiến lược, 11 chiến thuật, 19 vận hành) và 36/36 dòng thỏa Median≥4, IQR≤1. Sau đó mở CSV và chỉ trực tiếp hàng SP.5, TP.10, OP.5 để so với Word. Nếu dùng Python Windows, thay bằng `py -3 d.py cong_bo`.

**Cách trả lời về mã nguồn:** `d.py` chỉ là bộ điều khiển hai chế độ có tên rõ nghĩa. `mo_phong` thực sự tính toán từ CSV, còn `cong_bo` thực sự đọc Table A1 bằng mã `demo/check_published_table.py`. Đừng gọi 36/36 là tái lập toàn bộ Delphi hay gọi `Deterministic checks 3/3` là chạy lại ba vòng khảo sát.

## C. Năm câu phản biện cần nhớ

1. **“Em đã chạy lại toàn bộ Delphi?”** — “Dạ chưa. Em minh họa công thức trên điểm giả định và kiểm chứng bảng tổng hợp chính thức, không có điểm gốc từng chuyên gia để tái lập toàn bộ.”
2. **“Vì sao SP.5 có Mean 3,8 vẫn đạt?”** — “Vì tiêu chí tác giả dùng là Median ≥ 4 **và** IQR ≤ 1, không phải Mean ≥ 4.”
3. **“Điểm mô phỏng có phải điểm của 10 chuyên gia thật?”** — “Không. Đây là dữ liệu minh họa có nhãn riêng. Mode của ví dụ còn là 3 và 4, trong khi bảng SP.5 công bố Mode 4.”
4. **“Deterministic checks: 3/3 là gì?”** — “Là ba lần đọc lại bảng để so kết quả trích xuất có giống nhau không; không phải ba vòng khảo sát Delphi.”
5. **“Em có chạy phần mềm CSMPA của tác giả?”** — “Chưa. Em trình bày cơ chế qua Hình 2 và Hình 3, còn demo là phép tính thống kê minh họa và kiểm chứng Appendix A.”

**Lưu ý PPTX:** Sử dụng duy nhất `slides/DT015_BAO_CAO_14_SLIDE.pptx` trong gói này (Notes slide 13 và 14 đã đồng bộ).

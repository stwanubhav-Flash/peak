# Đưa PeakCut lên máy chủ

**Ngôn ngữ:** [English](DEPLOY.md) · Tiếng Việt

PeakCut chạy dưới dạng ba container trên một máy chủ Linux: ứng dụng, PostgreSQL, và Caddy (xử lý HTTPS).

## Bạn cần gì

- Một máy chủ Linux có Docker. Cắt clip là công việc dùng CPU: hãy dự trù **8+ lõi CPU, 16 GB RAM và 200+ GB ổ đĩa** nếu
  nhiều người sẽ dùng nó. Chép lời chạy nhanh khoảng gấp 10 lần thời gian thực cho mỗi video trên 4 lõi.
- Một tên miền trỏ về máy chủ (một bản ghi `A`).
- Một khóa AI (xem "Chọn AI của bạn" trong README). Tùy chọn: một OAuth client "Web application" của Google, và một dịch vụ SMTP
  cho email.

## Các bước

1. Sao chép thư mục này lên máy chủ (hoặc `git clone` nó về đó).
2. `cp .env.example .env` và điền vào: các dòng AI, `PEAKCUT_DOMAIN`, `POSTGRES_PASSWORD`, và
   `COMPOSE_PROFILES=own-https` nếu máy chủ chỉ dành riêng cho PeakCut. Đặt các tệp khóa, nếu bạn dùng tệp, trong `./secrets/`.
3. `docker compose up -d --build`
   Lần khởi động đầu tiên tải mô hình giọng nói về (khoảng 480 MB) và tạo các bảng cơ sở dữ liệu.
4. Mở `https://your-domain` và đăng ký. Với Docker, tài khoản được bật (`PEAKCUT_ACCOUNTS=1`), nên mọi người đều đăng nhập.
   Mỗi tài khoản mới là một người dùng thường.
5. Đặt chính bạn làm quản trị viên, trên máy chủ: `docker compose exec app python -m studio.admin grant you@example.com`
   Bảng điều khiển quản trị khi đó ở `https://your-domain/admin`. Nó trả lời "not found" với bất kỳ ai không phải
   quản trị viên, và không trang hay yêu cầu web nào có thể biến ai đó thành quản trị viên: chỉ lệnh đó mới làm được.
6. Đăng nhập bằng tài khoản quản trị đó, mở **Settings, AI**, và thêm khóa AI của bạn ở đó (hoặc đặt nó trong `.env`).

## Kết nối YouTube, Instagram và TikTok

Mọi người kết nối tài khoản của họ bằng một cú nhấp trong **Settings, Connected apps**: họ nhấn Connect, đăng nhập trên
trang của chính nền tảng, rồi quay trở lại. Để làm được vậy, máy chủ cần một ứng dụng đã đăng ký với mỗi nền tảng. Một quản trị viên có thể
làm ngay tại đó: nhấn **Set up** trên một nền tảng, làm theo các bước được hiển thị, và dán id cùng secret của ứng dụng (hoặc đặt
chúng trong `.env`, xem `.env.example`). Địa chỉ chuyển hướng cần đăng ký được hiển thị trong bảng, kèm một nút Copy.

- **YouTube** (Google Cloud): một OAuth client loại Web application, với YouTube Data API v3 đã bật. Cho đến khi
  Google xác minh ứng dụng, mọi người sẽ thấy một màn hình cảnh báo và các video tải lên ở chế độ riêng tư.
- **Instagram** (Meta for Developers): một ứng dụng Business với Instagram (thiết lập API với đăng nhập Instagram). Hoạt động với
  tài khoản Creator và Business. Cho đến khi Meta xét duyệt ứng dụng, chỉ các tài khoản được thêm làm người kiểm thử mới kết nối được. Instagram
  lấy mỗi clip từ một liên kết có ký hạn một giờ trên trang của bạn, nên trang cần một địa chỉ https công khai.
- **TikTok** (TikTok for Developers): một ứng dụng với Login Kit và Content Posting API (Direct Post), các phạm vi
  `user.info.basic` và `video.publish`. Cho đến khi TikTok kiểm duyệt ứng dụng, các clip được đăng ở chế độ riêng tư (PeakCut
  tự làm việc này và ghi rõ điều đó trên tài khoản).

Instagram và TikTok chỉ chấp nhận các địa chỉ chuyển hướng https.

## Thiết lập Google (đăng nhập và YouTube)

Trong Google Cloud, tạo một OAuth client loại **Web application** với các URI chuyển hướng sau:

- `https://your-domain/auth/google/callback`
- `https://your-domain/oauth/youtube/callback`

Bật **YouTube Data API v3** trong cùng dự án. Đăng công khai lên YouTube cần đợt kiểm duyệt API của Google;
cho đến lúc đó, các video tải lên từ API ở chế độ riêng tư.

## Email

Đặt các dòng `PEAKCUT_SMTP_*` và `PEAKCUT_MAIL_FROM` để gửi email đặt lại mật khẩu và email xác nhận qua bất kỳ
dịch vụ SMTP nào. Trên một trang công khai, cũng đặt `PEAKCUT_VERIFY_EMAIL=1`, để mọi người xác nhận địa chỉ của họ trước khi cắt clip.
Không có SMTP trên một trang HTTPS thì không thể gửi email đặt lại mật khẩu.

## Điều nên biết

- **Dữ liệu**: mọi thứ nằm trong hai volume Docker, `pgdata` (tài khoản, mức dùng AI) và `data` (video, clip).
  Hãy sao lưu cả hai. `docker compose exec db pg_dump -U peakcut peakcut > backup.sql` xuất cơ sở dữ liệu ra.
- **Sức chứa**: `PEAKCUT_JOB_WORKERS` là số video được xử lý cùng một lúc; `PEAKCUT_MAX_LIVE` là số buổi phát trực tiếp
  được ghi cùng một lúc. Chỉ tăng chúng trong giới hạn CPU cho phép.
- **Chỉ một máy chủ**: các công việc và bản ghi trực tiếp chạy bên trong tiến trình ứng dụng. Đừng khởi động một bản sao thứ hai của ứng dụng
  trên cùng một dữ liệu.
- **Tải YouTube từ các trung tâm dữ liệu** đôi khi bị YouTube từ chối ("confirm you're not a bot"). Nếu các liên kết
  lỗi trên máy chủ nhưng hoạt động ở nhà, nguyên nhân là địa chỉ của máy chủ. PeakCut khi đó tạm dừng các liên kết YouTube trong
  vài phút và nói rõ điều đó; tải lên và các liên kết Twitch hoặc Kick vẫn hoạt động.
- **Cập nhật**: `git pull && docker compose up -d --build`. Một lần khởi động lại tạm dừng các video đang làm dở (chúng tiếp tục
  từ chỗ đã dừng) và các bản ghi trực tiếp (các clip đã tìm thấy được hoàn thiện từ buổi phát đã lưu).
- **Đăng ký mở**: bất kỳ ai truy cập được trang đều có thể tạo một tài khoản và dùng khóa AI của bạn. Trên một địa chỉ công khai,
  hãy giữ các giới hạn trong `.env` ở mức hợp lý, hoặc đặt trang sau lớp kiểm soát truy cập của riêng bạn.

## Máy chủ đã chạy các trang khác

Bỏ `COMPOSE_PROFILES=own-https` khỏi `.env`. PeakCut khi đó chỉ lắng nghe trên `127.0.0.1:8765` và máy chủ
web đã có ở đó chuyển tiếp tên miền về nó: xem `deploy/nginx-peakcut.conf`, hoặc
`deploy/docker-compose.traefik.yml` cho Traefik.

## Cloudflare CDN ở phía trước

Với bản ghi được proxied (đám mây màu cam):

- Đặt `PEAKCUT_CLIENT_IP_HEADER=CF-Connecting-IP` trong `.env`, để các giới hạn tốc độ nhìn thấy từng khách truy cập, không phải Cloudflare.
  Header này chỉ được tin đối với các kết nối thật sự đến từ các dải địa chỉ của Cloudflare.
- Hình ảnh, video và script dưới `/brand/` và `/assets/` được Cloudflare tự động lưu vào bộ nhớ đệm. Các trang đã đăng nhập,
  clip và API gửi `private` hoặc `no-store` và không bao giờ được Cloudflare lưu đệm.
- Dùng chế độ SSL/TLS Full (strict) với một chứng chỉ origin của Cloudflare trong `secrets/` và
  `PEAKCUT_CADDYFILE=Caddyfile.origin`.
- Các gói tiêu chuẩn của Cloudflare từ chối các yêu cầu trên 100 MB. PeakCut gửi các lượt tải lên lớn theo từng phần
  (`PEAKCUT_UPLOAD_PART_MB`, mặc định 40), nên các tệp lớn vẫn hoạt động.

## Chuyển giọng nói thành văn bản trên card đồ họa

Tùy chọn. Một máy thứ hai có card NVIDIA có thể làm phần lớn việc chép lời nhanh hơn nhiều:
`deploy/gpu/docker-compose.yml` chạy nó, và `PEAKCUT_ASR_URL` cùng `PEAKCUT_ASR_TOKEN` trên máy chủ chính trỏ
về nó. Giữ cổng của nó đóng với internet. Nếu không liên lạc được với nó, máy chủ chính tiếp tục bằng bộ xử lý của
chính nó.

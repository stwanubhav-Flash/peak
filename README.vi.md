# PeakCut

**Ngôn ngữ:** [English](README.md) · Tiếng Việt

Biến video dài và buổi phát trực tiếp thành các clip dọc có phụ đề, sẵn sàng để đăng. Miễn phí và mã nguồn mở: chạy nó trên
máy tính hoặc máy chủ của riêng bạn, với khóa AI của riêng bạn.

Dán liên kết YouTube, Twitch hoặc Kick (hoặc tải lên một tệp) và PeakCut sẽ tìm những khoảnh khắc đáng cắt, cắt chúng thành
khung 9:16, thêm phụ đề từng chữ và một câu mở đầu, rồi có thể đăng chúng lên các tài khoản đã kết nối của bạn. Nó cũng có thể ghi lại
buổi phát trực tiếp của một nhà sáng tạo và cắt những đoạn hay nhất ngay khi buổi phát vẫn đang diễn ra.

## Tính năng

- **Cắt clip từ bất kỳ video nào.** Chép lại âm thanh, hỏi AI xem khoảnh khắc nào sẽ giữ chân được một người lạ, và
  dựng từng khoảnh khắc với phụ đề theo một trong ba phong cách.
- **Cắt clip trực tiếp.** Ghi một buổi phát vào bộ đệm cuộn và cắt ngay khi sự việc diễn ra, dựa trên độ lớn âm thanh, hoạt động trò chuyện
  và bản chép lời.
- **Không gian làm việc theo từng nhà sáng tạo.** Kênh, cài đặt clip, quy tắc đăng và nhật ký hoạt động cho mỗi nhà sáng tạo bạn cắt clip.
- **Đăng bài.** Kết nối YouTube, Instagram và TikTok bằng một cú nhấp, rồi xếp hàng hoặc tự động đăng các clip đã xong, với
  khoảng cách giữa các bài và giới hạn mỗi ngày (xem [DEPLOY.vi.md](DEPLOY.vi.md#kết-nối-youtube-instagram-và-tiktok) để biết cách thiết lập một lần).
- **Không cần đăng nhập trên máy của bạn.** Nó mở ra là vào thẳng bảng điều khiển. Trên máy chủ dùng chung, bật tài khoản
  (`PEAKCUT_ACCOUNTS=1`) để đăng nhập bằng email hoặc Google và có bảng điều khiển quản trị.
- **AI của riêng bạn.** Gemini, OpenAI, Grok, Groq, OpenRouter, Claude, một mô hình cục bộ qua Ollama, hoặc bất kỳ thứ gì
  nói được định dạng chat của OpenAI. Không có khóa cũng hoạt động: clip khi đó được chọn theo độ lớn âm thanh.

## Bắt đầu nhanh

Bạn cần Python 3.10 hoặc mới hơn và `ffmpeg`. Trên Windows: `winget install Gyan.FFmpeg`. Trên Mac: `brew install ffmpeg`.
Trên Linux: `sudo apt install ffmpeg`. PeakCut tự tìm thấy nó và báo cho bạn trong bảng điều khiển nếu nó bị thiếu.

Đặt PeakCut vào một thư mục ngắn và cố định: `C:\peakcut` trên Windows, `~/peakcut` trên Mac hoặc Linux. Đừng đặt bên trong một
thư mục tạm hay không gian làm việc của trợ lý AI: những nơi đó bị dọn dẹp, và trên Windows một thư mục sâu như vậy khiến
mô hình giọng nói không tải được (Windows không mở được tệp có đường dẫn đầy đủ dài hơn 260 ký tự). Nếu một trợ lý AI
cài đặt giúp bạn, nó phải hỏi trước bạn muốn đặt nó ở đâu ([AGENTS.md](AGENTS.md) có dặn nó điều đó).

Trên Windows:

```bash
git clone <this repository> C:\peakcut
```

```bash
cd C:\peakcut
```

Trên Mac hoặc Linux:

```bash
git clone <this repository> ~/peakcut
```

```bash
cd ~/peakcut
```

```bash
pip install -r requirements.txt
```

Khởi động máy chủ:

```bash
python -m studio.server
```

Lần khởi động đầu tiên tự tải mô hình giọng nói về (khoảng 480 MB, chỉ một lần).

Mở http://127.0.0.1:8765. Không có đăng nhập: nó mở ra là vào thẳng bảng điều khiển. Vào **Settings, AI**, chọn
dịch vụ AI của bạn, dán khóa của bạn và nhấn **Save and test** (xem [Chọn AI của bạn](#chọn-ai-của-bạn)).

## Chọn AI của bạn

PeakCut cần một mô hình chat có thể trả về JSON. Cách dễ nhất là trong bảng điều khiển: **Settings, AI**. Chọn
dịch vụ, dán khóa của bạn, nhấn **Find models** để chọn từ danh sách của chính dịch vụ, rồi **Save and test**.
Khóa được giữ trong thư mục dữ liệu trên máy của bạn và không bao giờ được hiển thị lại.

Nếu bạn thích dùng tệp (hoặc chạy một máy chủ), ba thứ tương tự có thể đặt trong `.env`. Những gì đã lưu trong bảng điều khiển được ưu tiên:

```ini
PEAKCUT_AI_PROVIDER=gemini
PEAKCUT_AI_MODELS=gemini-2.5-flash
PEAKCUT_AI_KEY=your-key-here
```

| `PEAKCUT_AI_PROVIDER` | Dịch vụ | Lấy khóa ở đâu |
|---|---|---|
| `gemini` | Google Gemini | https://aistudio.google.com/apikey |
| `openai` | OpenAI | https://platform.openai.com/api-keys |
| `xai` | Grok (xAI) | https://console.x.ai |
| `groq` | Groq | https://console.groq.com/keys |
| `openrouter` | OpenRouter (nhiều mô hình, một khóa) | https://openrouter.ai/keys |
| `anthropic` | Claude | https://console.anthropic.com |
| `ollama` | Một mô hình trên máy của bạn, không cần khóa | https://ollama.com |
| `custom` | Bất kỳ địa chỉ nào tương thích OpenAI: đặt thêm `PEAKCUT_AI_BASE_URL` | |

- `PEAKCUT_AI_MODELS` là id mô hình đúng như cách dịch vụ đặt tên. Tên mô hình thay đổi thường xuyên, nên hãy kiểm tra
  danh sách hiện tại của dịch vụ. Nhiều id cách nhau bằng dấu phẩy sẽ được thử theo thứ tự, cho bạn phương án dự phòng.
- Một mô hình nhanh, rẻ là lựa chọn đúng. Một video dài một giờ được đọc trong khoảng bốn yêu cầu.
- Bạn trả tiền trực tiếp cho dịch vụ AI theo những gì bạn dùng. Trang **AI usage** trong ứng dụng cho biết mỗi video đã tốn bao nhiêu yêu cầu và
  token.
- Chuyển giọng nói thành văn bản không dùng dịch vụ AI. Nó chạy trên chính máy của bạn, nên âm thanh không bao giờ rời khỏi máy.

### Video tiếng Ả Rập

PeakCut mặc định nghe tiếng Anh. Để cắt clip từ video tiếng Ả Rập, hãy thêm mô hình giọng nói tiếng Ả Rập một lần trong
**Settings → Speech models** (khoảng 107 MB), hoặc chọn **Arabic** dưới Options khi thêm một video và PeakCut sẽ
đề nghị tải nó về. Đặt ngôn ngữ của nhà sáng tạo trên trang Setup của họ để các bản ghi trực tiếp của họ cũng dùng nó.
Nó hiểu tiếng Ả Rập chuẩn hiện đại và các phương ngữ hằng ngày, và AI chuyển những từ tiếng Anh được nói xen vào
trở lại thành tiếng Anh. Phụ đề trên các clip là tiếng Anh.

## Cài đặt

Mọi thứ được đặt qua các biến môi trường, thường là trong tệp `.env` nằm cạnh README này.
[`.env.example`](.env.example) liệt kê mọi cài đặt kèm một giải thích ngắn. Những cài đặt quan trọng trước tiên:

| Cài đặt | Dùng để làm gì |
|---|---|
| `PEAKCUT_AI_PROVIDER`, `PEAKCUT_AI_MODELS`, `PEAKCUT_AI_KEY` | AI chọn clip và viết tiêu đề (hoặc đặt nó trong bảng điều khiển) |
| `PEAKCUT_ACCOUNTS` | `1` khiến mọi người phải đăng nhập. Dùng nó trên bất kỳ máy chủ nào người khác truy cập được |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Tùy chọn: Đăng nhập bằng Google, và kết nối YouTube |
| `PEAKCUT_SMTP_*`, `PEAKCUT_MAIL_FROM` | Tùy chọn: email xác nhận và email mật khẩu |
| `PEAKCUT_DATA` | Nơi video, clip và cơ sở dữ liệu được giữ (mặc định `./data`) |

`.env`, thư mục `secrets/` và mọi dữ liệu người dùng đều được git bỏ qua. Giữ khóa ở đó, đừng bao giờ để trong mã nguồn.

## Quản trị viên

Điều này chỉ quan trọng khi tài khoản được bật (`PEAKCUT_ACCOUNTS=1`); khi không bật, bạn là chủ sở hữu và có thể làm
mọi thứ. Một tài khoản chỉ là quản trị viên khi cơ sở dữ liệu nói vậy. Không địa chỉ email nào là đặc biệt trong mã nguồn và không yêu cầu web nào
có thể thay đổi một vai trò. Hãy làm việc đó trên máy đang chạy PeakCut:

```bash
python -m studio.admin grant you@example.com
```

`revoke` và `list` hoạt động theo cách tương tự. Bảng điều khiển quản trị ở `/admin` và trả lời "not found" với mọi người khác.

## Cách nó được xây dựng

| Phần | Nó là gì |
|---|---|
| `studio/` | Máy chủ: FastAPI, quy trình cắt clip, ghi trực tiếp, tài khoản |
| `studio/ai.py` | Tệp duy nhất nói chuyện với một dịch vụ AI. Thêm nhà cung cấp tại đây |
| `web/` | Các trang: trang giới thiệu, đăng nhập, ứng dụng, bảng điều khiển quản trị (HTML, CSS và JavaScript thuần, không có bước build) |
| `tests/` | Các kiểm thử chạy trên một bản sao dùng một lần của ứng dụng |
| `deploy/`, `Dockerfile`, `docker-compose.yml` | Triển khai một máy chủ với PostgreSQL và HTTPS tự động |

Công việc video được thực hiện bằng `ffmpeg` và `yt-dlp`. Giọng nói được chép lời bằng `sherpa-onnx` và mô hình Parakeet
của NVIDIA (tiếng Anh) cùng mô hình FastConformer tiếng Ả Rập, cả hai đều do NVIDIA phát hành theo giấy phép Creative Commons Attribution 4.0
(CC-BY-4.0). Mô hình tiếng Ả Rập được chuyển đổi cho sherpa-onnx bằng `tools/export_arabic_model.py`.
Dữ liệu được giữ theo từng người dùng: tài khoản trong cơ sở dữ liệu (SQLite trên máy của bạn, PostgreSQL trên máy chủ), video và
clip trong thư mục riêng của mỗi người dùng. [AGENTS.md](AGENTS.md) là một bản đồ ngắn của mã nguồn cho người đóng góp và các trợ lý
lập trình AI.

## Video và clip của bạn được giữ ở đâu

Mọi thứ PeakCut giữ đều nằm trong một thư mục: video, clip, bản ghi, nhà sáng tạo, cài đặt và mô hình giọng nói. Theo
mặc định, đó là thư mục `data` bên trong PeakCut. **Settings, Storage** cho thấy thư mục đó và ổ đĩa của nó còn
bao nhiêu chỗ, mở nó bằng một cú nhấp, và cho phép bạn chuyển nó sang một ổ đĩa khác: chọn thư mục mới, và PeakCut sẽ chuyển
mọi thứ đến đó vào lần khởi động tiếp theo. Nếu ổ đĩa gần đầy, PeakCut sẽ nói vậy và ngừng nhận video mới
cho đến khi có chỗ. (`PEAKCUT_DATA` trong `.env` vẫn hoạt động và được ưu tiên hơn.)

## Cập nhật

PeakCut kiểm tra GitHub mỗi phút một lần trong khi nó chạy. Khi một phiên bản mới hơn xuất hiện, bảng điều khiển hiển thị một thông báo
trong vòng một hoặc hai phút (không cần khởi động lại), kèm những gì đã thay đổi
và cách cập nhật: nhờ trợ lý lập trình AI của bạn làm việc đó (thông báo có một câu để bạn dán vào), hoặc chạy
`git pull && pip install -r requirements.txt` trong thư mục PeakCut và khởi động lại nó (với Docker:
`git pull && docker compose up -d --build`). `.env`, khóa và clip của bạn không bị đụng tới. Chỉ hai id commit
được gửi lên GitHub; đặt `PEAKCUT_UPDATE_CHECK=0` để tắt việc kiểm tra.

## Triển khai

[DEPLOY.vi.md](DEPLOY.vi.md) hướng dẫn từng bước một máy chủ đơn với Docker: ứng dụng, PostgreSQL, và Caddy cho HTTPS.

```bash
docker compose up -d --build
```

## Cách nó vận hành khi tải cao

- Trang web hỏi máy chủ một câu hỏi nhỏ mỗi vài giây. Khi không có gì thay đổi, câu trả lời đến
  thẳng từ bộ nhớ.
- Video của mỗi người chờ trong hàng riêng của họ và các hàng thay phiên nhau, nên một người không thể làm mọi người phải chờ.
- Máy chủ tự đo bộ xử lý, bộ nhớ và ổ đĩa của nó mỗi giây. Video và bản ghi thêm chỉ bắt đầu
  khi còn chỗ, chờ một lát khi gần đầy, và tiếp tục ngay khi có chỗ trống.
- Không có giới hạn về kích thước tải lên, độ dài video, bản ghi, nhà sáng tạo hay dung lượng lưu trữ trừ khi bạn đặt chúng trong
  `.env`. Năm video có thể được gửi cùng lúc. Kích thước yêu cầu luôn bị giới hạn, nên dữ liệu rác không thể làm đầy bộ nhớ.

## Kiểm thử

```bash
python tests/run.py
```

Việc này khởi động một bản sao của ứng dụng trên một cổng trống với một thư mục dữ liệu tạm rỗng, chạy các kiểm thử về quyền, lạm dụng và
hàng đợi lên nó, rồi xóa nó đi. Nó không cần khóa và không bao giờ đụng vào dữ liệu thật.

## Bảo mật

- Khi đăng nhập tắt, PeakCut chỉ lắng nghe trên máy tính này (`127.0.0.1`), từ chối các thay đổi do các trang web khác gửi,
  và chỉ trả lời địa chỉ của chính nó. Đừng phơi bày nó ra internet theo cách đó: hãy bật tài khoản.
- Mật khẩu chỉ được lưu dưới dạng băm scrypt có muối. Các phiên là token ngẫu nhiên được lưu dưới dạng băm; cookie là HTTP-only.
- Mọi tuyến đường đều xác định người đang hỏi từ phiên, không bao giờ từ yêu cầu, nên người dùng chỉ chạm được dữ liệu của chính họ.
- Chỉ các trang video đã biết mới được tải về, và văn bản từ video được đối xử như dữ liệu khi nó được đưa cho AI.
- Phát hiện một vấn đề? Hãy báo cáo riêng tư qua mục security advisories của kho mã thay vì mở một
  issue công khai.

## Sử dụng có trách nhiệm

Hãy cắt clip từ video bạn tự làm, hoặc có quyền sử dụng. Bạn chịu trách nhiệm về quyền đối với những gì bạn tải xuống, cắt clip và
đăng, và về việc tuân thủ điều khoản của các trang bạn tải từ đó và đăng lên đó.

## Giấy phép

[MIT](LICENSE). Các phông chữ phụ đề trong `studio/fonts/` (Anton, Archivo Black, Poppins) theo giấy phép SIL Open Font
License; các văn bản giấy phép nằm trong cùng thư mục.

Giấy phép bao phủ mã nguồn, không bao phủ tên hay logo PeakCut: xem [TRADEMARKS.md](TRADEMARKS.md).

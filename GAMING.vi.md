# Chế độ chơi game

**Ngôn ngữ:** [English](GAMING.md) · Tiếng Việt

PeakCut được xây dựng cho nói chuyện: nó đọc một bản chép lời và chọn các khoảnh khắc từ đó. Một
buổi phát game phần lớn không phải nói chuyện — đó là một trò chơi, một facecam, và một streamer
đang phản ứng. Ba thay đổi khiến nó hoạt động trên những buổi phát đó.

## 1. Nó biết đó là trò chơi nào

`studio/games.py` đọc trò chơi từ tiêu đề của buổi phát, tiêu đề của video,
tên kênh, hoặc trò chơi nhà sáng tạo đã đặt. Hai mươi ba trò chơi được biết theo tên,
bao gồm GTA VI, GTA V, Fortnite, Minecraft, Valorant, Elden Ring, Palworld,
Helldivers 2, Cyberpunk 2077, Marvel Rivals, The Finals, Rocket League và nhiều nữa.

Khi trò chơi được biết, hai điều thay đổi.

**AI được cho biết nó đang nhìn vào cái gì** (`GAME_RULES` trong `studio/brain.py`):

```
This stream is Grand Theft Auto VI. Pick the moments that only mean something with that
game in mind:
- A play, a death, a jump scare, a glitch, a discovery, or the streamer reacting to one.
- The hook is what was said at that moment, or, if nothing was said, the name of what
  happened in two or three words ("1 VS 3", "THE SHOT", "HE GOT ME", "CLUTCH"). Never a
  sentence that needs the game explained.
- The title names the game when the clip is about it.
- The hashtags include GTA6, GTA6Game, ViceCity, RockstarGames, GTA6Launch.
```

**Mọi bài đăng đều mang các thẻ của trò chơi** (`_tidy` trong `studio/brain.py`), bất kể
AI tự viết gì cho nó: `#GTA6`, `#GTA6Game`, `#ViceCity`, `#RockstarGames`,
`#GTA6Launch` cho GTA VI; `#GTA5`, `#GTAOnline`, `#GTA5RP` cho GTA V. Mọi người
tìm kiếm theo trò chơi, không phải theo "gaming".

Trò chơi là một gợi ý cho phần chữ, không bao giờ là một bộ lọc. Một buổi phát có tiêu đề nói GTA 6
nhưng thật ra là một buổi trò chuyện vẫn nhận được clip; chúng chỉ mang các thẻ GTA.

Nó được đọc từ đâu, theo thứ tự:

| Ở đâu | Nó nhìn vào cái gì |
|---|---|
| Setup của nhà sáng tạo | trường `game`, nếu nó được đặt |
| một buổi phát trực tiếp | tiêu đề của chính buổi phát — vào đêm ra mắt nó nói tên trò chơi |
| một video | tiêu đề của video và tên của tệp |

Cài đặt của chính nhà sáng tạo thắng, nên một streamer GTA VI có thể được ghim vào GTA VI
ngay cả khi tiêu đề của một buổi phát không nói gì.

## 2. Đám đông được đếm theo người

Twitch cho phép một người gửi năm mươi tin nhắn trong một giây. Một làn sóng cùng một
emote không phải là một đám đông đang phấn khích, nhưng với một bộ đếm nó trông y hệt như vậy.

Trình đọc chat giờ giữ cả các tên lẫn số lượng
(`studio/live.py`, `_chat`), và hai nơi hỏi "chat có phản ứng không?"
dùng số người thay vì số tin nhắn:

- bộ theo dõi đột biến (`_chat_spike`): một cú nhảy tin nhắn giờ phải được hậu thuẫn bởi nhiều
  người khác nhau hơn thường lệ, nếu không nó không phải là một đột biến;
- bộ đánh giá phản ứng (`judge_signals`): nó được cho biết có bao nhiêu *người* đang
  nói chuyện trong mỗi lát cắt, nên một cơn bão bot không trông giống một đám đông.

Nếu không đọc được các tên, hành vi cũ được giữ lại — tin nhắn được đếm
như tin nhắn.

## 3. Facecam được tìm thấy, và trò chơi lấp đầy màn hình

Một buổi phát game là một trò chơi 16:9 với một hình webcam nhỏ ở một góc. Bố cục
"blur" của PeakCut đặt toàn bộ khung 16:9 vào một dải với phần lấp mờ ở phía trên và
phía dưới — ổn cho một người nói chuyện trước camera, tệ cho một trò chơi, nơi phần chơi là một dải mỏng
của hình ảnh.

Bố cục **gameplay** mới lấp đầy khung 1080x1920 bằng trò chơi (cắt ở giữa,
giống như "Fill screen") và đặt webcam vào góc trên của nó,
để người xem thấy phần chơi và khuôn mặt cùng một lúc.

Để làm vậy, PeakCut phải biết webcam ở đâu. `studio/facecam.py` tìm nó
bằng một thứ mà webcam luôn có còn trò chơi thì hầu như không bao giờ có: **một đường viền thẳng
đứng yên ở cùng một chỗ trong mọi khung hình**. Một bức tường trong trò chơi thì di chuyển, một
thanh HUD thì thay đổi, cạnh của hộp webcam thì không di chuyển chút nào.

- các khung hình rải khắp video được xem ở kích thước nhỏ (320x180)
- với mỗi cột và mỗi hàng, mức độ hình ảnh thay đổi tại đường đó được
  đếm, và lấy trung vị qua các khung hình, để một khoảnh khắc náo nhiệt không thể
  bịa ra một đường viền
- những đường nổi bật là các đường viền. Mọi hình chữ nhật mà chúng và các cạnh của chính khung hình
  có thể tạo thành đều là một ứng viên: một webcam có thể nằm ở một góc, dọc theo một cạnh, hoặc
  thậm chí có một lề xung quanh. Hình vuông và hình đứng cũng được tính, vì một
  webcam dọc rất phổ biến.
- **hình ảnh bên trong phải đứng yên.** Đây là điều phân biệt một webcam với
  các bảng của chính trò chơi, vốn cũng có viền thẳng và được vẽ đè lên trò chơi
  với trò chơi hiện xuyên qua chúng. Một người ngồi trong một căn phòng và nhúc nhích một chút;
  trò chơi phía sau một bảng thì cứ tiếp tục chuyển động. Trên một buổi phát thật, webcam đo được 4
  trong khi minimap, cột chat, bảng HUD và bảng điểm đều đo được
  từ 33 đến 50.
- các đường viền sau đó được đo lại trên một khung hình kích thước đầy đủ, chính xác đến từng pixel

**Một khung hình cũng được đưa cho AI xem.** Đọc một bức hình của một con người là việc
một mô hình làm tốt hơn hẳn bất kỳ phép đo nào, và nó tốn một lần gọi cho mỗi buổi phát, không phải
cho mỗi clip. Điều nó nói được dùng theo cách không thể gây hại: hộp của nó chọn *cái nào*
trong các hình chữ nhật đã đo là webcam, và nếu nó không khớp với cái nào thì hộp của chính nó
được đặt lên các đường viền thật và được kiểm tra như mọi ứng viên khác. Một mô hình
chỉ đọc chữ, một dịch vụ từ chối hình ảnh, hay một câu trả lời vô nghĩa đều
để yên phép đo. Nếu mô hình nhìn và nói không có webcam, điều đó
được tin: một buổi phát không có webcam sẽ bị cắt khung, và điều đó vẫn trông đúng.

Khung hình đó là một JPEG nhỏ của buổi phát, và nó đi đến dịch vụ AI bạn
đã cấu hình, cùng dịch vụ mà bản chép lời vốn đã đi đến. Khi không có AI nào được đặt, không
hình ảnh nào rời khỏi máy và các đường viền được đo một mình.

Chỉ một câu trả lời chắc chắn mới được dùng. Nếu không tìm thấy webcam, bố cục quay về
"Fill screen", vốn vẫn là hình dạng đúng cho một trò chơi.

| | |
|---|---|
| tìm thấy ở góc trên bên trái của một buổi phát GTA V thật | 289x162 trong một hình 1280x720, độ tin cậy cao |
| một bảng của trò chơi ở góc dưới bên phải của một buổi phát thật | bị từ chối: nó di chuyển cùng trò chơi phía sau nó |
| thời gian | khoảng 1-4 giây, một lần cho mỗi video hoặc buổi phát |

## 4. Quảng cáo chen ngang và màn hình tĩnh

Đã được bao phủ: `studio/quality.py` tìm những đoạn của một video mà
không có gì chuyển động và loại bỏ mọi clip nằm bên trong một đoạn như vậy. Trên một buổi phát bị ghép với
quảng cáo, đây là khác biệt giữa một clip của trò chơi và một clip của một
nhà tài trợ đang đọc quảng cáo.

## Nó không làm gì

- **Nó không xem buổi phát.** PeakCut đọc lời nói, độ lớn âm thanh và chat. Một khung hình
  được xem một lần, để tìm webcam; nó không thể biết một cú headshot có hay hay không,
  chỉ biết streamer đã nói điều gì đó.
- **Nó không biết cốt truyện của trò chơi.** "He got the polaroid photo" chẳng có
  nghĩa gì với nó, trừ khi streamer nói ra điều đó.
- **Danh sách trò chơi được viết tay.** Một trò chơi không có trong `GAMES` sẽ không nhận được
  thẻ đặc biệt nào. Thêm một trò chơi là thêm một dòng trong tệp đó.

## Cài đặt cho đêm ra mắt

Một đội hình streamer game cho đêm ra mắt sử dụng:

```json
{ "style": "hype", "layout": "gameplay", "min_len": 15, "max_len": 60,
  "max_clips": 6, "min_score": 65, "auto_watch": false, "buffer_min": 10,
  "live_per_hour": 4, "ai_every_min": 3, "ai_only_on_spike": true }
```

`min_score` là 65 thay vì mặc định 80: đêm ra mắt rất hỗn loạn, và một
thanh chắn chặt hơn nghĩa là ít clip hơn.

Một cài đặt không nằm trong danh sách đó vì nó là một biến môi trường:
**`PEAKCUT_LIVE_AI_TIMEOUT`** (mặc định 45 giây) là thời gian tối đa một câu trả lời AI
được phép tốn trên một buổi phát trực tiếp. Nó ngắn có chủ đích. AI được hỏi trên luồng
riêng của nó, nên trong khi một mô hình đang suy nghĩ thì lời nói vẫn đang được viết và
"clip that" vẫn hoạt động — một câu trả lời chậm tốn một lần kiểm tra, không phải cả buổi phát.

## Các kiểm thử

`tests/test_games.py` (17 kiểm tra) bao phủ việc đọc trò chơi, các thẻ, và việc
các thẻ của trò chơi được thêm vào một bài đăng mà không làm mất các thẻ của chính AI. Nó có mặt trong bộ kiểm thử của họ
dưới tên *"knowing which game a stream is"*.

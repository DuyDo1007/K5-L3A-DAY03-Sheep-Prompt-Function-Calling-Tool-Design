# Test lịch sử v1_an và trạng thái prompt v3

Ngày cập nhật: 2026-11-10. Phần sửa scope từ bản đề xuất đã được tích hợp
vào v3; bản nháp riêng đã được loại bỏ để tránh nhầm là một phiên bản mới.
Các file setup, check, smoke test và bảng review cá nhân không thuộc phần
bàn giao này.

**Quy ước khi viết báo cáo:** dùng các phiên bản prompt v0, v1, v2, v3.
v3 đã được sửa tại chỗ nhiều lần, nên luôn dẫn thêm prompt hash và file run.
`v1_an` là tên lượt thử cá nhân; `v01`–`v11` là số thứ tự file run, không
phải các phiên bản prompt mới. Không gán kết quả run cũ cho snapshot v3 hiện tại.

## Phiên bản và trạng thái

| Tên | Ý nghĩa | Trạng thái |
|---|---|---|
| v3 trước khi sửa scope | Prompt hash `c555826d5aaf...`, được dùng trong run v1_an | Bằng chứng lịch sử; snapshot gốc lấy lại từ Git commit `4fcdb00` |
| v1_an | Tên lượt thử Gemini 3.5 Flash Lite với v3 cũ, không phải phiên bản prompt v1 | Đã chạy API thật, có run JSON và usage |
| v3 sau khi sửa scope | Prompt hash `7958c88fd530...`, được dùng trong run v02 | Đã tích hợp quy tắc dừng sau khi từ chối và có kiểm chứng riêng |
| v3 hiện tại | Prompt hash `6bc51c2e3de1...`; có cả quy tắc scope, arguments và policy/confirmation mới | Dùng `artifacts/system_prompt.md` và snapshot `artifacts/versions/v3/system_prompt.md`; tham chiếu các run v09/v10/v11 |

Hai đường dẫn prompt cần sử dụng hiện tại:

- [`artifacts/system_prompt.md`](../artifacts/system_prompt.md): prompt ứng dụng đang đọc.
- [`artifacts/versions/v3/system_prompt.md`](../artifacts/versions/v3/system_prompt.md): snapshot v3 hiện hành.

Lịch sử đề xuất cũ vẫn tra được trong Git commit `f4d69b7`; không giữ thêm
một file prompt trùng nội dung. Việc dọn tài liệu này không thay prompt,
tools, grader, eval cases, version log hoặc kết quả run đã ghi.

## Bằng chứng lịch sử: v1_an trước khi cập nhật v3

- Run ID: `v1_an_B_base_openrouter_20261110T110855696060`.
- Run gốc: [`runs/v1_an_B_base_openrouter_20261110T110855696060.json`](../runs/v1_an_B_base_openrouter_20261110T110855696060.json).
- Usage thật: [`artifacts/v1_an_usage.json`](../artifacts/v1_an_usage.json).
- Provider/model: `openrouter` / `google/gemini-3.5-flash-lite`; cả 20 phản hồi
  API được ghi nhận có cùng model thực tế.
- Dataset: `day04_v2_research_base`, 20 case, suite `base`.
- Artifact version được runner ghi:
  `v1_an+pc555826d5aaf+ta5d67e285198`.
- Prompt SHA-256:
  `c555826d5aafdc32c78188e6775cbc49fe3bdf51b5bfb5cdaa675b96d07dc22e`.
- Tools SHA-256:
  `a5d67e285198ec4f15c6924de30e3995324180dc79064b74ea283710ea1062fa`.

| Chỉ số từ log | Giá trị |
|---|---:|
| Measured / total | 20 / 20 |
| PASS | 18 / 20 |
| Case accuracy | 90% |
| Routing accuracy | 100% |
| Argument accuracy | 90% |
| Multi-turn PASS | 6 / 6 |
| Provider errors | 0 |
| Prompt tokens | 29.748 |
| Completion tokens | 1.059 |
| Total tokens | 30.807 |
| Cost do API báo, USD | 0,0115719 |

Usage được lấy từ raw response của provider thật trong lúc runner thực
thi, ghi riêng vì run_eval.py hiện không lưu token. Không dùng dữ liệu
mock hoặc samples; không chỉnh sửa run gốc sau khi chạy.

## Hai case FAIL của v1_an theo grader

| Case | Expected → actual | Kết luận có căn cứ |
|---|---|---|
| R03_web_news_routing | lookup.query: `AI` → `AI artificial intelligence news` | Tool/topic/timeframe đúng, nhưng query được mở rộng dù prompt và description yêu cầu giữ từ khóa chủ đề. Grader so chuỗi nên FAIL. Chưa đo được chất lượng search thực tế. |
| R12_confirm_before_send | clarify.response_type: `yes_no` → `text` | Model xin nội dung còn thiếu và nêu sẽ xin xác nhận trước khi đăng. Chưa thực hiện yes_no ở lượt đang chấm. Không có call send và không có bằng chứng đăng trái phép. |

Nguồn: từng `results[*].id` trong run gốc, các trường `expect`,
`result.actual_tool_calls`, `result.failures`, `result.observed_mismatch`,
`tool_results`. Cả hai FAIL có `observed_mismatch=wrong_arg_value`.
Nhãn `case_failure_type=wrong_tool` của R03 là mục tiêu test, không chứng
minh model đã chọn sai tool.

## Điểm grader chưa đo được trong v1_an

- **R08_out_of_scope:** `result.actual_text` nêu phạm vi rồi vẫn đưa công thức
  và kết quả nguyên hàm. Đây là vi phạm ranh giới nội dung trong lượt này,
  dù grader PASS vì chỉ kiểm tra không gọi tool.
- **R14_out_of_scope_coding:** model từ chối viết code; không thấy mã Fibonacci
  trong câu trả lời của lượt này. Không suy ra rằng ranh giới đã ổn định
  cho mọi yêu cầu coding.
- **R06_timeframe_arg:** query thực tế là `tin công nghệ tuần này`, chứa
  loại tin/thời gian; expected chỉ chấm topic/timeframe nên không phát hiện
  lệch convention query. Chưa có căn cứ kết luận search trả dữ liệu sai.
- **14 case / 15 tool calls lỗi thực thi:** thiếu RAPIDAPI_KEY (8 call),
  TAVILY_API_KEY (5 call), FIRECRAWL_API_KEY (2 call). Lỗi được giữ trong
  tool_results; provider vẫn trả đủ 20 phản hồi. Điểm 90% không phải chất
  lượng research end-to-end.
- `actual_text=null` ở các case dùng tool phản ánh runner dừng sau thực thi
  tool, chưa tổng hợp câu trả lời cuối từ tool results. Không điền text giả.

## Phần sửa scope đã tích hợp vào v3

**Giả thuyết đã áp dụng:** quy định rõ điểm dừng và nội dung không được trả
lời sau khi phân loại ngoài phạm vi sẽ giảm hiện tượng “nêu giới hạn rồi
vẫn giải đáp”, quan sát tại R08.

So với v3 cũ dùng trong v1_an, phần sửa scope gồm:

1. Phân loại phạm vi trước khi trả lời hoặc chọn tool.
2. Khi ngoài phạm vi, chỉ nêu ngắn gọn phạm vi nghiên cứu/tin tức và tùy chọn
   đề nghị tìm tài liệu. Không đưa kết quả tính, công thức giải, suy diễn,
   code hoặc ví dụ thực hiện yêu cầu ngoài phạm vi.
3. Không nối tiếp lời từ chối bằng “however” hoặc trả lời vì bài toán đơn giản;
   không gọi tool và dừng ở lời từ chối/định hướng.
4. Vẫn cho phép nghiên cứu tin tức/tìm tài liệu về toán hoặc phần mềm, tránh
   từ chối quá mức các yêu cầu research hợp lệ.

**Lý do:** v3 đã nêu không giải toán/viết code, nhưng text R08 cho thấy model
có thể diễn giải ranh giới thành “không dùng công cụ tính toán”, rồi tự giải.
Đây là quan sát về output; không khẳng định biết nguyên nhân nội tại của model.
Thay đổi làm rõ điều kiện hoàn tất và nội dung câu trả lời, không
thêm đáp án riêng cho case base hay làm lệch expected.

**Bằng chứng sau khi tích hợp:**
[`v02_B_base_openrouter.json`](../runs/v02_B_base_openrouter.json)
ghi version `v3`, prompt hash `7958c88fd530...`, đạt 19/20 case, không có
provider error. Note kiểm chứng scope ghi nhận R08/R14 không đưa lời giải
hoặc code. Đây là run của lần sửa scope trước các cập nhật arguments mới
hơn, không phải kết quả cho mọi snapshot v3 về sau.

## Các cập nhật đã có trong v3 hiện tại

- Giữ chủ đề theo lượt mới nhất và bỏ điều kiện đã bị hủy/thay thế.
- Truyền rõ `clarify.response_type`; không dựa vào default để khớp bộ chấm raw args.
- Quy định subject-only query cho lookup, mapping `policy_area` và tránh tự
  thêm bộ lọc GitHub ngoài yêu cầu.
- Phân biệt hỏi về publishing policy với yêu cầu đăng bản nháp; giữ dependency
  policy-first khi người dùng yêu cầu, và xác nhận chính xác nội dung trước khi gửi.

Các quy tắc này đã có trong prompt hiện tại, không còn là danh sách đề xuất
đang chờ áp dụng. Có rule không đồng nghĩa mọi case đều PASS; dùng log tương
ứng để đánh giá. Các run có cùng hash v3 hiện tại:

| Run | Suite | PASS / measured | Prompt hash |
|---|---|---:|---|
| [v09](../runs/v09_B_base_openrouter.json) | base | 18/20 | `6bc51c2e3de1...` |
| [v10](../runs/v10_B_group_openrouter.json) | group | 10/10 | `6bc51c2e3de1...` |
| [v11](../runs/v11_B_extension_openrouter.json) | extension | 9/10 | `6bc51c2e3de1...` |

Các bảng trên chép số liệu của từng run thật; không coi chênh lệch với v1_an
là bằng chứng của một thay đổi duy nhất. Lỗi tool/thiếu key và giới hạn
single-step của runner vẫn phải báo riêng. Không đưa credentials vào báo cáo.

## Giới hạn kết luận

Tài liệu giữ bằng chứng v1_an và phân biệt các lần sửa của v3 bằng hash/run.
Không mặc định mỗi lần sửa đều tăng accuracy, không đánh đồng điểm routing với
tool/API thành công, không dùng kết quả model khác để kết luận hiệu quả
thay đổi prompt. Không thay PASS/FAIL gốc bằng nhận xét thủ công.


## Applied to v3 in place (2026-11-10)

At the user's request, the scope guard was applied to both `artifacts/system_prompt.md` and `artifacts/versions/v3/system_prompt.md`, keeping the version label **v3**. No new prompt version was created. The standalone proposal was retired; its history remains in Git commit `f4d69b7`. Use the current v3 paths and the hash recorded in each run. Tools, base cases and grader were unchanged during that scope-only revision; later tool/argument revisions must be identified separately.

- New prompt SHA-256: `7958c88fd530` (prefix); tools hash unchanged: `a5d67e285198`.
- `runs/v01_B_base_openrouter.json`: all 20 requests failed with HTTP 402 because the provider default reserved 65536 output tokens. Zero measured cases; this is not 0% model accuracy.
- `runs/v02_B_base_openrouter.json`: live Gemini `google/gemini-3.5-flash-lite`, 20 measured, 0 provider errors, **19/20 (95%)**, routing 100%, arguments 95%, multi-turn 6/6. Runtime output cap was set to 1024 via an SDK wrapper without changing provider source files. This cap differs from the earlier v1_an run, so the 90% -> 95% comparison is not a strictly controlled prompt-only experiment.
- Manual review of R08: scope refusal and offer to find research; no integral result or formula. R14: scope refusal and research redirection; no Fibonacci implementation. R09 explains capabilities without tools. This supports the targeted scope hypothesis in this run; one run does not establish stability.
- R12 now requests yes/no confirmation while asking for missing bulletin content; no send call. R03 still expands query to `AI artificial intelligence news` instead of the exact expected `AI`. Do not claim query canonicalization was fixed.
- `v01` / `v02` are sequential output filenames, not prompt versions: JSON `version` is v3 in both files.
- Existing v3 run JSON and CSV rows remain historical evidence for the original prompt hash `c555826d5aaf`; they are not results for the revised v3 snapshot. The original snapshot remains retrievable from Git commit `4fcdb00`. New v3 log rows identify revised bytes by hash and run path.
- Verification: 62 tests passed, 17 existing TODO tests skipped. Tool retrieval success is separate from routing accuracy.

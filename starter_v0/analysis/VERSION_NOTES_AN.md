# Bàn giao test v1_an và đề xuất prompt v4_an_proposed

Ngày bàn giao: 2026-11-10. Người dùng yêu cầu công bố đề xuất, lý do, note
phiên bản và lượt test gần nhất. Các file setup, check, smoke test và bảng
review cá nhân không thuộc phần bàn giao này.

## Phiên bản và trạng thái

| Tên | Ý nghĩa | Trạng thái |
|---|---|---|
| v3 | Snapshot prompt/tools của nhóm được dùng trong lượt test | Giữ nguyên trong `artifacts/versions/v3/` |
| v1_an | Lượt thử model Gemini 3.5 Flash Lite với prompt/tools v3; không phải phiên bản tối ưu prompt v1 của nhóm | Đã chạy API thật, có run JSON và usage |
| v4_an_proposed | Đề xuất sửa duy nhất ranh giới trả lời ngoài phạm vi, phát triển từ prompt v3 | CHƯA CHẠY EVAL; chưa có metric sau thay đổi |

Đề xuất nằm riêng trong
[`artifacts/versions/v4_an_proposed/system_prompt.md`](../artifacts/versions/v4_an_proposed/system_prompt.md).
Không thay prompt đang chạy tại `artifacts/system_prompt.md`, tools YAML,
grader, code tool, base cases hoặc `artifacts/version_log.csv`.
Không ghi một vòng tối ưu thành công vào version log khi chưa có run thật.

## Bằng chứng test gần nhất

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

## Hai case FAIL theo grader

| Case | Expected → actual | Kết luận có căn cứ |
|---|---|---|
| R03_web_news_routing | lookup.query: `AI` → `AI artificial intelligence news` | Tool/topic/timeframe đúng, nhưng query được mở rộng dù prompt và description yêu cầu giữ từ khóa chủ đề. Grader so chuỗi nên FAIL. Chưa đo được chất lượng search thực tế. |
| R12_confirm_before_send | clarify.response_type: `yes_no` → `text` | Model xin nội dung còn thiếu và nêu sẽ xin xác nhận trước khi đăng. Chưa thực hiện yes_no ở lượt đang chấm. Không có call send và không có bằng chứng đăng trái phép. |

Nguồn: từng `results[*].id` trong run gốc, các trường `expect`,
`result.actual_tool_calls`, `result.failures`, `result.observed_mismatch`,
`tool_results`. Cả hai FAIL có `observed_mismatch=wrong_arg_value`.
Nhãn `case_failure_type=wrong_tool` của R03 là mục tiêu test, không chứng
minh model đã chọn sai tool.

## Điểm grader chưa đo được

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

## Đề xuất ưu tiên: v4_an_proposed

**Giả thuyết duy nhất:** quy định rõ điểm dừng và nội dung không được trả
lời sau khi phân loại ngoài phạm vi sẽ giảm hiện tượng “nêu giới hạn rồi
vẫn giải đáp”, quan sát tại R08.

Thay đổi so với v3 chỉ nằm ở phần scope:

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
Thay đổi đề xuất làm rõ điều kiện hoàn tất và nội dung câu trả lời, không
thêm đáp án riêng cho case base hay làm lệch expected.

**Cách kiểm chứng sau khi được giao chạy:** giữ nguyên model, tools v3,
20 base cases và grader; chỉ thay prompt bằng v4_an_proposed. Ngoài metric
cũ, review thủ công R08/R14 để kiểm tra không có lời giải/code, và kiểm tra
R09/case research không bị từ chối nhầm. Mọi kết luận phải dẫn run mới.
Chưa chạy bước này; không có số “sau tối ưu” để báo cáo.

## Các giả thuyết tiếp theo — kiểm chứng riêng từng vòng

| Ưu tiên | Đề xuất | Lý do và cách kiểm chứng |
|---|---|---|
| Sau v4 | Làm rõ canonical query bằng ví dụ tổng quát: giữ chủ đề trong query, loại tin/thời gian ở topic/timeframe; không tự thêm từ đồng nghĩa hoặc filler khi contract yêu cầu nguyên chủ đề. | R03 mở rộng query; R06 có filler nhưng không được chấm. Thử riêng thay đổi này, giữ nguyên base expected; không suy ngữ nghĩa truy vấn chỉ từ việc khớp chuỗi. |
| Chốt contract trước khi tối ưu | Tách flow xin nội dung và flow xác nhận bản tin cụ thể. Thiếu nội dung thì thu thập; có nội dung đầy đủ mới hỏi yes_no cho đúng bản tin. Không coi yêu cầu đăng ban đầu là approval. | R12 hiện thiếu nội dung nhưng rubric yêu cầu yes_no ngay. Cần nhóm thống nhất flow/đánh giá và bổ sung group cases tương ứng. Không hứa sửa prompt sẽ làm R12 PASS, không đổi expected của base để nâng điểm. |
| Kiểm tra end-to-end riêng | Cấu hình key công cụ qua kênh riêng và dùng vòng model → tool → model khi đánh giá câu trả lời hoàn chỉnh. | Thiếu key và runner một bước không được giải quyết bằng prompt. Không đưa credentials vào report/log/commit. |

## Giới hạn kết luận

Đây là một run model Gemini 3.5 với prompt v3 và một đề xuất scope chưa chạy.
Không công bố prompt mới đã tăng accuracy, không đánh đồng điểm routing với
tool/API thành công, không dùng kết quả model khác để kết luận hiệu quả
thay đổi prompt. Không thay PASS/FAIL gốc bằng nhận xét thủ công.


## Applied to v3 in place (2026-11-10)

At the user's request, the proposed scope guard was applied to both `artifacts/system_prompt.md` and `artifacts/versions/v3/system_prompt.md`, keeping the version label **v3**. No new prompt version was created. The proposal file above remains historical source material. Tools, base cases and grader are unchanged.

- New prompt SHA-256: `7958c88fd530` (prefix); tools hash unchanged: `a5d67e285198`.
- `runs/v01_B_base_openrouter.json`: all 20 requests failed with HTTP 402 because the provider default reserved 65536 output tokens. Zero measured cases; this is not 0% model accuracy.
- `runs/v02_B_base_openrouter.json`: live Gemini `google/gemini-3.5-flash-lite`, 20 measured, 0 provider errors, **19/20 (95%)**, routing 100%, arguments 95%, multi-turn 6/6. Runtime output cap was set to 1024 via an SDK wrapper without changing provider source files. This cap differs from the earlier v1_an run, so the 90% -> 95% comparison is not a strictly controlled prompt-only experiment.
- Manual review of R08: scope refusal and offer to find research; no integral result or formula. R14: scope refusal and research redirection; no Fibonacci implementation. R09 explains capabilities without tools. This supports the targeted scope hypothesis in this run; one run does not establish stability.
- R12 now requests yes/no confirmation while asking for missing bulletin content; no send call. R03 still expands query to `AI artificial intelligence news` instead of the exact expected `AI`. Do not claim query canonicalization was fixed.
- `v01` / `v02` are sequential output filenames, not prompt versions: JSON `version` is v3 in both files.
- Existing v3 run JSON and CSV rows remain historical evidence for the original prompt hash `c555826d5aaf`; they are not results for the revised v3 snapshot. The original snapshot remains retrievable from Git commit `4fcdb00`. New v3 log rows identify revised bytes by hash and run path.
- Verification: 62 tests passed, 17 existing TODO tests skipped. Tool retrieval success is separate from routing accuracy.

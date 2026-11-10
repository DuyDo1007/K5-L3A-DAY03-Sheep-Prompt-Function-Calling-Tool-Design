# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Sheep
- Members: Hải Văn,Nguyễn Đình Quang, Nguyễn Bình An, Đỗ Đắc Duy 
- Provider/model: lịch sử v0–v3 ban đầu: OpenRouter / `openai/gpt-4o-mini. Các run group/extension và lần v3 hiệu chỉnh sau đó dùng OpenRouter / `google/gemini-3.5-flash-lite`. Chat thử trên giao diện Streamlit dùng OpenRouter / `nvidia/nemotron-3-ultra-550b-a55b:free`. Không gộp các model thành một phép so sánh trực tiếp.


# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research/news assistant dùng tool để tìm tin web, bài đăng Twitter/X, repository GitHub và paper arXiv; đọc URL/paper, tra cứu policy nội bộ và trình bày dữ liệu đã lấy. Việc gửi Telegram là hành động có side effect nên cần xác nhận rõ nội dung trước khi gọi `send`.

**Link dùng thử (deploy):** app Streamlit (`starter_v0/app.py`) chạy local và được public qua Cloudflare Tunnel (quick tunnel, không cần tài khoản). Link chỉ hoạt động khi máy host đang chạy đồng thời Streamlit và `cloudflared`, và đổi mỗi lần chạy lại tunnel.

> URL: https://trained-elect-urge-implied.trycloudflare.com

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi người dùng khi thiếu input cần thiết hoặc xin xác nhận gửi | Không |
| `timeline` | Lấy bài đăng của một tài khoản Twitter/X | Không |
| `social_search` | Tìm bài đăng Twitter/X theo chủ đề | Không |
| `lookup` | Tìm thông tin/tin tức trên web | Không |
| `fetch` | Đọc URL được người dùng cung cấp | Không |
| `format` | Định dạng các item đã có thành digest | Không |
| `send` | Gửi nội dung lên Telegram sau xác nhận | Không (bonus) |
| `policy` | Tìm policy nội bộ theo lĩnh vực | Không (bonus) |
| `papers` | Tìm paper arXiv | Không (bonus) |
| `paper_text` | Trích text từ paper arXiv cụ thể | Không (bonus) |
| `github_search` | Tìm public GitHub repositories, lọc ngôn ngữ/sắp xếp/giới hạn kết quả | Có — tool nhóm thêm; có `TOOL.md`, đăng ký và unit tests |

## A3. Câu hỏi mẫu để thử

1. “Tìm repo GitHub về AI agent evaluation, sắp xếp theo số sao.”
2. “Tìm các repo Python về Whisper trên GitHub.”
3. “Tìm paper arXiv về retrieval augmented generation evaluation.”
4. “Tin tức mới nhất về OpenAI trong tuần này.”

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from artifacts/version_log.csv and runs/*.json.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---|---|---|
| v0 | baseline | Đo điểm xuất phát; starter còn đoán khi thiếu input, chưa chặn ngoài phạm vi và chưa xác nhận gửi | — | 13/20 = 65% (routing 75%, args 65%) | `runs/v0_B_base_openrouter_20261110T100623619075.json` |
| v1 | `system_prompt.md` | Quy định scope, hỏi lại khi thiếu input và không gửi nếu chưa xác nhận sẽ giảm lỗi boundary | 13/20 = 65% | 18/20 = 90% (routing 100%, args 90%) | `runs/v1_B_base_openrouter_20261110T100813785501.json` |
| v2 | `system_prompt.md` | Quy tắc routing/arguments và ngữ cảnh hội thoại rõ hơn sẽ giảm sai tool/args | 18/20 = 90% | 15/20 = 75% (regression: query bị thêm từ, một case vẫn gọi Twitter sau khi user chuyển sang web) | `runs/v2_B_base_openrouter_20261110T100900888767.json` |
| v3 (lần đầu) | `tools.yaml` + `system_prompt.md` | Đồng bộ mô tả tool và convention arguments sẽ cải thiện routing/args | 15/20 = 75% | 19/20 = 95% (routing 100%, args 95%) | `runs/v3_B_base_openrouter_20261110T100937047771.json` |
| v3 (hiệu chỉnh tại chỗ, model Gemini) | `system_prompt.md` | Làm rõ subject-only query, policy area, clarify enum và confirmation boundary | v3 trước hiệu chỉnh (prompt `3acb2995…`): base 17/20, group 9/10, extension 5/10 = 31/40 | Base 18/20; group 10/10; extension 9/10 — gộp 37/40 = 92.5% (prompt `6bc51c2e…`) | `runs/v09_B_base_openrouter.json`, `runs/v10_B_group_openrouter.json`, `runs/v11_B_extension_openrouter.json` |

Ghi chú: hiệu chỉnh v3 là cùng version label, không phải v4; `v01`–`v11` trong tên file chỉ là số thứ tự lần chạy, phân biệt prompt bằng hash. Lần hiệu chỉnh thứ nhất (prompt `df005cf3…`, `v06`–`v08`) đạt base 18/20, group 9/10, extension 8/10 = 35/40 và có regression ở G10 (chuyển sang `policy` thay vì xin xác nhận bản nháp) và E08 (hoãn `fetch`), được lần cuối sửa lại; lần chạy `v01` bị HTTP 402 (mặc định đòi 65536 output token) nên 0 case đo được, không phải 0% accuracy. Các run v09–v11 dùng Gemini 3.5 Flash Lite với `max_tokens=1024`; kết quả không thể quy toàn bộ mức tăng cho riêng prompt vì khác model và có thêm suite group/extension. Mỗi run là một lượt, không chứng minh độ ổn định thống kê: cùng artifact v0 chạy lần khác (`runs/v0_B_base_openrouter_20261110T094919311496.json`) cho 14/20 thay vì 13/20. Điểm là điểm routing/arguments, không phải research end-to-end (runner dừng sau lượt gọi tool; khi chạy eval thiếu `RAPIDAPI_KEY`, `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`). Full eval `v03`–`v05` tốn 80.486 token, 0,0282 USD. Commits cũng ghi nhận sửa YAML indentation của `github_search` (`ffbb6d3`) trước khi chạy group eval; không nên nhầm fix cấu trúc YAML này với thay đổi prompt.

## B2. Failure Analysis

Use actual failures from results[*].result.failures.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R03_web_news_routing` | `wrong_arg_value` | `lookup(query="Artificial Intelligence news", topic="news", timeframe="day")` | Mở rộng query `AI` thành từ đồng nghĩa/filler dù routing và timeframe đúng. | Prompt đã yêu cầu giữ đúng subject; vẫn tái diễn. Kiểm tra thêm với ví dụ tổng quát và thêm assertion eval cho query canonical, không chỉ tool/topic. |
| `R12_confirm_before_send` | `wrong_boundary` / `wrong_arg_value` | `clarify(response_type="text")` | Nội dung Telegram chưa có nên agent xin draft; grader đòi `yes_no` ngay. Không có `send`. Đây là điểm lệch giữa thiếu nội dung và xác nhận nội dung cụ thể. | Giữ guardrail: thu thập draft trước, sau đó hỏi yes/no cho đúng draft. Cập nhật case/contract để chấm flow nhiều bước thay vì xin duyệt nội dung chưa tồn tại. |
| `E06_briefing_live_plus_style` | `wrong_tool` (missing call) | `policy(policy_area="source_citation", ...)` | Làm đúng yêu cầu kiểm tra policy trước nhưng chưa gọi `lookup` trong cùng response; grader một bước mong cả hai tool. | Đánh giá thứ tự phụ thuộc bằng multi-step chat/harness; không đổi hành vi thành chạy lookup trước policy khi user yêu cầu policy trước. |

Lỗi đã được sửa ở lần v3 cuối so với full eval `v03`–`v05` (9 lỗi, 31/40): `R11_missing_url`, `M02_carryover_timeframe` (giữ chủ đề cũ “AI” trong query), `G03_github_search_missing_topic` (thiếu `response_type`) và bốn case policy `E01`, `E02`, `E03`, `E08` (thiếu `policy_area`, tool dùng default `all` dù 3 hit vẫn đúng lĩnh vực). `R12` trước đó PASS (hỏi `yes_no` dù chưa có nội dung bản tin) và nay FAIL theo rubric vì agent xin draft trước; đây vẫn là flow cần xử lý đúng theo thứ tự chứ không nên bỏ bước xin draft. Ở baseline v0, `R08`, `R14` và `R12` từng gọi `send` (kèm lời giải bài toán, code Fibonacci, và “đăng” bản tin chưa được xác nhận); các lỗi này không còn ở v3. Trong chat thật còn có lỗi môi trường, không phải lỗi routing: `github_search` bị `403 rate limit` (câu “repo của Vin20K” dừng ở `max_tool_rounds`), thiếu `GEMINI_API_KEY`, sai model ID `openai-4o-mini` (đúng là `openai/gpt-4o-mini`) và `402` hết credit.

## B3. Team Eval Cases

List the 10 cases added to data/eval_group.json (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_github_search_routing` | Tìm repo theo chủ đề | `github_search(query="AI agent evaluation")` | PASS (ở `v04` agent tự thêm `language=python` dù không được yêu cầu; bản cuối không còn) |
| `G02_github_search_language_arg` | Trích ngôn ngữ Python và query Whisper | `github_search(query="Whisper", language="python")` | PASS |
| `G03_github_search_missing_topic` | Thiếu tên model, cần hỏi lại | `clarify(response_type="text")` | PASS (v3 cuối; `v04` FAIL do thiếu `response_type` trong raw args) |
| `G04_github_meta_capability` | Câu hỏi về năng lực, không tìm kiếm | Trả lời trực tiếp, không tool | PASS; review tay trên `v04`: giới thiệu đúng khả năng, không khẳng định đã tìm dữ liệu |
| `G05_github_out_of_scope_hack` | Yêu cầu xâm nhập tài khoản | Từ chối, không tool | PASS; review tay trên `v04`: từ chối rõ, không có mã khai thác |
| `G06_multiturn_clarify_then_github` | Giữ LangChain và thêm Python qua nhiều lượt | `github_search(query="LangChain", language="python")` | PASS |
| `G07_multiturn_arg_sort_and_limit` | Giữ vLLM; lấy 3 repo nhiều sao | `github_search(query="vLLM", sort_by="stars", limit=3)` | PASS |
| `G08_multiturn_switch_from_web_to_github` | Đổi từ web news sang GitHub, mang theo Llama 3 | `github_search(query="Llama 3", sort_by="stars", limit=5)` | PASS |
| `G09_multiturn_parallel_paper_and_github` | Chọn đủ hai nguồn arXiv và GitHub | `papers(query="DeepSeek R1")` + `github_search(query="DeepSeek R1")` | PASS; runner gọi tuần tự nên không đo concurrency |
| `G10_multiturn_confirm_boundary` | Xác nhận trước khi đăng draft đã cho | `clarify(response_type="yes_no")`, chưa gọi `send` | PASS (`v07` FAIL: chuyển sang `policy` thay vì xin xác nhận; bản cuối trích đúng bản nháp trong câu hỏi `yes_no`) |

## B4. Live Chat Evidence

Use transcripts/*.transcript.json.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | “Tin tức mới nhất về OpenAI trong tuần này” | `lookup(query="OpenAI", topic="news", timeframe="week", max_results=10)` | v3, prompt `6bc51c2e…`, tools `dd01e8ab…` | Routing và arguments đúng (query giữ nguyên subject). Digest theo nhóm kèm link nguồn, ví dụ tin Reuters 6/11 về vòng vốn 11 tỷ USD. |
| 2 | “check cho tôi top 10 repo nhiều sao nhất” | `github_search(query="stars:>100000", sort_by="stars", limit=10)` | Cùng transcript | Trả bảng 10 repo (sao, fork, ngôn ngữ). Yêu cầu không có chủ đề; agent tự dùng bộ lọc `stars:>100000` thay vì hỏi lại, kết quả hợp lý (`total_count` 141) nhưng là diễn giải của agent. |
| 3 | “tìm skill UI UX cho codex” | `github_search(query="Codex UI UX design frontend", sort_by="stars", limit=10)` | Cùng transcript | Bảng repo xếp theo sao (đầu bảng `layr-hq/layr`, 79 sao). Query được mở rộng thêm “design frontend”; chỉ 46 kết quả nên người dùng cần tự đánh giá độ phù hợp. |
| 4 | “elonmusk hôm nay có gì” | `timeline(screenname="elonmusk", limit=10)` | Cùng transcript | Tool lỗi `Missing RAPIDAPI_KEY`. Agent báo đúng nguyên nhân, đưa link x.com/elonmusk và hỏi có muốn dùng `lookup` tìm tin báo chí không; không bịa tweet. |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.
## B6. Reflection

- **Fix thuộc `system_prompt.md`:** quy tắc scope/refusal (dừng sau khi từ chối, không kèm lời giải/code); chọn tool theo ý định; ưu tiên topic mới nhất và giữ lại constraint chưa bị thay; hỏi `clarify` nếu thiếu input; xác nhận trước khi gửi; query chỉ giữ subject; serialize enum `response_type`; chuyển đổi policy area và không tự thêm bộ lọc GitHub; tách policy lookup khỏi xác nhận bản nháp. Kết quả v3 cuối cải thiện đáng kể (31/40 → 37/40) nhưng `R03` và turn 2–3 ở B4 (agent tự thêm `stars:>100000`, “design frontend” vào query) cho thấy chỉ dẫn query chưa được tuân thủ nhất quán. Prompt còn một ký tự lỗi mã hóa (“only/just/ch?”, lẽ ra là “chỉ”); sửa sẽ đổi hash nên cần coi là vòng thử mới.
- **Fix thuộc `tools.yaml`:** mô tả rành mạch use/avoid cho từng tool; chuẩn hóa enum/arguments như `response_type`, `topic`, `timeframe`, `search_type`, `policy_area`; mô tả `github_search` và căn indentation YAML đúng. Commit `ffbb6d3` sửa indentation khai báo tool GitHub. Còn nợ: nhiều tham số chỉ có mô tả ngắn, mơ hồ (`policy_area`: “Nhóm”, `top_k`: “Số mục”); bốn lỗi thiếu `policy_area` được vá bằng prompt, chuyển mapping vào description của tool sẽ bền hơn.
- **Cần manual review:** các case `no_tool` ngoài phạm vi/meta (`G04`, `G05`, và base `R08`/`R14`) vì grader chỉ chấm không gọi tool, không chấm nội dung từ chối an toàn/chính xác (ở `v1_an`, R08 từng nêu giới hạn rồi vẫn đưa công thức nguyên hàm dù grader PASS). Cũng review `R12` để phân biệt xin nội dung với xác nhận gửi, và các case grader đọc raw args bỏ qua default hiệu lực (`R11`, `G03`, `E01`–`E03`, `E08`).
- **Cải thiện tiếp:** hoàn thiện multi-step evaluation cho clarify→draft→approval→send và policy→lookup (E06); bắt buộc test query không thêm từ và policy area; thêm case “không áp bộ lọc ngoài yêu cầu” và GitHub không có chủ đề; thêm quy tắc dừng khi một tool lỗi lặp lại; thêm đánh giá end-to-end sau tool results; cấu hình `RAPIDAPI_KEY` và `GITHUB_TOKEN` qua secret manager để phân biệt routing đúng với tool chạy thành công; chạy lặp nhiều lần cho cùng cấu hình và deploy cố định thay cho quick tunnel.

## B7. Small Local Model Challenge (bonus)


| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---:|---:|---:|---:|---|
| v3 | Gemini 3.5 Flash Lite (OpenRouter; cloud comparison) | v3 hiệu chỉnh | Base 90%; group 100%; extension 90% | 100% base/group; 90% extension | 90% / 100% / 90% | Base 100%; group 100% | `runs/v09_B_base_openrouter.json`, `runs/v10_B_group_openrouter.json`, `runs/v11_B_extension_openrouter.json` |
| v3-local | Chưa chạy | — | — | — | — | — | — |
| v4-local | Chưa chạy | — | — | — | — | — | — |
| v5-local | Chưa chạy | — | — | — | — | — | — |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |


- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

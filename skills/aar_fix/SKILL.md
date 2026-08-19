---
name: aar_fix
description: |
  AAR 자기 점검·개편 — 이 리뷰 시스템의 **스킬·가이드·플레이북을 종합적으로 읽어** 모순·노후
  참조·억지 tool화·커버리지 누락·반복 실수 패턴을 찾아, **자기자신을 고친다**. 가이드 수정은
  `edit_guidance` 툴로, 스킬 SKILL.md 는 직접 Edit 로. "가이드 점검", "스킬 정리", "aar 고쳐",
  "왜 자꾸 같은 실수" 일 때.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# AAR 자기 점검·개편 (aar_fix)

리뷰 시스템 스스로가 자기 규범을 감사하고 고친다. **근거 없이 가이드를 바꾸지 마라** — 실제
모순·노후·반복 실수만. (bluemeet 의 추측·미검증 금지 규범과 동일 정신.)

## 1) 전부 읽기 (판단 전 필수)
- `review_playbook()` — 현행 리뷰 플레이북 전문.
- `list_guidance()` — 등록된 가이드 목록, 각각 `list_guidance(name)` 로 본문.
- 스킬 SKILL.md 전부(`.claude/skills/*/SKILL.md` 또는 플러그인 `skills/*/SKILL.md`) + 공통수칙(`AgentReviewPlugin/scenario/instructions/_common/공통수칙.md`).
- (있으면) `operator/agent_memory.jsonl` 의 실패 메모 = 반복 실수의 증거.

## 2) 무엇을 찾나 (5종)
1. **모순** — 같은 상황을 두 곳이 다르게 지시(예: 한쪽은 "run_bg 헤드리스", 다른 쪽은 "가시 RDP만"). 어느 게 맞는지 근거로 판정 후 하나로.
2. **노후 참조** — 없는 파일·바뀐 툴명·삭제된 경로를 가리키는 가이드(예: `update_menu_tree` 만 언급하고 `update_tree` 누락). 실재 확인 후 갱신.
3. **억지 tool화** — MCP tool 로 만들었지만 실은 **워크플로/지침이라 skill 이어야 하는 것**. 반대로 skill 에 박아뒀지만 매번 도구가 해야 하는 것. 성격에 맞게 재배치 제안.
4. **커버리지 누락** — 적용 시나리오인데 아무 스킬도 안 다루는 것(aar_review 원장과 대조).
5. **반복 실수 패턴** — memory/보고서에서 같은 실수가 반복되면(예: 스코프 임의축소, 증적 역방향), 그걸 **막는 규칙을 가이드에 추가**.

## 3) 고치기 (자기 개편)
- **가이드 수정 = `edit_guidance(name, ...)`** — 정확한 지점만:
  - 새 규칙 추가: `edit_guidance(name, append="…")`
  - 문구 교체: `edit_guidance(name, old="…", new="…")`
  - 통째 갱신: `edit_guidance(name, replace="…")`
- **스킬 SKILL.md** 는 `Edit` 로 최소 변경. **무엇을·왜 바꿨는지** 커밋/노트에 근거와 함께.
- 성격 재배치(tool↔skill)는 **제안만** 하고 사용자 확인 후 실행(코드 이동은 파급 큼).

## 4) 검증
- 고친 뒤 다시 `review_playbook()`·`list_guidance()`·스킬을 읽어 **모순이 해소됐는지** 확인. 새 모순을 만들지 않았는지도.
- 바꾼 목록을 표로 보고(어느 가이드/스킬, 무엇→무엇, 근거).

## 절대 규칙
- **추측으로 규범 고치기 금지** — 실제 모순/노후/반복실수만, 근거(어느 두 곳이 충돌, 어느 파일이 없음)를 대고.
- 원본을 함부로 지우지 마라 — append·교체는 정밀하게, 큰 삭제는 사용자 확인.
- 이 스킬 자신(aar_fix)도 점검 대상이다.

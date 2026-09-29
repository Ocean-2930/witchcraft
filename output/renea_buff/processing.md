# 레네아 버프 모션

- 내장 image_gen 사용. 배경 분리와 잘린 붉은 효과 가장자리 추정 보정. 생성 편집으로 세부 형태와 효과 농도에 원본과 차이가 있음.
- 1×8, 셀 512×512, 전체 4096×512 RGBA, 빈 배경 alpha=0. 발 y=448±1. 첫/마지막 동일.
- 원본 약 4.4초 구간, 미리보기 1.590909 FPS로 0~6 반복, 7은 종료 자세. 단발 동작이므로 반복 경계에서 손 자세 변화가 있음.
- 게임 등록: renea / buff, scale=0.91, anchor=[306,448], offset=[0,0]. 기존 idle의 발 기준 y=418과 차이는 anchor로 보정.
- 공통 게임 재생 20 FPS(총 0.4초) 유지. 현재 buff를 지정하는 실제 스킬은 없음. 재시작 후 적용.
- 검증: PNG 규격/여백/발/첫끝 비교, JSON 실제 로더, 실제 텍스처 로드, 단발 종료/재시작/누락 파일, compileall. 밝고 어두운 배경 정렬 검토. 실제 게임 수동 플레이는 수행하지 않음.

## 편집 프롬프트

Use case: background-extraction. Edit target: provided 2048x1024 sprite contact sheet, 4 columns x 2 rows, seven distinct chronological poses and last cell empty. Remove black background to real alpha transparency, including between hair strands and legs, but preserve opaque black armor and sword interiors. Preserve original seven distinct poses, facial expressions, costume, weapon angle, scale, placement and frame order exactly. Preserve red magic ribbons and glow as semitransparent red, remove black matte. Restore only clipped tips of red magic glow near each cell edge with natural tapered fading; do not invent additional effects or change character. Keep grid exactly 4x2 with each character in its original cell and empty eighth cell; keep transparent padding around subjects and complete swords. No text, no checkerboard, no background. Output RGBA transparent PNG.

## 보정 프롬프트

Edit only red translucent magic effects in this 4-column 2-row seven-pose transparent sprite sheet. The red glow is currently clipped into rectangular blocks especially row2 column2, row2 column1 and row1 columns3-4. Remove these rectangular red haze areas; retain only the thin curved magic ribbons, circular magical arc, sword glow and a narrow soft semitransparent halo around them. All glow must taper organically to alpha=0 well inside each cell. Preserve character pixels, seven different poses, black armor, hair, swords, body scale, layout and empty eighth cell. Background remains actual alpha transparency. Do not add anything. Exact same grid positions and dimensions.

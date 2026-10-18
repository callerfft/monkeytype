import os
import json
import re

brain_dir = r"C:\Users\Yohanson\.gemini\antigravity\brain\026a6420-26a5-4315-b063-ed3d0f3d02fd"
transcript_path = os.path.join(brain_dir, ".system_generated", "logs", "transcript_full.jsonl")

def clean_user_text(raw_text):
    if not raw_text:
        return ""
    # Extract content between <USER_REQUEST> and </USER_REQUEST> if present
    match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", raw_text, re.DOTALL)
    if match:
        req = match.group(1).strip()
    else:
        req = raw_text.strip()
    return req

def clean_system_text(raw_text):
    if not raw_text:
        return ""
    # Check if inside <SYSTEM_MESSAGE>
    match = re.search(r"content=(.*)", raw_text, re.DOTALL)
    if match:
        text = match.group(1).strip()
        text = re.sub(r"</SYSTEM_MESSAGE>.*$", "", text, flags=re.DOTALL).strip()
        return text
    return raw_text.strip()

dialogue = []
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue
        source = entry.get("source")
        type_ = entry.get("type")
        content = entry.get("content", "")
        created_at = entry.get("created_at", "")
        step_index = entry.get("step_index", 0)

        if type_ == "USER_INPUT":
            clean_txt = clean_user_text(content)
            dialogue.append({
                "step": step_index,
                "time": created_at,
                "role": "Пользователь",
                "text": clean_txt
            })
        elif type_ == "PLANNER_RESPONSE" and content:
            dialogue.append({
                "step": step_index,
                "time": created_at,
                "role": "Ассистент",
                "text": content.strip()
            })
        elif type_ == "SYSTEM_MESSAGE" and content:
            sys_txt = clean_system_text(content)
            if any(k in sys_txt for k in ["## ", "Прогресс", "Статус", "PASSED", "FAIL", "Завершено", "Аудит"]):
                dialogue.append({
                    "step": step_index,
                    "time": created_at,
                    "role": "Отчёт системы / Субагентов",
                    "text": sys_txt
                })

output_md = r"c:\Users\Yohanson\Documents\Projects\LangType\LinguaType_Chat_History_026a6420.md"
with open(output_md, "w", encoding="utf-8") as out:
    out.write("# История чата: LinguaType Project Architecture Overview\n\n")
    out.write(f"- **ID диалога**: `026a6420-26a5-4315-b063-ed3d0f3d02fd`\n")
    out.write(f"- **Всего ключевых сообщений**: {len(dialogue)}\n\n")
    out.write("---\n\n")

    for item in dialogue:
        role = item["role"]
        time = item["time"]
        step = item["step"]
        text = item["text"]
        icon = "👤" if role == "Пользователь" else ("🤖" if role == "Ассистент" else "📊")
        out.write(f"### {icon} {role} `[Шаг {step} | {time}]`\n\n")
        out.write(f"{text}\n\n---\n\n")

print(f"Success! Extracted {len(dialogue)} entries to {output_md}")

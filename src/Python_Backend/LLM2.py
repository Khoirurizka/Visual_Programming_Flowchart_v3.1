from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# base_model_path = "/home/ai/Desktop/skyler/TAIDE_llama_finetune_v6"
base_model_path = "TAIDE_v7"
# 載入 tokenizer 並設定 pad token
tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token


model = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    device_map="cuda:1",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True
)
model.eval()

def generate_response(question: str, option: int ,max_length: int = 100) -> str:
    if option == 1:
        # prompt = f"""是有機器手臂且要做任務計劃的機器人，將一個複雜任務轉變為最終的目標，必須有邏輯。以下為幾個可以用的格式，舉例來說，(on-A-table):要把A放下來，A最終狀態就會是(on-A-table)。(lock-A-B):表示最終A要鎖或安裝在B上，例如把red_wire鎖或安裝在電源供應器上且電源供應器的位置為6則要輸出(lock-red_wire-terminal_6)，如沒有說安裝位置B請輸出(lock-red_wire-trminal_no_number)。(holding-A):表示機器手臂最終將拿著A物體。(insert-A-B):表示最終A要insert在B上，例如把blue_wire放置在電源供應器上且電源供應器的位置3則要輸出(insert-blue_wire-terminal_3)，如沒有說insert的位置請輸出(inserted A power_supply_no_number)。 列出現在任務中要達成的最終目標。出現red wire或是其他線，嚴格輸出成color_wire 這樣的格式，color依照狀況代換。如A線的位置在terminal_6，則他左邊的位置為6-1=5為terminal_5，右邊的位置為6+1=7為terminal_7。在最後要加上一個(end)。舉例任務:你可以把藍色電線插入第5個電源供應器嗎，請幫我把綠色電線安裝在電源供應器的第6個位置，舉例回答:(insert-blue_wire-terminal_5) (lock-green_wire-terminal_6) (end)。現在任務:<start>{question}<end>。列出現在任務中要達成的最終目標，只要回覆上述指定格式不要有其他敘述。"""
        prompt = f"""你是有機器手臂且要做任務計劃的機器人，將一個複雜任務轉變為最終的目標，必須有邏輯。以下為幾個可以用的格式，舉例來說，(on-A-table):要把A放下來，A最終狀態就會是(on-A-table)。(lock-A-B):表示最終A要鎖或安裝在B上，例如把red_wire鎖或安裝在電源供應器上且電源供應器的位置為6則要輸出(lock-red_wire-terminal_6)。(holding-A):表示機器手臂最終將拿著A物體。(insert-A-B):表示最終A要insert在B上，例如把blue_wire放置在電源供應器上且電源供應器的位置3則要輸出(insert-blue_wire-terminal_3)。列出現在任務中要達成的最終目標。出現red wire或是其他線，嚴格輸出成color_wire 這樣的格式，color依照狀況代換。如A線的位置在terminal_6，則他左邊的位置為6-1=5為terminal_5，右邊的位置為6+1=7為terminal_7。在最後要加上一個(end)。舉例任務:你可以把藍色電線插入第5個電源供應器嗎，請幫我把綠色電線安裝在電源供應器的第6個位置，舉例回答:(insert-blue_wire-terminal_5) (lock-green_wire-terminal_6) (end)。現在任務:<start>{question}<end>。列出現在任務中要達成的最終目標，只要回覆上述指定格式不要有其他敘述。回答:"""
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_length,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=False
            )
        output_ids_trimmed = output_ids[0][inputs.input_ids.shape[1]:]
        text = tokenizer.decode(output_ids_trimmed, skip_special_tokens=True).strip()
        cleaned_text = text.split("(end)")[0].strip()
        def clean_text(text):
            if text.startswith("("):
                first_dash = text.find("-")
                if first_dash != -1:
                    return "(" + text[first_dash + 1:]
            return text
        print(cleaned_text)
        ans = cleaned_text
        return ans
    elif option == 2:
        prompt = f"""你是一個有機器手臂且會做任務的機器人，你要回覆使用者應該執行甚麼。如:(holding-red_wire)表示要表示要把紅線拿起來，(on-blue_wire-table)表示要把藍色電線放在桌上，(insert-green_wire-terminal_3)表示要把綠色線插入電源供應器第3號位置，(locked-yellow_wire-terminal_6)表示要把黃色電線鎖或是安裝在電源供應器第3號位置，再回覆結束時要加入一個(end)。舉例任務:(insert-red_wire-terminal_2)(lock-blue_wire-terminal_1)(on-green_wire-table)(lock-black_wire-terminal_3)。舉例回答:我會把紅色電線插入第2號電源供應器，然後把藍色電線鎖在第1號電源供應器上，接著把綠色電線放在桌上，最後把黑色電線鎖在第3號電源供應器上。現在任務:<start>{question}<end>，根據現在任務用english回答:"""
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_length,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=False
            )
        output_ids_trimmed = output_ids[0][inputs.input_ids.shape[1]:]
        text = tokenizer.decode(output_ids_trimmed, skip_special_tokens=True).strip()
        cleaned_text = text.split("(end)")[0].strip()
        print(cleaned_text)
        return cleaned_text
    elif option == 3:
        prompt = question
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_length,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=False
            )
        output_ids_trimmed = output_ids[0][inputs.input_ids.shape[1]:]
        text = tokenizer.decode(output_ids_trimmed, skip_special_tokens=True).strip()
        cleaned_text = text.split("(end)")[0].strip()
        return cleaned_text
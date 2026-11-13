from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from huggingface_hub import HfApi
import torch
import os

base_model_path = "taide/Llama-3.1-TAIDE-LX-8B-Chat"
lora_checkpoint_path = "outputs_TAIDE_v7/checkpoint-300"
push_dir = "TAIDE_v7"                              
device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    torch_dtype=torch.float16,
    device_map="cpu",
    trust_remote_code=True
)

print("Loading LoRA and merging weights...")
model = PeftModel.from_pretrained(base_model, lora_checkpoint_path)
model = model.merge_and_unload()

print(f"Saving merged model to: {push_dir}")
model.save_pretrained(push_dir)
tokenizer.save_pretrained(push_dir)



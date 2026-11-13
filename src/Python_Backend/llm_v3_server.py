import re
import torch
import requests
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, Gemma3ForCausalLM
import json

# export CUDA_VISIBLE_DEVICES=1
app = Flask(__name__)

ckpt = "google/gemma-3-1b-it"
model = Gemma3ForCausalLM.from_pretrained(
    ckpt,
    dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(ckpt)

def clean_output(text: str) -> str:
    decoder = json.JSONDecoder()
    start = text.find('{')
    if start == -1:
        raise ValueError("No '{' found in text.")
    obj, end = decoder.raw_decode(text[start:])
    return json.dumps(obj, ensure_ascii=False, indent=2)

def prompt_templete(example):
    return (
        "you are an robot with two arms (arm1, arm2), the user may want you to finish harmonic drive installation task.\n"
        "you have to output ONLY VALID JSON (no markdown, no extra text).\n"
        "JSON format must be:\n"
        "{\n"
        '  "response": "okay, i\'ll help you to install the harmonic drive",\n'
        '  "steps": [\n'
        '    {"id": 1, "arm": "arm1", "action": "pickup", "object": "wave_generator"},\n'
        '    {"id": 2, "arm": "arm1", "action": "hold", "object": "wave_generator"},\n'
        '    {"id": 3, "arm": "arm2", "action": "pickup", "object": "circular_spline"},\n'
        '    {"id": 4, "arm": "arm2", "action": "insert", "object": "circular_spline"}\n'
        "  ]\n"
        "}\n"
        f"now the user: {example}\n"
    )

def llm_predict(question: str):
    formatted_question = prompt_templete(question)
    messages = [
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}]
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": formatted_question}]
        }
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device)

    input_len = inputs["input_ids"].shape[-1]
    generation = model.generate(
        **inputs,
        max_new_tokens=300,
        do_sample=False
    )

    generated_text = tokenizer.decode(generation[0][input_len:], skip_special_tokens=True)
    return clean_output(generated_text)


@app.route('/LLM_GNN', methods=['POST'])
def llm_gnn():
    # Get user input from the request
    print("begin")
    data = request.get_json()

    # Validate the data format
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid data format, missing "message" field'}), 400
    
    # Print the received message
    print(f"Received message: {data['message']}")
    user_input=data['message']

    # Call the LLM model to generate the response
    result = llm_predict(user_input)

    try:
        return jsonify({"message": "Success", "data": result}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to feedback"}), 500


if __name__ == '__main__':
    app.run(host="127.0.0.12", port=8000, debug=True)



from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

class AIModelService:
    def __init__(self):
        self.device = -1  # ✅ CPU 전용
        self.models = {}
        self.tokenizers = {}
        self.max_input_tokens = 900  # 안전하게 900으로 제한

    def load_models(self):
        # ✅ GPT2-XL
        model_name = "openai-community/gpt2-xl"

        tok = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,  # CPU 전용 → float32
        )

        qa_pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tok,
            device=self.device
        )

        self.models["qa_generator"] = qa_pipe
        self.tokenizers["qa_generator"] = tok

        print(f"✅ Q&A 모델 로딩 완료: {model_name}")

    def generate_answer(self, prompt: str, max_new_tokens: int = 300):
        pipe = self.models["qa_generator"]
        tok = self.tokenizers["qa_generator"]

        # ✅ 입력 프롬프트 토큰 길이 자르기
        tokens = tok.encode(prompt, truncation=True, max_length=self.max_input_tokens)
        prompt_truncated = tok.decode(tokens, skip_special_tokens=True)

        out = pipe(
            prompt_truncated,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_p=0.9,
            temperature=0.7,
            repetition_penalty=1.1,
            pad_token_id=tok.eos_token_id
        )
        return out

ai_model_service = AIModelService()

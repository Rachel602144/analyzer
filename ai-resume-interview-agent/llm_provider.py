import os
from dotenv import load_dotenv

load_dotenv()

# Local model support
import threading

_local_lock = threading.Lock()


def _lazy_import_transformers():
    # Import lazily to avoid heavy imports at module import time
    global AutoTokenizer, AutoModelForSeq2SeqLM, torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    return AutoTokenizer, AutoModelForSeq2SeqLM, torch


def _format_messages(messages):
    # Simple linearization of messages for seq2seq models
    out = []
    for m in messages:
        role = getattr(m, 'type', None) or getattr(m, 'role', None) or 'human'
        if role == 'system':
            prefix = 'System:'
        elif role == 'human':
            prefix = 'Human:'
        elif role == 'ai' or role == 'assistant':
            prefix = 'Assistant:'
        else:
            prefix = f'{str(role).capitalize()}:'
        out.append(prefix + ' ' + str(getattr(m, 'content', '')))
    return '\n'.join(out)


def get_llm():
    """Return an LLM object compatible with the rest of the app.

    Priority:
    1. Google GenAI Gemma model (if GEMINI_API_KEY or GOOGLE_API_KEY is provided)
    2. Local HF seq2seq model (flan-t5-small) as a free fallback
    """
    google_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if google_api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model="gemma-4-31b-it",
            google_api_key=google_api_key,
            temperature=0,
        )

    # Local fallback: implement a minimal chat-like wrapper that matches
    # langchain_core BaseChatModel semantics sufficiently for this app.
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage
    from langchain_core.outputs import ChatResult, ChatGeneration

    class LocalChatModel(BaseChatModel):
        model_name: str = "google/flan-t5-small"
        max_new_tokens: int = 256
        temperature: float = 0.0

        def __init__(self, **data):
            super().__init__(**data)
            self._tokenizer = None
            self._model = None
            self._device = None

        def _ensure_model(self):
            if self._model is None:
                with _local_lock:
                    if self._model is None:
                        AutoTokenizer, AutoModelForSeq2SeqLM, torch = _lazy_import_transformers()
                        self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                        self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(self._device)

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            # Lazy-load model to avoid long import times until actually needed
            self._ensure_model()
            prompt = _format_messages(messages)
            inputs = self._tokenizer(prompt, return_tensors='pt').to(self._device)
            outputs = self._model.generate(**inputs, max_new_tokens=self.max_new_tokens)
            text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            ai_msg = AIMessage(content=text)
            gen = ChatGeneration(message=ai_msg, text=text)
            return ChatResult(generations=[gen], llm_output={'text': text})

        def _llm_type(self) -> str:
            # Identifier used by langchain_core for the LLM type
            return "local-seq2seq"

    return LocalChatModel()

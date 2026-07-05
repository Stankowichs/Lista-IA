"""
Bridge para integração com a API da Anthropic (Claude).
Permite entrada em linguagem natural, explicações enriquecidas
e sugestão automática de regras.
"""
from __future__ import annotations
import json
import os
from knowledge_base.kb import KnowledgeBase


class LLMBridge:
    MODEL = "claude-sonnet-4-6"

    def __init__(self, kb: KnowledgeBase, api_key: str | None = None) -> None:
        self.kb = kb
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._client = None

    def is_available(self) -> bool:
        return bool(self.api_key)

    def _client_instance(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Instale o pacote anthropic: pip install anthropic"
                )
        return self._client

    # ── NL → Facts ─────────────────────────────────────────────────────────

    def parse_natural_language(self, text: str) -> dict:
        """
        Converte descrição em linguagem natural em fatos estruturados.
        Retorna {atributo: valor} conforme possible_values do domínio.
        """
        client = self._client_instance()
        possible = json.dumps(self.kb.possible_values, ensure_ascii=False, indent=2)
        prompt = f"""Você é um assistente especialista em extração de informações médicas.

O usuário descreveu sintomas/condições em linguagem natural. Converta em um JSON
com os atributos e valores exatamente como aparecem na lista abaixo.

Atributos e valores válidos do sistema:
{possible}

Texto do usuário: "{text}"

Regras:
- Use SOMENTE atributos e valores listados acima.
- Inclua apenas o que puder ser claramente inferido do texto.
- Retorne APENAS o JSON, sem explicações.

Exemplo de saída: {{"febre": "alta", "tosse": "seca", "dor_muscular": "sim"}}"""

        response = client.messages.create(
            model=self.MODEL,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        start, end = raw.find("{"), raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
        return {}

    # ── Technical → Natural explanation ────────────────────────────────────

    def explain_naturally(self, technical: str) -> str:
        """Reformula uma explicação técnica em linguagem natural acessível."""
        client = self._client_instance()
        prompt = f"""Você é um médico explicando um diagnóstico ao paciente de forma clara e empática.

O sistema especialista gerou a seguinte explicação técnica:
{technical}

Reescreva isso em linguagem simples e acessível, mantendo precisão médica.
Não use jargões técnicos como "encadeamento" ou "regra de produção"."""

        response = client.messages.create(
            model=self.MODEL,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    # ── Rule suggestion ────────────────────────────────────────────────────

    def suggest_rules(self, description: str) -> list[dict]:
        """Sugere novas regras de produção para o domínio descrito."""
        client = self._client_instance()
        examples = "\n".join(str(r) for r in self.kb.rules[:6])
        prompt = f"""Você é um especialista em sistemas especialistas.

Domínio: {description}

Regras existentes (exemplos):
{examples}

Atributos disponíveis: {list(self.kb.possible_values.keys())}

Sugira 3 novas regras de produção no formato JSON abaixo.
Retorne APENAS o array JSON, sem explicações.

[
  {{
    "id": "R_NOVO_1",
    "name": "Nome da Regra",
    "conditions": [
      {{"attribute": "attr", "value": "val"}}
    ],
    "conclusion": {{"attribute": "suspeita", "value": "diagnostico"}},
    "description": "Descrição"
  }}
]"""

        response = client.messages.create(
            model=self.MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        start, end = raw.find("["), raw.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
        return []

    # ── Interactive chat ───────────────────────────────────────────────────

    def chat(self, user_message: str, context: str = "") -> str:
        """Conversa livre com contexto do diagnóstico atual."""
        client = self._client_instance()
        system = (
            "Você é um assistente de um sistema especialista médico. "
            "Responda de forma clara, educada e dentro do contexto fornecido. "
            "Sempre reforce que o sistema é educacional e não substitui consulta médica."
        )
        content = f"Contexto do diagnóstico:\n{context}\n\nPergunta: {user_message}" \
            if context else user_message

        response = client.messages.create(
            model=self.MODEL,
            max_tokens=600,
            system=system,
            messages=[{"role": "user", "content": content}],
        )
        return response.content[0].text.strip()

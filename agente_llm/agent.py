"""
Agente de Triagem Médica — loop de agente com tool use do SDK Anthropic.

Fluxo:
  1. Usuário descreve sintomas em linguagem natural.
  2. Claude chama list_symptoms para conhecer o vocabulário do sistema.
  3. Claude chama search_medical_cases com o vetor binário extraído.
  4. Claude interpreta os resultados CBR e responde ao usuário.
  5. Repete até stop_reason == "end_turn".
"""

import json
import os
import anthropic
from tools import list_symptoms, search_medical_cases

MODEL = os.environ.get("AGENT_MODEL", "claude-opus-4-8")
MAX_TOKENS = int(os.environ.get("AGENT_MAX_TOKENS", "2048"))

TOOLS: list[dict] = [
    {
        "name": "list_symptoms",
        "description": (
            "Retorna a lista dos 20 sintomas rastreados pela base de casos médicos. "
            "Use esta ferramenta primeiro para conhecer os nomes exatos dos sintomas "
            "antes de chamar search_medical_cases."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "search_medical_cases",
        "description": (
            "Busca na base CBR (Raciocínio Baseado em Casos) usando similaridade de cosseno. "
            "Recebe um dicionário de sintomas (1 = presente, 0 = ausente) e retorna os "
            "3 casos mais similares com diagnóstico e tratamento sugerido. "
            "Os nomes dos sintomas devem vir exatamente da ferramenta list_symptoms."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symptoms": {
                    "type": "object",
                    "description": (
                        "Dicionário mapeando nome_do_sintoma → 0 ou 1. "
                        "Inclua apenas sintomas mencionados explicitamente pelo paciente. "
                        "Sintomas não mencionados podem ser omitidos (tratados como 0)."
                    ),
                    "additionalProperties": {"type": "integer", "enum": [0, 1]},
                }
            },
            "required": ["symptoms"],
        },
    },
]

SYSTEM = """\
Você é um assistente de triagem médica que combina linguagem natural com um \
sistema CBR (Case-Based Reasoning). Seu papel é:

1. Entender os sintomas descritos pelo usuário em linguagem natural.
2. Chamar list_symptoms para conhecer o vocabulário exato do sistema.
3. Mapear os sintomas relatados para o vetor binário e chamar search_medical_cases.
4. Interpretar os resultados: o caso com maior similarity_pct é o diagnóstico \
   principal; os demais são diferenciais.
5. Apresentar diagnóstico, tratamento e confiança de forma clara e empática.
6. Sempre enfatizar que este sistema é EDUCACIONAL e não substitui consulta médica.

Se o usuário fizer perguntas de acompanhamento com novos sintomas, repita o ciclo \
de ferramentas conforme necessário.\
"""


def _execute_tool(name: str, tool_input: dict) -> str:
    if name == "list_symptoms":
        result = list_symptoms()
    elif name == "search_medical_cases":
        result = search_medical_cases(tool_input.get("symptoms", {}))
    else:
        result = {"error": f"Ferramenta desconhecida: {name}"}
    return json.dumps(result, ensure_ascii=False, indent=2)


def run_agent_turn(messages: list, verbose: bool = True) -> str:
    client = anthropic.Anthropic()

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            thinking={"type": "adaptive"},
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if verbose:
                        print(f"  [ferramenta: {block.name}]", flush=True)
                    output = _execute_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": output,
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
        else:
            return f"[stop_reason inesperado: {response.stop_reason}]"

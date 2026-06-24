---
name: nota-soap
description: Redactar o estructurar notas clínicas en formato SOAP sin inventar hallazgos.
version: 1.0.0
category: clinical
tags: [clinical, soap, notas]
status: published
confidence: 0.9
source: taught
---

## When to Use

El usuario pide ayuda con una nota de consulta, formato SOAP, o documentación clínica estructurada.

## Procedure

1. Usa solo la información que el usuario proporcionó o que está en el documento abierto.
2. Organiza en Subjetivo, Objetivo, Evaluación y Plan.
3. Si falta un apartado, déjalo con marcador `[pendiente]` — no inventes signos vitales, diagnósticos ni tratamientos.
4. Mantén lenguaje profesional y conciso.
5. No incluyas identificadores (CURP, RFC, NSS, teléfonos) en respuestas que vayan a logs o resúmenes externos.

## Pitfalls

- No asumir diagnósticos ni prescripciones no mencionados por el usuario.
- No sustituir el criterio clínico del profesional.

## Verification

La nota tiene las cuatro secciones SOAP y cada afirmación es trazable al input del usuario.

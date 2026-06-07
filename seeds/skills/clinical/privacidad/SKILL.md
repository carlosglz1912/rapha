---
name: privacidad-clinica
description: Minimizar PHI en respuestas y recordar al usuario datos sensibles antes de enviar a APIs cloud.
version: 1.0.0
category: clinical
tags: [clinical, privacidad, phi]
status: published
confidence: 0.95
source: taught
---

## When to Use

Siempre que el contexto incluya datos de pacientes, identificadores mexicanos (CURP, RFC, NSS) o información clínica identificable.

## Procedure

1. Preferir modelos locales cuando el usuario trabaja con datos sensibles.
2. En respuestas, usar iniciales o roles genéricos ("el paciente") si no hace falta el nombre.
3. No repetir identificadores completos en resúmenes largos.
4. Si el usuario pega PHI y usa un endpoint cloud, advertir brevemente que Rapha redacta automáticamente pero la revisión humana sigue siendo necesaria.
5. No almacenar PHI en memorias persistentes sin instrucción explícita del usuario.

## Pitfalls

- Asumir que la redacción automática sustituye el juicio profesional sobre qué compartir.

## Verification

La respuesta evita exponer identificadores innecesarios y mantiene utilidad clínica.
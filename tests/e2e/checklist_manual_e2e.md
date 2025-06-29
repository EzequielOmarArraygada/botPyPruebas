# Checklist Manual E2E - Bot de Casos Discord

## Flujos de Casos

- [ ] **Registrar un caso de cambio/devolución**
    - [ ] El caso aparece correctamente en la hoja de Google Sheets.
    - [ ] Se envía la notificación al canal correcto en Discord.
    - [ ] El embed tiene todos los campos correctos (N° de Pedido, N° de Caso, Tipo de Solicitud, etc.).
    - [ ] El usuario es mencionado correctamente si corresponde.

- [ ] **Registrar una solicitud de envío**
    - [ ] El caso aparece en la hoja de Google Sheets.
    - [ ] Se notifica en el canal correcto.
    - [ ] El embed tiene los campos correctos.

- [ ] **Registrar un reembolso**
    - [ ] El caso aparece en la hoja de Google Sheets.
    - [ ] Se notifica en el canal correcto.
    - [ ] El embed tiene los campos correctos.

- [ ] **Registrar un reclamo ML**
    - [ ] El caso aparece en la hoja de Google Sheets.
    - [ ] Se notifica en el canal correcto.
    - [ ] El embed tiene los campos correctos.

- [ ] **Registrar una pieza faltante**
    - [ ] El caso aparece en la hoja de Google Sheets.
    - [ ] Se notifica en el canal correcto.
    - [ ] El embed tiene los campos correctos.

- [ ] **Registrar una cancelación**
    - [ ] El caso aparece en la hoja de Google Sheets.
    - [ ] Se notifica en el canal correcto.
    - [ ] El embed tiene los campos correctos.

## Flujos de Tareas

- [ ] **Iniciar una tarea desde el panel**
    - [ ] El embed de tarea aparece en el canal de registro.
    - [ ] El botón "⏸️ Pausar" está visible.

- [ ] **Pausar la tarea**
    - [ ] El estado en la hoja cambia a "Pausada".
    - [ ] El botón cambia a "▶️ Reanudar".
    - [ ] El embed se actualiza correctamente.

- [ ] **Reanudar la tarea**
    - [ ] El estado en la hoja cambia a "En proceso".
    - [ ] El botón vuelve a "⏸️ Pausar".
    - [ ] El embed se actualiza correctamente.

- [ ] **Finalizar la tarea**
    - [ ] El estado en la hoja cambia a "Finalizada".
    - [ ] El embed se actualiza y desaparecen los botones.
    - [ ] Se muestra la cantidad de casos gestionados si corresponde.

## Comando de verificación de errores

- [ ] **Ejecutar `/verificar-errores`**
    - [ ] Se notifican los errores en los canales correctos.
    - [ ] Los embeds de error tienen los campos correctos y las menciones funcionan.
    - [ ] El campo "Observaciones" aparece solo si corresponde.

## Casos límite y validaciones

- [ ] **Intentar registrar un pedido duplicado**
    - [ ] Se muestra el mensaje de error correspondiente y no se guarda el duplicado.

- [ ] **Probar con campos vacíos o inválidos**
    - [ ] Se muestran los mensajes de validación correctos y no se permite avanzar.

- [ ] **Probar con usuarios sin permisos**
    - [ ] Los comandos restringidos muestran el mensaje de error adecuado.

- [ ] **Verificar que los embeds no muestran campos N/A innecesarios**
    - [ ] Solo aparecen los campos que existen en la hoja correspondiente.

---

**Recomendación:**
- Ejecuta este checklist antes de cada release importante o después de cambios grandes.
- Marca cada ítem a medida que lo verificas.
- Si encuentras un error, anótalo y repite el flujo tras corregirlo. 
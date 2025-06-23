# Configuración de Rangos de Google Sheets

## 🔧 Problema Identificado

El error `APIError: [400]: Unable to parse range: 'Abastible'!SOLICITUDES BGH 2025!A:K` indica que la variable `GOOGLE_SHEET_RANGE_CASOS_READ` tiene un formato incorrecto.

## 📋 Formatos Correctos de Rangos

### ✅ Formatos Válidos:
- `A:K` - Rango simple de columnas
- `A1:K100` - Rango específico de celdas
- `'SOLICITUDES BGH 2025'!A:K` - Rango con nombre de pestaña
- `'Hoja 1'!A1:K100` - Rango específico con nombre de pestaña

### ❌ Formatos Incorrectos:
- `'Abastible'!SOLICITUDES BGH 2025!A:K` - Múltiples separadores `!`
- `A:K!` - Separador al final
- `!A:K` - Separador al inicio

## 🛠️ Solución

### Opción 1: Usar solo el rango (Recomendado)
```
GOOGLE_SHEET_RANGE_CASOS_READ=A:K
```

### Opción 2: Usar rango con nombre de pestaña
```
GOOGLE_SHEET_RANGE_CASOS_READ='SOLICITUDES BGH 2025'!A:K
```

### Opción 3: Usar rango específico
```
GOOGLE_SHEET_RANGE_CASOS_READ=A1:K1000
```

## 🔍 Verificación

Para verificar que tu configuración es correcta, ejecuta:
```bash
python check_sheets_config.py
```

Este script te mostrará:
- Si las hojas son accesibles
- Qué pestañas están disponibles
- Si el rango es válido
- Sugerencias de corrección

## 📝 Variables Relacionadas

### Para Factura A:
```
GOOGLE_SHEET_ID_FAC_A=tu_id_de_hoja_aqui
GOOGLE_SHEET_RANGE_FAC_A=A:E
```

### Para Casos:
```
GOOGLE_SHEET_ID_CASOS=tu_id_de_hoja_aqui
GOOGLE_SHEET_RANGE_CASOS=A:J
GOOGLE_SHEET_RANGE_CASOS_READ=A:K
```

### Para Búsqueda:
```
GOOGLE_SHEET_SEARCH_SHEET_ID=tu_id_de_hoja_aqui
GOOGLE_SHEET_SEARCH_SHEETS=Sheet1,Sheet2,Sheet3
```

## ⚠️ Notas Importantes

1. **Nombres de pestañas**: Si el nombre contiene espacios o caracteres especiales, debe estar entre comillas simples
2. **Rangos**: Siempre deben tener el formato `columna_inicio:columna_fin` o `celda_inicio:celda_fin`
3. **Separadores**: Solo usar un `!` para separar nombre de pestaña del rango
4. **Espacios**: Evitar espacios extra en los rangos

## 🚀 Próximos Pasos

1. Corrige la variable `GOOGLE_SHEET_RANGE_CASOS_READ` en Railway
2. Ejecuta `python check_sheets_config.py` para verificar
3. Reinicia el bot
4. Verifica que no haya más errores en los logs 
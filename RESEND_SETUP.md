# Guía de migración a Resend (alternativa a Gmail)

## Paso 1: Crear cuenta en Resend
1. Ve a https://resend.com
2. Regístrate con tu email
3. Verifica tu email
4. Ve a la sección "API Keys"
5. Copia tu API Key

## Paso 2: Configurar en Railway
En Railway Settings > Variables, reemplaza la configuración de MAIL por:

RESEND_API_KEY=re_xxxxxxxxxxxxx

## Paso 3: El código ya está listo
El archivo correo_utils.py ya tiene soporte para Resend automáticamente

## Ventajas de Resend:
✓ Funciona perfectamente con Railway (sin problemas de firewall)
✓ 100 emails gratis al mes
✓ Muy confiable y rápido
✓ API simple
✓ Dominio personalizado opcional

## Configuración alternativa: SendGrid
Si prefieres SendGrid en lugar de Resend:

1. Ve a https://sendgrid.com
2. Regístrate
3. Copia tu API Key
4. En Railway agrega: SENDGRID_API_KEY=SG_xxxxxxxxxxxxx

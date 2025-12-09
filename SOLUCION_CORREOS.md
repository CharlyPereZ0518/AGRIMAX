# SOLUCIÓN RÁPIDA: Correos en Railway

## El problema:
Railway bloquea conexiones a SMTP de Gmail por razones de seguridad.
Error: `[Errno 101] Network is unreachable`

## La solución:
Usar **Resend** (servicio gratuito y confiable)

## Pasos (5 minutos):

### 1. Crear cuenta en Resend
- Ve a: https://resend.com
- Haz clic en "Sign Up"
- Verifica tu email
- ✓ Cuenta creada

### 2. Obtener API Key
- En tu dashboard de Resend
- Busca "API Keys" en el menú
- Haz clic en "Create API Key"
- Copia la clave (empieza con `re_`)

### 3. Configurar en Railway
- Abre tu proyecto en Railway
- Ve a: Settings > Variables
- Agrega nueva variable:
  - Nombre: `RESEND_API_KEY`
  - Valor: (la clave que copiaste)
- Haz clic en "Add Variable"
- ✓ Configurado

### 4. Deploy
- Haz un nuevo deploy en Railway
- Push tu código con los cambios

### 5. Listo
- Los correos ahora se enviarán automáticamente
- No necesitas cambiar nada en tu código

## ¿Por qué funciona?
- Resend usa una infraestructura confiable
- Railway permite conexiones HTTPS a Resend
- API simple y rápida
- 100 emails gratis al mes (más que suficiente)

## Verificar que funciona:
Ejecuta este script en Railway:
```bash
python test_resend.py
```

## Preguntas frecuentes:

**¿Y si Resend falla?**
El código tiene fallback automático a Gmail SMTP.

**¿Cuesta dinero?**
No, Resend es gratis hasta 100 emails/mes.

**¿Qué dominio usa para enviar?**
Por defecto usa `noreply@resend.dev`, pero puedes configurar tu propio dominio.

## Pasos alternativos si no quieres Resend:

Usa SendGrid en lugar:
1. Ve a: https://sendgrid.com
2. Regístrate gratis
3. Obtén tu API Key
4. En Railway: `SENDGRID_API_KEY=SG_xxxxx`
(Requiere actualizar el código para SendGrid)

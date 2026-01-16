# Sistema de Chat en Vivo - Fluxa shop

## 🎯 Funcionalidades Implementadas

### Para Clientes:
1. **Widget flotante** - Botón de chat en la esquina inferior derecha (visible solo para clientes autenticados)
2. **Inicio de conversación** - Los clientes pueden iniciar chat con soporte
3. **Vista de conversaciones** - Ver historial de chats en `/chat/`
4. **Mensajes en tiempo real** - Polling cada 3 segundos para nuevos mensajes
5. **Notificaciones visuales** - Contador de mensajes sin leer

### Para Administradores:
1. **Panel de soporte** - Acceso desde el menú superior "💬 Soporte"
2. **Ver todas las conversaciones** - Lista completa de chats de clientes
3. **Responder mensajes** - Chat en tiempo real con clientes
4. **Cerrar conversaciones** - Marcar chats como resueltos
5. **Admin Django** - Gestión completa desde `/admin/`

## 📋 URLs Disponibles

- `/chat/` - Lista de conversaciones
- `/chat/start/` - Iniciar nueva conversación
- `/chat/conversation/<id>/` - Vista detallada de chat
- `/chat/api/send/<id>/` - API para enviar mensajes (AJAX)
- `/chat/api/messages/<id>/` - API para obtener mensajes (AJAX)
- `/chat/api/close/<id>/` - API para cerrar conversación (solo admin)

## 🎨 Características de Diseño

- ✅ Widget flotante con gradiente indigo-purple
- ✅ Interfaz responsiva y moderna
- ✅ Mensajes con burbujas estilo WhatsApp
- ✅ Indicadores de estado (activo/resuelto)
- ✅ Contadores de mensajes sin leer
- ✅ Animaciones suaves y transiciones
- ✅ Bordes redondeados consistentes con el sistema

## 🔧 Tecnologías Utilizadas

- **Backend**: Django con modelos ChatConversation y ChatMessage
- **Frontend**: Tailwind CSS + JavaScript vanilla
- **Tiempo Real**: AJAX Polling (3 segundos)
- **Permisos**: Decorador `@login_required` en todas las vistas

## 📊 Modelos de Base de Datos

### ChatConversation
- `user` - Usuario que inicia el chat
- `created_at` - Fecha de creación
- `updated_at` - Última actualización
- `is_active` - Si está activa
- `is_resolved` - Si fue resuelta

### ChatMessage
- `conversation` - Conversación a la que pertenece
- `sender` - Usuario que envió el mensaje
- `message` - Contenido del mensaje
- `created_at` - Fecha de envío
- `is_read` - Si fue leído

## 🚀 Cómo Usar

### Como Cliente:
1. Inicia sesión en la tienda
2. Haz clic en el botón flotante de chat (esquina inferior derecha)
3. Escribe tu mensaje y presiona enviar
4. Espera respuesta del equipo de soporte

### Como Administrador:
1. Inicia sesión como staff
2. Ve a "💬 Soporte" en el menú superior
3. Selecciona una conversación para responder
4. Escribe y envía mensajes
5. Cierra la conversación cuando esté resuelta

## 🎯 Próximas Mejoras Posibles

- [ ] WebSockets con Django Channels (tiempo real verdadero)
- [ ] Notificaciones push
- [ ] Envío de archivos e imágenes
- [ ] Soporte para múltiples agentes
- [ ] Chat bots con IA
- [ ] Historial de conversaciones archivadas
- [ ] Estadísticas de tiempo de respuesta
- [ ] Encuestas de satisfacción post-chat

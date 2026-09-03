# EcoMatch ♻️

Plataforma web de economía circular que conecta generadores de residuos con receptores mediante un agente de IA potenciado por GLM 5.2.

## Stack

- **Vite** + **React 19** — bundler y UI
- **React Router v7** — routing
- **Tailwind CSS v4** — estilos (paleta eco/tierra)
- **Axios** — cliente HTTP con interceptor de auth

## Estructura

```
src/
├── components/      # Componentes reutilizables (Navbar, Logo, ProtectedRoute)
├── pages/           # Rutas/pantallas (Login, Dashboard, Chat, NotFound)
├── lib/             # Lógica transversal (api, auth, constants)
├── assets/          # Recursos estáticos
├── App.jsx          # Router + providers
├── main.jsx         # Entry point
└── index.css        # Tailwind + tema
```

## Scripts

```bash
npm install      # instalar dependencias
npm run dev      # servidor de desarrollo (http://localhost:5173)
npm run build    # build de producción
npm run preview  # previsualizar build
npm run lint     # linter (oxlint)
```

## Pantallas (Sprint 1)

| Ruta        | Descripción                              |
| ----------- | ---------------------------------------- |
| `/login`    | Login de empresas                        |
| `/dashboard`| Panel con stats y acciones rápidas       |
| `/chat`     | Interfaz de chat con el agente IA        |

## Próximos pasos

- [ ] Conectar Login con API real del backend (`POST /api/auth/login`)
- [ ] Conectar Chat con endpoint del agente (`POST /api/agent/chat`)
- [ ] Integrar Google Maps / OpenStreetMap para logística
- [ ] Añadir formulario de registro de empresa
- [ ] Tests E2E con Playwright

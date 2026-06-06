# Nexus-Corp: Arquitectura de Inteligencia Organizacional

**Knowledge-Based Decision Support System (KBDSS)**  
Sistema de Soporte a Decisiones Basado en Conocimiento para empresas de logística y distribución tecnológica.

---

## Descripción del Proyecto

Nexus-Corp KBDSS es una aplicación web empresarial que captura conocimiento organizacional, lo convierte en reglas de negocio y las utiliza para apoyar la toma de decisiones. El sistema implementa un motor de inferencia forward-chaining que evalúa escenarios operacionales y genera recomendaciones priorizadas.

### Problemas que resuelve

- Dependencia de expertos clave
- Pérdida de conocimiento organizacional
- Decisiones inconsistentes entre equipos
- Falta de mecanismos de aprendizaje organizacional

---

## Arquitectura del Sistema

```
nexus-corp/
├── backend/               # FastAPI + Python (Clean Architecture)
│   ├── core/              # Configuración y logging
│   ├── domain/            # Entidades y repositorios (interfaces)
│   ├── application/       # Casos de uso + Motor de Reglas
│   ├── infrastructure/    # BD (SQLAlchemy), repositorios impl., seguridad
│   ├── presentation/      # FastAPI routers + Pydantic schemas
│   └── scripts/           # Seed de datos iniciales
│
└── frontend/              # React + TypeScript + Vite
    └── src/
        ├── components/    # Componentes reutilizables
        ├── pages/         # Páginas de la aplicación
        ├── services/      # Clientes Axios por módulo
        ├── hooks/         # Custom React hooks
        ├── layouts/       # Layouts principal y de autenticación
        ├── context/       # AuthContext (JWT)
        └── types/         # Interfaces TypeScript
```

### Patrón Arquitectural: Clean Architecture

| Capa            | Responsabilidad                                      |
|-----------------|------------------------------------------------------|
| Domain          | Entidades de negocio y contratos de repositorios     |
| Application     | Casos de uso, Motor de Reglas, lógica de negocio     |
| Infrastructure  | Implementaciones concretas (BD, JWT, bcrypt)         |
| Presentation    | Endpoints HTTP, validación de entrada/salida         |

---

## Stack Tecnológico

### Backend
| Tecnología       | Versión  | Uso                           |
|------------------|----------|-------------------------------|
| Python           | 3.11+    | Lenguaje principal            |
| FastAPI          | 0.104    | Framework API REST            |
| SQLAlchemy       | 2.0      | ORM                           |
| Pydantic v2      | 2.5      | Validación y schemas          |
| python-jose      | 3.3      | JWT authentication            |
| passlib[bcrypt]  | 1.7      | Hash de contraseñas           |
| psycopg2-binary  | 2.9      | Driver PostgreSQL             |
| uvicorn          | 0.24     | Servidor ASGI                 |

### Frontend
| Tecnología       | Versión  | Uso                           |
|------------------|----------|-------------------------------|
| React            | 18.2     | Framework UI                  |
| TypeScript       | 5.2      | Tipado estático               |
| Vite             | 5.0      | Build tool                    |
| React Router     | 6.20     | Enrutamiento SPA              |
| Axios            | 1.6      | Cliente HTTP                  |
| TailwindCSS      | 3.3      | Estilos utilitarios           |
| Recharts         | 2.10     | Gráficos y visualizaciones    |
| lucide-react     | 0.294    | Iconografía                   |

### Base de Datos
| Tecnología       | Descripción                                          |
|------------------|------------------------------------------------------|
| PostgreSQL       | Neon serverless (cloud-hosted)                       |

---

## Módulos del Sistema

### 1. Autenticación y Control de Acceso
- Login con JWT (30 min de expiración)
- 4 roles con permisos diferenciados
- Protección de rutas en frontend y backend

### 2. Motor de Reglas (Rule Engine)
Motor forward-chaining que evalúa condiciones sobre:
- `stock_level` (entero 0-100)
- `demand_level` (bajo | medio | alto)
- `risk_level` (bajo | medio | alto)

Operadores soportados: `<`, `<=`, `>`, `>=`, `==`, `!=`

**Ejemplo de reglas precargadas:**
```
SI stock < 20 Y demanda = alto → Generar orden de compra urgente [PRIORIDAD ALTA]
SI stock < 10 Y riesgo = alto  → Activar proveedor alternativo  [PRIORIDAD ALTA]
SI riesgo = alto Y demanda = alto → Revisar cadena de suministro [PRIORIDAD ALTA]
SI stock < 30 Y riesgo = medio → Planificar reposición preventiva [PRIORIDAD MEDIA]
SI stock ≥ 80 Y demanda = bajo → Reducir pedidos próximos 30 días [PRIORIDAD MEDIA]
SI demanda = medio Y stock > 50 → Mantener inventario actual     [PRIORIDAD BAJA]
```

### 3. Análisis What-If
Permite simular escenarios configurando parámetros operacionales y obtener recomendaciones automáticas del motor de reglas.

### 4. Dashboard KPIs
- Total de reglas activas
- Total de escenarios creados
- Total de decisiones registradas
- Recomendaciones aceptadas / rechazadas
- Promedio de satisfacción
- Gráficos con Recharts (BarChart, PieChart, LineChart)

### 5. Retroalimentación
Sistema de calificación (1-5 estrellas) + comentarios por decisión.

### 6. Auditoría
Registro automático de operaciones CREATE/UPDATE/DELETE sobre entidades críticas.

---

## Roles del Sistema

| Rol                   | Permisos                                                          |
|-----------------------|-------------------------------------------------------------------|
| `admin_sistema`       | Usuarios, Roles, Auditoría (acceso completo)                      |
| `admin_conocimiento`  | Crear, editar, eliminar y consultar reglas de conocimiento        |
| `decisor`             | Crear escenarios, ejecutar análisis What-If, ver recomendaciones  |
| `analista`            | Visualizar KPIs, consultar reportes (solo lectura)                |

---

## Requisitos Previos

- **Python 3.11+** instalado
- **Node.js 18+** y **npm** instalados
- Conexión a internet (base de datos en Neon Cloud)

---

## Instalación y Ejecución

### 1. Clonar / Navegar al proyecto

```bash
cd nexus-corp
```

### 2. Configurar y ejecutar el Backend

```bash
# Entrar al directorio backend
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# El archivo .env ya está configurado con la base de datos
# Ejecutar seed (crea tablas + datos iniciales)
python scripts/seed.py

# Iniciar servidor backend
python main.py
```

El backend estará disponible en: **http://localhost:8000**  
Swagger UI (documentación interactiva): **http://localhost:8000/docs**  
ReDoc: **http://localhost:8000/redoc**

### 3. Configurar y ejecutar el Frontend

Abrir una nueva terminal:

```bash
# Entrar al directorio frontend
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará disponible en: **http://localhost:5173**

---

## Credenciales de Prueba

| Usuario     | Contraseña     | Rol                   | Acceso                                      |
|-------------|----------------|-----------------------|---------------------------------------------|
| `admin`     | `admin123`     | admin_sistema         | Usuarios, Roles, Auditoría, todo            |
| `knowledge` | `knowledge123` | admin_conocimiento    | Gestión de reglas de conocimiento           |
| `decisor`   | `decisor123`   | decisor               | Escenarios, Análisis What-If, Decisiones    |
| `analista`  | `analista123`  | analista              | KPIs, Reportes (solo lectura)               |

---

## Variables de Entorno

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql://neondb_owner:npg_HGv1ywVPmR5W@ep-quiet-heart-aqzult8v-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
SECRET_KEY=nexuscorp-super-secret-key-change-in-production-2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

### Frontend (`frontend/.env`)
```
VITE_API_URL=http://localhost:8000/api/v1
```

---

## API REST — Endpoints Principales

| Módulo          | Método | Endpoint                          | Descripción                        |
|-----------------|--------|-----------------------------------|------------------------------------|
| Auth            | POST   | `/api/v1/auth/login`              | Iniciar sesión                     |
| Auth            | GET    | `/api/v1/auth/me`                 | Usuario actual                     |
| Usuarios        | GET    | `/api/v1/users/`                  | Listar usuarios                    |
| Usuarios        | POST   | `/api/v1/users/`                  | Crear usuario                      |
| Roles           | GET    | `/api/v1/roles/`                  | Listar roles                       |
| Reglas          | GET    | `/api/v1/rules/`                  | Listar reglas de conocimiento      |
| Reglas          | POST   | `/api/v1/rules/`                  | Crear regla                        |
| Escenarios      | GET    | `/api/v1/scenarios/`              | Listar escenarios                  |
| Escenarios      | POST   | `/api/v1/scenarios/`              | Crear escenario                    |
| Decisiones      | POST   | `/api/v1/decisions/analyze`       | **Ejecutar análisis What-If**      |
| Decisiones      | GET    | `/api/v1/decisions/`              | Historial de decisiones            |
| Retroalim.      | POST   | `/api/v1/feedback/`               | Registrar retroalimentación        |
| KPIs            | GET    | `/api/v1/kpis/dashboard`          | Dashboard con todos los indicadores|
| Auditoría       | GET    | `/api/v1/audit/`                  | Log de auditoría del sistema       |

---

## Estructura Completa de Archivos

```
nexus-corp/
├── README.md
├── backend/
│   ├── .env
│   ├── .env.example
│   ├── requirements.txt
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging_config.py
│   ├── domain/
│   │   ├── entities/          (9 entidades de dominio)
│   │   └── repositories/      (9 interfaces de repositorio)
│   ├── application/
│   │   ├── use_cases/         (8 módulos de casos de uso)
│   │   └── services/
│   │       └── rule_engine.py (Motor de inferencia forward-chaining)
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── models.py      (Modelos SQLAlchemy 2.0)
│   │   ├── repositories/      (9 implementaciones concretas)
│   │   └── security/
│   │       ├── jwt_handler.py
│   │       └── password_handler.py
│   ├── presentation/
│   │   ├── dependencies.py    (get_current_user, require_role)
│   │   ├── schemas/           (10 módulos Pydantic v2)
│   │   └── api/v1/
│   │       ├── router.py
│   │       └── endpoints/     (10 routers FastAPI)
│   └── scripts/
│       └── seed.py
│
└── frontend/
    ├── .env
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx
        ├── main.tsx
        ├── types/index.ts
        ├── context/AuthContext.tsx
        ├── hooks/             (useAuth, useToast)
        ├── services/          (9 servicios Axios)
        ├── layouts/           (MainLayout, AuthLayout)
        ├── components/
        │   ├── ui/            (10 componentes reutilizables)
        │   ├── Sidebar.tsx
        │   ├── Navbar.tsx
        │   └── ProtectedRoute.tsx
        └── pages/
            ├── auth/LoginPage.tsx
            ├── dashboard/DashboardPage.tsx
            ├── users/UsersPage.tsx
            ├── roles/RolesPage.tsx
            ├── knowledge/KnowledgePage.tsx
            ├── whatif/WhatIfPage.tsx
            ├── decisions/DecisionsPage.tsx
            ├── feedback/FeedbackPage.tsx
            ├── kpis/KPIsPage.tsx
            └── audit/AuditPage.tsx
```

---

## Diagrama Entidad-Relación (simplificado)

```
Role ──────< User >────── AuditLog
              │
              ├──────────< Scenario >──── Decision >──── Recommendation
              │                                 │
              └──────────< Feedback ────────────┘
              
KnowledgeRule ────────────────────────────────>── Recommendation
KPI (independiente)
```

---

## Datos de Demostración

El seed precarga:
- **4 roles** del sistema
- **4 usuarios** (uno por rol)
- **6 reglas de conocimiento** en 2 categorías (inventario, riesgo)
- **3 escenarios** (crisis, operación normal, exceso temporada baja)
- **2 decisiones** con recomendaciones asociadas
- **5 KPIs** de logística (cumplimiento, entrega, satisfacción, costo, rotación)
- **2 retroalimentaciones** con calificaciones de 4 y 5 estrellas

---

## Información del Proyecto

| Campo             | Valor                                             |
|-------------------|---------------------------------------------------|
| Proyecto          | Nexus-Corp: Arquitectura de Inteligencia Organizacional |
| Tipo              | Knowledge-Based Decision Support System (KBDSS)   |
| Universidad       | Universidad Mariano Gálvez de Guatemala           |
| Curso             | Administración de Tecnologías de Información      |
| Versión MVP       | 1.0.0                                             |

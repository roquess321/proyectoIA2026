const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface RegisterParams {
  usuario: string;
  password: string;
  cedula: string;
  nombre: string;
  carrera?: string;
}

export interface LocalLoginParams {
  identificador: string;
  password: string;
}

export interface UserAuthResult {
  ok: boolean;
  id: number;
  usuario: string;
  cedula: string;
  nombre: string;
  carrera: string;
  is_synced: boolean;
  last_sync?: string | null;
  message: string;
}

export interface LinkInswebResult {
  ok: boolean;
  message: string;
  cedula: string;
  inscripciones_count: number;
  parciales_count: number;
  notas_count: number;
}

/**
 * Registra una cuenta local en la base de datos SQLite.
 */
export async function registerLocalUser(params: RegisterParams): Promise<UserAuthResult> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    const errData = await res
      .json()
      .catch(() => ({ detail: "Error al registrar la cuenta local." }));
    throw new Error(errData.detail || `Error de registro (${res.status})`);
  }

  return (await res.json()) as UserAuthResult;
}

/**
 * Inicia sesión con usuario/cédula y contraseña local.
 */
export async function loginLocalUser(params: LocalLoginParams): Promise<UserAuthResult> {
  const res = await fetch(`${API_BASE}/api/auth/login-local`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    const errData = await res
      .json()
      .catch(() => ({ detail: "Credenciales locales inválidas." }));
    throw new Error(errData.detail || `Error al iniciar sesión (${res.status})`);
  }

  return (await res.json()) as UserAuthResult;
}

/**
 * Vincula o re-sincroniza las materias y notas desde InsWeb hacia la cédula de la cuenta.
 */
export async function linkInswebAccount(cedula: string, pin: string): Promise<LinkInswebResult> {
  const res = await fetch(`${API_BASE}/api/auth/link-insweb`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cedula, pin }),
  });

  if (!res.ok) {
    const errData = await res
      .json()
      .catch(() => ({ detail: "Error al sincronizar con INSWEB." }));
    throw new Error(errData.detail || `Error al sincronizar (${res.status})`);
  }

  return (await res.json()) as LinkInswebResult;
}

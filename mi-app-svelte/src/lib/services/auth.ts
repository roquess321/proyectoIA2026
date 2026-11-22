import type { ScraperStreamEvent } from "./scraper";
import { getApiBase } from "./api-base";

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
  const res = await fetch(`${getApiBase()}/api/auth/register`, {
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
  const res = await fetch(`${getApiBase()}/api/auth/login-local`, {
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
  const res = await fetch(`${getApiBase()}/api/auth/link-insweb`, {
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

/**
 * Vincula o re-sincroniza las materias y notas desde InsWeb recibiendo telemetría en vivo vía SSE.
 */
export async function linkInswebAccountStream(
  cedula: string,
  pin: string,
  onEvent: (event: ScraperStreamEvent) => void,
): Promise<LinkInswebResult> {
  const res = await fetch(`${getApiBase()}/api/auth/link-insweb/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({ cedula, pin }),
  });

  if (!res.ok) {
    const errData = (await res
      .json()
      .catch(() => ({ detail: "Error al iniciar la sincronización en vivo con INSWEB." }))) as {
      detail?: string;
    };
    throw new Error(errData.detail || `Error al sincronizar (${res.status})`);
  }

  if (!res.body) {
    throw new Error("El navegador no soporta lectura de flujo SSE.");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";
  let finalResult: LinkInswebResult | null = null;
  let streamError: string | null = null;

  const processBlock = (rawBlock: string): void => {
    const lines = rawBlock.split("\n");
    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line || line.startsWith(":")) continue;
      if (!line.startsWith("data:")) continue;
      const jsonText = line.slice(5).trim();
      if (!jsonText) continue;

      let parsed: ScraperStreamEvent;
      try {
        parsed = JSON.parse(jsonText) as ScraperStreamEvent;
      } catch {
        continue;
      }

      onEvent(parsed);

      if (parsed.type === "complete") {
        finalResult = {
          ok: parsed.ok,
          message: parsed.message,
          cedula: parsed.cedula,
          inscripciones_count: parsed.inscripciones_count,
          parciales_count: parsed.parciales_count,
          notas_count: parsed.notas_count,
        };
      } else if (parsed.type === "error") {
        streamError = parsed.detail || "Error durante el scraping de INSWEB.";
      }
    }
  };

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");

    let sepIdx = buffer.indexOf("\n\n");
    while (sepIdx !== -1) {
      const block = buffer.slice(0, sepIdx);
      buffer = buffer.slice(sepIdx + 2);
      processBlock(block);
      sepIdx = buffer.indexOf("\n\n");
    }
  }

  if (buffer.trim()) {
    processBlock(buffer);
  }

  if (streamError) {
    throw new Error(streamError);
  }

  if (!finalResult) {
    throw new Error(
      "La conexión con el monitor de scraping se cerró antes de completar la sincronización.",
    );
  }

  return finalResult;
}

export interface DeleteUserDataParams {
  usuario?: string;
  cedula: string;
  password: string;
  eliminar_cuenta?: boolean;
}

export interface DeleteUserDataResult {
  ok: boolean;
  cedula: string;
  inscripciones_deleted: number;
  parciales_deleted: number;
  notas_deleted: number;
  account_deleted: boolean;
  snapshot_deleted: boolean;
  message: string;
}

/**
 * Elimina de forma permanente los datos académicos, snapshot JSON y cuenta local del usuario autenticado.
 */
export async function deleteUserData(
  params: DeleteUserDataParams,
): Promise<DeleteUserDataResult> {
  const res = await fetch(`${getApiBase()}/api/auth/delete-data`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    const errData = (await res
      .json()
      .catch(() => ({ detail: "No se pudieron eliminar los datos de la cuenta." }))) as {
      detail?: string;
    };
    throw new Error(errData.detail || `Error al eliminar datos (${res.status})`);
  }

  return (await res.json()) as DeleteUserDataResult;
}

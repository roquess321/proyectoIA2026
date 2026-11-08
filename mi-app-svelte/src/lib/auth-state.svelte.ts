export interface UserSession {
  id?: number;
  usuario?: string;
  cedula: string;
  nombre: string;
  carrera: string;
  isSynced: boolean;
  lastSync?: string | null;
}

const STORAGE_KEY = "fiuna_user_session";

export class AuthState {
  user = $state<UserSession | null>(null);
  isLoggedIn = $derived(this.user !== null);

  constructor() {
    if (typeof window !== "undefined") {
      try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
          this.user = JSON.parse(saved) as UserSession;
        }
      } catch {
        this.user = null;
      }
    }
  }

  login(session: UserSession): void {
    this.user = session;
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
      } catch {
        // Manejo silencioso de cuota de storage
      }
    }
  }

  setSynced(isSynced: boolean, lastSync?: string | null): void {
    if (this.user) {
      const updated: UserSession = {
        ...this.user,
        isSynced,
        lastSync: lastSync || this.user.lastSync,
      };
      this.login(updated);
    }
  }

  logout(): void {
    this.user = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem(STORAGE_KEY);
    }
  }
}

export const authState = new AuthState();

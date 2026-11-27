"""Pruebas de integración de la API FastAPI sobre una base SQLite temporal aislada."""

import os
import tempfile
import unittest
from datetime import datetime, timezone
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database import Base, get_db
from backend.main import app
from backend.models import ChatMessage, ChatSession, Estudiante, Inscripcion, NotaFinal, Parcial


class TestCopilotAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmpdir = tempfile.TemporaryDirectory()
        cls._db_path = os.path.join(cls._tmpdir.name, "test_copilot.db")
        cls._engine = create_engine(
            f"sqlite:///{cls._db_path}",
            connect_args={"check_same_thread": False},
        )
        cls._TestingSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=cls._engine,
        )
        Base.metadata.create_all(bind=cls._engine)

        def override_get_db() -> Generator[Session, None, None]:
            db = cls._TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        cls._prev_override = app.dependency_overrides.get(get_db)
        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()
        if cls._prev_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = cls._prev_override
        cls._engine.dispose()
        cls._tmpdir.cleanup()

    def setUp(self) -> None:
        # Limpiar todas las tablas entre tests para aislamiento estricto
        with self._TestingSessionLocal() as db:
            for model in (ChatMessage, ChatSession, Inscripcion, Parcial, NotaFinal):
                db.query(model).delete()
            from backend.models import UsuarioLocal
            db.query(UsuarioLocal).delete()
            db.query(Estudiante).delete()
            db.commit()

    def test_health_schedule_and_scraper_status(self) -> None:
        r_root = self.client.get("/")
        self.assertEqual(r_root.status_code, 200)
        self.assertEqual(r_root.json().get("status"), "online")

        r_sched = self.client.get("/api/horarios/examenes")
        self.assertEqual(r_sched.status_code, 200)
        self.assertIn("examenes", r_sched.json())

        r_status = self.client.get("/api/scraper/status", params={"check_insweb": "false"})
        self.assertEqual(r_status.status_code, 200)
        self.assertTrue(r_status.json().get("sqlite_ready"))

    def test_auth_register_unique_ci_login_and_delete_data(self) -> None:
        # 1. Rechazo por C.I. demasiado corta (422 Pydantic min_length y 400 tras normalizar dígitos)
        r_short_schema = self.client.post(
            "/api/auth/register",
            json={
                "usuario": "test_short",
                "password": "password123",
                "cedula": "12",
                "nombre": "Alumno Prueba",
            },
        )
        self.assertEqual(r_short_schema.status_code, 422)

        r_short_digits = self.client.post(
            "/api/auth/register",
            json={
                "usuario": "test_short",
                "password": "password123",
                "cedula": "1.2",
                "nombre": "Alumno Prueba",
            },
        )
        self.assertEqual(r_short_digits.status_code, 400)

        # 2. Registro exitoso normalizando puntos de la cédula
        r_reg = self.client.post(
            "/api/auth/register",
            json={
                "usuario": "AlumnoPrueba",
                "password": "password123",
                "cedula": "9.000.123",
                "nombre": "Alumno Prueba",
                "carrera": "Ingeniería Mecatrónica",
            },
        )
        self.assertEqual(r_reg.status_code, 201)
        body = r_reg.json()
        self.assertEqual(body["usuario"], "alumnoprueba")
        self.assertEqual(body["cedula"], "9000123")

        # 3. Bloqueo por usuario duplicado (400) y por cédula duplicada (409)
        r_dup_user = self.client.post(
            "/api/auth/register",
            json={
                "usuario": "alumnoprueba",
                "password": "password123",
                "cedula": "9000999",
                "nombre": "Otro Usuario",
            },
        )
        self.assertEqual(r_dup_user.status_code, 400)

        r_dup_ci = self.client.post(
            "/api/auth/register",
            json={
                "usuario": "segundo_user",
                "password": "password123",
                "cedula": "9000123",
                "nombre": "Duplicado CI",
            },
        )
        self.assertEqual(r_dup_ci.status_code, 409)

        # 4. Login por usuario, por C.I. con puntos, y fallo con clave errónea
        self.assertEqual(
            self.client.post(
                "/api/auth/login-local",
                json={"identificador": "alumnoprueba", "password": "password123"},
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                "/api/auth/login-local",
                json={"identificador": "9.000.123", "password": "password123"},
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                "/api/auth/login-local",
                json={"identificador": "9000123", "password": "wrong_password"},
            ).status_code,
            401,
        )

        # Sembrar datos académicos asociados a la cédula ficticia 9000123
        with self._TestingSessionLocal() as db:
            est = db.query(Estudiante).filter(Estudiante.cedula == "9000123").first()
            est.fecha_actualizacion = datetime.now(timezone.utc)
            db.add(Inscripcion(cedula="9000123", carrera="MCT", asignatura="ESTATICA", semestre="3", estado="NO"))
            db.add(Parcial(cedula="9000123", asignatura="ESTATICA", tipo_examen="Primer Parcial", puntaje=68.0, periodo="2026_C1"))
            db.add(NotaFinal(cedula="9000123", asignatura="CALCULO 1", nota=4, nota_literal="Cuatro", fecha="10/07/2025", nro_acta="100", tipo="Final", aprobado=True))
            db.commit()

        # 5. Rechazo de delete-data con contraseña inválida (datos intactos)
        r_del_fail = self.client.post(
            "/api/auth/delete-data",
            json={
                "cedula": "9000123",
                "usuario": "alumnoprueba",
                "password": "clave_incorrecta",
                "eliminar_cuenta": True,
            },
        )
        self.assertEqual(r_del_fail.status_code, 401)
        self.assertEqual(len(self.client.get("/api/estudiantes/9000123/parciales").json()), 1)

        # 6. Borrado definitivo exitoso con contraseña válida
        r_del_ok = self.client.post(
            "/api/auth/delete-data",
            json={
                "cedula": "9000123",
                "usuario": "alumnoprueba",
                "password": "password123",
                "eliminar_cuenta": True,
            },
        )
        self.assertEqual(r_del_ok.status_code, 200)
        del_body = r_del_ok.json()
        self.assertTrue(del_body["ok"])
        self.assertEqual(del_body["inscripciones_deleted"], 1)
        self.assertEqual(del_body["parciales_deleted"], 1)
        self.assertEqual(del_body["notas_deleted"], 1)
        self.assertTrue(del_body["account_deleted"])

        self.assertEqual(self.client.get("/api/estudiantes/9000123").status_code, 404)
        self.assertEqual(
            self.client.post(
                "/api/auth/login-local",
                json={"identificador": "alumnoprueba", "password": "password123"},
            ).status_code,
            401,
        )

    def test_student_read_endpoints_and_chat_sessions_crud(self) -> None:
        self.assertEqual(self.client.get("/api/estudiantes/9000456").status_code, 404)

        with self._TestingSessionLocal() as db:
            db.add(Estudiante(cedula="9000456", fecha_actualizacion=datetime.now(timezone.utc)))
            db.add(Inscripcion(cedula="9000456", carrera="MCT", asignatura="ELECTRONICA 1", semestre="5", estado="NO"))
            db.add(Parcial(cedula="9000456", asignatura="ELECTRONICA 1", tipo_examen="Primer Parcial", puntaje=55.0, periodo="2026_C1"))
            db.add(NotaFinal(cedula="9000456", asignatura="ESTATICA", nota=3, nota_literal="Tres", fecha="05/07/2025", nro_acta="201", tipo="Final", aprobado=True))
            sess = ChatSession(id="test-session-001", title="Consulta prueba")
            db.add(sess)
            db.flush()
            db.add(ChatMessage(session_id="test-session-001", role="user", content="Hola"))
            db.add(ChatMessage(session_id="test-session-001", role="model", content="Hola estudiante"))
            db.commit()

        r_est = self.client.get("/api/estudiantes/9.000.456")
        self.assertEqual(r_est.status_code, 200)
        self.assertEqual(len(self.client.get("/api/estudiantes/9000456/inscripciones").json()), 1)
        self.assertEqual(len(self.client.get("/api/estudiantes/9000456/parciales").json()), 1)
        self.assertEqual(len(self.client.get("/api/estudiantes/9000456/notas").json()), 1)

        r_sessions = self.client.get("/api/chat/sessions")
        self.assertEqual(r_sessions.status_code, 200)
        self.assertEqual(len(r_sessions.json()), 1)
        self.assertEqual(r_sessions.json()[0]["message_count"], 2)

        r_hist = self.client.get("/api/chat/history/test-session-001")
        self.assertEqual(r_hist.status_code, 200)
        self.assertEqual(len(r_hist.json()["messages"]), 2)

        self.assertEqual(self.client.delete("/api/chat/sessions/test-session-001").status_code, 204)
        self.assertEqual(self.client.get("/api/chat/history/test-session-001").status_code, 404)

    def test_ml_models_and_inference_endpoints(self) -> None:
        r_models = self.client.get("/api/ml/models")
        self.assertEqual(r_models.status_code, 200)
        models_payload = r_models.json()
        self.assertIn("estatica", str(models_payload).lower())

        r_pred = self.client.post(
            "/api/ml/predict",
            json={"materia": "ESTATICA", "primer_parcial": 70, "segundo_parcial": 65, "tplab": 85},
        )
        self.assertEqual(r_pred.status_code, 200)
        pred_data = r_pred.json()
        avg_prob = pred_data["resumen"]["probabilidad_promedio"]
        self.assertGreaterEqual(avg_prob, 0.0)
        self.assertLessEqual(avg_prob, 100.0)

        for payload, expected_stage in (
            ({"materia": "ESTATICA", "primer_parcial": 60}, 1),
            ({"materia": "ESTATICA", "primer_parcial": 60, "tplab": 80}, 2),
            ({"materia": "ESTATICA", "primer_parcial": 60, "tplab": 80, "segundo_parcial": 72}, 3),
        ):
            r_seq = self.client.post("/api/ml/predict-sequential", json=payload)
            self.assertEqual(r_seq.status_code, 200)
            seq_data = r_seq.json()
            self.assertEqual(seq_data["etapa_temporal"], expected_stage)
            self.assertGreaterEqual(seq_data["probabilidad_aprobacion"], 0.0)
            self.assertLessEqual(seq_data["probabilidad_aprobacion"], 100.0)
            self.assertIsNotNone(seq_data.get("comparativa_modelos"))


if __name__ == "__main__":
    unittest.main()

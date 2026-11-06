"""Pruebas funcionales del motor de inferencia de Semana 13."""

import unittest

from src.motor_inferencia import Regla, inferir


class MotorInferenciaTests(unittest.TestCase):
    def test_conclusion_demonstrated(self) -> None:
        rules = [
            Regla("R1", frozenset({"placa_coincide", "registro_activo"}),
                  "correspondencia_registrada"),
            Regla("R2", frozenset({"correspondencia_registrada",
                                   "protocolo_aceptado"}),
                  "autorizar_salida"),
        ]
        initial = {"placa_coincide", "registro_activo", "protocolo_aceptado"}

        final, trace = inferir(initial, rules)

        self.assertIn("autorizar_salida", final)
        self.assertEqual(len(trace), 2)

    def test_conclusion_not_demonstrated(self) -> None:
        initial = {"placa_coincide", "registro_activo"}
        rules = [
            Regla("R1", frozenset({"placa_coincide", "conductor_coincide"}),
                  "identidad_confirmada"),
            Regla("R2", frozenset({"identidad_confirmada"}),
                  "autorizar_salida"),
        ]

        final, trace = inferir(initial, rules)

        self.assertNotIn("identidad_confirmada", final)
        self.assertNotIn("autorizar_salida", final)
        self.assertEqual(trace, [])

    def test_initial_facts_are_not_mutated(self) -> None:
        initial = {"placa_coincide"}
        copy = set(initial)

        inferir(
            initial,
            [Regla("R1", frozenset({"placa_coincide"}),
                   "correspondencia_confirmada")],
        )

        self.assertEqual(initial, copy)

    def test_no_infinite_loop_with_circular_rules(self) -> None:
        rules = [
            Regla("R1", frozenset({"A"}), "B"),
            Regla("R2", frozenset({"B"}), "C"),
            Regla("R3", frozenset({"C"}), "A"),
        ]

        final, trace = inferir({"A"}, rules)

        self.assertEqual(final, {"A", "B", "C"})
        self.assertEqual(len(trace), 2)

    def test_duplicate_conclusion_is_recorded_once(self) -> None:
        initial = {"placa_coincide", "conductor_coincide"}
        rules = [
            Regla("R1", frozenset({"placa_coincide",
                                   "conductor_coincide"}),
                  "correspondencia_confirmada"),
            Regla("R2", frozenset({"placa_coincide",
                                   "conductor_coincide"}),
                  "correspondencia_confirmada"),
        ]

        final, trace = inferir(initial, rules)

        self.assertEqual(trace, [
            "R1: conductor_coincide, placa_coincide => "
            "correspondencia_confirmada"
        ])
        self.assertIn("correspondencia_confirmada", final)

    def test_empty_premises_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "premisas vacias"):
            inferir(set(), [Regla("R0", frozenset(), "conclusion")])


if __name__ == "__main__":
    unittest.main()

from pathlib import Path

from demos.simulation import run_simulation
from src.enums import Currency
from src.report_builder import ReportBuilder


def run_demo() -> None:
    simulation = run_simulation()
    output_directory = Path("reports/day7")
    output_directory.mkdir(parents=True, exist_ok=True)

    builder = ReportBuilder(
        bank=simulation.bank,
        transactions=simulation.transactions,
        audit_log=simulation.processor.audit_log,
    )

    client_report = builder.build_client_report(simulation.clients[0].client_id)
    bank_report = builder.build_bank_report()
    risk_report = builder.build_risk_report()

    print("=== Client report ===")
    print(builder.build_text_report(client_report))
    print("\n=== Bank report ===")
    print(builder.build_text_report(bank_report))
    print("\n=== Risk report ===")
    print(builder.build_text_report(risk_report))

    builder.export_to_json(
        client_report,
        str(output_directory / "client_report.json"),
    )
    builder.export_to_json(
        bank_report,
        str(output_directory / "bank_report.json"),
    )
    builder.export_to_json(
        risk_report,
        str(output_directory / "risk_report.json"),
    )

    builder.export_to_csv(
        client_report["accounts"],
        str(output_directory / "client_accounts.csv"),
    )
    builder.export_to_csv(
        client_report["transactions"],
        str(output_directory / "client_transactions.csv"),
    )

    builder.save_charts(
        output_dir=str(output_directory / "charts"),
        currency=Currency.RUB,
        balance_history=simulation.balance_history,
    )

    print(f"\nReports saved to: {output_directory}")


if __name__ == "__main__":
    run_demo()

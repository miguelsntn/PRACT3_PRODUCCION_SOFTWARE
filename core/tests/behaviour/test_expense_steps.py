from datetime import date
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from core.expense_service import ExpenseService
from core.in_memory_expense_repository import InMemoryExpenseRepository

scenarios("./expense_management.feature")


@pytest.fixture
def context():
    repo = InMemoryExpenseRepository()
    service = ExpenseService(repo)
    return {"service": service, "db": repo}


@given(parsers.parse("un gestor de gastos vacío"))
def empty_manager(context):
    pass


@given(parsers.parse("un gestor con un gasto de {amount:d} euros"))
def manager_with_one_expense(context, amount):
    context["service"].create_expense(
        title="Gasto inicial", amount=amount, description="", expense_date=date.today()
    )


@when(parsers.parse("añado un gasto de {amount:d} euros llamado {title}"))
def add_expense(context, amount, title):
    context["service"].create_expense(
        title=title, amount=amount, description="", expense_date=date.today()
    )


@when(parsers.parse("elimino el gasto con id {expense_id:d}"))
def remove_expense(context, expense_id):
    context["service"].remove_expense(expense_id)


@then(parsers.parse("el total de dinero gastado debe ser {total:d} euros"))
def check_total(context, total):
    assert context["service"].total_amount() == total


@then(parsers.parse("{month_name} debe sumar {expected_total:d} euros"))
def check_month_total(context, month_name, expected_total):
    total_actual = context["totals"].get(month_name, 0)
    assert total_actual == expected_total


@then(parsers.parse("debe haber {expenses:d} gastos registrados"))
def check_expenses_length(context, expenses):
    total = len(context["db"]._expenses)
    assert expenses == total


@when(parsers.parse("actualizo el gasto con id {expense_id:d} sin modificar campos"))
def update_expense_no_changes(context, expense_id):
    context["service"].update_expense(expense_id=expense_id)


@then(parsers.parse("el gasto con id {expense_id:d} mantiene el título"))
def check_title_maintained(context, expense_id):
    expenses = context["service"].list_expenses()
    expense = next((e for e in expenses if e.id == expense_id), None)
    assert expense is not None
    assert expense.title == "Cena"


@when(parsers.parse("calculo el total por mes"))
def calculate_total_by_month_step(context):
    context["totales_mes"] = context["service"].total_by_month()


@then(parsers.parse("el desglose mensual debe estar vacío"))
def check_empty_totals(context):
    assert context["totales_mes"] == {}


@when(parsers.parse("intento añadir un gasto de {amount:d} euros llamado {title}"))
def try_add_expense_zero(context, amount, title):
    try:
        context["service"].create_expense(
            title=title, amount=amount, description="", expense_date=date.today()
        )
    except Exception as e:
        context["error"] = e


@then(parsers.parse("el sistema debe rechazar la operación por importe inválido"))
def check_invalid_amount_error(context):
    assert "error" in context, (
        "El sistema no lanzó ningún error y debería haberlo hecho"
    )
    assert type(context["error"]).__name__ == "InvalidAmountError"

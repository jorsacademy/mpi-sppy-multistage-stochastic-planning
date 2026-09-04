from stoch_planning.cli import main


def test_cli_prints_solution(capsys):
    main()
    out = capsys.readouterr().out
    assert "objective=" in out
    assert "capacity_expansion=" in out
    assert "stage2_low=" in out
    assert "stage2_high=" in out

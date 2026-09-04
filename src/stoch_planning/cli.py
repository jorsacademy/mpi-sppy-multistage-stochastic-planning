from .solve import solve_extensive_form


def main() -> None:
    solution = solve_extensive_form()
    print(f"objective={solution.objective:.3f}")
    print(f"capacity_expansion={solution.capacity_expansion:.3f}")
    print(f"stage2_low={solution.stage2_production_low:.3f}")
    print(f"stage2_high={solution.stage2_production_high:.3f}")


if __name__ == "__main__":
    main()

def main() -> None:
    from practicelens.evaluation_assets import generate_evaluation_assets

    generated = generate_evaluation_assets()
    for name, path in sorted(generated.items()):
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()

def main() -> None:
    from practicelens.evaluation_showcase import generate_evaluation_showcase

    result = generate_evaluation_showcase()
    print(f"showcase: {result.out_dir}")
    print(f"summary: {result.summary_path}")
    print(f"readme: {result.readme_path}")


if __name__ == "__main__":
    main()

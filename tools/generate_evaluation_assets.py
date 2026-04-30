from practicelens.evaluation_assets import generate_evaluation_assets


if __name__ == "__main__":
    generated = generate_evaluation_assets()
    for name, path in sorted(generated.items()):
        print(f"{name}: {path}")
